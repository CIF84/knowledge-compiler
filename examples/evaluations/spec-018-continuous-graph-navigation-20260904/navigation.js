"use strict";

const state = {
  fixture: null,
  camera: null,
  selectedNodeId: null,
  selectedEdgeKey: null,
  previewNodeId: null,
  previewEdgeKey: null,
  backStack: [],
  forwardStack: [],
  animationFrame: null,
  animating: false,
  panStart: null,
};
const svgNS = "http://www.w3.org/2000/svg";
const byId = id => document.getElementById(id);

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function svgElement(tag, attributes = {}) {
  const node = document.createElementNS(svgNS, tag);
  Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
  return node;
}

function pathData(route) {
  const points = route.points;
  if (route.path_kind === "LINE") return `M ${points[0].x} ${points[0].y} L ${points[1].x} ${points[1].y}`;
  if (route.path_kind === "QUADRATIC") return `M ${points[0].x} ${points[0].y} Q ${points[1].x} ${points[1].y} ${points[2].x} ${points[2].y}`;
  return `M ${points[0].x} ${points[0].y} C ${points[1].x} ${points[1].y} ${points[2].x} ${points[2].y} ${points[3].x} ${points[3].y}`;
}

function appendArrowMarker(defs, id, color) {
  const marker = svgElement("marker", {id, viewBox:"0 0 10 10", refX:"9", refY:"5", markerWidth:"7", markerHeight:"7", orient:"auto-start-reverse"});
  marker.append(svgElement("path", {d:"M 0 0 L 10 5 L 0 10 z", fill:color}));
  defs.append(marker);
}

function cameraSnapshot() {
  return {camera:{...state.camera}, selectedNodeId:state.selectedNodeId, selectedEdgeKey:state.selectedEdgeKey};
}

function sameCamera(left, right) {
  return Math.abs(left.x-right.x)<.001 && Math.abs(left.y-right.y)<.001 && left.scale===right.scale;
}

function viewSize(camera=state.camera) {
  return {width:state.fixture.camera.viewport.width/camera.scale, height:state.fixture.camera.viewport.height/camera.scale};
}

function clampCamera(camera) {
  const size=viewSize(camera), bounds=state.fixture.world.bounds;
  return {x:Math.max(bounds.min_x,Math.min(bounds.max_x-size.width,camera.x)), y:Math.max(bounds.min_y,Math.min(bounds.max_y-size.height,camera.y)), scale:camera.scale};
}

function applyViewBox() {
  const size=viewSize();
  byId("graph").setAttribute("viewBox",`${state.camera.x} ${state.camera.y} ${size.width} ${size.height}`);
  updateFrontiers();
}

function setCamera(target, animate=true) {
  target=clampCamera(target);
  if (state.animationFrame) cancelAnimationFrame(state.animationFrame);
  const reduced=window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!animate || reduced || sameCamera(state.camera,target)) { state.animating=false; state.camera=target; applyViewBox(); return; }
  state.animating=true;
  const start={...state.camera}, started=performance.now(), duration=state.fixture.camera.focus_animation_ms;
  const frame=now=>{
    const t=Math.min(1,(now-started)/duration), eased=1-Math.pow(1-t,3);
    state.camera={x:start.x+(target.x-start.x)*eased,y:start.y+(target.y-start.y)*eased,scale:start.scale};
    applyViewBox();
    if(t<1) state.animationFrame=requestAnimationFrame(frame); else { state.animationFrame=null; state.animating=false; clearPreview(); }
  };
  state.animationFrame=requestAnimationFrame(frame);
}

function pointVisible(point, margin=0) {
  const size=viewSize();
  return point.x>=state.camera.x+margin && point.x<=state.camera.x+size.width-margin && point.y>=state.camera.y+margin && point.y<=state.camera.y+size.height-margin;
}

function focusTarget(nodeId) {
  const node=nodeById(nodeId), size=viewSize(), zone=state.fixture.camera.focus_zone;
  const comfortable=node.world.x>=state.camera.x+size.width*zone.horizontal_margin_ratio && node.world.x<=state.camera.x+size.width*(1-zone.horizontal_margin_ratio) && node.world.y>=state.camera.y+size.height*zone.vertical_margin_ratio && node.world.y<=state.camera.y+size.height*(1-zone.vertical_margin_ratio);
  const adjacentOutside=state.fixture.navigation.adjacency[nodeId].some(id=>!pointVisible(nodeById(id).world,84));
  if(comfortable&&!adjacentOutside) return {...state.camera};
  return clampCamera({x:node.world.x-size.width/2,y:node.world.y-size.height/2,scale:state.camera.scale});
}

function nodeById(id) { return state.fixture.nodes.find(node=>node.entity_id===id); }
function edgeByKey(key) { return state.fixture.edges.find(edge=>edge.edge_key===key); }

function effectiveSelection() {
  if(state.previewEdgeKey)return{kind:"edge",id:state.previewEdgeKey,preview:true};
  if(state.previewNodeId)return{kind:"node",id:state.previewNodeId,preview:true};
  if(state.selectedEdgeKey)return{kind:"edge",id:state.selectedEdgeKey,preview:false};
  if(state.selectedNodeId)return{kind:"node",id:state.selectedNodeId,preview:false};
  return null;
}

function resetDetail() {
  byId("detail").replaceChildren(element("span","Detail","eyebrow"),element("h2","Select a node or relationship"),element("p","Inspect concept context or relationship meaning and source evidence."));
}

function showNode(node,preview) {
  const detail=byId("detail");
  detail.replaceChildren(element("span",preview?"Preview · Concept":"Selected · Concept","eyebrow interaction-status"),element("h2",node.label));
  const dl=element("dl",undefined,"detail-grid");
  [["Type",node.entity_type],["Entity ID",node.entity_id],["World position",`${node.world.x}, ${node.world.y}`]].forEach(([term,value])=>dl.append(element("dt",term),element("dd",value)));
  detail.append(dl,element("p",node.description));
}

function showEdge(edge,preview) {
  const detail=byId("detail"),source=nodeById(edge.source_entity_id),target=nodeById(edge.target_entity_id);
  detail.replaceChildren(element("span",preview?"Preview · Relationship":"Selected · Relationship","eyebrow interaction-status"),element("h2",`${source.label} → ${target.label}`));
  const dl=element("dl",undefined,"detail-grid");
  [["Predicate",edge.relationship_type],["Direction",edge.direction],["Relationship IDs",edge.relationship_ids.join(", ")],["Provenance",edge.provenance_status]].forEach(([term,value])=>dl.append(element("dt",term),element("dd",value)));
  detail.append(dl,element("p",edge.meaning),element("h3","Source evidence"));
  edge.evidence.forEach(item=>detail.append(element("blockquote",`“${item.quote}”`),element("small",`${item.relationship_id} · characters ${item.start_char}–${item.end_char}`)));
}

function updateInteraction() {
  const effective=effectiveSelection();
  document.querySelectorAll("[data-node-id]").forEach(node=>{
    const matches=effective?.kind==="node"&&node.dataset.nodeId===effective.id;
    node.classList.toggle("is-selected",matches&&!effective.preview);node.classList.toggle("is-preview",matches&&effective.preview);node.classList.toggle("is-unrelated",Boolean(effective)&&!matches);node.setAttribute("aria-pressed",String(matches));
  });
  document.querySelectorAll("[data-edge-key]").forEach(node=>{
    const matches=effective?.kind==="edge"&&node.dataset.edgeKey===effective.id;
    node.classList.toggle("is-selected",matches&&!effective.preview);node.classList.toggle("is-preview",matches&&effective.preview);node.classList.toggle("is-unrelated",Boolean(effective)&&!matches);if(node.getAttribute("role")==="button")node.setAttribute("aria-pressed",String(matches));
  });
  byId("clear-selection").disabled=!(state.selectedNodeId||state.selectedEdgeKey);
  byId("history-back").disabled=!state.backStack.length;byId("history-forward").disabled=!state.forwardStack.length;
  if(!effective){resetDetail();return;}if(effective.kind==="node")showNode(nodeById(effective.id),effective.preview);else showEdge(edgeByKey(effective.id),effective.preview);
}

function selectNode(nodeId) {
  const previous=cameraSnapshot();
  state.selectedNodeId=nodeId;state.selectedEdgeKey=null;state.previewNodeId=null;state.previewEdgeKey=null;
  const target=focusTarget(nodeId);
  if(!sameCamera(target,state.camera)){state.backStack.push(previous);state.forwardStack=[];setCamera(target,true);}
  byId("focus-status").textContent=`Focused: ${nodeById(nodeId).label}`;updateInteraction();
}

function selectEdge(edgeKey){state.selectedEdgeKey=edgeKey;state.selectedNodeId=null;state.previewNodeId=null;state.previewEdgeKey=null;updateInteraction();}
function previewNode(nodeId){if(state.animating)return;state.previewNodeId=nodeId;state.previewEdgeKey=null;updateInteraction();}
function previewEdge(edgeKey){if(state.animating)return;state.previewEdgeKey=edgeKey;state.previewNodeId=null;updateInteraction();}
function clearPreview(){state.previewNodeId=null;state.previewEdgeKey=null;updateInteraction();}
function keyboardSelect(event,callback){if(event.key==="Enter"||event.key===" "){event.preventDefault();callback();}}

function clearSelection(){state.selectedNodeId=null;state.selectedEdgeKey=null;state.previewNodeId=null;state.previewEdgeKey=null;byId("focus-status").textContent="Map position preserved";updateInteraction();}

function updateFrontiers(){
  if(!state.fixture)return;
  document.querySelectorAll("[data-node-id]").forEach(node=>{
    const id=node.dataset.nodeId;
    const frontier=pointVisible(nodeById(id).world,84)&&state.fixture.navigation.adjacency[id].some(neighbor=>!pointVisible(nodeById(neighbor).world,84));
    node.querySelector(".frontier-mark")?.toggleAttribute("hidden",!frontier);
  });
}

function renderGraph(){
  const svg=byId("graph");svg.replaceChildren();
  const defs=svgElement("defs");appendArrowMarker(defs,"arrow","#697870");appendArrowMarker(defs,"arrow-selected","#176b50");appendArrowMarker(defs,"arrow-preview","#9a5f10");svg.append(defs);
  const routes=new Map(state.fixture.world.routes.map(route=>[route.edge_key,route]));
  state.fixture.edges.forEach(edge=>{
    const route=routes.get(edge.edge_key),data={"data-edge-key":edge.edge_key},path=pathData(route);
    const line=svgElement("path",{d:path,class:"edge-line",...data});
    const hit=svgElement("path",{d:path,class:"edge-hit",tabindex:"0",role:"button","aria-pressed":"false","aria-label":`${nodeById(edge.source_entity_id).label} ${edge.relationship_label} ${nodeById(edge.target_entity_id).label}`,...data});
    hit.addEventListener("click",event=>{event.stopPropagation();selectEdge(edge.edge_key);});hit.addEventListener("keydown",event=>keyboardSelect(event,()=>selectEdge(edge.edge_key)));hit.addEventListener("mouseenter",()=>previewEdge(edge.edge_key));hit.addEventListener("mouseleave",clearPreview);
    const label=svgElement("text",{x:route.label_x,y:route.label_y,"text-anchor":"middle",class:"edge-label",...data});label.textContent=edge.relationship_label;
    svg.append(line,hit,label);
  });
  state.fixture.nodes.forEach(node=>{
    const group=svgElement("g",{class:"node",tabindex:"0",role:"button","aria-pressed":"false","aria-label":node.label,"data-node-id":node.entity_id});
    group.append(svgElement("rect",{x:node.world.x-84,y:node.world.y-30,width:"168",height:"60",rx:"8"}));
    const label=svgElement("text",{x:node.world.x,y:node.world.y+4,"text-anchor":"middle"});label.textContent=node.label.length>24?`${node.label.slice(0,22)}…`:node.label;group.append(label);
    group.append(svgElement("circle",{class:"frontier-mark",cx:node.world.x+76,cy:node.world.y-22,r:"6",hidden:""}));
    group.addEventListener("pointerdown",event=>event.stopPropagation());group.addEventListener("click",event=>{event.stopPropagation();selectNode(node.entity_id);});group.addEventListener("keydown",event=>keyboardSelect(event,()=>selectNode(node.entity_id)));group.addEventListener("mouseenter",()=>previewNode(node.entity_id));group.addEventListener("mouseleave",clearPreview);svg.append(group);
  });
  applyViewBox();updateInteraction();
}

function pushPanHistory(start){if(!sameCamera(start.camera,state.camera)){state.backStack.push(start);state.forwardStack=[];updateInteraction();}}

function installPanning(){
  const viewport=byId("graph-viewport"),svg=byId("graph");
  viewport.addEventListener("pointerdown",event=>{
    if(event.target!==svg&&event.target!==viewport)return;
    if(state.animationFrame)cancelAnimationFrame(state.animationFrame);state.animationFrame=null;state.animating=false;
    state.panStart={pointerId:event.pointerId,x:event.clientX,y:event.clientY,lastX:event.clientX,lastY:event.clientY,snapshot:cameraSnapshot()};viewport.setPointerCapture(event.pointerId);viewport.classList.add("is-panning");
  });
  viewport.addEventListener("pointermove",event=>{
    if(!state.panStart||event.pointerId!==state.panStart.pointerId)return;
    const rect=viewport.getBoundingClientRect(),dx=event.clientX-state.panStart.lastX,dy=event.clientY-state.panStart.lastY,size=viewSize();state.panStart.lastX=event.clientX;state.panStart.lastY=event.clientY;
    state.camera=clampCamera({x:state.camera.x-dx*size.width/rect.width,y:state.camera.y-dy*size.height/rect.height,scale:state.camera.scale});applyViewBox();
  });
  const finish=event=>{if(!state.panStart||event.pointerId!==state.panStart.pointerId)return;pushPanHistory(state.panStart.snapshot);state.panStart=null;viewport.classList.remove("is-panning");};
  viewport.addEventListener("pointerup",finish);viewport.addEventListener("pointercancel",finish);
}

function restoreSnapshot(snapshot,animate=true){state.selectedNodeId=snapshot.selectedNodeId;state.selectedEdgeKey=snapshot.selectedEdgeKey;setCamera(snapshot.camera,animate);byId("focus-status").textContent=state.selectedNodeId?`Focused: ${nodeById(state.selectedNodeId).label}`:"Map position restored";updateInteraction();}
function historyBack(){if(!state.backStack.length)return;state.forwardStack.push(cameraSnapshot());restoreSnapshot(state.backStack.pop());}
function historyForward(){if(!state.forwardStack.length)return;state.backStack.push(cameraSnapshot());restoreSnapshot(state.forwardStack.pop());}
function overview(){state.backStack.push(cameraSnapshot());state.forwardStack=[];state.selectedNodeId=null;state.selectedEdgeKey=null;setCamera({...state.fixture.camera.initial},true);byId("focus-status").textContent="Overview";updateInteraction();}

fetch("manifest.json").then(response=>response.json()).then(manifest=>fetch(manifest.fixture)).then(response=>response.json()).then(fixture=>{
  state.fixture=fixture;state.camera={...fixture.camera.initial};renderGraph();installPanning();
  byId("clear-selection").addEventListener("click",clearSelection);byId("history-back").addEventListener("click",historyBack);byId("history-forward").addEventListener("click",historyForward);byId("overview").addEventListener("click",overview);
}).catch(error=>{byId("model-title").textContent="Viewer data could not be loaded";byId("detail").textContent=String(error);});
