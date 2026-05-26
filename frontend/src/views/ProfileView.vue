<template>
  <div class="profile-page">
    <div class="tabs"><button :class="{a:tab==='info'}" @click="tab='info'">个人资料</button><button :class="{a:tab==='settings'}" @click="tab='settings'">设置</button><button :class="{a:tab==='sync'}" @click="tab='sync'">数据同步</button></div>
    <div v-if="tab==='info'" class="tab-content"><div class="card"><div class="avatar" :style="{bg:user?.avatar_color||'#002EA6'}">{{user?.display_name?.[0]||'?'}}</div><h2>{{user?.display_name}}</h2><span class="role" :class="user?.role">{{user?.role==='admin'?'管理员':'船员'}}</span><div class="stats"><div class="st"><strong>{{s.total_questions||0}}</strong><span>问答</span></div><div class="st"><strong>{{s.total_likes||0}}</strong><span>👍</span></div><div class="st"><strong>{{s.total_dislikes||0}}</strong><span>👎</span></div></div></div></div>
    <div v-if="tab==='settings'" class="tab-content"><div class="card"><div class="f"><label>显示名</label><input v-model="f.display_name"/></div><div class="f"><label>新密码</label><input v-model="f.password" type="password" placeholder="留空不修改"/></div><div class="f"><label>头像颜色</label><div class="colors"><span v-for="c in colors" :key="c" :style="{bg:c}" :class="{a:f.avatar_color===c}" @click="f.avatar_color=c"></span></div></div><button @click="save" :disabled="saving" class="btn">{{saving?'保存中…':'保存'}}</button></div></div>
    <div v-if="tab==='sync'" class="tab-content"><div class="card"><h3>数据同步</h3><p class="desc">将知识库导出到 U 盘，或从 U 盘导入</p><div class="sync-btns"><button @click="exportData" class="btn-e">📤 导出知识包</button><button @click="triggerImport" class="btn-i">📥 导入知识包</button><input type="file" ref="fileInput" accept=".zip" style="display:none" @change="importData"/></div><p v-if="syncMsg" class="msg">{{syncMsg}}</p></div></div>
    <button @click="logout" class="btn-out">退出登录</button>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import api, { authAPI, syncAPI } from '../api/index.js'
const emit=defineEmits(['logout'])
const tab=ref('info'),user=ref(null),s=ref({}),saving=ref(false),syncMsg=ref(''),fileInput=ref(null)
const colors=['#002EA6','#FFE76F','#52C41A','#FF4D4F','#722ED1','#13C2C2','#FA8C16']
const f=reactive({display_name:'',password:'',avatar_color:'#002EA6'})
onMounted(async()=>{try{user.value=JSON.parse(localStorage.getItem('a21_user')||'{}');f.display_name=user.value.display_name||'';f.avatar_color=user.value.avatar_color||'#002EA6';const{data}=await api.get('/user/stats',{params:{token:localStorage.getItem('a21_token')}});s.value=data.stats}catch(e){}})
async function save(){saving.value=true;try{await api.put('/user/profile',f,{params:{token:localStorage.getItem('a21_token')}});alert('已保存')}catch(e){alert('保存失败')}finally{saving.value=false}}
async function exportData(){try{const r=await syncAPI.export();const url=URL.createObjectURL(r.data);const a=document.createElement('a');a.href=url;a.download='a21_sync.zip';a.click();syncMsg.value='导出成功'}catch(e){syncMsg.value='导出失败'}}
function triggerImport(){fileInput.value?.click()}
async function importData(e){const file=e.target.files[0];if(!file)return;try{await syncAPI.import(file);syncMsg.value='导入成功'}catch(err){syncMsg.value='导入失败'}}
function logout(){localStorage.removeItem('a21_token');localStorage.removeItem('a21_user');emit('logout')}
</script>
<style scoped>
.profile-page{padding:20px;max-width:560px;margin:0 auto}
.tabs{display:flex;gap:4px;margin-bottom:20px;background:#F0F2F5;border-radius:10px;padding:4px}
.tabs button{flex:1;padding:10px;border:none;background:transparent;border-radius:8px;cursor:pointer;font-size:14px;color:#666;transition:all .2s}
.tabs button.a{background:#fff;color:#002EA6;font-weight:600;box-shadow:0 1px 4px rgba(0,0,0,0.08)}
.card{background:#fff;border-radius:12px;padding:24px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.04)}
.avatar{width:72px;height:72px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:28px;color:#fff;font-weight:700}
h2{font-size:20px;color:#1A1A2E;margin-bottom:4px}
.role{display:inline-block;padding:2px 12px;border-radius:12px;font-size:12px;margin:4px 0;background:#F0F4FF;color:#002EA6}
.role.admin{background:#FFFDF0;color:#B8860B}
.stats{display:flex;justify-content:center;gap:32px;margin-top:20px}
.st{text-align:center}.st strong{display:block;font-size:22px;color:#002EA6}.st span{font-size:12px;color:#999}
.f{margin-bottom:16px;text-align:left}
.f label{display:block;font-size:13px;color:#666;margin-bottom:6px}
.f input{width:100%;padding:10px 14px;border:2px solid #E8ECF1;border-radius:8px;font-size:14px;outline:none}
.f input:focus{border-color:#002EA6}
.colors{display:flex;gap:10px}.colors span{width:28px;height:28px;border-radius:50%;cursor:pointer;border:3px solid transparent;transition:transform .2s}
.colors span.a{border-color:#1A1A2E;transform:scale(1.2)}
.btn{width:100%;padding:12px;background:linear-gradient(135deg,#002EA6,#0040D0);color:#fff;border:none;border-radius:10px;font-size:15px;cursor:pointer;font-weight:600}
.btn:disabled{opacity:.5}
.btn-out{display:block;margin:20px auto 0;padding:10px 32px;background:transparent;color:#FF4D4F;border:2px solid #FF4D4F;border-radius:10px;cursor:pointer;font-size:14px}
.desc{color:#999;font-size:13px;margin:8px 0 20px}
.sync-btns{display:flex;gap:10px;justify-content:center}
.btn-e,.btn-i{padding:10px 20px;border-radius:8px;border:2px solid #002EA6;background:#fff;color:#002EA6;cursor:pointer;font-weight:600;font-size:14px}
.btn-e:hover,.btn-i:hover{background:#F0F4FF}
.msg{margin-top:12px;color:#52C41A;font-size:13px}
.tab-content{min-height:200px}
</style>
