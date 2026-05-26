<template>
  <div class="chat">
    <div class="msgs" ref="ml">
      <div v-for="m in msgs" :key="m.id" :class="['msg',m.role]">
        <div class="av">{{m.role==='user'?'👤':'🤖'}}</div>
        <div class="bc" v-html="m.role==='user'?esc(m.content):md(m.content)"></div>
        <div v-if="m.role==='assistant'" class="fb">
          <button @click="rate(m,1)" :class="{a:m._r===1}">👍</button>
          <button @click="rate(m,-1)" :class="{a:m._r===-1}">👎</button>
        </div>
      </div>
      <div v-if="st" class="msg assistant"><div class="av">🤖</div><div class="bc" v-html="md(stx)"></div></div>
    </div>
    <div class="ia">
      <div class="ir">
        <textarea v-model="tx" placeholder="输入问题..." @keydown.enter.exact.prevent="send" :disabled="st" rows="2"/>
        <button @click="toggleVoice" :class="['vb',{recording}]" :title="recording?'停止录音':'语音输入'">{{recording?'⏹':'🎤'}}</button>
        <button @click="send" :disabled="st||!tx.trim()" class="sb"><svg w="18" h="18" viewBox="0 0 24 24" fill="currentColor"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg></button>
      </div>
      <label class="ub">📄<input type="file" accept=".docx,.pdf,.txt" @change="upload" hidden/></label>
    </div>
    <div v-if="recording" class="voice-bar">🔴 正在录音... {{recordTime}}s</div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { askStream, feedbackAPI } from '../api/index.js'
import api from '../api/index.js'

const msgs=ref([]),tx=ref(''),st=ref(false),stx=ref(''),ml=ref(null)
const recording=ref(false),recordTime=ref(0)
const sessId=ref('sess_'+Date.now())
let mediaRecorder=null,chunks=[],recordTimer=null

function esc(s){return(s||'').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function md(s){return(s||'').replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/### (.+)/g,'<h3>$1</h3>').replace(/\n\n/g,'</p><p>').replace(/\n/g,'<br>').replace(/^- (.+)/gm,'<li>$1</li>').replace(/\[(\d+)\]/g,'<sup class="c">[$1]</sup>')}

async function send(){
  if(!tx.value.trim()||st.value)return
  const q=tx.value.trim();tx.value='';msgs.value.push({id:Date.now(),role:'user',content:q})
  st.value=true;stx.value='';await nextTick();scroll()
  try{
    const hist=msgs.value.slice(-6).map(m=>({role:m.role,content:m.content}))
    const r=await askStream(q,{mode:'chat',session_id:sessId.value,history:hist})
    const d=new TextDecoder();let b=''
    while(true){const{done,value}=await r.read();if(done)break;b+=d.decode(value,{stream:true});const ls=b.split('\n');b=ls.pop()||'';for(const l of ls){if(l.startsWith('data: ')){stx.value+=l.slice(6);scroll()}}}
    msgs.value.push({id:Date.now()+1,role:'assistant',content:stx.value})
  }catch(e){msgs.value.push({id:Date.now()+1,role:'assistant',content:'[错误]'})}
  finally{st.value=false;stx.value=''}
}

function scroll(){nextTick(()=>{if(ml.value)ml.value.scrollTop=ml.value.scrollHeight})}

// 语音: MediaRecorder 录制 WAV → fetch vosk HTTP
async function toggleVoice(){
  if(recording.value){stopRecording();return}
  try{
    const stream=await navigator.mediaDevices.getUserMedia({audio:true})
    mediaRecorder=new MediaRecorder(stream,{mimeType:'audio/webm'})
    chunks=[];recording.value=true;recordTime.value=0
    recordTimer=setInterval(()=>recordTime.value++,1000)
    mediaRecorder.ondataavailable=e=>chunks.push(e.data)
    mediaRecorder.onstop=async()=>{
      clearInterval(recordTimer);recording.value=false;stream.getTracks().forEach(t=>t.stop())
      const blob=new Blob(chunks,{type:'audio/webm'})
      const fd=new FormData();fd.append('audio',blob,'recording.webm')
      try{const{data}=await api.post('http://127.0.0.1:8765/transcribe',fd,{headers:{'Content-Type':'multipart/form-data'}});if(data.text)tx.value=data.text}catch{}
    }
    mediaRecorder.start()
  }catch(e){recording.value=false}
}
function stopRecording(){if(mediaRecorder&&mediaRecorder.state==='recording')mediaRecorder.stop()}

async function upload(e){
  const f=e.target.files[0];if(!f)return
  const fd=new FormData();fd.append('file',f)
  try{const{data}=await api.post('/parse',fd,{headers:{'Content-Type':'multipart/form-data'}});tx.value='请分析:\n'+(data.candidates||[]).map(c=>'- '+c.type+': '+c.name).join('\n')}catch{}
}
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
.vb{width:40px;height:40px;border:1.5px solid #E5E7EB;border-radius:10px;background:#fff;cursor:pointer;font-size:18px;flex-shrink:0}.vb:hover{background:#F0F4FF}.vb.recording{background:#EF4444;color:#fff;animation:pulse .8s infinite}@keyframes pulse{50%{transform:scale(1.1)}}
.ub{cursor:pointer;font-size:18px;padding:6px;border-radius:8px}.ub:hover{background:#F0F4FF}
.voice-bar{position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:#EF4444;color:#fff;padding:8px 20px;border-radius:20px;font-size:14px;z-index:999;box-shadow:0 4px 12px rgba(0,0,0,0.2)}
</style>
