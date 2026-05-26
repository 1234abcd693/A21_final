# Vosk 离线语音识别

## 是什么

Vosk 是一个**完全离线**的语音识别工具包，支持 20+ 种语言（含中文）。模型小巧（42MB），CPU 就能跑。

## 和 whisper.cpp 的区别

| | whisper.cpp | Vosk |
|------|-----------|------|
| 模型大小 | 142MB | **42MB** |
| 中文准确率 | 中等 | **较好** |
| 流式识别 | 需要完整音频 | ✅ **边说边出字** |
| 部署方式 | 独立 exe | Python 库 |

## 我们的用法

```
用户点击 🎤 → MediaRecorder 录制 → 点击停止 → WAV 发送到 Vosk → 返回文字 → 填入输入框
```

Vosk 服务跑在 `http://localhost:8765`，通过 HTTP POST 接收音频文件。

## 模型下载

中文小模型 42MB：
```
https://alphacephei.com/vosk/models → vosk-model-small-cn-0.22.zip
解压到: A21_final\model\vosk-model-small-cn-0.22\
```
