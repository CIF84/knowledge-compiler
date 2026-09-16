"use strict";

const reviewState={packet:null,index:0,mode:"A",selected:null,territory:"SPEC-056 · fixed review territory",errors:[],warnings:[]};
const byId=id=>document.getElementById(id);
const el=(tag,className,text)=>{const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node;};
const current=()=>reviewState.packet.cases[reviewState.index];

function trustedButton(className,text,role){
  const button=el("button",`${className} trusted-fragment`,text);
  button.type="button";
  button.dataset.trustedFragment=text;
  button.dataset.fragmentRole=role;
  button.addEventListener("click",()=>selectFragment(text,role));
  button.addEventListener("mouseenter",()=>previewFragment(text,role));
  button.addEventListener("mouseleave",()=>{if(!reviewState.selected)showDefaultInspect();});
  return button;
}

function showEvidence(){
  const host=byId("evidence-list");host.replaceChildren();
  current().evidence_quotes.forEach(quote=>host.append(el("blockquote",null,quote)));
}

function showDefaultInspect(){
  byId("inspect-mode").textContent="PREVIEW";
  byId("inspect-title").textContent=reviewState.mode==="A"?"Prose-only control":"Representation detail";
  byId("inspect-body").textContent=reviewState.mode==="A"
    ?"A presents only the unchanged trusted claim."
    :current().strategy==="CONCISE_PROSE"
      ?"This control deliberately adds no visual structure."
      :"Select a meaningful visual element to inspect its exact trusted fragment.";
}

function previewFragment(text,role){
  if(reviewState.selected)return;
  byId("inspect-mode").textContent="PREVIEW";
  byId("inspect-title").textContent=role.replaceAll("_"," ");
  byId("inspect-body").textContent=text;
}

function selectFragment(text,role){
  reviewState.selected={text,role};
  byId("inspect-mode").textContent="SELECTED";
  byId("inspect-title").textContent=role.replaceAll("_"," ");
  byId("inspect-body").textContent=text;
}

function renderComparison(host,payload){
  const visual=el("div","comparison-visual");visual.dataset.strategyDom="COMPARISON";
  visual.append(trustedButton("comparison-side",payload.sides[0],"comparison_side_a"));
  visual.append(el("div","comparison-cue",payload.explicit_cue));
  visual.append(trustedButton("comparison-side",payload.sides[1],"comparison_side_b"));
  if(payload.quantity_excerpts.length){
    const row=el("div","quantity-row");
    payload.quantity_excerpts.forEach(value=>row.append(trustedButton("quantity-chip",value,"explicit_quantity")));
    visual.append(row);
  }
  host.append(visual);
}

function renderQuantity(host,payload){
  const visual=el("div","quantity-visual");visual.dataset.strategyDom="QUANTITATIVE_CALLOUT";
  payload.quantity_excerpts.forEach(value=>{
    const button=trustedButton("quantity-callout",value,"explicit_quantity");
    button.replaceChildren(el("strong",null,value),el("span",null,"trusted quantity"));
    visual.append(button);
  });
  host.append(visual);
}

function renderQualified(host,payload){
  const visual=el("div","qualified-visual");visual.dataset.strategyDom="QUALIFIED_STATEMENT";
  const qualifier=trustedButton("qualifier-block",payload.explicit_qualifier_or_condition,"explicit_qualifier_or_condition");
  qualifier.replaceChildren(el("span",null,"scope / condition"),el("strong",null,payload.explicit_qualifier_or_condition));
  visual.append(qualifier,el("div","qualification-link"));
  const anchor=el("div","meaning-anchor");anchor.append(el("strong",null,"Main meaning"),el("span",null,"Read with the trusted concise explanation below."));
  visual.append(anchor);host.append(visual);
}

function renderRepresentation(){
  const item=current(),host=byId("representation-host");host.replaceChildren();
  host.dataset.mode=reviewState.mode;host.dataset.caseIdentity=item.case_identity;host.dataset.strategy=item.strategy;
  byId("prose-panel").classList.toggle("prose-dominant",reviewState.mode==="A"||item.strategy==="CONCISE_PROSE");
  byId("mode-a").setAttribute("aria-pressed",String(reviewState.mode==="A"));
  byId("mode-b").setAttribute("aria-pressed",String(reviewState.mode==="B"));
  if(reviewState.mode==="A"){
    host.append(el("p","prose-control","Prose-only control · no additional structure"));
  }else if(item.strategy==="COMPARISON")renderComparison(host,item.structured_payload);
  else if(item.strategy==="QUANTITATIVE_CALLOUT")renderQuantity(host,item.structured_payload);
  else if(item.strategy==="QUALIFIED_STATEMENT")renderQualified(host,item.structured_payload);
  else {const note=el("p","prose-only-note","No richer structure is justified by the frozen plan. B remains the same concise prose as A.");note.dataset.strategyDom="CONCISE_PROSE";host.append(note);}
  byId("claim-prose").textContent=item.prose;
  byId("strategy-label").textContent=reviewState.mode==="A"?"A · CONCISE_PROSE CONTROL":`B · ${item.strategy}`;
  reviewState.selected=null;showDefaultInspect();showEvidence();
}

function renderCase(){
  const item=current();
  byId("case-counter").textContent=`CASE ${item.review_index} OF ${reviewState.packet.cases.length} · ${item.character.replaceAll("_"," ")}`;
  byId("case-title").textContent=item.claim_id;
  byId("case-source").textContent=`${item.source_id} · ${item.domain}`;
  byId("next-description").textContent=reviewState.index===reviewState.packet.cases.length-1?"Return to the first frozen review case.":`Next: ${reviewState.packet.cases[reviewState.index+1].claim_id}`;
  [...byId("case-map").querySelectorAll("button")].forEach((button,index)=>button.setAttribute("aria-current",String(index===reviewState.index)));
  renderRepresentation();
}

function installMap(){
  const host=byId("case-map");
  reviewState.packet.cases.forEach((item,index)=>{
    const entry=el("li"),button=el("button",null,item.strategy.replaceAll("_"," "));
    button.type="button";button.dataset.index=String(index+1).padStart(2,"0");button.dataset.caseIdentity=item.case_identity;
    button.addEventListener("click",()=>selectCase(index));entry.append(button);host.append(entry);
  });
}

function selectCase(index){reviewState.index=(index+reviewState.packet.cases.length)%reviewState.packet.cases.length;reviewState.mode="A";renderCase();}
function setMode(mode){if(!["A","B"].includes(mode))throw new Error(`Unknown mode ${mode}`);reviewState.mode=mode;renderRepresentation();}
function nextCase(){selectCase(reviewState.index+1);}
function previousCase(){selectCase(reviewState.index-1);}

function snapshot(){
  const host=byId("representation-host"),item=current();
  return {case_identity:item.case_identity,index:reviewState.index,mode:reviewState.mode,strategy:item.strategy,strategy_dom:host.querySelector("[data-strategy-dom]")?.dataset.strategyDom||null,trusted_fragments:[...host.querySelectorAll("[data-trusted-fragment]")].map(node=>node.dataset.trustedFragment),prose:byId("claim-prose").textContent,territory:reviewState.territory,selected:reviewState.selected?{...reviewState.selected}:null};
}

function machineGate(){
  const start={index:reviewState.index,mode:reviewState.mode},territory=reviewState.territory,rows=[];
  for(let index=0;index<reviewState.packet.cases.length;index++){
    selectCase(index);const item=current();const identity=item.case_identity;
    setMode("A");const a=snapshot();setMode("B");const b=snapshot();
    const allowed=new Set(item.display_fragments),fragmentsTrusted=b.trusted_fragments.every(value=>allowed.has(value));
    const expectedDom=item.strategy==="CONCISE_PROSE"?"CONCISE_PROSE":item.strategy;
    const local=hostLocalInteractionProbe();
    rows.push({case_identity:identity,a_prose_exact:a.prose===item.prose,b_prose_exact:b.prose===item.prose,a_has_no_richer_dom:a.strategy_dom===null,b_strategy_dom:b.strategy_dom===expectedDom,prose_control_has_no_fake_structure:item.strategy!=="CONCISE_PROSE"||b.strategy_dom==="CONCISE_PROSE"&&b.trusted_fragments.length===0,all_fragments_frozen:fragmentsTrusted,all_expected_fragments_visible:item.display_fragments.every(value=>byId("representation-host").textContent.includes(value)),local_interaction_preserves_case:local.case_identity===identity,local_interaction_preserves_territory:local.territory===territory});
  }
  selectCase(start.index);setMode(start.mode);
  const counts=reviewState.packet.cases.reduce((value,item)=>(value[item.strategy]=(value[item.strategy]||0)+1,value),{});
  return {case_count:reviewState.packet.cases.length,strategy_counts:counts,all_cases_pass:rows.every(row=>Object.entries(row).filter(([key])=>key!=="case_identity").every(([,value])=>value===true)),rows,territory_unchanged:reviewState.territory===territory,errors:[...reviewState.errors],warnings:[...reviewState.warnings]};
}

function hostLocalInteractionProbe(){
  const before=snapshot(),target=byId("representation-host").querySelector(".trusted-fragment");if(target)target.click();const after=snapshot();
  return {case_identity:after.case_identity,territory:after.territory,case_preserved:before.case_identity===after.case_identity,territory_preserved:before.territory===after.territory};
}

async function install(){
  try{
    const [packet,rubric]=await Promise.all([fetch("cases.json").then(response=>response.json()),fetch("owner-review-rubric.json").then(response=>response.json())]);
    reviewState.packet=packet;installMap();rubric.criteria.forEach(item=>byId("rubric-list").append(el("li",null,`${item.label} — ${item.question}`)));
    byId("previous-case").addEventListener("click",previousCase);byId("next-case").addEventListener("click",nextCase);byId("explore-next").addEventListener("click",nextCase);byId("mode-a").addEventListener("click",()=>setMode("A"));byId("mode-b").addEventListener("click",()=>setMode("B"));
    renderCase();
    window.__SPEC056_REVIEW__={snapshot,selectCase,setMode,nextCase,previousCase,machineGate,hostLocalInteractionProbe,state:reviewState};
    const contract=byId("spec056-contract"),gate=machineGate();
    contract.dataset.browserGate=JSON.stringify(gate);contract.dataset.browserReady="true";
    document.dispatchEvent(new CustomEvent("spec056-review-ready"));
  }catch(error){reviewState.errors.push(String(error));document.body.dataset.loadError=String(error);throw error;}
}

window.addEventListener("error",event=>reviewState.errors.push(event.message));
window.addEventListener("unhandledrejection",event=>reviewState.errors.push(String(event.reason)));
install();
