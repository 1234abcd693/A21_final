<template>
  <div class="detail-panel">
    <div v-if="!node" class="placeholder">👆 点击图谱节点查看详情</div>
    <div v-else class="content">
      <div class="node-header">
        <span class="label-tag" :style="{ background: colorMap[node.label] || '#002EA6' }">{{ node.label }}</span>
        <h3>{{ node.name }}</h3>
      </div>
      <div class="meta" v-if="node.properties?.source_doc">📄 {{ node.properties.source_doc }}</div>
      <div class="meta" v-if="node.properties?.source_page">📍 {{ node.properties.source_page }}</div>
      <div v-if="node.properties" class="props">
        <div v-for="(v, k) in displayProps" :key="k" class="prop-row"><strong>{{ k }}</strong><span>{{ v }}</span></div>
      </div>
      <div v-if="node.relations" class="relations">
        <h4>关联关系</h4>
        <div v-for="r in node.relations.incoming" :key="r.from_uid" class="rel in">← {{ r.type }} {{ r.from_name }} <span v-if="r.priority" class="pri">[P{{ r.priority }}]</span></div>
        <div v-for="r in node.relations.outgoing" :key="r.to_uid" class="rel out">→ {{ r.type }} {{ r.to_name }} <span v-if="r.priority" class="pri">[P{{ r.priority }}]</span></div>
      </div>
      <button class="ask-btn" @click="$emit('ask', node.name)">💬 以此提问</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ node: Object })
defineEmits(['ask'])
const colorMap = { Equipment: '#002EA6', Symptom: '#FF4D4F', Cause: '#FA8C16', Step: '#52C41A', Precaution: '#722ED1', SparePart: '#13C2C2', Tool: '#8C8C8C' }
const displayProps = computed(() => {
  if (!props.node?.properties) return {}
  const skip = ['uid', 'name', 'source_doc', 'source_page', 'source_author', 'source_publisher', 'created_at']
  return Object.fromEntries(Object.entries(props.node.properties).filter(([k]) => !skip.includes(k)))
})
</script>

<style scoped>
.detail-panel { padding: 20px; height: 100%; overflow-y: auto; }
.placeholder { color: #bbb; text-align: center; padding: 60px 0; font-size: 14px; }
.content {}
.node-header { margin-bottom: 12px; }
.label-tag { display: inline-block; padding: 2px 10px; border-radius: 12px; color: #fff; font-size: 11px; margin-bottom: 8px; }
h3 { font-size: 18px; color: #1A1A2E; }
.meta { color: #888; font-size: 12px; margin: 4px 0; }
.props { margin: 16px 0; background: #F8FAFC; border-radius: 8px; padding: 12px; }
.prop-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; border-bottom: 1px solid #EEE; }
.prop-row strong { color: #002EA6; }
.relations { margin-top: 16px; }
.relations h4 { font-size: 14px; margin-bottom: 8px; color: #002EA6; }
.rel { padding: 6px 10px; margin: 4px 0; border-radius: 6px; font-size: 13px; }
.rel.in { background: #F0F4FF; color: #002EA6; }
.rel.out { background: #FFFDF0; color: #B8860B; }
.pri { font-size: 11px; opacity: 0.6; }
.ask-btn { width: 100%; margin-top: 20px; padding: 12px; background: linear-gradient(135deg, #002EA6, #0040D0); color: #fff; border: none; border-radius: 10px; cursor: pointer; font-size: 15px; font-weight: 600; }
</style>
