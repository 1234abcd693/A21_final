"""
ChromaDB 智能重建脚本 v2.0
===========================
策略: KG引导提取 + 滑动窗口分块 + 噪音清洗 + KG元数据关联

重建流程:
  1. 从 Neo4j 获取所有 Symptom/Cause/Step 节点及其 source_page
  2. 在源文本中搜索每个实体名，提取上下文窗口（前后各300字）
  3. 对全文进行滑动窗口分块（300字窗口，50字重叠）作为通用知识补充
  4. 所有文本清洗（去图片标记、表格、目录）
  5. bge-base-zh-v1.5 生成 embedding
  6. 写入 ChromaDB，metadata 关联 Neo4j UID

输出: data/chroma_db/ (覆盖旧数据)
"""

import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from core.config import settings
from sentence_transformers import SentenceTransformer


def clean_text(text: str) -> str:
    """清洗文本噪音"""
    # 去掉图片标记
    text = re.sub(r'\[Image:.*?\]', '', text)
    # 去掉目录行
    text = re.sub(r'^\[目录\].*$', '', text, flags=re.MULTILINE)
    # 去掉纯表格线
    text = re.sub(r'^[\|\-\+\=]+$', '', text, flags=re.MULTILINE)
    # 去掉页码标记
    text = re.sub(r'\*p\.\d+\*', '', text)
    # 合并多余空白
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    # 去掉太短的碎片行（单字符或无意义短行）
    lines = text.split('\n')
    lines = [l for l in lines if len(l.strip()) > 3 or re.search(r'[\u4e00-\u9fff]', l)]
    text = '\n'.join(lines)
    return text.strip()


def sliding_window_chunks(text: str, window: int = 300, overlap: int = 50) -> list[str]:
    """滑动窗口分块，确保不在句子中间切断"""
    # 先按句子边界切分
    sentences = re.split(r'(?<=[。！？\n])\s*', text)
    chunks = []
    current = ""
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        if len(current) + len(sent) > window and len(current) > overlap:
            chunks.append(current.strip())
            # 保留最后一句作为重叠
            overlap_text = current[-overlap:] if len(current) > overlap else current
            current = overlap_text + sent
        else:
            current += sent
    if current.strip() and len(current.strip()) > 30:
        chunks.append(current.strip())
    return chunks


def extract_kg_contexts(source_text: str) -> list[dict]:
    """从 Neo4j KG 提取实体相关的文本上下文"""
    try:
        from kg.neo4j_client import _get_driver
        with _get_driver().session() as session:
            # 获取所有 Symptom（带 source_page）
            symptoms = session.run("""
                MATCH (s:Symptom)
                WHERE s.name IS NOT NULL
                RETURN s.uid AS uid, s.name AS name, labels(s)[0] AS label,
                       s.source_page AS source_page
            """).data()

            # 获取 Cause 和 Step
            causes = session.run("""
                MATCH (c:Cause) WHERE c.name IS NOT NULL
                RETURN c.uid AS uid, c.name AS name, 'Cause' AS label
                LIMIT 50
            """).data()

            steps = session.run("""
                MATCH (st:Step) WHERE st.name IS NOT NULL
                RETURN st.uid AS uid, st.name AS name, 'Step' AS label
                LIMIT 50
            """).data()

        all_entities = symptoms + causes + steps
        print(f"  KG entities: {len(symptoms)} symptoms + {len(causes)} causes + {len(steps)} steps")
    except Exception as e:
        print(f"  WARNING: Could not read KG entities: {e}")
        return []

    contexts = []
    seen_texts = set()

    for entity in all_entities:
        name = entity.get("name", "")
        if not name or len(name) < 3:
            continue

        # 在源文本中搜索实体名
        for m in re.finditer(re.escape(name), source_text):
            start = max(0, m.start() - 300)
            end = min(len(source_text), m.end() + 300)
            ctx = source_text[start:end]

            # 去重（相同文本去重）
            ctx_hash = hash(ctx[:100])
            if ctx_hash in seen_texts:
                continue
            seen_texts.add(ctx_hash)

            contexts.append({
                "entity_uid": entity.get("uid", ""),
                "entity_name": name,
                "entity_label": entity.get("label", "Unknown"),
                "source_page": entity.get("source_page", ""),
                "text": ctx,
            })

    print(f"  Extracted {len(contexts)} KG-linked contexts")
    return contexts


def make_chunks(contexts: list[dict], source_text: str) -> list[dict]:
    """将 KG 上下文 + 全文滑动窗口合并为最终 chunk 列表"""
    chunks = []

    # 1. KG 上下文 → 滑动窗口分块
    for ctx in contexts:
        text = clean_text(ctx["text"])
        if len(text) < 50:
            continue
        sub_chunks = sliding_window_chunks(text, window=300, overlap=50)
        for i, sc in enumerate(sub_chunks):
            chunks.append({
                "text": sc,
                "entity_uid": ctx["entity_uid"],
                "entity_name": ctx["entity_name"],
                "entity_label": ctx["entity_label"],
                "source": "kg_context",
                "source_page": ctx["source_page"],
            })

    # 2. 全文滑动窗口（补充通用知识）
    cleaned_full = clean_text(source_text)
    full_chunks = sliding_window_chunks(cleaned_full, window=300, overlap=50)
    added = 0
    for fc in full_chunks:
        if len(fc) < 50:
            continue
        chunks.append({
            "text": fc,
            "entity_uid": "",
            "entity_name": "",
            "entity_label": "",
            "source": "full_text",
            "source_page": "",
        })
        added += 1
    print(f"  Added {added} full-text chunks")

    # 去重
    seen = set()
    unique = []
    for c in chunks:
        key = c["text"][:80]
        if key not in seen:
            seen.add(key)
            unique.append(c)

    print(f"  Final chunks: {len(unique)} (after dedup, was {len(chunks)})")
    return unique


def embed_and_store(chunks: list[dict], output_path: str):
    """生成 embedding 并写入 ChromaDB"""
    print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
    # 使用绝对路径避免工作目录问题
    model_path = settings.EMBEDDING_MODEL
    if not os.path.isabs(model_path):
        model_path = str(BASE_DIR / "model" / "bge-base-zh-v1.5")
    embedder = SentenceTransformer(model_path)

    # 清空旧 collection
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    os.makedirs(output_path, exist_ok=True)
    client = chromadb.PersistentClient(
        path=output_path,
        settings=ChromaSettings(anonymized_telemetry=False),
    )

    # 删除旧 collection，重新创建
    try:
        client.delete_collection("knowledge_chunks")
        print("  Deleted old collection")
    except Exception:
        pass

    collection = client.create_collection(
        name="knowledge_chunks",
        metadata={
            "description": "船舶故障诊断知识库 v2.0 - KG关联重建",
            "embedding_model": settings.EMBEDDING_MODEL,
            "hnsw:space": "cosine",
        },
    )

    # 批量编码 + 写入
    BATCH_SIZE = 32
    total = len(chunks)
    print(f"Embedding {total} chunks (batch_size={BATCH_SIZE})...")

    for start in range(0, total, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total)
        batch = chunks[start:end]

        texts = [c["text"] for c in batch]
        embeddings = embedder.encode(texts, normalize_embeddings=True).tolist()
        ids = [f"chunk_v2_{start + i:05d}" for i in range(len(batch))]
        metadatas = [{
            "entity_uid": c.get("entity_uid") or "",
            "entity_name": c.get("entity_name") or "",
            "entity_label": c.get("entity_label") or "",
            "source": c.get("source") or "",
            "source_page": c.get("source_page") or "",
        } for c in batch]

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        pct = (end * 100) // total
        print(f"  [{pct:3d}%] {end}/{total} chunks")

    print(f"Done! Collection size: {collection.count()}")
    return collection.count()


def main():
    data_file = BASE_DIR / "data" / "raw" / "船舶电气设备维护与修理_增强.txt"
    if not data_file.exists():
        print(f"ERROR: {data_file}")
        sys.exit(1)

    print("=" * 50)
    print("ChromaDB 智能重建 v2.0")
    print("=" * 50)

    # Step 1: 加载源文本
    print("\n[1/4] Loading source text...")
    with open(data_file, 'r', encoding='utf-8') as f:
        source_text = f.read()
    print(f"  {len(source_text)} chars")

    # Step 2: KG 引导提取
    print("\n[2/4] Extracting KG-linked contexts...")
    contexts = extract_kg_contexts(source_text)

    # Step 3: 分块
    print("\n[3/4] Chunking...")
    chunks = make_chunks(contexts, source_text)

    # Step 4: 嵌入 + 存储
    print("\n[4/4] Embedding + storing...")
    chroma_path = settings.CHROMA_PERSIST_PATH  # 使用 config 中的路径
    count = embed_and_store(chunks, chroma_path)

    print(f"\n{'='*50}")
    print(f"Rebuild complete: {count} chunks in {chroma_path}")
    print("Restart backend to use new ChromaDB.")


if __name__ == "__main__":
    main()
