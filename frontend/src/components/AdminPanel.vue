<template>
  <div class="admin-panel">
    <h2>管理员后台</h2>

    <!-- Auth check -->
    <div v-if="!authorized" class="auth-box">
      <label>请输入管理员密码：</label>
      <input v-model="adminPass" type="password" class="inp" placeholder="管理员密码" @keydown.enter="checkAdmin" />
      <button @click="checkAdmin" class="btn-primary" :disabled="checking">{{ checking ? '验证中...' : '验证' }}</button>
      <div v-if="authErr" class="err">{{ authErr }}</div>
    </div>

    <!-- User list -->
    <div v-else>
      <div class="user-table">
        <div class="table-header">
          <span class="col-id">ID</span>
          <span class="col-name">用户名</span>
          <span class="col-disp">显示名</span>
          <span class="col-role">角色</span>
          <span class="col-time">创建时间</span>
          <span class="col-actions">操作</span>
        </div>
        <div v-for="u in users" :key="u.id" class="table-row">
          <span class="col-id">{{ u.id }}</span>
          <span class="col-name">{{ u.username }}</span>
          <span class="col-disp">{{ u.display_name }}</span>
          <span class="col-role">
            <select :value="u.role" @change="changeRole(u, $event.target.value)" class="role-select">
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
          </span>
          <span class="col-time">{{ formatTime(u.created_at) }}</span>
          <span class="col-actions">
            <button @click="deleteUser(u)" class="btn-danger-sm" :disabled="u.role==='admin'">删除</button>
          </span>
        </div>
      </div>
      <div class="user-count">共 {{ users.length }} 个用户</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'

const authorized = ref(false)
const adminPass = ref('')
const checking = ref(false)
const authErr = ref('')
const users = ref([])

async function checkAdmin() {
  checking.value = true; authErr.value = ''
  try {
    await api.post('/auth/admin-verify', { password: adminPass.value })
    authorized.value = true
    loadUsers()
  } catch { authErr.value = '密码错误' }
  finally { checking.value = false }
}

async function loadUsers() {
  try { const { data } = await api.get('/users'); users.value = data.users || [] } catch {}
}

async function deleteUser(u) {
  if (!confirm('确定删除用户: ' + u.username + '?')) return
  try { await api.delete('/users/' + u.id); loadUsers() } catch {}
}

async function changeRole(u, newRole) {
  try {
    await api.put('/users/' + u.id + '/role', null, { params: { role: newRole, token: localStorage.getItem('a21_token') } })
    loadUsers()
  } catch {}
}

function formatTime(t) { return t ? t.replace('T',' ').slice(0,16) : '' }

onMounted(() => {})
</script>

<style scoped>
.admin-panel { padding: 30px; max-width: 900px; margin: 0 auto; }
.admin-panel h2 { font-size: 22px; color: #fff; margin-bottom: 20px; }
.auth-box { padding: 20px; background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 10px; max-width: 400px; }
.auth-box label { display: block; font-size: 14px; color: var(--sub); margin-bottom: 10px; }
.inp { width: 100%; padding: 10px 14px; background: rgba(255,255,255,0.06); border: 1px solid var(--border); border-radius: 8px; color: #fff; font-size: 14px; outline: none; margin-bottom: 10px; }
.inp:focus { border-color: var(--accent); }
.btn-primary { padding: 8px 20px; background: var(--accent); border: none; border-radius: 8px; color: #fff; cursor: pointer; font-size: 14px; }
.btn-primary:disabled { opacity: .5; }
.err { color: #EF4444; font-size: 13px; margin-top: 8px; }
.user-table { margin-top: 16px; }
.table-header, .table-row { display: flex; gap: 8px; padding: 10px 12px; border-bottom: 1px solid var(--border); font-size: 13px; align-items: center; }
.table-header { color: var(--sub); font-weight: 600; background: rgba(255,255,255,0.02); border-radius: 8px 8px 0 0; }
.table-row { color: var(--text); }
.table-row:hover { background: rgba(255,255,255,0.02); }
.col-id { width: 40px; }
.col-name { width: 100px; }
.col-disp { width: 100px; }
.col-role { width: 80px; }
.col-time { flex: 1; min-width: 130px; }
.col-actions { width: 60px; text-align: right; }
.role-select { padding: 4px 8px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 4px; color: #fff; font-size: 12px; }
.btn-danger-sm { padding: 4px 10px; background: transparent; border: 1px solid #EF4444; border-radius: 4px; color: #EF4444; cursor: pointer; font-size: 11px; }
.btn-danger-sm:hover { background: rgba(239,68,68,0.1); }
.btn-danger-sm:disabled { opacity: .3; cursor: not-allowed; }
.user-count { margin-top: 12px; font-size: 13px; color: var(--sub); }
</style>
