<template>
  <details class="trace-card">
    <summary>
      🟢🟡🔴 可信度: {{ confidenceLabel }} ({{ traceability.keywords_matched || 0 }}/{{ traceability.keywords_total || 0 }})
    </summary>
    <div class="trace-content">
      <div v-for="c in citations" :key="c.num" class="trace-item">
        <p><strong>[{{ c.num }}]</strong> {{ c.doc_name }} — {{ c.page }}</p>
        <p v-if="c.graph_nodes?.length" class="graph-link">
          图谱节点: {{ c.graph_nodes.join(', ') }}
        </p>
      </div>
    </div>
  </details>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ traceability: Object, citations: Array })

const confidenceLabel = computed(() => {
  const c = props.traceability.confidence
  if (c === 'green') return '可信'
  if (c === 'yellow') return '部分可信'
  return '不可信'
})
</script>

<style scoped>
.trace-card { margin-top: 8px; padding: 8px 12px; background: #fffbeb; border-radius: 6px; font-size: 13px; }
.trace-card summary { cursor: pointer; color: #fa8c16; }
.trace-content { margin-top: 8px; }
.trace-item { padding: 6px 0; border-bottom: 1px solid #f0e0b0; }
.graph-link { color: #1890ff; font-size: 12px; margin-top: 4px; }
</style>
