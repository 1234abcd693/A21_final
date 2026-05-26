<template>
  <div class="ap"><div v-if="!verified" class="gate"><h3>🔒 管理员验证</h3><input v-model="pw" type="password" placeholder="请输入管理员密码" @keyup.enter="verify"/><button @click="verify">验证</button><p v-if="err" class="err">{{err}}</p></div>
    <div v-else><div class="hd"><h2>⚙️ 用户管理</h2><button @click="show=!show" class="add">{{show?'取消':'+ 添加'}}</button></div>
    <div v-if="show" class="fm"><div class="r"><input v-model="a.username" placeholder="用户名"/><input v-model="a.password" type="password" placeholder="密码"/><input v-model="a.display_name" placeholder="显示名"/><select v-model="a.role"><option value="user">船员</option><option value="admin">管理员</option></select><button @click="addUser" class="s">注册</button></div></div>
    <div class="tb"><div class="rh"><span>ID</span><span>用户名</span><span>显示名</span><span>角色</span><span></span></div><div v-for="u in users" :key="u.id" class="rr"><span>{{u.id}}</span><span>{{u.username}}</span><span>{{u.display_name}}</span><span :class="u.role">{{u.role==='admin'?'管理员':'船员'}}</span><span><button v-if="u.role!=='admin'" @click="del(u.id)" class="del">删除</button></span></div></div></div>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { authAPI } from '../api/index.js'
const verified=ref(false),pw=ref(''),err=ref(''),users=ref([]),show=ref(false),a=reactive({username:'',password:'',display_name:'',role:'user'})
function verify(){if(pw.value==='admin123'){verified.value=true}else{err.value='密码错误'}}
onMounted(async()=>{if(verified.value){const{data}=await authAPI.users();users.value=data.users||[]}})
async function addUser(){if(!a.username||!a.password)return alert('请填写完整');await authAPI.register({...a});a.username=a.password=a.display_name='';show.value=false;const{data}=await authAPI.users();users.value=data.users||[]}
async function del(id){if(!confirm('确定删除？'))return;await authAPI.deleteUser(id);const{data}=await authAPI.users();users.value=data.users||[]}
</script>
<style scoped>
.ap{padding:24px;max-width:800px;margin:0 auto}
.gate{text-align:center;padding:40px}.gate h3{margin-bottom:16px;color:#002EA6}.gate input{padding:10px 14px;border:2px solid #E8ECF1;border-radius:8px;font-size:15px;width:240px;outline:none;margin-right:8px}.gate input:focus{border-color:#002EA6}.gate button{padding:10px 20px;background:#002EA6;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600}.err{color:#FF4D4F;margin-top:8px;font-size:13px}
.hd{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}h2{font-size:18px;color:#002EA6}
.add{padding:8px 18px;background:#FFE76F;color:#002EA6;border:none;border-radius:8px;cursor:pointer;font-weight:600}
.fm{background:#FFFDF0;padding:14px;border-radius:10px;margin-bottom:16px}.r{display:flex;gap:8px}.r input,.r select{padding:8px 12px;border:2px solid #E8ECF1;border-radius:6px;font-size:13px;outline:none;flex:1}.r input:focus,.r select:focus{border-color:#002EA6}
.s{padding:8px 16px;background:#002EA6;color:#fff;border:none;border-radius:6px;cursor:pointer}
.tb{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.04)}
.rh{display:grid;grid-template-columns:50px 1fr 1fr 80px 60px;padding:14px 20px;background:#F0F4FF;color:#002EA6;font-weight:600;font-size:13px;gap:8px}
.rr{display:grid;grid-template-columns:50px 1fr 1fr 80px 60px;padding:12px 20px;border-bottom:1px solid #F5F7FA;font-size:14px;align-items:center;gap:8px}
.del{padding:4px 12px;background:#fff;color:#FF4D4F;border:1px solid #FF4D4F;border-radius:4px;cursor:pointer;font-size:12px}
</style>
