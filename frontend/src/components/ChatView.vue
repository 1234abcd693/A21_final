<template>
  <div class="chat"><div class="msgs" ref="ml"><div v-for="m in msgs" :key="m.id" :class="['msg',m.role]"><div class="av">{{m.role==='user'?'👤':'🤖'}}</div><div class="bc" v-html="m.role==='user'?esc(m.content):md(m.content)"></div><div v-if="m.role==='assistant'" class="fb"><button @click="rate(m,1)" :class="{a:m._r===1}">👍</button><button @click="rate(m,-1)" :class="{a:m._r===-1}">👎</button></div></div><div v-if="st" class="msg assistant"><div class="av">🤖</div><div class="bc" v-html="md(stx)"></div></div></div>
    <div class="ia"><div class="ir"><textarea v-model="tx" placeholder="输入问题..." @keydown.enter.exact.prevent="send" :disabled="st" rows="2"/><button @click="startVoice" class="vb">🎤</button><button @click="send" :disabled="st||!tx.trim()" class="sb"><svg w="18" h="18" viewBox="0 0 24 24" fill="currentColor"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg></button></div><label class="ub">📄<input type="file" accept=".docx,.pdf,.txt" @change="upload" hidden/></label></div>
    <Teleport to="body"><div v-if="va" class="vol"><div class="vbx"><div class="vp"></div><p>正在聆听...</p><p class="vt">{{vt||'请说话'}}</p><button @click="stopVoice" class="vs">完成</button></div></div></Teleport>
  </div>
</template>
<script setup>
import { ref, nextTick } from 'vue';import { askStream, feedbackAPI } from '../api/index.js';import api from '../api/index.js'
const msgs=ref([]),tx=ref(''),st=ref(false),stx=ref(''),ml=ref(null),va=ref(false),vt=ref(''),sessId=ref('sess_'+Date.now())
let ws=null,mediaStream=null,audioCtx=null,processor=null
function esc(s){return(s||'').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function md(s){return(s||'').replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/### (.+)/g,'<h3>$1</h3>').replace(/\n\n/g,'</p><p>').replace(/\n/g,'<br>').replace(/^- (.+)/gm,'<li>$1</li>').replace(/\[(\d+)\]/g,'<sup class="c">[$1]</sup>')}
async function send(){if(!tx.value.trim()||st.value)return;const q=tx.value.trim();tx.value='';msgs.value.push({id:Date.now(),role:'user',content:q});st.value=true;stx.value='';await nextTick();scroll()
  try{const hist=msgs.value.slice(-6).map(m=>({role:m.role,content:m.content}));const r=await askStream(q,{mode:'chat',session_id:sessId.value,history:hist});const d=new TextDecoder();let b=''
    while(true){const{done,value}=await r.read();if(done)break;b+=d.decode(value,{stream:true});const ls=b.split('\n');b=ls.pop()||'';for(const l of ls){if(l.startsWith('data: ')){stx.value+=l.slice(6);scroll()}}}
    msgs.value.push({id:Date.now()+1,role:'assistant',content:stx.value})}catch(e){msgs.value.push({id:Date.now()+1,role:'assistant',content:'[错误]'})}
  finally{st.value=false;stx.value=''}}
function scroll(){nextTick(()=>{if(ml.value)ml.value.scrollTop=ml.value.scrollHeight})}
// Vosk WebSocket voice
async function startVoice(){try{va.value=true;vt.value='';mediaStream=await navigator.mediaDevices.getUserMedia({audio:{sampleRate:16000,channelCount:1,echoCancellation:true}})
    ws=new WebSocket('ws://127.0.0.1:8765');ws.onmessage=e=>{try{const d=JSON.parse(e.data);if(d.type==='partial')vt.value=d.text;else if(d.type==='final'&&d.text)vt.value+=' '+d.text}catch{}}
    ws.onerror=()=>stopVoice();ws.onclose=()=>stopVoice()
    await new Promise(r=>{ws.onopen=r})
    audioCtx=new AudioContext({sampleRate:16000});const src=audioCtx.createMediaStreamSource(mediaStream)
    processor=audioCtx.createScriptProcessor(4096,1,1);processor.onaudioprocess=e=>{if(ws?.readyState===WebSocket.OPEN){const d=e.inputBuffer.getChannelData(0);const buf=new Int16Array(d.length);for(let i=0;i<d.length;i++)buf[i]=Math.max(-1,Math.min(1,d[i]))*0x7FFF;ws.send(buf.buffer)}}
    src.connect(processor);processor.connect(audioCtx.destination)}catch{stopVoice()}}
function stopVoice(){if(ws){ws.close();ws=null}if(processor){processor.disconnect();processor=null}if(mediaStream){mediaStream.getTracks().forEach(t=>t.stop());mediaStream=null}if(audioCtx){audioCtx.close();audioCtx=null}if(vt.value.trim())tx.value=vt.value.trim();va.value=false}
async function upload(e){const f=e.target.files[0];if(!f)return;const fd=new FormData();fd.append('file',f);try{const{data}=await api.post('/parse',fd,{headers:{'Content-Type':'multipart/form-data'}});tx.value=`请分析:\n${data.candidates?.map(c=>`- ${c.type}: ${c.name}`).join('\n')||'无结果'}`}catch{}}
async function rate(msg,v){msg._r=msg._r===v?0:v;const q=msgs.value.find(m=>m.role==='user'&&m.id<msg.id)?.content||'';try{await feedbackAPI.submit({message_id:msg.id+'',rating:v,question:q,answer_text:msg.content,retrieved_chunks:'[]'})}catch{}}
</script>
<style scoped>
.chat{display:flex;flex-direction:column;height:100%;max-width:800px;margin:0 auto;width:100%}
.msgs{flex:1;overflow-y:auto;padding:24px 20px}.msg{display:flex;gap:12px;margin-bottom:20px}.msg.user{flex-direction:row-reverse}
.av{font-size:22px;flex-shrink:0;width:32px;text-align:center}.bc{max-width:80%;padding:14px 18px;border-radius:14px;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.04);line-height:1.7}.user .bc{background:#002EA6;color:#fff}
:deep(h3){font-size:16px;margin:8px 0 4px}:deep(strong){font-weight:600}:deep(li){margin:4px 0 4px 16px}:deep(.c){color:#06B6D4;font-size:11px;cursor:pointer;margin:0 2px}:deep(p){margin:6px 0}
.fb{display:flex;gap:6px;margin-top:6px}.fb button{padding:3px 8px;border:1.5px solid #E5E7EB;border-radius:6px;background:#fff;cursor:pointer;font-size:13px}.fb button.a{border-color:#FFE76F;background:#FFFDF0}
.ia{padding:14px 20px;border-top:1px solid #F0F0F0;background:#fff;display:flex;align-items:flex-end;gap:10px}
.ir{display:flex;gap:8px;align-items:flex-end;flex:1}textarea{flex:1;padding:10px 14px;border:1.5px solid #E5E7EB;border-radius:12px;resize:none;outline:none;font-size:15px;line-height:1.5;font-family:inherit}textarea:focus{border-color:#002EA6;box-shadow:0 0 0 3px rgba(0,46,166,0.1)}
.sb{width:40px;height:40px;border:none;border-radius:10px;background:#002EA6;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}.sb:disabled{background:#D1D5DB}
.vb{width:40px;height:40px;border:1.5px solid #E5E7EB;border-radius:10px;background:#fff;cursor:pointer;font-size:18px;flex-shrink:0}.vb:hover{background:#F0F4FF}.ub{cursor:pointer;font-size:18px;padding:6px;border-radius:8px}.ub:hover{background:#F0F4FF}
.vol{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;z-index:9999}
.vbx{background:#fff;border-radius:20px;padding:40px 48px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.2)}
.vp{width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#002EA6,#0040D0);margin:0 auto 20px;animation:p 1.5s ease-in-out infinite}@keyframes p{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.15);opacity:.7}}
.vbx p{font-size:16px;color:#333;margin-bottom:4px}.vt{font-size:18px!important;color:#002EA6!important;font-weight:500;min-height:28px;margin:12px 0!important}.vs{margin-top:16px;padding:10px 32px;background:#002EA6;color:#fff;border:none;border-radius:10px;cursor:pointer;font-size:15px;font-weight:500}
</style>
