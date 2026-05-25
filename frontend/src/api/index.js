import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

export default api

// 流式问答（SSE）
export async function askStream(question, options = {}) {
  const response = await fetch('http://localhost:8000/api/v1/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      mode: options.mode || 'chat',
      session_id: options.session_id || null,
      context_nodes: options.context_nodes || [],
      history: options.history || [],
    }),
  })
  return response.body.getReader()
}

// 快捷方法
export const symptomsAPI = {
  search: (keyword) => api.get('/symptoms', { params: { keyword, limit: 10 } }),
}

export const graphAPI = {
  search: (q) => api.get('/graph/search', { params: { q, limit: 10 } }),
  node: (uid) => api.get(`/graph/node/${uid}`),
  expand: (uid) => api.get(`/graph/expand/${uid}`),
  overview: () => api.get('/graph/overview'),
}

export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  me: (token) => api.get('/auth/me', { params: { token } }),
  users: () => api.get('/users'),
  deleteUser: (id) => api.delete(`/users/${id}`),
}

export const feedbackAPI = {
  submit: (data) => api.post('/feedback', data),
  optimize: () => api.post('/optimize'),
}

export const historyAPI = {
  list: (params) => api.get('/history', { params }),
  search: (params) => api.get('/history/search', { params }),
  detail: (sid) => api.get(`/history/${sid}`),
  delete: (sid) => api.delete(`/history/${sid}`),
  pin: (sid, pinned) => api.patch(`/history/${sid}`, { pinned }),
  batchDelete: (ids) => api.delete('/history/batch', { data: { session_ids: ids } }),
}

export const syncAPI = {
  export: () => api.get('/export', { responseType: 'blob' }),
  import: (file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/import', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
}

export const transcribeAPI = {
  send: (audioBlob) => {
    const form = new FormData()
    form.append('audio', audioBlob)
    return api.post('/transcribe', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
}
