<template>
  <div class="chat">
    <div class="msgs" ref="ml">
      <div v-for="m in msgs" :key="m.id" :class="['msg',m.role]">
        <div class="av">{{m.role==='user'?'👤':'🤖'}}</div>
        <div class="bc"><div class="tx">{{m.content}}</div></div>
      </div>
      <div v-if="st" class="msg assistant"><div class="av">🤖</div><div class="bc"><div class="tx">{{stx}}<span class="cr">|</span></div></div></div>
    </div>
    <div class="input-area">
      <div class="ir">
        <textarea v-model="tx" placeholder="输入故障现象或问题..." @keydown.enter.exact.prevent="send" :disabled="st" rows="2" ref="ta"/>
        <button @click="send" :disabled="st||!tx.trim()" class="sb"><svg w="18" h="18" viewBox="0 0 24 24" fill="currentColor"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg></button>
      </div>
      <div class="hints">支持自然语言提问，如"接触器线圈烧毁怎么修"</div>
    </div>
  </div>
</template>
<script setup>
import { ref, nextTick } from 'vue'
import { askStream } from '../api/index.js'
const msgs=ref([]),tx=ref(''),st=ref(false),stx=ref(''),ml=ref(null),ta=ref(null)
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
function scroll(){nextTick(()=>{if(ml.value)ml.value.scrollTop=ml.value.scrollHeight})}
</script>
<style scoped>
.chat{display:flex;flex-direction:column;height:100%;max-width:800px;margin:0 auto;width:100%}
.msgs{flex:1;overflow-y:auto;padding:24px 20px}
.msg{display:flex;gap:12px;margin-bottom:24px}.msg.user{flex-direction:row-reverse}
.av{font-size:22px;flex-shrink:0;width:32px;text-align:center}
.bc{max-width:75%;padding:12px 16px;border-radius:14px;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.04)}.user .bc{background:#002EA6}.user .bc .tx{color:#fff}
.tx{font-size:15px;line-height:1.6;white-space:pre-wrap;word-break:break-word}.cr{animation:bl 1s infinite}@keyframes bl{50%{opacity:0}}
.input-area{padding:16px 20px;border-top:1px solid #F0F0F0;background:#fff}
.ir{display:flex;gap:10px;align-items:flex-end}
textarea{flex:1;padding:12px 16px;border:1.5px solid #E5E7EB;border-radius:12px;resize:none;outline:none;font-size:15px;line-height:1.5;font-family:inherit}textarea:focus{border-color:#002EA6;box-shadow:0 0 0 3px rgba(0,46,166,0.1)}
.sb{width:42px;height:42px;border:none;border-radius:10px;background:#002EA6;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}.sb:disabled{background:#D1D5DB;cursor:not-allowed}
.hints{text-align:center;margin-top:8px;font-size:12px;color:#999}
</style>
