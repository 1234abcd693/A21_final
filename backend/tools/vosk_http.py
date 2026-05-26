"""
Vosk 语音识别 HTTP 服务（简化版）
POST /transcribe - 接收 WAV 音频，返回文本
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
import json
import wave
import io
from pathlib import Path
import os

MODEL_DIR = Path(os.getenv("VOSK_MODEL_DIR", str(Path(__file__).parent.parent.parent / "model" / "vosk-model-small-cn-0.22")))
SAMPLE_RATE = 16000

app = FastAPI()
model = None

def get_model():
    global model
    if model is None:
        from vosk import Model
        model = Model(str(MODEL_DIR))
    return model

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    try:
        data = await audio.read()
        # 解析 WAV
        wav = io.BytesIO(data)
        # 跳过 WAV 头，读原始 PCM
        wf = wave.open(wav, 'rb')
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            return JSONResponse({"text": "", "error": "需要 16kHz 单声道 16bit WAV"}, status_code=400)
        pcm = wf.readframes(wf.getnframes())
        wf.close()

        # Vosk 识别
        m = get_model()
        rec = m.create_recognizer(SAMPLE_RATE)
        rec.SetWords(True)
        if rec.AcceptWaveform(pcm):
            result = json.loads(rec.Result())
        else:
            result = json.loads(rec.FinalResult())
        return {"text": result.get("text", "").strip()}
    except Exception as e:
        return JSONResponse({"text": "", "error": str(e)}, status_code=500)

if __name__ == "__main__":
    if not MODEL_DIR.exists():
        print(f"[ERROR] Vosk model not found: {MODEL_DIR}")
        print(f"Download: https://alphacephei.com/vosk/models → vosk-model-small-cn-0.22.zip")
        exit(1)
    print(f"[vosk-http] Model: {MODEL_DIR}")
    print(f"[vosk-http] Server: http://127.0.0.1:8765/transcribe")
    uvicorn.run(app, host="127.0.0.1", port=8765)
