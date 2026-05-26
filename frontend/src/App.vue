<template><div class="app"><div class="sb"><div class="sb-top"><button @click="newChat" class="nc">+ 新对话</button></div><div class="sb-list"><div v-for="c in convs" :key="c.id" :class="['ci',{active:c.id===cid}]" @click="loadChat(c.id)">{{c.title||'新对话'}}</div></div><div class="sb-bot"><div class="user-info" @click="showSet=!showSet"><span class="av">{{user?.display_name?.[0]||'?'}}</span><span>{{user?.display_name||'用户'}}</span></div></div></div><div class="main"><div class="chat"><div class="msgs" ref="ml"><div v-for="m in msgs" :key="m.id" :class="['msg',m.role]"><div class="mc" v-html="m.role==='user'?esc(m.content):md(m.content)"></div><div v-if="m.role==='assistant'" class="fb"><button @click="rate(m,1)" :class="{a:m._r===1}">👍</button><button @click="rate(m,-1)" :class="{a:m._r===-1}">👎</button></div></div><div v-if="st" class="msg assistant"><div class="mc" v-html="md(stx)"></div></div></div><div class="ia"><textarea v-model="tx" placeholder="输入故障现象或问题..." @keydown.enter.exact.prevent="send" :disabled="st" rows="2"/><div class="ib"><button @click="toggleVoice" :class="['vb',{rec:recording}]">{{recording?'⏹':'🎤'}}</button><button @click="send" :disabled="st||!tx.trim()" class="sb"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg></button></div></div><div v-if="recording" class="vr">🔴 录音中... {{rt}}s</div></div></div><Transition name="fade"><div v-if="showSet" class="modal-bg" @click.self="showSet=false"><div class="modal"><h3>个人设置</h3><input v-model="dn" placeholder="显示名" class="inp"/><input v-model="pw" type="password" placeholder="新密码(留空不修改)" class="inp"/><button @click="saveProfile" class="btn">保存</button><button @click="logout" class="btn-out">退出登录</button></div></div></Transition></div></template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import api, { askStream, feedbackAPI, authAPI, historyAPI } from './api/index.js'
const msgs=ref([]),tx=ref(''),st=ref(false),stx=ref(''),ml=ref(null),recording=ref(false),rt=ref(0),showSet=ref(false),convs=ref([]),cid=ref(''),user=ref({}),dn=ref(''),pw=ref('')
let mediaRecorder=null,chunks=[],timer=null
function esc(s){return(s||'').replace(/</g,'&lt;')}
function md(s){return(s||'').replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/### (.+)/g,'<h3>$1</h3>').replace(/\n\n/g,'</p><p>').replace(/\n/g,'<br>').replace(/^- (.+)/gm,'<li>$1</li>').replace(/\[(\d+)\]/g,'<sup class="c">[$1]</sup>')}
onMounted(async()=>{
  try{user.value=JSON.parse(localStorage.getItem('a21_user')||'{}');dn.value=user.value.display_name||''}catch{}
  loadConvs()
})
async function loadConvs(){try{const{data}=await historyAPI.list({page:1,page_size:50});convs.value=(data.sessions||[]).map(s=>({id:s.session_id,title:s.title}))}catch{}}
async function newChat(){msgs.value=[];cid.value='sess_'+Date.now();loadConvs()}
async function loadChat(id){cid.value=id;try{const{data}=await historyAPI.detail(id);msgs.value=(data.messages||[]).map(m=>({id:m.message_id,role:m.role,content:m.content}))}catch{}}
async function saveConv(q,a){if(!cid.value)return;try{await api.post('/history/save',{session_id:cid.value,title:q.slice(0,30),user_msg:q,assistant_msg:a,user_id:user.value.id||0})}catch{};loadConvs()}
async function send(){if(!tx.value.trim()||st.value)return;const q=tx.value.trim();tx.value='';msgs.value.push({id:Date.now(),role:'user',content:q});st.value=true;stx.value='';await nextTick();scroll()
  try{const hist=msgs.value.slice(-6).map(m=>({role:m.role,content:m.content}));const r=await askStream(q,{mode:'chat',session_id:cid.value,history:hist});const d=new TextDecoder();let b=''
    while(true){const{done,value}=await r.read();if(done)break;b+=d.decode(value,{stream:true});const ls=b.split('\n');b=ls.pop()||'';for(const l of ls){if(l.startsWith('data: ')){stx.value+=l.slice(6);scroll()}}}
    msgs.value.push({id:Date.now()+1,role:'assistant',content:stx.value});saveConv(q,stx.value)}catch(e){msgs.value.push({id:Date.now()+1,role:'assistant',content:'[错误]'})}
  finally{st.value=false;stx.value=''}}
function scroll(){nextTick(()=>{if(ml.value)ml.value.scrollTop=ml.value.scrollHeight})}
async function toggleVoice(){if(recording.value){stopVoice();return}
  try{const s=await navigator.mediaDevices.getUserMedia({audio:true});mediaRecorder=new MediaRecorder(s);chunks=[];recording.value=true;rt.value=0;timer=setInterval(()=>rt.value++,1000);mediaRecorder.ondataavailable=e=>chunks.push(e.data);mediaRecorder.onstop=async()=>{clearInterval(timer);recording.value=false;s.getTracks().forEach(t=>t.stop());try{const b=new Blob(chunks,{type:'audio/webm'});const fd=new FormData();fd.append('audio',b);const{data}=await api.post('http://127.0.0.1:8765/transcribe',fd,{headers:{'Content-Type':'multipart/form-data'}});if(data.text)tx.value=data.text}catch{}};mediaRecorder.start()}catch(e){recording.value=false}}
function stopVoice(){if(mediaRecorder&&mediaRecorder.state==='recording')mediaRecorder.stop()}
async function rate(m,v){m._r=m._r===v?0:v;try{await feedbackAPI.submit({message_id:m.id+'',rating:v,question:'',answer_text:m.content,retrieved_chunks:'[]'})}catch{}}
async function saveProfile(){try{await api.put('/user/profile',{display_name:dn.value,password:pw.value||undefined},{params:{token:localStorage.getItem('a21_token')}});alert('已保存')}catch{}}
function logout(){localStorage.clear();location.reload()}
</script>

<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:#212121;color:#ECECEC}
.app{display:flex;height:100vh}
.sb{width:260px;background:#171717;display:flex;flex-direction:column;border-right:1px solid #2A2A2A}
.sb-top{padding:12px}.nc{width:100%;padding:10px;background:transparent;color:#ECECEC;border:1px solid #3A3A3A;border-radius:8px;cursor:pointer;font-size:14px}.nc:hover{background:#2A2A2A}
.sb-list{flex:1;overflow-y:auto;padding:4px 8px}
.ci{padding:10px 12px;border-radius:8px;cursor:pointer;font-size:13px;color:#B0B0B0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.ci:hover{background:#2A2A2A}.ci.active{background:#323232;color:#ECECEC}
.sb-bot{padding:12px;border-top:1px solid #2A2A2A}.user-info{display:flex;align-items:center;gap:8px;cursor:pointer;padding:6px;border-radius:8px}.user-info:hover{background:#2A2A2A}.av{width:28px;height:28px;border-radius:50%;background:#002EA6;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600}
.main{flex:1;display:flex;flex-direction:column;max-width:800px;margin:0 auto;width:100%}
.chat{display:flex;flex-direction:column;height:100%}
.msgs{flex:1;overflow-y:auto;padding:24px 0}.msg{margin-bottom:24px;padding:0 20px}.msg.user{display:flex;justify-content:flex-end}.mc{max-width:85%;padding:14px 18px;border-radius:14px;background:#2A2A2A;line-height:1.6;font-size:15px}.msg.user .mc{background:#002EA6}.fb{display:flex;gap:6px;margin-top:6px}.fb button{padding:3px 8px;border:1px solid #3A3A3A;border-radius:6px;background:transparent;color:#888;cursor:pointer;font-size:12px}.fb button.a{border-color:#FFE76F;color:#FFE76F}:deep(h3){margin:8px 0 4px;font-size:16px}:deep(strong){font-weight:600}:deep(li){margin:4px 0 4px 16px}:deep(.c){color:#06B6D4;font-size:11px;margin:0 2px}:deep(p){margin:6px 0}
.ia{padding:12px 20px;display:flex;gap:10px;align-items:flex-end}textarea{flex:1;padding:12px 16px;background:#2A2A2A;border:1px solid #3A3A3A;border-radius:12px;resize:none;outline:none;font-size:15px;color:#ECECEC;line-height:1.5;font-family:inherit}textarea:focus{border-color:#002EA6}.ib{display:flex;gap:8px}.sb{width:38px;height:38px;border:none;border-radius:8px;background:#002EA6;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center}.sb:disabled{background:#3A3A3A}.vb{width:38px;height:38px;border:1px solid #3A3A3A;border-radius:8px;background:transparent;color:#888;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center}.vb:hover{background:#2A2A2A}.vb.rec{background:#CC0000;color:#fff;animation:p .8s infinite}@keyframes p{50%{transform:scale(1.1)}}
.vr{position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:#CC0000;color:#fff;padding:6px 18px;border-radius:16px;font-size:13px;z-index:999}
.modal-bg{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:100}
.modal{background:#2A2A2A;border-radius:16px;padding:28px;width:380px}.modal h3{margin-bottom:16px;color:#ECECEC}.inp{width:100%;padding:10px 14px;background:#1A1A1A;border:1px solid #3A3A3A;border-radius:8px;color:#ECECEC;font-size:14px;outline:none;margin-bottom:12px}.inp:focus{border-color:#002EA6}
.btn{width:100%;padding:10px;background:#002EA6;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px;margin-bottom:8px}.btn-out{width:100%;padding:10px;background:transparent;color:#CC0000;border:1px solid #CC0000;border-radius:8px;cursor:pointer;font-size:14px}
.fade-enter-active,.fade-leave-active{transition:opacity .2s}.fade-enter-from,.fade-leave-to{opacity:0}
</style>
