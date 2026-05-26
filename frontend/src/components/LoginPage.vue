<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo">⚓</div>
      <h1>A21 船舶故障诊断</h1>
      <p>智能问答系统</p>
      <input
        :value="uname"
        @input="$emit('update:uname', $event.target.value)"
        placeholder="用户名"
        class="inp"
        @keyup.enter="$emit('login')"
      />
      <input
        :value="upass"
        @input="$emit('update:upass', $event.target.value)"
        type="password"
        placeholder="密码"
        class="inp"
        @keyup.enter="$emit('login')"
      />
      <button @click="$emit('login')" :disabled="loading" class="lbtn">
        {{ loading ? '登录中...' : '登 录' }}
      </button>
      <p v-if="err" class="err">{{ err }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  uname: { type: String, default: '' },
  upass: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  err: { type: String, default: '' }
})

defineEmits(['update:uname', 'update:upass', 'login'])
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(135deg, #1A1A2E, #16213E);
}
.login-card {
  background: #1E2A4A;
  border-radius: 20px;
  padding: 48px 40px;
  width: 400px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.logo {
  font-size: 48px;
  margin-bottom: 12px;
}
h1 {
  font-size: 22px;
  margin-bottom: 4px;
  color: #fff;
}
p {
  color: var(--sub);
  font-size: 13px;
  margin-bottom: 24px;
}
.lbtn {
  width: 100%;
  padding: 12px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  cursor: pointer;
}
.lbtn:disabled {
  opacity: .5;
}
</style>
