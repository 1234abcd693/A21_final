<template>
  <div class="graph-panel" ref="c"><div v-if="loading" class="ld"><div class="sp"></div></div>
    <div class="lg"><span v-for="l in lg" :key="l.l" class="li"><span class="d" :style="{bg:l.c}"></span>{{l.l}}</span></div>
  </div>
</template>
<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import G6 from '@antv/g6'
import { graphAPI } from '../api/index.js'
const p=defineProps({highlightNodes:{type:Array,default:()=>[]}}),emit=defineEmits(['node-click'])
const c=ref(null),loading=ref(false);let graph=null
const lg=[{l:'设备',c:'#002EA6'},{l:'故障',c:'#FF4D4F'},{l:'原因',c:'#FA8C16'},{l:'维修',c:'#52C41A'},{l:'注意',c:'#722ED1'},{l:'备件',c:'#13C2C2'},{l:'工具',c:'#8C8C8C'}]
const nc={Equipment:'#002EA6',Symptom:'#FF4D4F',Cause:'#FA8C16',Step:'#52C41A',Precaution:'#722ED1',SparePart:'#13C2C2',Tool:'#8C8C8C'}
const ec={CAUSED_BY:'#FA8C16',FIXED_BY:'#52C41A',NEXT_STEP:'#13C2C2',BELONGS_TO:'#002EA6',SUBCLASS_OF:'#002EA6',HAS_PRECAUTION:'#722ED1',REQUIRES_TOOL:'#8C8C8C',USES_SPAREPART:'#13C2C2'}
onMounted(async()=>{loading.value=true;try{const{data}=await graphAPI.overview();init(data.nodes||[],data.edges||[])}catch(e){}loading.value=false})
onBeforeUnmount(()=>{graph?.destroy()})
watch(()=>p.highlightNodes,ids=>{if(!graph)return;const s=new Set(ids);graph.getNodes().forEach(n=>{const m=n.getModel();const h=s.has(m.id);graph.updateItem(n,{style:{opacity:ids.length&&!h?0.06:1,lineWidth:ids.length&&h?4:2,stroke:ids.length&&h?'#FFE76F':nc[m.label]||'#002EA6'},labelCfg:{style:{fontWeight:ids.length&&h?'bold':'normal',fontSize:ids.length&&h?13:10}}})})})
function init(ns,es){
  const w=c.value?.clientWidth||900,h=c.value?.clientHeight||600
  graph=new G6.Graph({container:c.value,width:w,height:h,fitView:true,fitViewPadding:60,animate:true,minZoom:0.2,maxZoom:5,
    modes:{default:['drag-canvas','zoom-canvas','drag-node']},
    layout:{type:'gForce',preventOverlap:true,nodeSpacing:150,linkDistance:220,nodeStrength:2000,edgeStrength:0.1,gravity:8},
    defaultNode:{size:30,labelCfg:{style:{fill:'#fff',fontSize:10,fontFamily:'Microsoft YaHei'}},style:{stroke:'#fff',lineWidth:2,cursor:'pointer'}},
    defaultEdge:{type:'cubic-horizontal',style:{lineWidth:1.5,stroke:'#B0BEC5',endArrow:{path:G6.Arrow.triangle(5,7,0),fill:'#B0BEC5'},cursor:'pointer'}},
  })
  graph.data({nodes:ns.map(n=>({id:n.uid,label:n.name.length>8?n.name.slice(0,8)+'…':n.name,_n:n.name,lt:n.label,size:n.label==='Equipment'?36:n.label==='Symptom'?28:22,style:{fill:nc[n.label]||'#002EA6'}})),
    edges:es.map(e=>({id:`${e.from}-${e.to}`,source:e.from,target:e.to,_t:e.type,style:{stroke:ec[e.type]||'#B0BEC5',lineWidth:['CAUSED_BY','FIXED_BY'].includes(e.type)?2.5:1.5,endArrow:{path:G6.Arrow.triangle(5,7,0),fill:ec[e.type]||'#B0BEC5'}},label:['CAUSED_BY','FIXED_BY','NEXT_STEP'].includes(e.type)?{CAUSED_BY:'原因',FIXED_BY:'维修',NEXT_STEP:'→'}[e.type]:''}))})
  graph.render()
  graph.on('node:click',async e=>{try{const{data:d}=await graphAPI.node(e.item.getModel().id);emit('node-click',d)}catch(_){}})
  graph.on('node:dblclick',async e=>{await expand(e.item.getModel().id)})
  graph.on('node:mouseenter',e=>{const n=e.item,eds=n.getEdges(),ns=new Set([n.getID()]);eds.forEach(ed=>{ns.add(ed.getSource().getID());ns.add(ed.getTarget().getID())});graph.getNodes().forEach(n=>graph.updateItem(n,{style:{opacity:ns.has(n.getID())?1:0.1}}));graph.getEdges().forEach(e=>graph.updateItem(e,{style:{opacity:ns.has(e.getModel().source)&&ns.has(e.getModel().target)?1:0.03}}))})
  graph.on('node:mouseleave',()=>{graph.getNodes().forEach(n=>graph.updateItem(n,{style:{opacity:1}}));graph.getEdges().forEach(e=>graph.updateItem(e,{style:{opacity:1}}))})
}
async function expand(uid){loading.value=true;try{const{data}=await graphAPI.expand(uid);const ex=new Set(graph.getNodes().map(n=>n.getModel().id));for(const n of data.nodes||[]){if(!ex.has(n.uid)){graph.addItem('node',{id:n.uid,label:n.name.length>8?n.name.slice(0,8)+'…':n.name,_n:n.name,lt:n.label,size:n.label==='Equipment'?36:n.label==='Symptom'?28:22,style:{fill:nc[n.label]||'#002EA6'}});ex.add(n.uid)}}for(const e of data.edges||[]){const eid=`${e.from}-${e.to}`;if(!graph.findById(eid))graph.addItem('edge',{id:eid,source:e.from,target:e.to,style:{stroke:ec[e.type]||'#B0BEC5',lineWidth:2,endArrow:{path:G6.Arrow.triangle(5,7,0),fill:ec[e.type]||'#B0BEC5'}}})}graph.layout();graph.fitView(40)}catch(e){}loading.value=false}
</script>
<style scoped>
.graph-panel{width:100%;height:100%;position:relative;background:#F4F6F9}
.ld{position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(245,247,250,0.7);display:flex;align-items:center;justify-content:center;z-index:20}
.sp{width:36px;height:36px;border:3px solid #E8ECF1;border-top-color:#002EA6;border-radius:50%;animation:k .8s linear infinite}
@keyframes k{to{transform:rotate(360deg)}}
.lg{position:absolute;bottom:14px;left:14px;display:flex;gap:12px;background:rgba(255,255,255,0.95);padding:8px 16px;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);flex-wrap:wrap;z-index:10}
.li{display:flex;align-items:center;gap:6px;font-size:12px;color:#555;font-weight:500}
.d{width:12px;height:12px;border-radius:50%}
</style>
