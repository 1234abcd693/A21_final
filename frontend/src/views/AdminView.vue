<template>
  <div class="admin-page">
    <div class="header">
      <h2>⚙️ 用户管理</h2>
      <button @click="showAdd = !showAdd" class="btn-add">{{ showAdd ? '取消' : '+ 添加用户' }}</button>
    </div>

    <div v-if="showAdd" class="add-form">
      <div class="row">
        <input v-model="addForm.username" placeholder="用户名" />
        <input v-model="addForm.password" type="password" placeholder="密码" />
        <input v-model="addForm.display_name" placeholder="显示名" />
        <select v-model="addForm.role">
          <option value="user">船员</option>
          <option value="admin">管理员</option>
        </select>
        <button @click="addUser" class="btn-submit">注册</button>
      </div>
    </div>

    <div class="table">
      <div class="row header-row">
        <span>ID</span><span>用户名</span><span>显示名</span><span>角色</span><span>创建时间</span><span></span>
      </div>
      <div v-for="u in users" :key="u.id" class="row">
        <span>{{ u.id }}</span><span>{{ u.username }}</span><span>{{ u.display_name }}</span>
        <span :class="u.role">{{ u.role === 'admin' ? '管理员' : '船员' }}</span>
        <span class="time">{{ (u.created_at || '').slice(0, 16) }}</span>
        <span>
          <button v-if="u.role !== 'admin'" @click="delUser(u.id)" class="btn-del">删除</button>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { authAPI } from '../api/index.js'

const users = ref([])
const showAdd = ref(false)
const addForm = reactive({ username: '', password: '', display_name: '', role: 'user' })

onMounted(async () => {
  const { data } = await authAPI.users()
  users.value = data.users || []
})

async function addUser() {
  if (!addForm.username || !addForm.password) return alert('请填写完整')
  await authAPI.register(addForm)
  addForm.username = addForm.password = addForm.display_name = ''
  showAdd.value = false
  const { data } = await authAPI.users()
  users.value = data.users || []
}

async function delUser(id) {
  if (!confirm('确定删除？')) return
  await authAPI.deleteUser(id)
  const { data } = await authAPI.users()
  users.value = data.users || []
}
</script>

<style scoped>
.admin-page { padding: 24px; max-width: 800px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header h2 { color: #002EA6; font-size: 18px; }
.btn-add { padding: 8px 20px; background: #FFE76F; color: #002EA6; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px; }
.add-form { background: #FFFDF0; padding: 16px; border-radius: 10px; margin-bottom: 20px; }
.add-form .row { display: flex; gap: 10px; }
.add-form input, .add-form select { padding: 8px 12px; border: 2px solid #E8ECF1; border-radius: 6px; font-size: 13px; outline: none; flex: 1; }
.add-form input:focus, .add-form select:focus { border-color: #002EA6; }
.btn-submit { padding: 8px 16px; background: #002EA6; color: #fff; border: none; border-radius: 6px; cursor: pointer; white-space: nowrap; }
.table { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.row { display: grid; grid-template-columns: 50px 1fr 1fr 80px 1fr 60px; padding: 14px 20px; border-bottom: 1px solid #F5F7FA; align-items: center; font-size: 14px; gap: 8px; }
.header-row { background: #F0F4FF; color: #002EA6; font-weight: 600; font-size: 13px; }
.time { color: #999; font-size: 12px; }
.btn-del { padding: 4px 12px; background: #fff; color: #FF4D4F; border: 1px solid #FF4D4F; border-radius: 4px; cursor: pointer; font-size: 12px; }
</style>
