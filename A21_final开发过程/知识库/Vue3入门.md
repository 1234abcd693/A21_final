# Vue 3 入门

## 一句话解释

Vue = 把网页**拆成积木块**，每块管自己的事，拼起来就是一个完整界面。

## 类比：搭乐高

传统网页写法：一整块画布，到处画东西，改一处可能影响到别处。

Vue 写法：每个 UI 零件是一个独立的"组件"（Component），像一个乐高积木。每个积木有自己的外观和行为，拼在一起就是完整的界面。

```
┌─────────────────────────────────────────┐
│  App.vue（总框架）                        │
│  ┌─────────────┐  ┌───────────────────┐ │
│  │ Sidebar.vue │  │ ChatWindow.vue    │ │
│  │ 知识库列表   │  │ ┌───────────────┐ │ │
│  │ 上传按钮     │  │ │ MessageBubble │ │ │
│  │ 设置按钮     │  │ │ (用户消息)     │ │ │
│  │             │  │ ├───────────────┤ │ │
│  │             │  │ │ MessageBubble │ │ │
│  │             │  │ │ (AI回复+引用)  │ │ │
│  │             │  │ ├───────────────┤ │ │
│  │             │  │ │ InputBox.vue  │ │ │
│  │             │  │ │ 输入框+发送    │ │ │
│  └─────────────┘  │ └───────────────┘ │ │
│                    └───────────────────┘ │
└─────────────────────────────────────────┘
```

每个 `.vue` 文件就是一个组件，包含三部分：

```vue
<template>
  <!-- HTML：这个组件长什么样 -->
  <div class="message-bubble">
    <p>{{ message.text }}</p>
    <button @click="like">👍</button>
  </div>
</template>

<script setup>
  // JavaScript：这个组件能干什么
  import { ref } from 'vue'
  const message = ref({ text: '发动机无法启动怎么办？' })
  function like() {
    // 发送点赞请求到后端
  }
</script>

<style scoped>
  /* CSS：这个组件什么配色 */
  .message-bubble {
    background: #f0f0f0;
    border-radius: 8px;
    padding: 10px;
  }
</style>
```

## 核心概念（你需要的全部）

### 1. 组件 (Component)

可复用的 UI 积木块。你的项目大概需要这些组件：

| 组件 | 功能 |
|------|------|
| `ChatWindow.vue` | 聊天主界面，管理消息列表 |
| `MessageBubble.vue` | 单条消息气泡，支持引用悬浮 |
| `InputBox.vue` | 输入框 + 发送按钮 |
| `GraphView.vue` | 知识图谱可视化（力导向图） |
| `UploadPanel.vue` | 文档上传 + 抽取预览 |
| `FeedbackButtons.vue` | 点赞/点踩按钮组 |
| `HistoryPanel.vue` | 历史对话列表 |

### 2. 响应式数据 (Reactive Data)

数据变了，界面自动更新 —— 不用手动操作 DOM。

```vue
<script setup>
import { ref } from 'vue'

const count = ref(0)  // 定义一个响应式变量

function add() {
  count.value++  // 改数据
  // 界面上用到 count 的地方自动更新！
}
</script>

<template>
  <p>当前计数：{{ count }}</p>
  <button @click="add">+1</button>
</template>
```

### 3. 事件处理

`@click`、`@input` 等，和普通 HTML 的 `onclick` 一样直觉。

```vue
<button @click="sendMessage">发送</button>
<input @keyup.enter="sendMessage" v-model="inputText" />
```

### 4. v-model（双向绑定）

输入框的内容和变量自动同步：

```vue
<input v-model="question" />
<!-- 用户输入 "发动机漏油" → question 变量自动变成 "发动机漏油" -->
<!-- question 变量改成别的 → 输入框自动显示新内容 -->
```

### 5. v-for（列表渲染）

```vue
<ul>
  <li v-for="msg in messages" :key="msg.id">
    {{ msg.text }}
  </li>
</ul>
<!-- messages 数组有 3 条消息 → 渲染 3 个 <li> -->
```

### 6. v-if（条件渲染）

```vue
<div v-if="loading">加载中...</div>
<div v-else>加载完成</div>
```

## 和 Python 后端怎么通信

用 `axios` 库（类似 Python 的 `requests`）：

```javascript
import axios from 'axios'

// 发送问答请求（流式 SSE）
async function askQuestion(question) {
  const response = await fetch('http://localhost:8000/api/v1/ask', {
    method: 'POST',
    body: JSON.stringify({ question }),
  })
  // 流式读取 SSE 响应...
}

// 发送反馈
async function sendFeedback(msgId, rating) {
  await axios.post('http://localhost:8000/api/v1/feedback', {
    message_id: msgId,
    rating: rating,  // 1 或 -1
  })
}
```

## 学习路线（按优先级）

1. **Vue 3 教程（官方）**：看前三章就够了（组件基础、响应式、模板语法）
2. **Vite**：用 Vite 创建项目（一行命令）
3. **axios**：发 HTTP 请求（5 分钟学会）
4. **Element Plus**：UI 组件库（按钮、输入框、对话框直接用现成的）

不需要学 TypeScript（先用纯 JavaScript），不需要学 Vuex/Pinia（项目小，用简单方案）。

## 和传统 web 开发的区别

| 传统方式 | Vue 方式 |
|----------|----------|
| `document.getElementById()` 手动改 DOM | 改数据，DOM 自己更新 |
| HTML、CSS、JS 分三个文件 | 一个 `.vue` 文件搞定一个组件 |
| 页面刷新才能看到新数据 | 数据变了界面瞬间更新（响应式） |
