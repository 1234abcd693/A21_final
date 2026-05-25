<template>
  <div class="app-container">
    <TopBar @search="onSearch" @toggleChat="chatVisible = !chatVisible" />
    <div class="main-area">
      <div class="graph-area">
        <GraphPanel ref="graphRef" :highlight-nodes="highlightNodes" @node-click="onNodeClick" />
      </div>
      <div class="detail-area">
        <DetailPanel :node="selectedNode" @ask="onAskAbout" />
      </div>
    </div>
    <ChatPanel
      v-if="chatVisible"
      :session-id="sessionId"
      :context-nodes="contextNodes"
      @message-sent="onMessageSent"
      @close="chatVisible = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TopBar from './components/TopBar.vue'
import GraphPanel from './components/GraphPanel.vue'
import DetailPanel from './components/DetailPanel.vue'
import ChatPanel from './components/ChatPanel.vue'

const graphRef = ref(null)
const chatVisible = ref(false)
const sessionId = ref('sess_' + Date.now())
const highlightNodes = ref([])
const selectedNode = ref(null)
const contextNodes = ref([])

function onSearch(query) {
  import('./api/index.js').then(({ graphAPI }) => {
    graphAPI.search(query).then(({ data }) => {
      highlightNodes.value = data.results.map(r => r.uid)
    })
  })
}

function onNodeClick(node) {
  selectedNode.value = node
}

function onAskAbout() {
  chatVisible.value = true
  contextNodes.value = selectedNode.value ? [selectedNode.value.uid] : []
}

function onMessageSent() {}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
.app-container { display: flex; flex-direction: column; height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.main-area { display: flex; flex: 1; overflow: hidden; }
.graph-area { flex: 1; min-width: 0; }
.detail-area { width: 360px; border-left: 1px solid #e8e8e8; overflow-y: auto; }
</style>
