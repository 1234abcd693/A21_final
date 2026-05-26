/**
 * A21 前端 API 封装层
 * =====================
 * 
 * 基于 axios 的统一 HTTP 客户端 + 原生 fetch 的 SSE 流式支持。
 * 
 * 架构：
 *   - api (axios instance)       — 基础 HTTP 客户端（baseURL + timeout + headers）
 *   - askStream()                — SSE 流式问答（fetch API，返回 ReadableStream reader）
 *   - symptomsAPI / graphAPI / ... — 按功能分组的快捷方法
 * 
 * 认证：
 *   - 登录后 token 存在 localStorage('a21_token')
 *   - authAPI.me() 通过 URL query param 传 token（TODO: 改为 Authorization header）
 * 
 * 错误处理：
 *   - 当前为最小化实现，业务层自己 try/catch
 *   - 建议：后续添加 axios interceptor 统一处理 401/503
 */

import axios from 'axios'

// ==================== Axios 基础实例 ====================
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',  // 后端 FastAPI 地址
  timeout: 30000,                           // 30 秒超时（SSE 流式不受此限制）
  headers: { 'Content-Type': 'application/json' },
})

export default api

// ==================== 流式问答（SSE） ====================
/**
 * SSE 流式问答 — 核心问答接口。
 * 
 * 为什么不用 axios 而用原生 fetch？
 *   - axios 不支持 ReadableStream body.getReader()
 *   - SSE 需要逐块读取响应，fetch 的 body.getReader() 是原生支持
 *   - axios 的 onDownloadProgress 不能处理 SSE 格式
 * 
 * 调用方用法（见 App.vue send()）：
 *   const reader = await askStream(question, options)
 *   while (true) {
 *     const { done, value } = await reader.read()
 *     if (done) break
 *     // 解析 SSE 文本流，逐行处理 "data: ..." 事件
 *   }
 * 
 * @param {string} question - 用户问题
 * @param {object} options - { mode: "chat"|"keyword", session_id, context_nodes, history }
 * @returns {ReadableStreamDefaultReader} — SSE 流的 reader
 */
export async function askStream(question, options = {}) {
  const response = await fetch('http://localhost:8000/api/v1/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      mode: options.mode || 'chat',
      session_id: options.session_id || null,
      context_nodes: options.context_nodes || [],
      history: options.history || [],  // 多轮对话历史 [{role, content}, ...]
    }),
  })
  return response.body.getReader()  // 返回 ReadableStream reader
}

// ==================== API 分组快捷方法 ====================

/** 故障现象联想 — 输入框实时搜索提示 */
export const symptomsAPI = {
  search: (keyword) => api.get('/symptoms', { params: { keyword, limit: 10 } }),
}

/** 知识图谱操作 — 搜索/节点详情/展开/全貌 */
export const graphAPI = {
  search: (q) => api.get('/graph/search', { params: { q, limit: 10 } }),
  node: (uid) => api.get(`/graph/node/${uid}`),
  expand: (uid) => api.get(`/graph/expand/${uid}`),
  overview: () => api.get('/graph/overview'),
}

/** 用户认证 — 登录/注册/个人信息/用户管理 */
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  // TODO: token 应通过 Authorization header 传递，而非 URL query param
  me: (token) => api.get('/auth/me', { params: { token } }),
  users: () => api.get('/users'),
  deleteUser: (id) => api.delete(`/users/${id}`),
}

/** 反馈评价 — 点赞/点踩 + 触发参数优化 */
export const feedbackAPI = {
  submit: (data) => api.post('/feedback', data),
  optimize: () => api.post('/optimize'),
}

/** 历史对话 — CRUD + 搜索/置顶/批量删除 */
export const historyAPI = {
  list: (params) => api.get('/history', { params }),
  search: (params) => api.get('/history/search', { params }),
  detail: (sid) => api.get(`/history/${sid}`),
  delete: (sid) => api.delete(`/history/${sid}`),
  pin: (sid, pinned) => api.patch(`/history/${sid}`, { pinned }),
  batchDelete: (ids) => api.delete('/history/batch', { data: { session_ids: ids } }),
}

/** 数据同步 — U盘导出/导入知识包 */
export const syncAPI = {
  export: () => api.get('/export', { responseType: 'blob' }),  // 二进制流下载
  import: (file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/import', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
}

/** 语音转文字 — 上传录音 → Vosk 转文字 */
export const transcribeAPI = {
  send: (audioBlob) => {
    const form = new FormData()
    form.append('audio', audioBlob)
    return api.post('/transcribe', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
}
