<template>
  <div class="hp"><div class="ph"><h3>📜 历史对话</h3><span v-if="sel.size" class="bb">已选{{sel.size}}<button @click="batchDel" class="bd">删除</button></span></div>
    <div class="sb"><input v-model="q" placeholder="搜索..." @input="onS"/></div>
    <div class="lst"><div v-for="s in sessions" :key="s.session_id" :class="['it',{p:s.pinned,sl:sel.has(s.session_id)}]">
      <input type="checkbox" :checked="sel.has(s.session_id)" @change="tg(s.session_id)" class="cb"/>
      <div class="ct" @click="$emit('select',s)"><div class="tr"><span v-if="s.pinned">📌</span><span class="tl">{{s.title||'(无标题)'}}</span></div><div class="mt">{{s.message_count||0}}条 · {{fmt(s.updated_at)}}</div></div>
      <div class="ac"><button @click.stop="pin(s)">{{s.pinned?'📌':'📍'}}</button><button @click.stop="del(s.session_id)">🗑</button></div>
    </div><div v-if="!sessions.length" class="em">暂无历史</div></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';import { historyAPI } from '../api/index.js'
const emit=defineEmits(['select']);const sessions=ref([]),q=ref(''),sel=ref(new Set);let t=null
onMounted(load)
function load(){const p={page:1,page_size:50};if(q.value)historyAPI.search({q:q.value,...p}).then(({data})=>sessions.value=data.sessions||[]);else historyAPI.list(p).then(({data})=>sessions.value=data.sessions||[])}
function onS(){clearTimeout(t);t=setTimeout(load,300)}
async function del(sid){await historyAPI.delete(sid);load()}
async function pin(s){await historyAPI.pin(s.session_id,!s.pinned);load()}
async function batchDel(){await historyAPI.batchDelete([...sel.value]);sel.value.clear();load()}
function tg(sid){const s=new Set(sel.value);s.has(sid)?s.delete(sid):s.add(sid);sel.value=s}
function fmt(t){return t?t.slice(0,16).replace('T',' '):''}
</script>
<style scoped>
.hp{max-width:800px;margin:0 auto;width:100%;padding:20px}
.ph{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}.ph h3{font-size:18px;color:#1A1A2E}.bb{font-size:12px;color:#EF4444}.bd{background:#EF4444;color:#fff;border:none;padding:3px 8px;border-radius:4px;cursor:pointer;font-size:11px;margin-left:6px}
.sb{margin-bottom:16px}.sb input{width:100%;padding:10px 14px;border:1.5px solid #E5E7EB;border-radius:8px;font-size:14px;outline:none}.sb input:focus{border-color:#002EA6}
.lst{display:flex;flex-direction:column;gap:2px}.it{display:flex;align-items:center;padding:12px 14px;border-radius:8px;cursor:pointer;transition:background .15s}.it:hover{background:#F0F4FF}.it.p{background:#FFFDF0}.it.sl{background:#E8F0FF}
.cb{margin-right:10px}.ct{flex:1;min-width:0}.tr{display:flex;align-items:center;gap:4px}.tl{font-size:14px;font-weight:500}.mt{font-size:12px;color:#999;margin-top:2px}
.ac{display:flex;gap:4px;opacity:0;transition:.2s}.it:hover .ac{opacity:1}.ac button{background:none;border:none;cursor:pointer;font-size:13px;padding:4px;border-radius:4px}.ac button:hover{background:#F0F0F0}
.em{text-align:center;padding:40px;color:#999;font-size:14px}
</style>
