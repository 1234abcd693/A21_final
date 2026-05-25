<template>
  <div class="topbar">
    <div class="logo" @click="$emit('nav', 'home')">
      <svg width="28" height="28" viewBox="0 0 48 48"><circle cx="24" cy="24" r="22" fill="none" stroke="#FFE76F" stroke-width="3"/><path d="M16 20 L24 14 L32 20 L28 20 L28 34 L20 34 L20 20 Z" fill="#FFE76F" stroke="#FFE76F" stroke-width="1"/></svg>
      <span>A21 船舶故障诊断</span>
    </div>
    <div class="search-box">
      <input v-model="query" placeholder="搜索实体、故障、关键词..." @keyup.enter="onSearch" />
      <button @click="onSearch">🔍</button>
    </div>
    <div class="nav">
      <button :class="{ active: currentView === 'home' }" @click="$emit('nav', 'home')">图谱</button>
      <button :class="{ active: currentView === 'history' }" @click="$emit('nav', 'history')">历史</button>
      <button :class="{ active: currentView === 'profile' }" @click="$emit('nav', 'profile')">个人</button>
      <button v-if="isAdmin" :class="{ active: currentView === 'admin' }" @click="$emit('nav', 'admin')">管理</button>
      <button class="btn-chat" @click="$emit('toggleChat')">💬 问答</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
const props = defineProps({ currentView: String })
const emit = defineEmits(['search', 'nav', 'toggleChat'])
const query = ref('')
const isAdmin = computed(() => { try { return JSON.parse(localStorage.getItem('a21_user') || '{}').role === 'admin' } catch { return false } })
function onSearch() { if (query.value.trim()) emit('search', query.value.trim()) }
</script>

<style scoped>
.topbar { display: flex; align-items: center; padding: 0 20px; height: 56px; background: linear-gradient(135deg, #002EA6, #001A5C); color: #fff; gap: 16px; position: relative; z-index: 100; }
.logo { display: flex; align-items: center; gap: 10px; cursor: pointer; white-space: nowrap; }
.logo span { font-size: 16px; font-weight: 700; }
.search-box { flex: 1; display: flex; max-width: 420px; }
.search-box input { flex: 1; padding: 8px 14px; border: none; border-radius: 8px 0 0 8px; outline: none; font-size: 14px; background: rgba(255,255,255,0.15); color: #fff; }
.search-box input::placeholder { color: rgba(255,255,255,0.5); }
.search-box button { padding: 8px 14px; border: none; border-radius: 0 8px 8px 0; background: #FFE76F; color: #002EA6; cursor: pointer; font-weight: 600; }
.nav { display: flex; gap: 4px; }
.nav button { background: none; border: none; color: rgba(255,255,255,0.75); padding: 8px 14px; border-radius: 8px; cursor: pointer; font-size: 13px; transition: all 0.2s; }
.nav button:hover, .nav button.active { background: rgba(255,255,255,0.12); color: #fff; }
.btn-chat { background: #FFE76F !important; color: #002EA6 !important; font-weight: 600 !important; padding: 8px 18px !important; }
</style>
