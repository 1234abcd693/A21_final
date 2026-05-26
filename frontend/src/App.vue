<template>
  <div v-if="v==='login'" class="app"><LoginView @login-success="onLogin"/></div>
  <div v-else class="app"><TopBar :currentView="v" @search="onS" @nav="v=$event" @toggleChat="cv=!cv"/>
    <div class="ma"><HistoryPanel v-if="v==='history'" @select="onH" @close="v='home'"/>
      <div class="ga"><GraphPanel ref="gr" :highlight-nodes="hn" @node-click="onN"/></div>
      <div class="da" v-if="v==='home'||v==='profile'||v==='admin'">
        <DetailPanel v-if="v==='home'" :node="sn" @ask="onA"/>
        <ProfileView v-if="v==='profile'" @logout="onL"/>
        <AdminView v-if="v==='admin'"/>
      </div></div>
    <ChatPanel v-if="cv" @close="cv=false" @messageSent="onM"/></div>
</template>
<script setup>
import { ref } from 'vue'
import TopBar from './components/TopBar.vue';import GraphPanel from './components/GraphPanel.vue';import DetailPanel from './components/DetailPanel.vue'
import HistoryPanel from './components/HistoryPanel.vue';import ChatPanel from './components/ChatPanel.vue'
import LoginView from './views/LoginView.vue';import ProfileView from './views/ProfileView.vue';import AdminView from './views/AdminView.vue'
import { graphAPI, authAPI } from './api/index.js'
const v=ref(localStorage.getItem('a21_token')?'home':'login'),cv=ref(false),hn=ref([]),sn=ref(null)
if(localStorage.getItem('a21_token')){authAPI.me(localStorage.getItem('a21_token')).catch(()=>{const a=localStorage.getItem('a21_auto');if(a){const[u,p]=a.split(':');authAPI.login({username:u,password:p}).then(({data})=>{localStorage.setItem('a21_token',data.token);localStorage.setItem('a21_user',JSON.stringify(data.user))}).catch(()=>v.value='login')}else v.value='login'})}
function onLogin(d){v.value='home'}
function onL(){v.value='login'}
function onS(q){graphAPI.search(q).then(({data})=>{hn.value=data.results?.map(r=>r.uid)||[]})}
function onN(n){sn.value=n}
function onA(){cv.value=true}
function onH(s){v.value='home'}
function onM(){}
</script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
.app{display:flex;flex-direction:column;height:100vh;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:#F5F7FA;color:#1A1A2E}
.ma{display:flex;flex:1;overflow:hidden}.ga{flex:1;min-width:0}.da{width:380px;border-left:1px solid #E8ECF1;overflow-y:auto;background:#fff}
</style>
