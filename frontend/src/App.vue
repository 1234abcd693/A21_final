<template>
<div class="app">
  <!-- Login -->
  <div v-if="!loggedIn" class="login-page">
    <div class="login-card">
      <div class="logo">⚓</div>
      <h1>A21 船舶故障诊断</h1>
      <p>智能问答系统</p>
      <input v-model="uname" placeholder="用户名" class="inp" @keyup.enter="doLogin"/>
      <input v-model="upass" type="password" placeholder="密码" class="inp" @keyup.enter="doLogin"/>
      <button @click="doLogin" :disabled="loading" class="lbtn">{{loading?'登录中...':'登 录'}}</button>
      <p v-if="err" class="err">{{err}}</p>
    </div>
  </div>

  <!-- Main -->
  <div v-else class="main-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <button @click="newChat" class="new-btn">+ 新对话</button>
      <nav class="conv-list">
        <div v-for="c in conversations" :key="c.id" @click="loadChat(c.id)" :class="['conv-item',{active:c.id===activeId}]">
          <span class="conv-icon">💬</span>
          <span class="conv-title">{{c.title||'新对话'}}</span>
          <button @click.stop="delConv(c.id)" class="del-btn">×</button>
        </div>
        <div v-if="!conversations.length" class="empty">暂无对话记录</div>
      </nav>
      <div class="sidebar-foot">
        <div class="user-bar" @click="showProfile=!showProfile">
          <span class="avatar">{{userName?.charAt(0)||'?'}}</span>
          <span class="username">{{userName||'用户'}}</span>
        </div>
      </div>
    </aside>

    <!-- Chat -->
    <main class="chat-area">
      <div class="messages" ref="msgRef">
        <div v-if="!messages.length && !streaming" class="welcome">
          <h2>船舶故障智能诊断</h2>
          <p>输入故障现象，获取维修建议</p>
          <div class="examples">
            <button v-for="ex in examples" :key="ex" @click="tx=ex;send()" class="ex-btn">{{ex}}</button>
          </div>
        </div>
        <div v-for="(m,i) in messages" :key="i" :class="['msg',m.role]">
          <div class="msg-content" v-html="m.role==='user'?esc(m.content):renderMd(m.content)"></div>
          <div v-if="m.role==='assistant'" class="msg-actions">
            <button @click="rateMsg(m,1)" :class="{active:m._rating===1}">👍</button>
            <button @click="rateMsg(m,-1)" :class="{active:m._rating===-1}">👎</button>
          </div>
        </div>
        <div v-if="streaming" class="msg assistant">
          <div class="msg-content" v-html="renderMd(streamText)"></div>
          <span class="cursor">▊</span>
        </div>
      </div>

      <div class="input-area">
        <textarea v-model="tx" placeholder="输入故障现象..." @keydown.enter.exact.prevent="send" :disabled="streaming" rows="1" ref="txRef" @input="autoResize"/>
        <button @click="toggleVoice" :class="['voice-btn',{recording}]">{{recording?'⏹':'🎤'}}</button>
        <button @click="send" :disabled="streaming||!tx.trim()" class="send-btn">↑</button>
      </div>
      <div v-if="recording" class="rec-bar">🔴 录音中 {{recTime}}s — 点击⏹停止</div>
    </main>

    <!-- Profile Modal -->
    <Teleport to="body">
      <div v-if="showProfile" class="modal-bg" @click.self="showProfile=false">
        <div class="modal">
          <h3>个人设置</h3>
          <input v-model="dispName" placeholder="显示名" class="inp"/>
          <input v-model="newPass" type="password" placeholder="新密码(留空不修改)" class="inp"/>
          <button @click="saveProfile" class="btn">保存</button>
          <button @click="doLogout" class="btn-out">退出登录</button>
        </div>
      </div>
    </Teleport>
  </div>
</div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import api, { askStream, feedbackAPI, authAPI, historyAPI } from './api/index.js'

// Auth
const loggedIn=ref(!!localStorage.getItem('a21_token'))
const uname=ref('admin'),upass=ref(''),loading=ref(false),err=ref('')
const userName=ref(''),userId=ref(0)

// Chat
const messages=ref([]),tx=ref(''),streaming=ref(false),streamText=ref('')
const conversations=ref([]),activeId=ref('')
const msgRef=ref(null),txRef=ref(null)

// Voice
const recording=ref(false),recTime=ref(0)
let mediaRecorder=null,chunks=[],recTimer=null

// Profile
const showProfile=ref(false),dispName=ref(''),newPass=ref('')

// Examples
const examples=['接触器线圈烧毁怎么修？','电动机不能起动怎么办？','发电机电压异常的原因']

onMounted(async()=>{
  if(loggedIn.value){
    try{const u=JSON.parse(localStorage.getItem('a21_user')||'{}');userName.value=u.display_name||u.username;userId.value=u.id;dispName.value=u.display_name||''}catch{}
    loadConversations()
  }
})

// Auth
async function doLogin(){
  if(!uname.value||!upass.value)return
  loading.value=true;err.value=''
  try{const{data}=await authAPI.login({username:uname.value,password:upass.value});localStorage.setItem('a21_token',data.token);localStorage.setItem('a21_user',JSON.stringify(data.user));loggedIn.value=true;userName.value=data.user.display_name;userId.value=data.user.id;loadConversations()}catch(e){err.value='登录失败'}finally{loading.value=false}
}
function doLogout(){localStorage.clear();loggedIn.value=false;messages.value=[]}

// Conversations
async function loadConversations(){
  try{const{data}=await historyAPI.list({page:1,page_size:100});conversations.value=(data.sessions||[]).map(s=>({id:s.session_id,title:s.title}))}catch{}
}
function newChat(){messages.value=[];activeId.value='sess_'+Date.now();streamText.value='';loadConversations()}
async function loadChat(id){activeId.value=id;try{const{data}=await historyAPI.detail(id);messages.value=(data.messages||[]).map(m=>({id:m.message_id,role:m.role,content:m.content,_rating:0}));scrollBottom()}catch{}}
async function delConv(id){try{await historyAPI.delete(id);if(activeId.value===id){messages.value=[];activeId.value=''};loadConversations()}catch{}}
async function saveConv(q,a){
  if(!activeId.value)return
  try{await api.post('/history/save',{session_id:activeId.value,title:q.slice(0,40),user_msg:q,assistant_msg:a,user_id:userId.value})}catch{}
  loadConversations()
}

// Chat
function esc(s){return(s||'').replace(/</g,'&lt;')}
function renderMd(s){return(s||'').replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/### (.+)/g,'<h3>$1</h3>').replace(/\n\n/g,'</p><p>').replace(/\n/g,'<br>').replace(/^- (.+)/gm,'<li>$1</li>').replace(/\[(\d+)\]/g,'<sup style="color:#06B6D4;font-size:11px">[$1]</sup>')}

async function send(){
  if(!tx.value.trim()||streaming.value)return
  const q=tx.value.trim();tx.value='';txRef.value.style.height='auto'
  messages.value.push({role:'user',content:q,_rating:0})
  streaming.value=true;streamText.value='';await nextTick();scrollBottom()
  try{
    const hist=messages.value.slice(-6).map(m=>({role:m.role,content:m.content}))
    const r=await askStream(q,{mode:'chat',session_id:activeId.value,history:hist})
    const d=new TextDecoder();let b=''
    while(true){const{done,value}=await r.read();if(done)break;b+=d.decode(value,{stream:true});const ls=b.split('\n');b=ls.pop()||'';for(const l of ls){if(l.startsWith('data: ')){streamText.value+=l.slice(6);scrollBottom()}}}
    messages.value.push({role:'assistant',content:streamText.value,_rating:0})
    saveConv(q,streamText.value)
  }catch(e){messages.value.push({role:'assistant',content:'抱歉，生成回答时出错。',_rating:0})}
  finally{streaming.value=false;streamText.value=''}
}

function scrollBottom(){nextTick(()=>{if(msgRef.value)msgRef.value.scrollTop=msgRef.value.scrollHeight})}
function autoResize(){const el=txRef.value;el.style.height='auto';el.style.height=Math.min(el.scrollHeight,120)+'px'}

// Voice
async function toggleVoice(){
  if(recording.value){stopVoice();return}
  try{const s=await navigator.mediaDevices.getUserMedia({audio:true});mediaRecorder=new MediaRecorder(s);chunks=[];recording.value=true;recTime.value=0;recTimer=setInterval(()=>recTime.value++,1000);mediaRecorder.ondataavailable=e=>chunks.push(e.data);mediaRecorder.onstop=async()=>{clearInterval(recTimer);recording.value=false;s.getTracks().forEach(t=>t.stop());try{const b=new Blob(chunks,{type:'audio/webm'});const fd=new FormData();fd.append('audio',b);const{data}=await api.post('http://127.0.0.1:8765/transcribe',fd,{headers:{'Content-Type':'multipart/form-data'}});if(data.text)tx.value=data.text}catch{}};mediaRecorder.start()}catch(e){recording.value=false}}
function stopVoice(){if(mediaRecorder&&mediaRecorder.state==='recording')mediaRecorder.stop()}

// Feedback
async function rateMsg(m,v){m._rating=m._rating===v?0:v;try{await feedbackAPI.submit({message_id:m.id||'',rating:v,question:'',answer_text:m.content,retrieved_chunks:'[]'})}catch{}}

// Profile
async function saveProfile(){try{await api.put('/user/profile',{display_name:dispName.value,password:newPass.value||undefined},{params:{token:localStorage.getItem('a21_token')}});alert('已保存');showProfile.value=false}catch{}}
</script>

<style>
:root{--bg:#1A1A2E;--sb:#16213E;--card:#0F3460;--accent:#533483;--text:#E0E0E0;--sub:#888;--border:#2A2A4A}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:var(--bg);color:var(--text);overflow:hidden}
.app{height:100vh}
/* Login */
.login-page{display:flex;align-items:center;justify-content:center;height:100vh;background:linear-gradient(135deg,#1A1A2E,#16213E)}
.login-card{background:#1E2A4A;border-radius:20px;padding:48px 40px;width:400px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.5)}.logo{font-size:48px;margin-bottom:12px}h1{font-size:22px;margin-bottom:4px;color:#fff}p{color:var(--sub);font-size:13px;margin-bottom:24px}
.inp{width:100%;padding:12px 16px;background:rgba(255,255,255,0.06);border:1px solid var(--border);border-radius:10px;color:#fff;font-size:15px;outline:none;margin-bottom:12px}.inp:focus{border-color:var(--accent)}
.lbtn{width:100%;padding:12px;background:var(--accent);color:#fff;border:none;border-radius:10px;font-size:15px;cursor:pointer}.lbtn:disabled{opacity:.5}.err{color:#EF4444;font-size:13px;margin-top:8px}
/* Layout */
.main-layout{display:flex;height:100vh}
.sidebar{width:280px;background:var(--sb);display:flex;flex-direction:column;border-right:1px solid var(--border)}
.new-btn{margin:14px;padding:10px;background:transparent;color:var(--text);border:1px solid var(--border);border-radius:10px;cursor:pointer;font-size:14px;transition:all .2s}.new-btn:hover{background:rgba(255,255,255,0.06)}
.conv-list{flex:1;overflow-y:auto;padding:0 8px}.conv-item{display:flex;align-items:center;padding:10px 12px;border-radius:8px;cursor:pointer;transition:all .15s;gap:8px}.conv-item:hover{background:rgba(255,255,255,0.04)}.conv-item.active{background:rgba(83,52,131,0.2)}.conv-icon{font-size:14px}.conv-title{flex:1;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text)}.del-btn{background:none;border:none;color:var(--sub);cursor:pointer;font-size:16px;opacity:0;transition:opacity .2s}.conv-item:hover .del-btn{opacity:1}.del-btn:hover{color:#EF4444}
.empty{padding:20px;text-align:center;color:var(--sub);font-size:13px}
.sidebar-foot{padding:12px;border-top:1px solid var(--border)}.user-bar{display:flex;align-items:center;gap:10px;padding:8px;border-radius:8px;cursor:pointer}.user-bar:hover{background:rgba(255,255,255,0.04)}.avatar{width:32px;height:32px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600}.username{font-size:14px;color:var(--text)}
/* Chat */
.chat-area{flex:1;display:flex;flex-direction:column;max-width:860px;margin:0 auto;width:100%}
.messages{flex:1;overflow-y:auto;padding:24px 20px}.welcome{text-align:center;padding:80px 20px}.welcome h2{font-size:24px;color:#fff;margin-bottom:8px}.welcome p{color:var(--sub);font-size:15px;margin-bottom:24px}
.examples{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}.ex-btn{padding:10px 18px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:10px;color:var(--text);cursor:pointer;font-size:13px;transition:all .2s}.ex-btn:hover{background:rgba(83,52,131,0.2);border-color:var(--accent)}
.msg{margin-bottom:28px;padding:0 4px}.msg.user{display:flex;justify-content:flex-end}.msg-content{max-width:85%;padding:14px 20px;border-radius:16px;background:rgba(255,255,255,0.04);line-height:1.7;font-size:15px;color:var(--text)}.msg.user .msg-content{background:var(--accent)}.msg-content :deep(h3){font-size:17px;margin:10px 0 6px;color:#fff}.msg-content :deep(strong){font-weight:600;color:#fff}.msg-content :deep(li){margin:4px 0 4px 20px}.msg-content :deep(p){margin:8px 0}
.msg-actions{display:flex;gap:8px;margin-top:6px;padding-left:4px}.msg-actions button{padding:4px 10px;border:1px solid var(--border);border-radius:6px;background:transparent;color:var(--sub);cursor:pointer;font-size:12px;transition:all .2s}.msg-actions button:hover{border-color:var(--accent)}.msg-actions button.active{border-color:#FFE76F;color:#FFE76F}
.cursor{animation:blink 1s infinite;color:var(--accent);font-size:20px;margin-left:4px}@keyframes blink{50%{opacity:0}}
.input-area{display:flex;gap:10px;padding:14px 20px;align-items:flex-end}textarea{flex:1;padding:14px 18px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:14px;resize:none;outline:none;font-size:15px;color:var(--text);line-height:1.5;font-family:inherit;max-height:120px}textarea:focus{border-color:var(--accent)}
.voice-btn{width:42px;height:42px;border:1px solid var(--border);border-radius:12px;background:transparent;color:var(--sub);cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center;transition:all .2s}.voice-btn:hover{background:rgba(255,255,255,0.04)}.voice-btn.recording{background:#EF4444;color:#fff;border-color:#EF4444}
.send-btn{width:42px;height:42px;border:none;border-radius:12px;background:var(--accent);color:#fff;cursor:pointer;font-size:20px;display:flex;align-items:center;justify-content:center;transition:all .2s}.send-btn:hover{opacity:.9}.send-btn:disabled{opacity:.3;cursor:not-allowed}
.rec-bar{position:fixed;bottom:90px;left:50%;transform:translateX(-50%);background:#EF4444;color:#fff;padding:8px 20px;border-radius:20px;font-size:13px;z-index:99;box-shadow:0 4px 12px rgba(0,0,0,0.4)}
/* Modal */
.modal-bg{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;z-index:200}
.modal{background:#1E2A4A;border-radius:16px;padding:30px;width:400px;box-shadow:0 20px 60px rgba(0,0,0,0.5)}.modal h3{font-size:18px;color:#fff;margin-bottom:16px}.modal .inp{margin-bottom:14px}.btn{width:100%;padding:12px;background:var(--accent);color:#fff;border:none;border-radius:10px;cursor:pointer;font-size:15px;margin-bottom:10px}.btn-out{width:100%;padding:12px;background:transparent;color:#EF4444;border:1px solid #EF4444;border-radius:10px;cursor:pointer;font-size:15px}
</style>
