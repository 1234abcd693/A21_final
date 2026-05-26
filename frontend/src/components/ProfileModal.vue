<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal"><div class="hd"><h3>个人设置</h3><button @click="$emit('close')" class="x">✕</button></div>
    <div class="user-info"><div class="av" :style="{bg:u?.avatar_color||'#002EA6'}">{{u?.display_name?.[0]||'?'}}</div><div><strong>{{u?.display_name}}</strong><p>{{u?.role==='admin'?'管理员':'船员'}}</p></div></div>
    <div class="f"><label>显示名</label><input v-model="dn"/></div>
    <div class="f"><label>新密码</label><input v-model="pw" type="password" placeholder="留空不修改"/></div>
    <button @click="save" class="btn">保存</button>
    <button @click="logout" class="btn-out">退出登录</button>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';import api from '../api/index.js'
const emit=defineEmits(['close'])
const u=ref({}),dn=ref(''),pw=ref('')
onMounted(()=>{try{u.value=JSON.parse(localStorage.getItem('a21_user')||'{}');dn.value=u.value.display_name||''}catch{}})
async function save(){try{await api.put('/user/profile',{display_name:dn.value,password:pw.value||undefined},{params:{token:localStorage.getItem('a21_token')}});alert('已保存')}catch{}} 
function logout(){localStorage.removeItem('a21_token');localStorage.removeItem('a21_user');location.reload()}
</script>
<style scoped>
.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;z-index:100}
.modal{background:#fff;border-radius:16px;padding:28px;width:400px;max-height:80vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,0.15)}
.hd{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}.hd h3{font-size:18px;color:#1A1A2E}.x{background:none;border:none;font-size:18px;cursor:pointer;color:#999}
.user-info{display:flex;align-items:center;gap:14px;margin-bottom:24px;padding:14px;background:#F9FAFB;border-radius:10px}.av{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;font-weight:600}strong{font-size:15px}p{font-size:12px;color:#999;margin-top:2px}
.f{margin-bottom:14px}.f label{display:block;font-size:13px;color:#666;margin-bottom:4px}.f input{width:100%;padding:10px 14px;border:1.5px solid #E5E7EB;border-radius:8px;font-size:14px;outline:none}.f input:focus{border-color:#002EA6}
.btn{width:100%;padding:11px;background:#002EA6;color:#fff;border:none;border-radius:8px;font-size:14px;cursor:pointer;font-weight:500;margin-bottom:10px}
.btn-out{width:100%;padding:11px;background:transparent;color:#EF4444;border:1.5px solid #EF4444;border-radius:8px;cursor:pointer;font-size:14px}
</style>
