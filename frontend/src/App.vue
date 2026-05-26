<template>
  <div v-if="v==='login'" class="login-page">
    <div class="login-card">
      <svg w="40" h="40" viewBox="0 0 48 48"><circle cx="24" cy="24" r="22" fill="none" stroke="#002EA6" stroke-width="2.5"/><path d="M16 20 L24 14 L32 20 L28 20 L28 34 L20 34 L20 20 Z" fill="#FFE76F"/></svg>
      <h1>A21 船舶故障诊断</h1>
      <div class="f"><input v-model="u" placeholder="用户名" @keyup.enter="login"/></div>
      <div class="f"><input v-model="p" type="password" placeholder="密码" @keyup.enter="login"/></div>
      <button @click="login" :disabled="ld" class="btn">{{ld?'登录中…':'登 录'}}</button>
      <p v-if="er" class="er">{{er}}</p>
    </div>
  </div>
  <div v-else class="app">
    <Sidebar :current="v" @nav="v=$event" @logout="v='login'" />
    <div class="main">
      <ChatView v-if="v==='chat'" />
      <GraphView v-if="v==='graph'" @node-click="onN" />
      <ProfileModal v-if="v==='profile'" @close="v='chat'" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import ChatView from './components/ChatView.vue'
import GraphView from './components/GraphView.vue'
import ProfileModal from './components/ProfileModal.vue'
import { authAPI } from './api/index.js'

const v=ref(localStorage.getItem('a21_token')?'chat':'login')
const u=ref('admin'),p=ref(''),ld=ref(false),er=ref('')

async function login(){
  if(!u.value||!p.value){er.value='请输入用户名和密码';return}
  ld.value=true;er.value=''
  try{const{data}=await authAPI.login({username:u.value,password:p.value});localStorage.setItem('a21_token',data.token);localStorage.setItem('a21_user',JSON.stringify(data.user));v.value='chat'}catch(e){er.value='登录失败'}finally{ld.value=false}
}

function onN(n){}
</script>

<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:#FAFAFA;color:#1A1A2E}
.app{display:flex;height:100vh;background:#FAFAFA}
.main{flex:1;overflow:hidden;display:flex;flex-direction:column}
.login-page{display:flex;align-items:center;justify-content:center;height:100vh;background:#F5F5F5}
.login-card{background:#fff;border-radius:16px;padding:48px 40px;width:380px;box-shadow:0 2px 20px rgba(0,0,0,0.06);text-align:center}
.login-card svg{margin-bottom:20px}
.login-card h1{font-size:20px;color:#1A1A2E;margin-bottom:28px;font-weight:600}
.f{margin-bottom:14px}.f input{width:100%;padding:11px 14px;border:1.5px solid #E5E7EB;border-radius:8px;font-size:14px;outline:none}.f input:focus{border-color:#002EA6}
.btn{width:100%;padding:12px;background:#002EA6;color:#fff;border:none;border-radius:8px;font-size:15px;cursor:pointer;font-weight:500;margin-top:4px}.btn:disabled{opacity:.5}
.er{color:#EF4444;margin-top:10px;font-size:13px}
</style>
