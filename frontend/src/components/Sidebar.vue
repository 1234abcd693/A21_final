<template>
  <div class="sidebar">
    <div class="top">
      <button class="new-chat" @click="$emit('nav','chat')">
        <svg w="16" h="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新对话
      </button>
    </div>
    <div class="nav">
      <button :class="{a:current==='chat'}" @click="$emit('nav','chat')">💬 对话</button>
      <button :class="{a:current==='graph'}" @click="$emit('nav','graph')">🔗 知识图谱</button>
      <button :class="{a:current==='history'}" @click="$emit('nav','history')">📜 历史</button>
    </div>
    <div class="bot">
      <div class="user" @click="$emit('nav','profile')">
        <div class="av" :style="{bg:'#002EA6'}">{{user?.display_name?.[0]||'?'}}</div>
        <span>{{user?.display_name||'用户'}}</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue'
const p=defineProps({current:String})
const emit=defineEmits(['nav','logout'])
const user=computed(()=>{try{return JSON.parse(localStorage.getItem('a21_user')||'{}')}catch{return{}}})
</script>
<style scoped>
.sidebar{width:240px;background:#F9FAFB;border-right:1px solid #F0F0F0;display:flex;flex-direction:column;height:100vh;padding:12px}
.top{margin-bottom:8px}.new-chat{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:10px;background:#002EA6;color:#fff;border:none;border-radius:10px;cursor:pointer;font-size:14px;font-weight:500}
.nav{flex:1;display:flex;flex-direction:column;gap:2px}.nav button{display:flex;align-items:center;gap:8px;width:100%;padding:10px 12px;border:none;border-radius:8px;background:transparent;cursor:pointer;font-size:14px;color:#555;text-align:left;transition:all .15s}.nav button:hover{background:#F0F0F0}.nav button.a{background:#fff;color:#002EA6;font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
.bot{padding-top:12px;border-top:1px solid #F0F0F0}.user{display:flex;align-items:center;gap:10px;padding:8px;border-radius:8px;cursor:pointer;transition:background .15s}.user:hover{background:#F0F0F0}.av{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;font-weight:600}span{font-size:14px;color:#333}
</style>
