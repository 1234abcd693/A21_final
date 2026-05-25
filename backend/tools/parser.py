"""
文档解析（Word/PDF → 纯文本）
"""

from pathlib import Path
from typing import Optional


def parse_docx(file_path: str) -> str:
    """解析 .docx 文件"""
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())
        return "\n".join(paragraphs)
    except ImportError:
        raise RuntimeError("python-docx 未安装")


def parse_pdf(file_path: str) -> str:
    """解析 .pdf 文件"""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except ImportError:
        raise RuntimeError("pdfplumber 未安装")


def parse_file(file_path: str) -> dict:
    """自动判断文件类型并解析"""
    ext = Path(file_path).suffix.lower()
    if ext == ".docx":
        text = parse_docx(file_path)
    elif ext == ".pdf":
        text = parse_pdf(file_path)
    elif ext == ".txt":
        text = Path(file_path).read_text(encoding="utf-8")
    else:
        raise ValueError(f"不支持的文件格式: {ext}")

    return {
        "file_name": Path(file_path).name,
        "text": text,
        "text_length": len(text),
    }
