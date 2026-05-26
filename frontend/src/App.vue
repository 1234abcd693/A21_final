<template>
  <div v-if="view === 'login'" class="app">
    <LoginView @login-success="onLogin" />
  </div>
  <div v-else class="app">
    <TopBar :currentView="view" @search="onSearch" @nav="view = $event" @toggleChat="chatVisible = !chatVisible" />
    <div class="main-area">
      <HistoryPanel v-if="view === 'history'" @select="onHistorySelect" @close="view = 'home'" />
      <div class="graph-area">
        <GraphPanel ref="graphRef" :highlight-nodes="highlightNodes" @node-click="onNodeClick" />
      </div>
      <div class="detail-area" v-if="view === 'home'">
        <DetailPanel :node="selectedNode" @ask="onAskAbout" />
      </div>
      <div class="detail-area" v-if="view === 'profile'">
        <ProfileView @logout="onLogout" />
      </div>
      <div class="detail-area" v-if="view === 'admin'">
        <AdminView />
      </div>
    </div>
    <ChatPanel v-if="chatVisible" @close="chatVisible = false" @messageSent="onMessageSent" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TopBar from './components/TopBar.vue'
import GraphPanel from './components/GraphPanel.vue'
import DetailPanel from './components/DetailPanel.vue'
import HistoryPanel from './components/HistoryPanel.vue'
import ChatPanel from './components/ChatPanel.vue'
import LoginView from './views/LoginView.vue'
import ProfileView from './views/ProfileView.vue'
import AdminView from './views/AdminView.vue'
import { graphAPI, authAPI } from './api/index.js'

const view = ref(localStorage.getItem('a21_token') ? 'home' : 'login')
const chatVisible = ref(false)
const highlightNodes = ref([])
const selectedNode = ref(null)
const graphRef = ref(null)

// 自动验证已有 token（后端重启后 session 丢失则退到登录）
if (localStorage.getItem('a21_token')) {
  authAPI.me(localStorage.getItem('a21_token')).catch(() => {
    const auto = localStorage.getItem('a21_auto')
    if (auto) {
      const [u, p] = auto.split(':')
      authAPI.login({ username: u, password: p }).then(({ data }) => {
        localStorage.setItem('a21_token', data.token)
        localStorage.setItem('a21_user', JSON.stringify(data.user))
      }).catch(() => { view.value = 'login' })
    } else { view.value = 'login' }
  })
}

function onLogin(data) {
  view.value = 'home'
}
function onLogout() {
  view.value = 'login'
}

function onSearch(query) {
  graphAPI.search(query).then(({ data }) => {
    highlightNodes.value = data.results?.map(r => r.uid) || []
  })
}
function onNodeClick(node) { selectedNode.value = node }
function onAskAbout() { chatVisible.value = true }
function onHistorySelect(session) { view.value = 'home'; /* TODO: 加载历史对话 */ }
function onMessageSent() {}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
.app { display: flex; flex-direction: column; height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #F5F7FA; color: #1A1A2E; }
.main-area { display: flex; flex: 1; overflow: hidden; }
.graph-area { flex: 1; min-width: 0; }
.detail-area { width: 380px; border-left: 1px solid #E8ECF1; overflow-y: auto; background: #fff; }
</style>
