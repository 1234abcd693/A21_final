<template>
  <div class="gv"><div class="top-bar"><input v-model="q" placeholder="搜索实体、故障..." @keyup.enter="onS"/><button @click="onS">搜索</button></div>
    <div ref="c" class="gc"></div>
    <div class="lg"><span v-for="l in lg" :key="l.l" class="li"><span class="d" :style="{bg:l.c}"></span>{{l.l}}</span></div>
  </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue'
import G6 from '@antv/g6'
import { graphAPI } from '../api/index.js'
const emit=defineEmits(['node-click']);const c=ref(null),q=ref('');let graph=null
const lg=[{l:'设备',c:'#002EA6'},{l:'故障',c:'#EF4444'},{l:'原因',c:'#F59E0B'},{l:'维修',c:'#10B981'},{l:'注意',c:'#8B5CF6'},{l:'备件',c:'#06B6D4'},{l:'工具',c:'#6B7280'}]
const nc={Equipment:'#002EA6',Symptom:'#EF4444',Cause:'#F59E0B',Step:'#10B981',Precaution:'#8B5CF6',SparePart:'#06B6D4',Tool:'#6B7280'}
const ec={CAUSED_BY:'#F59E0B',FIXED_BY:'#10B981',NEXT_STEP:'#06B6D4',BELONGS_TO:'#002EA6',SUBCLASS_OF:'#002EA6',HAS_PRECAUTION:'#8B5CF6',REQUIRES_TOOL:'#6B7280',USES_SPAREPART:'#06B6D4'}

onMounted(async()=>{try{const{data}=await graphAPI.overview();init(data.nodes||[],data.edges||[])}catch(e){}})

function onS(){if(!q.value.trim())return;graphAPI.search(q.value).then(({data})=>{const s=new Set((data.results||[]).map(r=>r.uid));if(graph)graph.getNodes().forEach(n=>{const h=s.has(n.getModel().id);graph.updateItem(n,{style:{opacity:!s.size||h?1:0.06,stroke:s.has(n.getModel().id)?'#FFE76F':nc[n.getModel().lt]||'#002EA6',lineWidth:s.has(n.getModel().id)?4:2}})})})}

function init(ns,es){
  const w=c.value?.clientWidth||800,h=c.value?.clientHeight||500
  graph=new G6.Graph({container:c.value,width:w,height:h,fitView:true,fitViewPadding:60,animate:true,
    modes:{default:['drag-canvas','zoom-canvas','drag-node']},
    layout:{type:'gForce',preventOverlap:true,nodeSpacing:180,linkDistance:240,nodeStrength:2500,gravity:10},
    defaultNode:{size:28,labelCfg:{style:{fill:'#fff',fontSize:10,fontFamily:'Microsoft YaHei'}},style:{stroke:'#fff',lineWidth:2,cursor:'pointer'}},
    defaultEdge:{type:'cubic-horizontal',style:{lineWidth:1.5,stroke:'#D1D5DB',endArrow:{path:G6.Arrow.triangle(5,7,0),fill:'#D1D5DB'},cursor:'pointer'}},
  })
  graph.data({nodes:ns.map(n=>({id:n.uid,label:n.name.length>10?n.name.slice(0,10)+'…':n.name,lt:n.label,size:n.label==='Equipment'?38:n.label==='Symptom'?30:24,style:{fill:nc[n.label]||'#002EA6'}})),
    edges:es.map(e=>({id:`${e.from}-${e.to}`,source:e.from,target:e.to,style:{stroke:ec[e.type]||'#D1D5DB',lineWidth:['CAUSED_BY','FIXED_BY'].includes(e.type)?2.5:1.5,endArrow:{path:G6.Arrow.triangle(5,7,0),fill:ec[e.type]||'#D1D5DB'}},label:['CAUSED_BY','FIXED_BY'].includes(e.type)?{CAUSED_BY:'原因',FIXED_BY:'维修'}[e.type]:''}))})
  graph.render()
  graph.on('node:click',async e=>{try{const{data:d}=await graphAPI.node(e.item.getModel().id);emit('node-click',d)}catch(_){}})
  graph.on('node:dblclick',async e=>{await expand(e.item.getModel().id)})
}
async function expand(uid){try{const{data}=await graphAPI.expand(uid);const ex=new Set(graph.getNodes().map(n=>n.getModel().id));for(const n of data.nodes||[]){if(!ex.has(n.uid)){graph.addItem('node',{id:n.uid,label:n.name.length>10?n.name.slice(0,10)+'…':n.name,lt:n.label,size:24,style:{fill:nc[n.label]||'#002EA6'}});ex.add(n.uid)}}for(const e of data.edges||[]){const eid=`${e.from}-${e.to}`;if(!graph.findById(eid))graph.addItem('edge',{id:eid,source:e.from,target:e.to,style:{stroke:ec[e.type]||'#D1D5DB',lineWidth:2,endArrow:{path:G6.Arrow.triangle(5,7,0),fill:ec[e.type]||'#D1D5DB'}}})}graph.layout();graph.fitView(40)}catch(e){}}
</script>
<style scoped>
.gv{width:100%;height:100%;position:relative;display:flex;flex-direction:column}
.top-bar{display:flex;gap:8px;padding:12px 16px;background:#fff;border-bottom:1px solid #F0F0F0}.top-bar input{flex:1;padding:8px 14px;border:1.5px solid #E5E7EB;border-radius:8px;font-size:14px;outline:none}.top-bar input:focus{border-color:#002EA6}.top-bar button{padding:8px 18px;background:#002EA6;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:500}
.gc{flex:1;background:#F9FAFB}
.lg{position:absolute;bottom:14px;left:14px;display:flex;gap:12px;background:rgba(255,255,255,0.95);padding:6px 14px;border-radius:10px;box-shadow:0 1px 6px rgba(0,0,0,0.06);flex-wrap:wrap;z-index:10}.li{display:flex;align-items:center;gap:5px;font-size:11px;color:#666}.d{width:10px;height:10px;border-radius:50%}
</style>
