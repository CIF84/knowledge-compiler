"use strict";

// SPEC-030 is a one-way presentation projection. Semantic state and dispatch
// remain owned by the unchanged SPEC-029 atomic reducer.
const learningSurfaceApi=window.__BASELINE003_SEAM__;
const learningSurfaceSvgNS="http://www.w3.org/2000/svg";
let learningSurfaceScheduled=false;

function learningSurfaceElement(tag,text,className){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;}
function learningSurfaceSvg(tag,attributes={}){const node=document.createElementNS(learningSurfaceSvgNS,tag);Object.entries(attributes).forEach(([name,value])=>node.setAttribute(name,String(value)));return node;}
function learningSurfaceState(){return window.__SPEC029_ATOMIC__?.snapshot();}
function learningSurfaceDomain(state){return learningSurfaceApi.state.fixture.domains.find(item=>item.domain_id===state.activeContext.domainId);}
function learningSurfaceRepresentation(state,domain){return domain.learning_model.representations[state.activeContext.representationIndex];}
function learningSurfaceEffective(state){if(state.hovered)return{key:state.hovered,ancestry:state.hoverAncestry,mode:"preview"};if(state.selected)return{key:state.selected,ancestry:state.selectedAncestry,mode:"selected"};return null;}
function learningSurfaceExpansion(ancestry){const id=ancestry.at(-1);return id&&typeof depthState!=="undefined"?depthState.registry.get(id):null;}
function learningSurfaceEvidence(value){return(value.evidence||[]).map(item=>({...item}));}
function learningSurfaceForm(kind,predicate=""){if(kind==="orientation")return"ORIENTATION_SUMMARY";if(kind==="concept")return"CONCISE_CONCEPT_EXPLANATION";if(kind==="explanation")return"SOURCE_BACKED_EXPLANATION";if(["CAUSES","INCREASES","DECREASES","INDUCES"].includes(predicate))return"FOCUSED_CAUSAL_RELATIONSHIP";if(["PART_OF","IS_A"].includes(predicate))return"FOCUSED_HIERARCHY_RELATIONSHIP";if(["PRECEDES","ENABLES"].includes(predicate))return"FOCUSED_SEQUENCE_RELATIONSHIP";return"FOCUSED_RELATIONSHIP";}

function learningSurfaceResolve(){
  const state=learningSurfaceState();
  if(!state?.activeContext||!learningSurfaceApi.state.fixture)return null;
  const domain=learningSurfaceDomain(state),representation=learningSurfaceRepresentation(state,domain),effective=learningSurfaceEffective(state);
  if(!effective){const ancestry=[...state.revealed],expansion=learningSurfaceExpansion(ancestry);if(expansion)return{identity:null,kind:"orientation",mode:"clear",ancestry,form:learningSurfaceForm("orientation"),title:"Double-slit experiment · deeper map",summary:"Focus-centered deeper explanatory context",facts:[{label:"Concepts",value:expansion.concepts.length},{label:"Canonical relationships",value:expansion.canonical_items.length},{label:"Source explanations",value:expansion.explanatory_items.length}],domain,representation,evidence:[],interactive:[]};return{identity:null,kind:"orientation",mode:"clear",ancestry:[],form:learningSurfaceForm("orientation"),title:domain.label,summary:representation.title,facts:[{label:"Concepts",value:representation.nodes.length},{label:"Relationships",value:representation.edges.length},{label:"Structure",value:representation.layout.strategy}],domain,representation,evidence:[],interactive:[]};}
  const identity=effective.key.identity,kind=effective.key.kind,ancestry=[...effective.ancestry],expansion=learningSurfaceExpansion(ancestry);
  if(expansion){
    if(kind==="concept"){
      const item=expansion.concepts.find(value=>value.entity_id===identity);if(!item)throw new Error(`SPEC-030 depth concept ${identity} is absent`);
      return{identity,kind,mode:effective.mode,ancestry,form:learningSurfaceForm(kind),title:item.label,description:item.description,entityType:item.entity_type,contextLabel:"Double-slit experiment · deeper map",evidence:[],interactive:[identity],domain,representation};
    }
    if(kind==="canonical"){
      const item=expansion.canonical_items.find(value=>value.id===identity);if(!item)throw new Error(`SPEC-030 depth relationship ${identity} is absent`);const labels=Object.fromEntries(expansion.concepts.map(value=>[value.entity_id,value.label]));
      return{identity,kind,mode:effective.mode,ancestry,form:learningSurfaceForm(kind,item.relationship_type),title:`${labels[item.source_entity_id]} → ${labels[item.target_entity_id]}`,predicate:item.relationship_type,meaning:item.predicate_meaning,statement:item.statement,source:{id:item.source_entity_id,label:labels[item.source_entity_id]},target:{id:item.target_entity_id,label:labels[item.target_entity_id]},provenance:"EXACT SOURCE EVIDENCE",evidence:learningSurfaceEvidence(item),interactive:[item.source_entity_id,identity,item.target_entity_id],domain,representation};
    }
    const item=expansion.explanatory_items.find(value=>value.id===identity);if(!item)throw new Error(`SPEC-030 depth explanation ${identity} is absent`);
    return{identity,kind,mode:effective.mode,ancestry,form:learningSurfaceForm(kind),title:item.short_label,statement:item.statement,presentationRole:item.presentation_role,semanticTier:item.semantic_tier,participants:[...item.participant_entity_ids],provenance:"EXACT SOURCE EVIDENCE",evidence:learningSurfaceEvidence(item),interactive:[identity,...item.participant_entity_ids],domain,representation};
  }
  if(kind==="concept"){
    const item=representation.nodes.find(value=>value.entity_id===identity);if(!item)throw new Error(`SPEC-030 concept ${identity} is absent from active representation`);
    return{identity,kind,mode:effective.mode,ancestry,form:learningSurfaceForm(kind),title:item.label,description:item.description||"No description was provided.",entityType:item.entity_type,contextLabel:domain.label,evidence:[],interactive:[identity],domain,representation};
  }
  const edge=representation.edges.find(value=>value.relationship_ids.includes(identity));if(!edge)throw new Error(`SPEC-030 relationship ${identity} is absent from active representation`);const nodes=Object.fromEntries(representation.nodes.map(value=>[value.entity_id,value]));
  return{identity,kind,mode:effective.mode,ancestry,form:learningSurfaceForm(kind,edge.relationship_type),title:`${nodes[edge.source_entity_id].label} → ${nodes[edge.target_entity_id].label}`,predicate:edge.relationship_type,meaning:edge.meaning,source:{id:edge.source_entity_id,label:nodes[edge.source_entity_id].label},target:{id:edge.target_entity_id,label:nodes[edge.target_entity_id].label},provenance:edge.provenance_status.replaceAll("_"," "),evidence:learningSurfaceEvidence(edge),interactive:[edge.source_entity_id,identity,edge.target_entity_id],domain,representation};
}

function learningSurfaceDecorate(node,identity,kind,payload,label){node.dataset.atomicId=identity;node.dataset.atomicKind=kind;node.dataset.atomicAncestry=payload.ancestry.join("/");node.dataset.atomicSurface="representation";node.dataset.atomicDomain=payload.domain.domain_id;node.dataset.atomicRepresentationIndex=String(payload.domain.learning_model.representations.indexOf(payload.representation));node.dataset.learningSemantic="";node.setAttribute("role","button");node.setAttribute("tabindex","0");node.setAttribute("aria-label",label);}
function learningSurfaceEvidenceBlock(payload){const section=learningSurfaceElement("section",undefined,"learning-surface-evidence"),heading=learningSurfaceElement("h4","Evidence & provenance");section.append(heading);if(!payload.evidence.length){section.append(learningSurfaceElement("p","No source excerpt is attached to this concept description.","learning-surface-muted"));return section;}payload.evidence.forEach(item=>{const quote=learningSurfaceElement("blockquote",item.quote),meta=learningSurfaceElement("p",`${payload.provenance} · ${item.document_id} · characters ${item.start_char}–${item.end_char}`,"learning-surface-source");section.append(quote,meta);});return section;}
function learningSurfaceBadge(payload){return payload.mode==="preview"?`PREVIEW · ${payload.kind.toUpperCase()}`:payload.kind==="canonical"?"TRUSTED CANONICAL RELATIONSHIP":payload.kind==="explanation"?"SOURCE-BACKED EXPLANATION · NON-CANONICAL":payload.kind.toUpperCase();}
function learningSurfaceInteractiveText(payload,identity,kind,label,className){const node=learningSurfaceElement("button",label,className);node.type="button";learningSurfaceDecorate(node,identity,kind,payload,label);return node;}

function learningSurfaceRenderRelationship(svg,detail,payload){
  svg.setAttribute("viewBox","0 0 760 280");svg.setAttribute("aria-label",`Focused explanation of ${payload.title}`);
  const defs=learningSurfaceSvg("defs"),marker=learningSurfaceSvg("marker",{id:"spec030-arrow",viewBox:"0 0 10 10",refX:9,refY:5,markerWidth:7,markerHeight:7,orient:"auto"});marker.append(learningSurfaceSvg("path",{d:"M 0 0 L 10 5 L 0 10 z"}));defs.append(marker);svg.append(defs);
  const line=learningSurfaceSvg("path",{d:"M 240 140 L 520 140",class:"learning-surface-relation"}),predicate=learningSurfaceSvg("g",{class:"learning-surface-predicate"}),predicateBox=learningSurfaceSvg("rect",{x:310,y:105,width:140,height:50,rx:25}),predicateText=learningSurfaceSvg("text",{x:380,y:136,"text-anchor":"middle"});predicateText.textContent=payload.predicate.replaceAll("_"," ");predicate.append(predicateBox,predicateText);learningSurfaceDecorate(predicate,payload.identity,"canonical",payload,`${payload.predicate} relationship`);
  const endpoint=(item,x)=>{const group=learningSurfaceSvg("g",{class:"learning-surface-endpoint"});group.append(learningSurfaceSvg("rect",{x:x-105,y:95,width:210,height:90,rx:12}));const text=learningSurfaceSvg("text",{x,y:136,"text-anchor":"middle"});text.textContent=item.label.length>27?`${item.label.slice(0,25)}…`:item.label;group.append(text);learningSurfaceDecorate(group,item.id,"concept",payload,item.label);return group;};
  svg.append(line,endpoint(payload.source,130),endpoint(payload.target,630),predicate);
  detail.append(learningSurfaceElement("span",learningSurfaceBadge(payload),`eyebrow learning-surface-marker${payload.ancestry.length?" depth-detail-marker":""}`),learningSurfaceElement("h3",payload.title),learningSurfaceElement("p",payload.meaning));if(payload.statement)detail.append(learningSurfaceElement("p",payload.statement,"learning-surface-statement"));const grid=learningSurfaceElement("dl",undefined,"detail-grid");[["Source",payload.source.label],["Relationship",payload.predicate.replaceAll("_"," ")],["Target",payload.target.label]].forEach(([term,value])=>grid.append(learningSurfaceElement("dt",term),learningSurfaceElement("dd",value)));detail.append(grid,learningSurfaceEvidenceBlock(payload));
}
function learningSurfaceRenderText(detail,payload){
  detail.append(learningSurfaceElement("span",learningSurfaceBadge(payload),`eyebrow learning-surface-marker${payload.ancestry.length?" depth-detail-marker":""}`),learningSurfaceElement("h3",payload.title));
  if(payload.kind==="orientation"){
    detail.append(learningSurfaceElement("p",`The active learning view is ${payload.summary}. Choose an object on the map to understand it here.`));const grid=learningSurfaceElement("dl",undefined,"detail-grid");payload.facts.forEach(item=>grid.append(learningSurfaceElement("dt",item.label),learningSurfaceElement("dd",String(item.value).replaceAll("_"," "))));detail.append(grid);return;
  }
  if(payload.kind==="concept")detail.append(learningSurfaceElement("p",payload.description),learningSurfaceElement("p",`${payload.entityType.replaceAll("_"," ")} · ${payload.contextLabel}`,"learning-surface-source"));
  else{detail.append(learningSurfaceElement("div","Grounded explanatory material, not a canonical relationship.","noncanonical-note"),learningSurfaceElement("p",payload.statement));const participants=learningSurfaceElement("div",undefined,"learning-surface-participants");payload.participants.forEach(identity=>participants.append(learningSurfaceInteractiveText(payload,identity,"concept",identity,"learning-surface-participant")));detail.append(participants);}
}
function learningSurfaceRender(){
  const payload=learningSurfaceResolve();if(!payload)return;
  const svg=document.getElementById("learning-graph"),detail=document.getElementById("learning-detail"),workspace=document.querySelector(".learning-workspace"),signature=JSON.stringify([learningSurfaceState().revision,payload.identity,payload.kind,payload.mode,payload.ancestry,payload.form]);
  if(svg.dataset.spec030Signature===signature&&detail.querySelector(".learning-surface-marker"))return;
  const interactivePreview=payload.mode==="preview"&&document.querySelector(`#learning-pane [data-learning-semantic][data-atomic-id="${CSS.escape(payload.identity)}"]`);
  if(interactivePreview){
    detail.replaceChildren();learningSurfaceRenderText(detail,payload);if(payload.kind!=="orientation"&&payload.kind!=="canonical")detail.append(learningSurfaceEvidenceBlock(payload));
    document.getElementById("representation-badge").textContent=payload.form.replaceAll("_"," ");document.getElementById("representation-meta").textContent="One canonical state · preview · interaction target preserved";
    const previewMarker=document.getElementById("spec030-learning-contract");previewMarker.dataset.form=payload.form;previewMarker.dataset.mode=payload.mode;previewMarker.dataset.identity=payload.identity;previewMarker.dataset.kind=payload.kind;previewMarker.dataset.canonicalIdentity=payload.identity;previewMarker.dataset.semanticAgreement="PASS";previewMarker.dataset.fullNavigationMapCount="0";previewMarker.dataset.interactiveSemanticElementCount=String(payload.interactive.length);previewMarker.dataset.depth=String(payload.ancestry.length);return;
  }
  svg.replaceChildren();detail.replaceChildren();svg.dataset.spec030Signature=signature;svg.dataset.focusKind=payload.kind;svg.dataset.focusId=payload.identity||"NONE";workspace.dataset.learningForm=payload.form;workspace.classList.toggle("learning-surface-text",payload.kind!=="canonical");
  document.getElementById("representation-badge").textContent=payload.form.replaceAll("_"," ");document.getElementById("representation-meta").textContent=`One canonical state · ${payload.mode==="preview"?"preview":"committed focus"} · no duplicate navigation map`;
  if(payload.kind==="canonical")learningSurfaceRenderRelationship(svg,detail,payload);else learningSurfaceRenderText(detail,payload);
  if(payload.kind!=="orientation"&&payload.kind!=="canonical")detail.append(learningSurfaceEvidenceBlock(payload));
  const marker=document.getElementById("spec030-learning-contract");marker.dataset.form=payload.form;marker.dataset.mode=payload.mode;marker.dataset.identity=payload.identity||"NONE";marker.dataset.kind=payload.kind;marker.dataset.canonicalIdentity=learningSurfaceEffective(learningSurfaceState())?.key.identity||"NONE";marker.dataset.semanticAgreement=marker.dataset.identity===marker.dataset.canonicalIdentity?"PASS":"FAIL";marker.dataset.fullNavigationMapCount="0";marker.dataset.interactiveSemanticElementCount=String(payload.interactive.length);marker.dataset.depth=String(payload.ancestry.length);
}
function learningSurfaceSchedule(){if(learningSurfaceScheduled)return;learningSurfaceScheduled=true;requestAnimationFrame(()=>{learningSurfaceScheduled=false;try{learningSurfaceRender();}catch(error){console.error("SPEC-030 learning-surface projection failed",error);}});}
function learningSurfaceInstall(){if(!window.__SPEC029_ATOMIC__||!learningSurfaceApi?.state.fixture||typeof depthState==="undefined"||!depthState.packet){requestAnimationFrame(learningSurfaceInstall);return;}const marker=document.createElement("div");marker.id="spec030-learning-contract";marker.hidden=true;marker.dataset.stateOwner="SPEC-029 atomicLearnerState";marker.dataset.authoritativeStateCount="0";marker.dataset.independentSelectionStateCount="0";marker.dataset.resolver="learningSurfaceResolve";marker.dataset.renderer="learningSurfaceRender";marker.dataset.mapResponsibility="navigation-orientation";marker.dataset.learningResponsibility="understanding-translation";document.body.append(marker);new MutationObserver(learningSurfaceSchedule).observe(document.getElementById("learning-graph"),{childList:true,subtree:true});new MutationObserver(learningSurfaceSchedule).observe(document.getElementById("learning-detail"),{childList:true,subtree:true});document.addEventListener("spec024-depth-expanded",learningSurfaceSchedule);document.addEventListener("spec024-depth-collapsed",learningSurfaceSchedule);learningSurfaceSchedule();document.dispatchEvent(new CustomEvent("spec030-learning-surface-ready"));}

learningSurfaceInstall();
window.__SPEC030_LEARNING__={resolve:learningSurfaceResolve,render:learningSurfaceRender,contract:()=>{const marker=document.getElementById("spec030-learning-contract");return marker?{...marker.dataset}:null;}};
