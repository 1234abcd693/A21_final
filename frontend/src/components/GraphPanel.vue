<template>
  <div class="graph-panel" ref="container">
    <div v-if="loading" class="loading">加载图谱...</div>
    <svg ref="svgRef"></svg>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { graphAPI } from '../api/index.js'

const props = defineProps({
  highlightNodes: { type: Array, default: () => [] },
})
const emit = defineEmits(['node-click'])
const loading = ref(true)
const container = ref(null)
const svgRef = ref(null)
const nodes = ref([])
const edges = ref([])

onMounted(async () => {
  try {
    const { data } = await graphAPI.overview()
    nodes.value = data.nodes || []
    edges.value = data.edges || []
  } catch (e) {
    console.error('图谱加载失败:', e)
  } finally {
    loading.value = false
  }
})

watch(() => props.highlightNodes, (ids) => {
  // 简化：高亮逻辑可通过 D3 selection 实现
})
</script>

<style scoped>
.graph-panel { width: 100%; height: 100%; position: relative; background: #f5f5f5; }
.loading { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); color: #999; }
svg { width: 100%; height: 100%; }
</style>
