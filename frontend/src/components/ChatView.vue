<template>
  <div class="chat">
    <div class="msgs" ref="ml">
      <div v-for="m in msgs" :key="m.id" :class="['msg',m.role]">
        <div class="av">{{m.role==='user'?'👤':'🤖'}}</div>
        <div class="bc" v-html="m.role==='user'?escapeHtml(m.content):renderMd(m.content)"></div>
      </div>
      <div v-if="st" class="msg assistant"><div class="av">🤖</div><div class="bc" v-html="renderMd(stx)"></div><span class="cr">|</span></div>
    </div>
    <div class="input-area">
      <div class="ir">
        <textarea v-model="tx" placeholder="输入故障现象或问题..." @keydown.enter.exact.prevent="send" :disabled="st" rows="2" ref="ta"/>
        <button @mousedown.prevent="startVoice" @mouseup.prevent="stopVoice" class="vb" title="按住说话">🎤</button>
        <button @click="send" :disabled="st||!tx.trim()" class="sb"><svg w="18" h="18" viewBox="0 0 24 24" fill="currentColor"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg></button>
      </div>
      <div class="tools">
        <label class="upload-btn" title="上传文档抽取知识">📄<input type="file" accept=".docx,.pdf,.txt" @change="uploadDoc" style="display:none"/></label>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, nextTick } from 'vue'
import { askStream, transcribeAPI, feedbackAPI } from '../api/index.js'
import api from '../api/index.js'
const msgs=ref([]),tx=ref(''),st=ref(false),stx=ref(''),ml=ref(null),ta=ref(null)
function escapeHtml(s){return s.replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function renderMd(s){return s.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/### (.*)/g,'<h3>$1</h3>').replace(/\n/g,'<br>').replace(/\[(\d+)\]/g,'<sup class="cite">[$1]</sup>').replace(/^- (.*)/gm,'<li>$1</li>')}
async function send(){
  if(!tx.value.trim()||st.value)return
  const q=tx.value.trim();tx.value='';msgs.value.push({id:Date.now(),role:'user',content:q})
  st.value=true;stx.value='';await nextTick();scroll()
  try{const r=await askStream(q,{mode:'chat'});const d=new TextDecoder();let buf=''
    while(true){const{done,value}=await r.read();if(done)break;buf+=d.decode(value,{stream:true})
      const ls=buf.split('\n');buf=ls.pop()||''
      for(const l of ls){if(l.startsWith('data: ')){stx.value+=l.slice(6);scroll()}}}
    msgs.value.push({id:Date.now()+1,role:'assistant',content:stx.value})}
  catch(e){msgs.value.push({id:Date.now()+1,role:'assistant',content:'[错误: '+e.message+']'})}
  finally{st.value=false;stx.value=''}
}
let recorder,chunks
async function startVoice(){try{const s=await navigator.mediaDevices.getUserMedia({audio:true});recorder=new MediaRecorder(s);chunks=[];recorder.ondataavailable=e=>chunks.push(e.data);recorder.onstop=async()=>{const b=new Blob(chunks,{type:'audio/wav'});try{const{data}=await transcribeAPI.send(b);if(data.text)tx.value=data.text}catch{}};recorder.start()}catch{}}
function stopVoice(){if(recorder?.state!=='inactive'){recorder.stop();recorder.stream.getTracks().forEach(t=>t.stop())}}
async function uploadDoc(e){const f=e.target.files[0];if(!f)return;const fd=new FormData();fd.append('file',f);try{const{data}=await api.post('/parse',fd,{headers:{'Content-Type':'multipart/form-data'}});tx.value=`请分析以下文档内容:\n${data.candidates?.map(c=>`- ${c.type}: ${c.name}`).join('\n')||'无提取结果'}`}catch{tx.value='文档上传失败'}}
async function rate(msg,rating){const q=msgs.value.find(m=>m.role==='user'&&m.id<msg.id)?.content||'';try{await feedbackAPI.submit({message_id:msg.id+'',rating,question:q,answer_text:msg.content,retrieved_chunks:'[]'})}catch{}}
function scroll(){nextTick(()=>{if(ml.value)ml.value.scrollTop=ml.value.scrollHeight})}
</script>
<style scoped>
.chat{display:flex;flex-direction:column;height:100%;max-width:800px;margin:0 auto;width:100%}
.msgs{flex:1;overflow-y:auto;padding:24px 20px}
.msg{display:flex;gap:12px;margin-bottom:24px}.msg.user{flex-direction:row-reverse}
.av{font-size:22px;flex-shrink:0;width:32px;text-align:center}
.bc{max-width:80%;padding:14px 18px;border-radius:14px;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.04);line-height:1.7}.user .bc{background:#002EA6;color:#fff}
:deep(h3){font-size:16px;margin:8px 0 4px;color:inherit}:deep(strong){font-weight:600}:deep(li){margin:4px 0 4px 16px}:deep(.cite){color:#06B6D4;font-size:11px;cursor:pointer;margin:0 2px}
.cr{animation:bl 1s infinite;margin-left:2px}@keyframes bl{50%{opacity:0}}
.input-area{padding:16px 20px;border-top:1px solid #F0F0F0;background:#fff}
.ir{display:flex;gap:10px;align-items:flex-end}
textarea{flex:1;padding:12px 16px;border:1.5px solid #E5E7EB;border-radius:12px;resize:none;outline:none;font-size:15px;line-height:1.5;font-family:inherit}textarea:focus{border-color:#002EA6;box-shadow:0 0 0 3px rgba(0,46,166,0.1)}
.sb{width:42px;height:42px;border:none;border-radius:10px;background:#002EA6;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}.sb:disabled{background:#D1D5DB;cursor:not-allowed}
.vb{width:42px;height:42px;border:1.5px solid #E5E7EB;border-radius:10px;background:#fff;cursor:pointer;font-size:18px;flex-shrink:0}.vb:hover{background:#F0F4FF}
</style>

