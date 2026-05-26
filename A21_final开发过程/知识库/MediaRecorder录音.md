# MediaRecorder 浏览器录音

## 是什么

浏览器内置 API，可以录制麦克风音频，不需要任何插件。

## 基本用法

```javascript
// 1. 获取麦克风权限
const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

// 2. 创建录音器
const recorder = new MediaRecorder(stream)
const chunks = []
recorder.ondataavailable = e => chunks.push(e.data)  // 收集音频数据
recorder.onstop = () => {
  const blob = new Blob(chunks, { type: 'audio/webm' })  // 最终音频文件
  // 发送给后端...
}

// 3. 开始/停止
recorder.start()   // 开始录音
recorder.stop()    // 停止录音
```

## 在我们的项目中

点击 🎤 → `recorder.start()` → 按钮变红脉冲 → 再点 ⏹ → `recorder.stop()` → 音频 blob 发送到 Vosk HTTP → 文字填入输入框。
