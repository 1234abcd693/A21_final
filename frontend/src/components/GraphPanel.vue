<template>
  <div class="graph-panel">
    <div ref="container" class="net"></div>
    <div class="controls"><button @click="fit">⌂</button></div>
    <div class="legend">
      <span v-for="l in legend" :key="l.label" class="leg"><span class="dot" :style="{background:l.color}"></span>{{l.label}}</span>
    </div>
    <div v-if="loading" class="loading"><div class="spin"></div></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Network } from 'vis-network'
import { DataSet } from 'vis-data'
import { graphAPI } from '../api/index.js'

const props = defineProps({ highlightNodes: { type: Array, default: () => [] } })
const emit = defineEmits(['node-click'])
const container = ref(null), loading = ref(false)
let net, nodes, edges

const legend = [
  { label:'设备',color:'#002EA6'},{label:'故障',color:'#FF4D4F'},{label:'原因',color:'#FA8C16'},
  { label:'维修',color:'#52C41A'},{label:'注意',color:'#722ED1'},{label:'备件',color:'#13C2C2'},{label:'工具',color:'#8C8C8C'},
]
const colors = {
  Equipment:{bg:'#002EA6',b:'#001A5C'},Symptom:{bg:'#FF4D4F',b:'#CC0000'},Cause:{bg:'#FA8C16',b:'#D46B08'},
  Step:{bg:'#52C41A',b:'#389E0D'},Precaution:{bg:'#722ED1',b:'#531DAB'},SparePart:{bg:'#13C2C2',b:'#08979C'},Tool:{bg:'#8C8C8C',b:'#595959'},
}
const edgeColors = {
  CAUSED_BY:{color:'#FA8C16',w:2},FIXED_BY:{color:'#52C41A',w:2},NEXT_STEP:{color:'#13C2C2',w:1.5},
  BELONGS_TO:{color:'#002EA6',d:true,w:1},SUBCLASS_OF:{color:'#002EA6',d:true,w:1},
  HAS_PRECAUTION:{color:'#722ED1',w:1.5},REQUIRES_TOOL:{color:'#8C8C8C',w:1},USES_SPAREPART:{color:'#13C2C2',w:1},
}

onMounted(async()=>{
  loading.value=true
  try{const{data}=await graphAPI.overview();build(data.nodes||[],data.edges||[])}catch(e){}
  loading.value=false
})

watch(()=>props.highlightNodes,ids=>{
  if(!net)return
  const s=new Set(ids)
  nodes.forEach(n=>nodes.update({id:n.id,opacity:ids.length&&!s.has(n.id)?0.12:1,borderWidth:ids.length&&s.has(n.id)?3:2,color:ids.length&&s.has(n.id)?{...colors[n.group]||colors.Equipment,border:'#FFE76F'}:colors[n.group]||colors.Equipment}))
})

function build(ns,es){
  nodes=new DataSet(ns.map(n=>({
    id:n.uid,label:n.name.length>10?n.name.slice(0,10)+'…':n.name,title:`<b>${n.label}</b><br>${n.name}`,
    group:n.label,color:colors[n.label]||colors.Equipment,
    shape:n.label==='Equipment'?'box':'dot',size:n.label==='Equipment'?28:n.label==='Symptom'?22:16,
    font:{size:11,color:'#333',face:'Microsoft YaHei'},borderWidth:2,
  })))
  edges=new DataSet(es.map(e=>({
    id:`${e.from}-${e.to}`,from:e.from,to:e.to,
    arrows:{to:{enabled:true,scaleFactor:0.6}},
    ...(edgeColors[e.type]||{color:'#999',w:1}),width:edgeColors[e.type]?.w||1,
    dashes:edgeColors[e.type]?.d||false,title:e.type,smooth:{type:'continuous'},
  })))
  net=new Network(container.value,{nodes,edges},{
    physics:{solver:'forceAtlas2Based',forceAtlas2Based:{gravitationalConstant:-60,centralGravity:0.005,springLength:250,springConstant:0.06,damping:0.4},stabilization:{iterations:300}},
    interaction:{hover:true,zoomView:true,dragView:true},
    nodes:{borderWidth:2,shadow:{enabled:true,size:4}},
  })
  net.on('click',async p=>{if(p.nodes.length===1)try{const{data:d}=await graphAPI.node(p.nodes[0]);emit('node-click',d)}catch(e){}})
  net.on('doubleClick',async p=>{if(p.nodes.length===1)await expand(p.nodes[0])})
  net.once('stabilizationIterationsDone',()=>net.fit({animation:{duration:800}}))
}

async function expand(uid){
  loading.value=true
  try{
    const{data}=await graphAPI.expand(uid)
    const ids=new Set(nodes.getIds())
    for(const n of data.nodes||[]){if(!ids.has(n.uid)){nodes.add({id:n.uid,label:n.name.length>10?n.name.slice(0,10)+'…':n.name,title:`<b>${n.label}</b><br>${n.name}`,group:n.label,color:colors[n.label]||colors.Equipment,shape:n.label==='Equipment'?'box':'dot',size:n.label==='Equipment'?28:n.label==='Symptom'?22:16,font:{size:11,color:'#333',face:'Microsoft YaHei'},borderWidth:2});ids.add(n.uid)}}
    for(const e of data.edges||[]){const eid=`${e.from}-${e.to}`;if(!edges.get(eid))edges.add({id:eid,from:e.from,to:e.to,arrows:{to:{enabled:true,scaleFactor:0.6}},...(edgeColors[e.type]||{color:'#999',w:1}),width:edgeColors[e.type]?.w||1,dashes:edgeColors[e.type]?.d||false,title:e.type,smooth:{type:'continuous'}})}
    net.fit({animation:{duration:500}})
  }catch(e){}
  loading.value=false
}

function fit(){net?.fit({animation:{duration:500}})}
</script>

<style scoped>
.graph-panel{width:100%;height:100%;position:relative;background:linear-gradient(180deg,#F5F7FA,#EEF1F6)}
.net{width:100%;height:100%}
.controls{position:absolute;top:12px;right:12px;z-index:10}
.controls button{width:32px;height:32px;border-radius:8px;border:1px solid #D0D8E8;background:#fff;cursor:pointer;font-size:16px;color:#002EA6}
.controls button:hover{background:#F0F4FF;border-color:#002EA6}
.legend{position:absolute;bottom:12px;left:12px;display:flex;gap:10px;background:rgba(255,255,255,0.94);padding:6px 14px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.06);flex-wrap:wrap;z-index:10}
.leg{display:flex;align-items:center;gap:5px;font-size:11px;color:#555}
.dot{width:10px;height:10px;border-radius:50%}
.loading{position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(245,247,250,0.7);display:flex;align-items:center;justify-content:center;z-index:20}
.spin{width:36px;height:36px;border:3px solid #E8ECF1;border-top-color:#002EA6;border-radius:50%;animation:s .8s linear infinite}
@keyframes s{to{transform:rotate(360deg)}}
</style>
