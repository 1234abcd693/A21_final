<template>
  <div class="detail-panel">
    <div v-if="!node" class="placeholder">点击图谱节点查看详情</div>
    <div v-else>
      <h3>{{ node.name }}</h3>
      <p><span class="label">{{ node.label }}</span></p>
      <p v-if="node.properties?.source_doc">来源: {{ node.properties.source_doc }}</p>
      <p v-if="node.properties?.source_page">{{ node.properties.source_page }}</p>

      <div v-if="node.relations" class="relations">
        <h4>关联关系</h4>
        <div v-for="rel in node.relations.incoming" :key="rel.from_uid" class="rel-item">
          ← {{ rel.type }} {{ rel.from_name }}
        </div>
        <div v-for="rel in node.relations.outgoing" :key="rel.to_uid" class="rel-item">
          → {{ rel.type }} {{ rel.to_name }}
          <span v-if="rel.priority">[优先级: {{ rel.priority }}]</span>
        </div>
      </div>

      <button class="ask-btn" @click="$emit('ask', node.name)">💬 以此提问</button>
    </div>
  </div>
</template>

<script setup>
defineProps({ node: Object })
defineEmits(['ask'])
</script>

<style scoped>
.detail-panel { padding: 20px; }
.placeholder { color: #999; text-align: center; padding: 40px 0; }
h3 { margin-bottom: 8px; font-size: 18px; }
.label { background: #e6f7ff; color: #1890ff; padding: 1px 8px; border-radius: 4px; font-size: 12px; }
.relations { margin-top: 16px; }
.rel-item { padding: 4px 0; border-bottom: 1px solid #f0f0f0; font-size: 13px; }
.ask-btn { margin-top: 20px; width: 100%; padding: 10px; background: #1890ff; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 15px; }
</style>
