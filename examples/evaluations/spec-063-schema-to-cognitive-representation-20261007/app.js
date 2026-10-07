"use strict";

const state={packet:null,index:0,mode:"P0",selectedUnit:null,errors:[],warnings:[]};
const byId=id=>document.getElementById(id);
const el=(tag,className,text)=>{const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node;};
const current=()=>state.packet.cases[state.index];

function defaultTrace(){
  const item=current(),audit=item.provenance_recoverability_audit;
  byId("trace-title").textContent="Every learner unit remains inspectable";
  byId("trace-body").textContent=`${audit.learner_unit_count} learner units retain ${audit.evidence_excerpt_count} exact evidence excerpts. Select a P2 unit to inspect its support.`;
  byId("trace-list").replaceChildren();
}

function selectUnit(unit,index){
  state.selectedUnit=index;
  byId("trace-title").textContent=unit.label;
  byId("trace-body").textContent=unit.concise_prose;
  const host=byId("trace-list");host.replaceChildren();
  host.append(el("h3",null,"Grounded detail"));
  unit.detail_statements.forEach(statement=>host.append(el("p",null,statement)));
  host.append(el("h3",null,"Exact source evidence"));
  unit.evidence.forEach(row=>{host.append(el("blockquote",null,row.quote));host.append(el("p",null,row.source_title));});
}

function renderP0(host,item){
  const prose=el("p","baseline-prose",item.views.P0.text);prose.dataset.viewIdentity=item.views.P0.identity_sha256;host.append(prose);
}

function renderP1(host,item){
  const raw=el("pre","raw-schema-control",item.views.P1.text);raw.dataset.viewIdentity=item.views.P1.identity_sha256;host.append(raw);
}

function renderConnections(host,rows){
  if(!rows.length)return;
  const section=el("section","connections"),heading=el("h3",null,"Supported connections");section.append(heading);
  const primary=rows.filter(row=>row.primary),secondary=rows.filter(row=>!row.primary);
  const list=el("ul","connection-list");
  primary.forEach(row=>{const li=el("li");li.append(el("strong",null,`${row.from_label} → ${row.to_label}: `));li.append(document.createTextNode(row.statement));list.append(li);});
  section.append(list);
  if(secondary.length){const details=el("details","more-connections"),summary=el("summary",null,`Explore ${secondary.length} additional preserved connection${secondary.length===1?"":"s"}`),more=el("ul","connection-list");details.append(summary);secondary.forEach(row=>more.append(el("li",null,row.statement)));details.append(more);section.append(details);}
  host.append(section);
}

function renderP2(host,item){
  const view=item.views.P2.learner_representation,grammar=item.compilation_decision.selected_grammar;
  const root=el("article",`representation family-${grammar.toLowerCase().replaceAll("_","-")}`);root.dataset.grammar=grammar;
  root.append(el("p","orientation",view.orientation_prose));
  let unitIndex=0;
  view.groups.forEach(group=>{const section=el("section","concept-group");section.append(el("h3",null,group.heading));const grid=el("div","unit-grid");group.units.forEach(unit=>{const index=unitIndex++,button=el("button","learner-unit");button.type="button";button.dataset.unitIndex=String(index);button.append(el("strong",null,unit.label));button.append(el("span",null,unit.concise_prose));button.addEventListener("click",()=>selectUnit(unit,index));grid.append(button);});section.append(grid);root.append(section);});
  renderConnections(root,view.connections);
  host.append(root);
}

function renderAudit(host,item){
  const c=item.cognitive_utility_audit,s=item.semantic_schema_preservation_audit,i=item.implication_preservation_audit,p=item.provenance_recoverability_audit;
  const cards=[
    ["GRAMMAR",item.compilation_decision.selected_grammar.replaceAll("_"," ")],
    ["SEMANTICS",`${s.p2_recoverable_semantic_item_count}/${s.frozen_semantic_item_count} recoverable · ${s.schema_mutations} schema mutations`],
    ["IMPLICATIONS",`${i.p2_recoverable_implication_count}/${i.frozen_material_implication_count} recoverable · ${i.lost_count} lost`],
    ["PROVENANCE",`${p.learner_units_with_evidence}/${p.learner_unit_count} units evidenced · coverage ${p.coverage_ratio}`],
    ["COGNITIVE FORM",`${c.primary_learner_visible_conceptual_units} primary groups · ${c.nested_learner_units} nested units`],
    ["SAFETY",`${s.unsupported_inference_count} unsupported inferences · raw metadata hidden`]
  ];
  const grid=el("div","audit-grid");cards.forEach(([label,text])=>{const card=el("article","audit-card");card.append(el("strong",null,label));card.append(el("p",null,text));grid.append(card);});host.append(grid);
  const details=el("details","audit-trace"),summary=el("summary",null,"Inspect compiler trace (audit only)"),pre=el("pre",null,JSON.stringify(item.audit_trace,null,2));details.append(summary,pre);host.append(details);
}

function renderMetrics(item){
  const host=byId("metric-strip"),s=item.semantic_schema_preservation_audit,i=item.implication_preservation_audit,p=item.provenance_recoverability_audit;host.replaceChildren();
  [["FACTS",s.frozen_semantic_item_count,"all recoverable"],["IMPLICATIONS",i.frozen_material_implication_count,"all recoverable"],["GROUPS",item.cognitive_utility_audit.primary_learner_visible_conceptual_units,"schema-derived"],["EVIDENCE",p.evidence_excerpt_count,"exact excerpts"]].forEach(([label,value,note])=>{const card=el("div","metric");card.append(el("strong",null,String(value)));card.append(document.createTextNode(`${label} · ${note}`));host.append(card);});
}

function renderResolution(){
  const item=current(),host=byId("resolution-host");host.replaceChildren();host.dataset.caseIdentity=item.case_identity;host.dataset.mode=state.mode;
  ["P0","P1","P2","AUDIT"].forEach(mode=>byId(`mode-${mode.toLowerCase()}`).setAttribute("aria-pressed",String(state.mode===mode)));
  if(state.mode==="P0"){byId("resolution-label").textContent="P0 · FROZEN EXPLANATORY PROSE";renderP0(host,item);}
  else if(state.mode==="P1"){byId("resolution-label").textContent="P1 · FROZEN RAW SCHEMA CONTROL";renderP1(host,item);}
  else if(state.mode==="P2"){byId("resolution-label").textContent=`P2 · ${item.compilation_decision.selected_grammar.replaceAll("_"," ")}`;renderP2(host,item);}
  else{byId("resolution-label").textContent="PRESERVATION AND COMPILER AUDIT";renderAudit(host,item);}
  renderMetrics(item);state.selectedUnit=null;defaultTrace();
}

function renderCase(){
  const item=current();byId("case-counter").textContent=`CASE ${state.index+1} OF ${state.packet.cases.length}`;byId("case-title").textContent=item.source_identity.title;byId("case-domain").textContent=`${item.source_identity.domain} · ${item.source_identity.institutional_publisher}`;
  [...byId("case-list").querySelectorAll("button")].forEach((button,index)=>button.setAttribute("aria-current",String(index===state.index)));renderResolution();
}
function selectCase(index){state.index=(index+state.packet.cases.length)%state.packet.cases.length;state.mode="P0";renderCase();}
function setMode(mode){if(!["P0","P1","P2","AUDIT"].includes(mode))throw new Error(`Unknown mode ${mode}`);state.mode=mode;renderResolution();}
function installCases(){const host=byId("case-list");state.packet.cases.forEach((item,index)=>{const row=el("li"),button=el("button",null,item.source_identity.title);button.type="button";button.dataset.caseIdentity=item.case_identity;button.addEventListener("click",()=>selectCase(index));row.append(button);host.append(row);});}

function snapshot(){
  const item=current(),host=byId("resolution-host");return{case_identity:item.case_identity,host_case_identity:host.dataset.caseIdentity,mode:state.mode,text_length:host.textContent.trim().length,p0:host.querySelectorAll(".baseline-prose").length,p1:host.querySelectorAll(".raw-schema-control").length,p2:host.querySelectorAll(".representation").length,audit_cards:host.querySelectorAll(".audit-card").length,grammar:host.querySelector(".representation")?.dataset.grammar||null,unit_count:host.querySelectorAll(".learner-unit").length,selected_unit:state.selectedUnit};
}

function machineGate(){
  const start={index:state.index,mode:state.mode},rows=[],buttons=[...byId("case-list").querySelectorAll("button")];
  for(let index=0;index<state.packet.cases.length;index++){
    buttons[index].click();const item=current(),selectable=item.case_identity===buttons[index].dataset.caseIdentity;
    byId("mode-p0").click();const p0=snapshot();
    byId("mode-p1").click();const p1=snapshot();
    byId("mode-p2").click();const p2=snapshot(),first=byId("resolution-host").querySelector(".learner-unit");if(first)first.click();const selected=snapshot(),traceVisible=byId("trace-list").children.length>2;
    byId("mode-audit").click();const audit=snapshot();
    rows.push({case_identity:item.case_identity,case_button_selectable:selectable,p0_nonempty:p0.text_length>0&&p0.p0===1,p1_nonempty:p1.text_length>0&&p1.p1===1,p2_nonempty:p2.text_length>0&&p2.p2===1,audit_nonempty:audit.text_length>0&&audit.audit_cards===6,p1_p2_perceptually_distinct:p1.p1===1&&p1.p2===0&&p2.p1===0&&p2.p2===1,grammar_exact:p2.grammar===item.compilation_decision.selected_grammar,unit_count_exact:p2.unit_count===item.provenance_recoverability_audit.learner_unit_count,detail_selection_works:selected.selected_unit===0,detail_and_evidence_visible:traceVisible});
  }
  selectCase(start.index);setMode(start.mode);
  const threeCasesPresent=state.packet.cases.length===3&&buttons.length===3,allCasesSelectable=rows.length===3&&rows.every(row=>row.case_button_selectable);
  return{case_count:state.packet.cases.length,case_button_count:buttons.length,three_cases_present:threeCasesPresent,all_cases_selectable:allCasesSelectable,all_cases_pass:threeCasesPresent&&allCasesSelectable&&rows.every(row=>Object.entries(row).filter(([key])=>key!=="case_identity").every(([,value])=>value===true)),rows,errors:[...state.errors],warnings:[...state.warnings]};
}

function install(){
  try{
    const data=window.__SPEC063_REVIEW_DATA__;if(!data)throw new Error("SPEC-063 deterministic review packet is unavailable");if(data.packet.cases.length!==3)throw new Error(`SPEC-063 requires three cases; received ${data.packet.cases.length}`);
    state.packet=data.packet;installCases();data.rubric.criteria.forEach(item=>byId("rubric-list").append(el("li",null,`${item.label} — ${item.question}`)));
    byId("previous-case").addEventListener("click",()=>selectCase(state.index-1));byId("next-case").addEventListener("click",()=>selectCase(state.index+1));["P0","P1","P2","AUDIT"].forEach(mode=>byId(`mode-${mode.toLowerCase()}`).addEventListener("click",()=>setMode(mode)));
    renderCase();window.__SPEC063_REVIEW__={snapshot,selectCase,setMode,machineGate,state};const gate=machineGate(),contract=byId("spec063-contract");contract.dataset.packetSource="DETERMINISTIC_EMBEDDED_PACKET";contract.dataset.browserGate=JSON.stringify(gate);contract.dataset.browserReady="true";document.dispatchEvent(new CustomEvent("spec063-review-ready"));
  }catch(error){state.errors.push(String(error));document.body.dataset.loadError=String(error);byId("case-title").textContent="Review artifact failed to load";byId("resolution-host").textContent=String(error);throw error;}
}
window.addEventListener("error",event=>state.errors.push(event.message));window.addEventListener("unhandledrejection",event=>state.errors.push(String(event.reason)));install();
