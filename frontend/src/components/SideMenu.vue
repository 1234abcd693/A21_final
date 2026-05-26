<template>
  <aside class="sidebar">
    <button @click="$emit('new-chat')" class="new-btn">+ 新对话</button>
    <nav class="conv-list">
      <div
        v-for="c in conversations"
        :key="c.id"
        @click="$emit('load-chat', c.id)"
        :class="['conv-item', { active: c.id === activeId }]"
      >
        <span class="conv-icon">💬</span>
        <span class="conv-title">{{ c.title || '新对话' }}</span>
        <button @click.stop="$emit('del-conv', c.id)" class="del-btn">×</button>
      </div>
      <div v-if="!conversations.length" class="empty">暂无对话记录</div>
    </nav>
    <div class="sidebar-foot">
      <div class="user-bar" @click="$emit('toggle-profile')">
        <span class="avatar">{{ userName?.charAt(0) || '?' }}</span>
        <span class="username">{{ userName || '用户' }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  conversations: { type: Array, default: () => [] },
  activeId: { type: String, default: '' },
  userName: { type: String, default: '' }
})

defineEmits(['new-chat', 'load-chat', 'del-conv', 'toggle-profile'])
</script>

<style scoped>
.sidebar {
  width: 280px;
  background: var(--sb);
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border);
}
.new-btn {
  margin: 14px;
  padding: 10px;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  transition: all .2s;
}
.new-btn:hover {
  background: rgba(255,255,255,0.06);
}
.conv-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}
.conv-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all .15s;
  gap: 8px;
}
.conv-item:hover {
  background: rgba(255,255,255,0.04);
}
.conv-item.active {
  background: rgba(83,52,131,0.2);
}
.conv-icon {
  font-size: 14px;
}
.conv-title {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text);
}
.del-btn {
  background: none;
  border: none;
  color: var(--sub);
  cursor: pointer;
  font-size: 16px;
  opacity: 0;
  transition: opacity .2s;
}
.conv-item:hover .del-btn {
  opacity: 1;
}
.del-btn:hover {
  color: #EF4444;
}
.empty {
  padding: 20px;
  text-align: center;
  color: var(--sub);
  font-size: 13px;
}
.sidebar-foot {
  padding: 12px;
  border-top: 1px solid var(--border);
}
.user-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
}
.user-bar:hover {
  background: rgba(255,255,255,0.04);
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}
.username {
  font-size: 14px;
  color: var(--text);
}
</style>
