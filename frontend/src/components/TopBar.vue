<template>
  <div class="tb"><div class="lo" @click="$emit('nav','home')"><svg w="26" h="26" viewBox="0 0 48 48"><circle cx="24" cy="24" r="22" fill="none" stroke="#FFE76F" stroke-width="3"/><path d="M16 20 L24 14 L32 20 L28 20 L28 34 L20 34 L20 20 Z" fill="#FFE76F" stroke="#FFE76F" stroke-width="1"/></svg><span>A21 船舶故障诊断</span></div>
    <div class="s"><input v-model="q" :placeholder="kwMode?'输入关键词搜索...':'搜索实体、故障...'" @keyup.enter="onS"/><button @click="onS">🔍</button></div>
    <div class="n"><button :class="{a:v==='home'}" @click="$emit('nav','home')">图谱</button><button :class="{a:v==='history'}" @click="$emit('nav','history')">历史</button><button :class="{a:v==='profile'}" @click="$emit('nav','profile')">个人</button><button v-if="isA" :class="{a:v==='admin'}" @click="$emit('nav','admin')">管理</button><button class="c" @click="$emit('toggleChat')">💬</button></div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue';const p=defineProps({currentView:String});const emit=defineEmits(['search','nav','toggleChat']);const q=ref('');const kwMode=ref(false);const isA=computed(()=>{try{return JSON.parse(localStorage.getItem('a21_user')||'{}').role==='admin'}catch{return false}})
function onS(){if(q.value.trim()){emit('search',q.value.trim());q.value=''}}
</script>
<style scoped>
.tb{display:flex;align-items:center;padding:0 18px;height:56px;background:linear-gradient(135deg,#002EA6,#001A5C);color:#fff;gap:14px;z-index:100}
.lo{display:flex;align-items:center;gap:8px;cursor:pointer;white-space:nowrap}.lo span{font-size:15px;font-weight:700}
.s{flex:1;display:flex;max-width:400px}.s input{flex:1;padding:7px 14px;border:none;border-radius:8px 0 0 8px;outline:none;font-size:13px;background:rgba(255,255,255,0.12);color:#fff}.s input::placeholder{color:rgba(255,255,255,0.5)}.s button{padding:7px 14px;border:none;border-radius:0 8px 8px 0;background:#FFE76F;color:#002EA6;cursor:pointer;font-weight:600}
.n{display:flex;gap:2px}.n button{background:none;border:none;color:rgba(255,255,255,0.7);padding:7px 12px;border-radius:8px;cursor:pointer;font-size:13px;transition:.2s}.n button:hover,.n button.a{background:rgba(255,255,255,0.1);color:#fff}.c{background:#FFE76F!important;color:#002EA6!important;font-weight:700!important;padding:7px 16px!important}
</style>
