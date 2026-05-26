<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo">⚓</div>
      <h1>A21 船舶故障诊断</h1>
      <p>智能问答系统</p>

      <!-- Login Mode -->
      <template v-if="!isRegister">
        <input :value="uname" @input="$emit('update:uname', $event.target.value)" placeholder="用户名" class="inp" @keyup.enter="$emit('login')" />
        <input :value="upass" @input="$emit('update:upass', $event.target.value)" type="password" placeholder="密码" class="inp" @keyup.enter="$emit('login')" />
        <button @click="$emit('login')" :disabled="loading" class="lbtn">{{ loading ? '登录中...' : '登 录' }}</button>
      </template>

      <!-- Register Mode -->
      <template v-else>
        <input :value="regUname" @input="regUname=$event.target.value" placeholder="用户名" class="inp" />
        <input :value="regDisp" @input="regDisp=$event.target.value" placeholder="显示名称" class="inp" />
        <input :value="regPass" @input="regPass=$event.target.value" type="password" placeholder="密码" class="inp" />
        <button @click="doRegister" :disabled="regLoading" class="lbtn">{{ regLoading ? '注册中...' : '注 册' }}</button>
      </template>

      <p v-if="err" class="err">{{ err }}</p>
      <p class="toggle" @click="toggleMode">{{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/index.js'

defineProps({
  uname: { type: String, default: '' },
  upass: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  err: { type: String, default: '' }
})

const emit = defineEmits(['update:uname', 'update:upass', 'login', 'registered'])

const isRegister = ref(false)
const regUname = ref('')
const regDisp = ref('')
const regPass = ref('')
const regLoading = ref(false)

function toggleMode() { isRegister.value = !isRegister.value }

async function doRegister() {
  if (!regUname.value || !regPass.value) return
  regLoading.value = true
  try {
    await api.post('/auth/register', {
      username: regUname.value,
      password: regPass.value,
      display_name: regDisp.value || regUname.value
    })
    alert('注册成功！请登录')
    isRegister.value = false
    emit('registered', regUname.value)
  } catch (e) {
    alert('注册失败: ' + (e.response?.data?.detail || e.message))
  } finally { regLoading.value = false }
}
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; height: 100vh; background: linear-gradient(135deg, #1A1A2E, #16213E); }
.login-card { background: #1E2A4A; border-radius: 20px; padding: 48px 40px; width: 400px; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }
.logo { font-size: 48px; margin-bottom: 12px; }
h1 { font-size: 22px; margin-bottom: 4px; color: #fff; }
p { color: var(--sub); font-size: 13px; margin-bottom: 24px; }
.lbtn { width: 100%; padding: 12px; background: var(--accent); color: #fff; border: none; border-radius: 10px; font-size: 15px; cursor: pointer; }
.lbtn:disabled { opacity: .5; }
.toggle { cursor: pointer; color: var(--accent); margin-top: 16px; font-size: 13px; }
.toggle:hover { text-decoration: underline; }
</style>
