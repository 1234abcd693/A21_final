<template>
  <div class="login-page">
    <div class="login-card">
      <div class="brand">
        <svg width="48" height="48" viewBox="0 0 48 48">
          <circle cx="24" cy="24" r="22" fill="none" stroke="#002EA6" stroke-width="3"/>
          <path d="M16 20 L24 14 L32 20 L28 20 L28 34 L20 34 L20 20 Z" fill="#FFE76F" stroke="#002EA6" stroke-width="1.5"/>
        </svg>
        <h1>A21 船舶故障诊断系统</h1>
        <p>智能问答 · 知识图谱 · 离线运行</p>
      </div>

      <div class="form">
        <div class="field">
          <label>用户名</label>
          <input v-model="username" placeholder="请输入用户名" @keyup.enter="login" />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" @keyup.enter="login" />
        </div>
        <div class="remember">
          <label><input type="checkbox" v-model="remember" /> 记住密码</label>
        </div>
        <button class="btn-login" @click="login" :disabled="loading">{{ loading ? '登录中...' : '登 录' }}</button>
        <p v-if="error" class="error">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { authAPI } from '../api/index.js'

const emit = defineEmits(['login-success'])
const username = ref('admin')
const password = ref('')
const remember = ref(false)
const loading = ref(false)
const error = ref('')

async function login() {
  if (!username.value || !password.value) { error.value = '请输入用户名和密码'; return }
  loading.value = true; error.value = ''
  try {
    const { data } = await authAPI.login({ username: username.value, password: password.value })
    localStorage.setItem('a21_token', data.token)
    if (remember.value) localStorage.setItem('a21_auto', username.value + ':' + password.value)
    localStorage.setItem('a21_user', JSON.stringify(data.user))
    emit('login-success', data)
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #002EA6 0%, #001A5C 100%); }
.login-card { background: #fff; border-radius: 16px; padding: 48px 40px; width: 420px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.brand { text-align: center; margin-bottom: 32px; }
.brand h1 { font-size: 22px; color: #002EA6; margin: 16px 0 4px; }
.brand p { font-size: 13px; color: #666; }
.field { margin-bottom: 20px; }
.field label { display: block; font-size: 13px; color: #333; margin-bottom: 6px; font-weight: 500; }
.field input { width: 100%; padding: 12px 14px; border: 2px solid #E8ECF1; border-radius: 10px; font-size: 15px; transition: border-color 0.2s; outline: none; }
.field input:focus { border-color: #002EA6; }
.remember { margin-bottom: 20px; font-size: 13px; color: #666; }
.btn-login { width: 100%; padding: 14px; background: linear-gradient(135deg, #002EA6, #0040D0); color: #fff; border: none; border-radius: 10px; font-size: 16px; cursor: pointer; font-weight: 600; transition: transform 0.2s; }
.btn-login:hover:not(:disabled) { transform: translateY(-2px); }
.btn-login:disabled { opacity: 0.5; cursor: not-allowed; }
.error { color: #FF4D4F; text-align: center; margin-top: 12px; font-size: 13px; }
</style>
