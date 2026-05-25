<template>
  <div class="profile-page" v-if="user">
    <div class="profile-card">
      <div class="avatar" :style="{ background: user.avatar_color || '#002EA6' }">{{ user.display_name?.[0] || '?' }}</div>
      <h2>{{ user.display_name }}</h2>
      <p class="role-tag">{{ user.role === 'admin' ? '管理员' : '船员' }}</p>

      <div class="stats-row">
        <div class="stat"><strong>{{ stats.total_questions }}</strong><span>问答</span></div>
        <div class="stat"><strong>{{ stats.total_likes }}</strong><span>👍</span></div>
        <div class="stat"><strong>{{ stats.total_dislikes }}</strong><span>👎</span></div>
      </div>
    </div>

    <div class="section">
      <h3>个人设置</h3>
      <div class="field">
        <label>显示名</label>
        <input v-model="form.display_name" />
      </div>
      <div class="field">
        <label>新密码</label>
        <input v-model="form.password" type="password" placeholder="留空则不修改" />
      </div>
      <div class="field">
        <label>头像颜色</label>
        <div class="color-options">
          <span v-for="c in colors" :key="c" :style="{ background: c }" :class="{ active: form.avatar_color === c }" @click="form.avatar_color = c"></span>
        </div>
      </div>
      <button @click="save" :disabled="saving" class="btn-save">{{ saving ? '保存中...' : '保存设置' }}</button>
    </div>

    <button @click="logout" class="btn-logout">退出登录</button>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import api, { authAPI } from '../api/index.js'

const emit = defineEmits(['logout'])
const user = ref(null)
const stats = ref({ total_questions: 0, total_likes: 0, total_dislikes: 0 })
const saving = ref(false)
const colors = ['#002EA6', '#FFE76F', '#52C41A', '#FF4D4F', '#722ED1', '#13C2C2', '#FA8C16']
const form = reactive({ display_name: '', password: '', avatar_color: '#002EA6' })

onMounted(async () => {
  const raw = localStorage.getItem('a21_user')
  if (raw) user.value = JSON.parse(raw)
  form.display_name = user.value?.display_name || ''
  form.avatar_color = user.value?.avatar_color || '#002EA6'
  try {
    const token = localStorage.getItem('a21_token')
    const { data } = await api.get('/user/stats', { params: { token } })
    stats.value = data.stats
  } catch (e) { /* ignore */ }
})

async function save() {
  saving.value = true
  try {
    const token = localStorage.getItem('a21_token')
    await api.put('/user/profile', form, { params: { token } })
    alert('保存成功')
  } catch (e) { alert('保存失败') }
  finally { saving.value = false }
}

function logout() {
  localStorage.removeItem('a21_token')
  localStorage.removeItem('a21_user')
  emit('logout')
}
</script>

<style scoped>
.profile-page { padding: 24px; max-width: 480px; margin: 0 auto; }
.profile-card { text-align: center; padding: 32px 0; }
.avatar { width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; font-size: 32px; color: #fff; font-weight: bold; }
.profile-card h2 { font-size: 22px; color: #1A1A2E; }
.role-tag { display: inline-block; padding: 2px 12px; background: #F0F4FF; color: #002EA6; border-radius: 12px; font-size: 12px; margin: 8px 0; }
.stats-row { display: flex; justify-content: center; gap: 32px; margin-top: 20px; }
.stat { text-align: center; }
.stat strong { display: block; font-size: 24px; color: #002EA6; }
.stat span { font-size: 12px; color: #999; }
.section { background: #fff; border-radius: 12px; padding: 24px; margin-top: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.section h3 { font-size: 16px; margin-bottom: 16px; color: #002EA6; }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; margin-bottom: 6px; color: #666; }
.field input { width: 100%; padding: 10px 14px; border: 2px solid #E8ECF1; border-radius: 8px; font-size: 14px; outline: none; }
.field input:focus { border-color: #002EA6; }
.color-options { display: flex; gap: 10px; }
.color-options span { width: 28px; height: 28px; border-radius: 50%; cursor: pointer; border: 3px solid transparent; transition: transform 0.2s; }
.color-options span.active { border-color: #1A1A2E; transform: scale(1.2); }
.btn-save { width: 100%; padding: 12px; background: linear-gradient(135deg, #002EA6, #0040D0); color: #fff; border: none; border-radius: 10px; font-size: 15px; cursor: pointer; font-weight: 600; }
.btn-logout { display: block; margin: 20px auto; padding: 10px 32px; background: #fff; color: #FF4D4F; border: 2px solid #FF4D4F; border-radius: 10px; cursor: pointer; font-size: 14px; }
</style>
