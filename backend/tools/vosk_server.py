"""
Vosk 语音识别 WebSocket 服务器
实时流式识别，支持中文
启动: python tools/vosk_server.py
"""

import asyncio
import json
import os
import sys
import websockets
from pathlib import Path

# 模型路径
MODEL_DIR = Path(os.getenv("VOSK_MODEL_DIR", str(Path(__file__).parent.parent.parent / "model" / "vosk-model-cn")))
SAMPLE_RATE = 16000

model = None
rec = None

def get_model():
    global model
    if model is None:
        from vosk import Model
        model = Model(str(MODEL_DIR))
    return model

async def handler(websocket):
    global rec
    print(f"[vosk] Client connected")
    m = get_model()
    rec = m.create_recognizer(SAMPLE_RATE)
    rec.SetWords(True)
    
    try:
        async for message in websocket:
            if isinstance(message, bytes):
                if rec.AcceptWaveform(message):
                    result = json.loads(rec.Result())
                    await websocket.send(json.dumps({"type": "final", "text": result.get("text", "")}))
                else:
                    partial = json.loads(rec.PartialResult())
                    text = partial.get("partial", "")
                    if text:
                        await websocket.send(json.dumps({"type": "partial", "text": text}))
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # 发送最终结果
        final = json.loads(rec.FinalResult())
        await websocket.send(json.dumps({"type": "final", "text": final.get("text", "")}))
        print("[vosk] Client disconnected")

async def main():
    if not MODEL_DIR.exists():
        print(f"\n[ERROR] Vosk model not found: {MODEL_DIR}")
        print(f"Download from: https://alphacephei.com/vosk/models")
        print(f"Chinese small model: vosk-model-small-cn-0.22.zip (~42MB)")
        print(f"Extract to: {MODEL_DIR}\n")
        sys.exit(1)
    
    print(f"[vosk] Model: {MODEL_DIR}")
    print(f"[vosk] Server starting on ws://127.0.0.1:8765")
    async with websockets.serve(handler, "127.0.0.1", 8765, max_size=2**20):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())
