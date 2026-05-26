<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-bg" @click.self="$emit('update:modelValue', false)">
      <div class="modal">
        <h3>个人设置</h3>
        <input
          :value="dispName"
          @input="$emit('update:dispName', $event.target.value)"
          placeholder="显示名"
          class="inp"
        />
        <input
          :value="newPass"
          @input="$emit('update:newPass', $event.target.value)"
          type="password"
          placeholder="新密码(留空不修改)"
          class="inp"
        />
        <button @click="$emit('save')" class="btn">保存</button>
        <button @click="$emit('logout')" class="btn-out">退出登录</button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  dispName: { type: String, default: '' },
  newPass: { type: String, default: '' }
})

defineEmits(['update:modelValue', 'update:dispName', 'update:newPass', 'save', 'logout'])
</script>

<style scoped>
.modal-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.modal {
  background: #1E2A4A;
  border-radius: 16px;
  padding: 30px;
  width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.modal h3 {
  font-size: 18px;
  color: #fff;
  margin-bottom: 16px;
}
.btn {
  width: 100%;
  padding: 12px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
  margin-bottom: 10px;
}
.btn-out {
  width: 100%;
  padding: 12px;
  background: transparent;
  color: #EF4444;
  border: 1px solid #EF4444;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
}
</style>
