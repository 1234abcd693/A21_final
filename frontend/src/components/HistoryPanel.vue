<template>
  <div class="hp"><div class="ph"><h3>📜 历史</h3><span v-if="sel.size" class="bb">已选{{sel.size}}<button @click="batchDel" class="bd">🗑 删除</button></span></div>
    <div class="sb"><input v-model="q" placeholder="搜索会话..." @input="onS"/></div>
    <div class="lst"><div v-for="s in sessions" :key="s.session_id" :class="['it',{p:s.pinned,sl:sel.has(s.session_id)}]">
      <input type="checkbox" :checked="sel.has(s.session_id)" @change="tg(s.session_id)" class="cb"/>
      <div class="ct" @click="$emit('select',s)"><div class="tr"><span v-if="s.pinned" class="pn">📌</span><span class="tl">{{s.title||'(无标题)'}}</span></div><div class="mt">{{s.message_count||0}} 条 · {{(s.updated_at||'').slice(0,16).replace('T',' ')}}</div></div>
      <div class="ac"><button @click.stop="pin(s)" :title="s.pinned?'取消':'置顶'">{{s.pinned?'📌':'📍'}}</button><button @click.stop="del(s.session_id)" title="删除">🗑</button></div>
    </div><div v-if="!sessions.length" class="em">暂无历史对话</div></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';import { historyAPI } from '../api/index.js'
const emit=defineEmits(['select','close']);const sessions=ref([]),q=ref(''),sel=ref(new Set);let t=null
onMounted(load)
function load(){const p={page:1,page_size:50};if(q.value)historyAPI.search({q:q.value,...p}).then(({data})=>sessions.value=data.sessions||[]);else historyAPI.list(p).then(({data})=>sessions.value=data.sessions||[])}
function onS(){clearTimeout(t);t=setTimeout(load,300)}
async function del(sid){await historyAPI.delete(sid);load()}
async function pin(s){await historyAPI.pin(s.session_id,!s.pinned);load()}
async function batchDel(){await historyAPI.batchDelete([...sel.value]);sel.value.clear();load()}
function tg(sid){const s=new Set(sel.value);s.has(sid)?s.delete(sid):s.add(sid);sel.value=s}
</script>
<style scoped>
.hp{width:360px;background:#fff;border-right:1px solid #E8ECF1;display:flex;flex-direction:column;height:100%}
.ph{padding:14px 18px;border-bottom:1px solid #E8ECF1;display:flex;justify-content:space-between;align-items:center}
.ph h3{font-size:15px;color:#002EA6}.bb{font-size:12px;color:#FF4D4F}.bd{background:#FF4D4F;color:#fff;border:none;padding:3px 8px;border-radius:4px;cursor:pointer;font-size:11px;margin-left:6px}
.sb{padding:10px 14px;border-bottom:1px solid #E8ECF1}.sb input{width:100%;padding:8px 12px;border:2px solid #E8ECF1;border-radius:8px;font-size:13px;outline:none}.sb input:focus{border-color:#002EA6}
.lst{flex:1;overflow-y:auto}.it{display:flex;align-items:center;padding:10px 14px;border-bottom:1px solid #F5F7FA;cursor:pointer;transition:background .15s}.it:hover{background:#F0F4FF}.it.p{background:#FFFDF0}.it.sl{background:#E8F0FF}
.cb{margin-right:8px}.ct{flex:1;min-width:0}.tr{display:flex;align-items:center;gap:4px}.tl{font-size:14px;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.pn{font-size:11px}.mt{font-size:11px;color:#999;margin-top:3px}
.ac{display:flex;gap:2px;opacity:0;transition:.2s}.it:hover .ac{opacity:1}.ac button{background:none;border:none;cursor:pointer;font-size:13px;padding:3px;border-radius:4px}.ac button:hover{background:#F5F7FA}
.em{text-align:center;padding:40px;color:#999;font-size:13px}
</style>
