<template>
  <div class="graph-panel" ref="container">
    <div v-if="loading" class="loading"><div class="spin"></div></div>
    <div class="legend">
      <span v-for="l in legend" :key="l.label" class="leg"><span class="dot" :style="{background:l.color}"></span>{{l.label}}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import G6 from '@antv/g6'
import { graphAPI } from '../api/index.js'

const props = defineProps({ highlightNodes: { type: Array, default: () => [] } })
const emit = defineEmits(['node-click'])
const container = ref(null), loading = ref(false)
let graph = null

const legend = [
  { label:'设备',color:'#002EA6'},{label:'故障',color:'#FF4D4F'},{label:'原因',color:'#FA8C16'},
  { label:'维修',color:'#52C41A'},{label:'注意',color:'#722ED1'},{label:'备件',color:'#13C2C2'},{label:'工具',color:'#8C8C8C'},
]

const nodeColors = {
  Equipment:'#002EA6',Symptom:'#FF4D4F',Cause:'#FA8C16',Step:'#52C41A',Precaution:'#722ED1',SparePart:'#13C2C2',Tool:'#8C8C8C',
}

const edgeStyle = {
  CAUSED_BY:{stroke:'#FA8C16',lineWidth:2},
  FIXED_BY:{stroke:'#52C41A',lineWidth:2},
  NEXT_STEP:{stroke:'#13C2C2',lineWidth:1.5},
  BELONGS_TO:{stroke:'#002EA6',lineWidth:1,lineDash:[5,5]},
  SUBCLASS_OF:{stroke:'#002EA6',lineWidth:1,lineDash:[5,5]},
  HAS_PRECAUTION:{stroke:'#722ED1',lineWidth:1.5},
  REQUIRES_TOOL:{stroke:'#8C8C8C',lineWidth:1},
  USES_SPAREPART:{stroke:'#13C2C2',lineWidth:1},
}

onMounted(async()=>{loading.value=true;try{const{data}=await graphAPI.overview();initGraph(data.nodes||[],data.edges||[])}catch(e){}finally{loading.value=false}})
onBeforeUnmount(()=>{graph?.destroy()})

watch(()=>props.highlightNodes,ids=>{
  if(!graph)return
  const s=new Set(ids)
  graph.getNodes().forEach(n=>{
    const m=n.getModel()
    const hit=s.has(m.id)||s.has(m._uid||'')
    graph.updateItem(n,{style:{opacity:ids.length&&!hit?0.08:1,lineWidth:ids.length&&hit?3:1,stroke:ids.length&&hit?'#FFE76F':nodeColors[m.label]||'#002EA6'}})
  })
})

function initGraph(nodes,edges){
  const w=container.value?.clientWidth||900
  const h=container.value?.clientHeight||600
  const tooltip=new G6.Tooltip({offsetX:10,offsetY:10,fixToNode:[1,0.5],itemTypes:['node','edge'],
    getContent(e){const m=e.item.getModel();return e.item.getType()==='node'?`<div style="padding:8px 12px;background:#fff;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.2)"><b>${m.label}</b><br>${m._name||m.label}</div>`:`<div style="padding:4px 10px;background:#fff;border-radius:6px;font-size:12px">${m._type||''}</div>`}
  })

  graph=new G6.Graph({
    container:container.value,width:w,height:h,
    fitView:true,fitViewPadding:40,
    animate:true,minZoom:0.2,maxZoom:5,
    modes:{default:['drag-canvas','zoom-canvas','drag-node']},
    layout:{type:'force',preventOverlap:true,nodeSpacing:80,linkDistance:180,nodeStrength:1000,edgeStrength:0.2,alpha:0.3,alphaDecay:0.028,alphaMin:0.01},
    defaultNode:{type:'circle',size:28,labelCfg:{style:{fill:'#fff',fontSize:11,fontFamily:'Microsoft YaHei'}},style:{stroke:'#fff',lineWidth:2,cursor:'pointer'}},
    defaultEdge:{type:'polyline',style:{endArrow:{path:G6.Arrow.triangle(6,8,0),fill:'#999'},cursor:'pointer'}},
    plugins:[tooltip],
  })

  const ns=nodes.map(n=>({id:n.uid,label:n.name.length>8?n.name.slice(0,8)+'…':n.name,_name:n.name,_uid:n.uid,labelType:n.label,size:n.label==='Equipment'?36:n.label==='Symptom'?26:20,style:{fill:nodeColors[n.label]||'#002EA6'}}))
  const es=edges.map(e=>({id:`${e.from}-${e.to}`,_type:e.type,source:e.from,target:e.to,label:e.type==='CAUSED_BY'?'原因':e.type==='FIXED_BY'?'维修':e.type==='BELONGS_TO'?'归属':'',style:{...(edgeStyle[e.type]||{stroke:'#999',lineWidth:1}),endArrow:{path:G6.Arrow.triangle(6,8,0),fill:edgeStyle[e.type]?.stroke||'#999'}}}))

  graph.data({nodes:ns,edges:es})
  graph.render()

  // 单击 → 详情
  graph.on('node:click',async e=>{
    try{const{data:d}=await graphAPI.node(e.item.getModel()._uid);emit('node-click',d)}catch(_){}
  })

  // 双击 → 展开
  graph.on('node:dblclick',async e=>{await expandNode(e.item.getModel()._uid)})

  // 悬浮 → 高亮邻居
  graph.on('node:mouseenter',e=>{
    const node=e.item;const edges=node.getEdges();const neighbors=new Set([node.getID()])
    edges.forEach(edge=>{neighbors.add(edge.getSource().getID());neighbors.add(edge.getTarget().getID())})
    graph.getNodes().forEach(n=>{const m=n.getModel();graph.updateItem(n,{style:{opacity:neighbors.has(n.getID())?1:0.15}})})})
  graph.on('node:mouseleave',()=>{graph.getNodes().forEach(n=>graph.updateItem(n,{style:{opacity:1}}))})
}

async function expandNode(uid){
  loading.value=true
  try{
    const{data}=await graphAPI.expand(uid)
    const existing=new Set(graph.getNodes().map(n=>n.getModel()._uid))
    for(const n of data.nodes||[]){if(!existing.has(n.uid)){graph.addItem('node',{id:n.uid,label:n.name.length>8?n.name.slice(0,8)+'…':n.name,_name:n.name,_uid:n.uid,labelType:n.label,size:n.label==='Equipment'?36:n.label==='Symptom'?26:20,style:{fill:nodeColors[n.label]||'#002EA6'}});existing.add(n.uid)}}
    for(const e of data.edges||[]){const eid=`${e.from}-${e.to}`;if(!graph.findById(eid))graph.addItem('edge',{id:eid,_type:e.type,source:e.from,target:e.to,style:{...(edgeStyle[e.type]||{stroke:'#999',lineWidth:1}),endArrow:{path:G6.Arrow.triangle(6,8,0),fill:edgeStyle[e.type]?.stroke||'#999'}}})}
    graph.layout();graph.fitView(40)
  }catch(e){}
  loading.value=false
}
</script>

<style scoped>
.graph-panel{width:100%;height:100%;position:relative;background:linear-gradient(180deg,#F0F2F5,#E8ECF1)}
.loading{position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(245,247,250,0.7);display:flex;align-items:center;justify-content:center;z-index:20}
.spin{width:36px;height:36px;border:3px solid #E8ECF1;border-top-color:#002EA6;border-radius:50%;animation:s .8s linear infinite}
@keyframes s{to{transform:rotate(360deg)}}
.legend{position:absolute;bottom:14px;left:14px;display:flex;gap:12px;background:rgba(255,255,255,0.95);padding:8px 16px;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);flex-wrap:wrap;z-index:10}
.leg{display:flex;align-items:center;gap:6px;font-size:12px;color:#555;font-weight:500}
.dot{width:12px;height:12px;border-radius:50%}
</style>
