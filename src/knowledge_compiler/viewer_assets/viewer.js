"use strict";

const state = { model: null, representation: null };
const svgNS = "http://www.w3.org/2000/svg";
const byId = id => document.getElementById(id);

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function warningsInto(target, warnings) {
  target.replaceChildren(...warnings.map(text => element("div", text, "warning")));
}

function svgElement(tag, attributes = {}) {
  const node = document.createElementNS(svgNS, tag);
  Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
  return node;
}

function positionsFor(representation, width, height) {
  const nodes = representation.nodes;
  const positions = {};
  if (representation.representation_type === "FEEDBACK_CANDIDATE") {
    const radius = Math.min(width, height) * 0.3;
    nodes.forEach((node, index) => {
      const angle = -Math.PI / 2 + index * 2 * Math.PI / nodes.length;
      positions[node.entity_id] = [width / 2 + radius * Math.cos(angle), height / 2 + radius * Math.sin(angle)];
    });
    return positions;
  }
  const levels = Object.fromEntries(nodes.map(node => [node.entity_id, 0]));
  for (let pass = 0; pass < nodes.length; pass += 1) {
    representation.edges.forEach(edge => {
      levels[edge.target_entity_id] = Math.max(levels[edge.target_entity_id], levels[edge.source_entity_id] + 1);
    });
  }
  const groups = {};
  nodes.forEach(node => (groups[levels[node.entity_id]] ||= []).push(node.entity_id));
  const levelKeys = Object.keys(groups).map(Number).sort((a,b) => a-b);
  levelKeys.forEach((level, levelIndex) => {
    groups[level].sort().forEach((id, rowIndex, rows) => {
      positions[id] = [90 + levelIndex * ((width - 180) / Math.max(1, levelKeys.length - 1)), 70 + rowIndex * ((height - 140) / Math.max(1, rows.length - 1))];
    });
  });
  return positions;
}

function showNode(node) {
  const detail = byId("detail");
  detail.replaceChildren(element("span", "Concept", "eyebrow"), element("h2", node.label));
  const dl = element("dl", undefined, "detail-grid");
  [["Type", node.entity_type], ["Entity ID", node.entity_id]].forEach(([term, value]) => {
    dl.append(element("dt", term), element("dd", value));
  });
  detail.append(dl, element("p", node.description || "No description was provided."));
}

function showEdge(edge) {
  const model = state.model;
  const labels = Object.fromEntries(state.representation.nodes.map(node => [node.entity_id, node.label]));
  const detail = byId("detail");
  detail.replaceChildren(element("span", "Relationship", "eyebrow"), element("h2", `${labels[edge.source_entity_id]} → ${labels[edge.target_entity_id]}`));
  const dl = element("dl", undefined, "detail-grid");
  [["Predicate", edge.relationship_type], ["Direction", edge.direction], ["Relationship IDs", edge.relationship_ids.join(", ")], ["Provenance", edge.provenance_status]].forEach(([term, value]) => {
    dl.append(element("dt", term), element("dd", value));
  });
  detail.append(dl, element("p", edge.meaning));
  if (edge.evidence.length) {
    detail.append(element("h3", "Source evidence"));
    edge.evidence.forEach(item => detail.append(element("blockquote", `“${item.quote}”`), element("small", `${item.relationship_id} · characters ${item.start_char}–${item.end_char}`)));
  } else {
    detail.append(element("p", "This relationship is inferred and has no source evidence.", "warning"));
  }
}

function renderGraph(representation) {
  const svg = byId("graph");
  svg.replaceChildren();
  const edgeList = byId("edge-list");
  edgeList.replaceChildren();
  const width = 900, height = Math.max(400, representation.nodes.length * 62);
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  const defs = svgElement("defs");
  const marker = svgElement("marker", { id:"arrow", viewBox:"0 0 10 10", refX:"9", refY:"5", markerWidth:"7", markerHeight:"7", orient:"auto-start-reverse" });
  marker.append(svgElement("path", { d:"M 0 0 L 10 5 L 0 10 z", fill:"#697870" })); defs.append(marker); svg.append(defs);
  const positions = positionsFor(representation, width, height);
  const nodeLabels = Object.fromEntries(representation.nodes.map(node => [node.entity_id, node.label]));
  representation.edges.forEach(edge => {
    const [x1,y1] = positions[edge.source_entity_id], [x2,y2] = positions[edge.target_entity_id];
    const dx=x2-x1, dy=y2-y1, distance=Math.max(1,Math.hypot(dx,dy)), ux=dx/distance, uy=dy/distance;
    const sx=x1+ux*74, sy=y1+uy*26, tx=x2-ux*74, ty=y2-uy*26;
    const reciprocal = representation.edges.some(other => other.source_entity_id === edge.target_entity_id && other.target_entity_id === edge.source_entity_id);
    const bend = reciprocal ? 92 : 0, cx=(sx+tx)/2-uy*bend, cy=(sy+ty)/2+ux*bend;
    const pathData = `M ${sx} ${sy} Q ${cx} ${cy} ${tx} ${ty}`;
    const line = svgElement("path", { d:pathData, class:"edge-line" });
    const hit = svgElement("path", { d:pathData, class:"edge-hit", tabindex:"0", role:"button", "aria-label":`${nodeLabels[edge.source_entity_id]} ${edge.relationship_label} ${nodeLabels[edge.target_entity_id]}` });
    hit.addEventListener("click", () => showEdge(edge)); hit.addEventListener("keydown", event => { if (event.key === "Enter") showEdge(edge); });
    const label = svgElement("text", { x:(sx+2*cx+tx)/4, y:(sy+2*cy+ty)/4-7, "text-anchor":"middle", class:"edge-label" }); label.textContent=edge.relationship_label;
    svg.append(line, hit, label);
    const edgeButton = element("button", `${nodeLabels[edge.source_entity_id]} — ${edge.relationship_label} → ${nodeLabels[edge.target_entity_id]}`);
    edgeButton.addEventListener("click", () => showEdge(edge)); edgeList.append(edgeButton);
  });
  representation.nodes.forEach(node => {
    const [x,y] = positions[node.entity_id];
    const group = svgElement("g", { class:"node", tabindex:"0", role:"button", "aria-label":node.label });
    group.append(svgElement("rect", { x:x-72, y:y-25, width:"144", height:"50", rx:"7" }));
    const label = svgElement("text", { x, y:y+4, "text-anchor":"middle" }); label.textContent = node.label.length > 22 ? `${node.label.slice(0,20)}…` : node.label;
    group.append(label); group.addEventListener("click", () => showNode(node)); group.addEventListener("keydown", event => { if (event.key === "Enter") showNode(node); }); svg.append(group);
  });
}

function selectRepresentation(representation, button) {
  state.representation = representation;
  document.querySelectorAll("#representations button").forEach(item => item.classList.toggle("active", item === button));
  byId("structure-title").textContent = representation.title;
  byId("salience").textContent = representation.salience;
  byId("structure-meta").textContent = `${representation.nodes.length} concepts · ${representation.edges.length} relationships`;
  warningsInto(byId("structure-warnings"), representation.warnings);
  byId("empty-state").hidden = true; byId("graph").hidden = false;
  byId("graph").style.display = "block"; byId("edge-list").style.display = "flex";
  renderGraph(representation);
  byId("detail").replaceChildren(element("span", "Detail", "eyebrow"), element("h2", "Select a node or edge"), element("p", "Inspect concept context or relationship meaning and source evidence."));
}

async function loadDomain(entry) {
  const model = await fetch(entry.representation).then(response => response.json()); state.model=model;
  byId("model-title").textContent=model.title; warningsInto(byId("global-warnings"), model.warnings);
  const nav=byId("representations"); nav.replaceChildren();
  if (!model.representations.length) {
    state.representation=null; byId("structure-title").textContent="No detected representation"; byId("salience").textContent="EMPTY"; byId("structure-meta").textContent="0 structures";
    byId("structure-warnings").replaceChildren(); byId("graph").replaceChildren(); byId("graph").hidden=true; byId("graph").style.display="none"; byId("edge-list").replaceChildren(); byId("edge-list").style.display="none"; const empty=byId("empty-state"); empty.hidden=false; empty.textContent=model.empty_state;
    byId("detail").replaceChildren(element("span", "Detail", "eyebrow"), element("h2", "No structure to inspect"), element("p", "This domain has no supported higher-order representation."));
    return;
  }
  model.representations.forEach((representation,index) => {
    const button=element("button", `${representation.title} · ${representation.salience}`); button.addEventListener("click",()=>selectRepresentation(representation,button)); nav.append(button); if(index===0) selectRepresentation(representation,button);
  });
}

fetch("manifest.json").then(response => response.json()).then(manifest => {
  const select=byId("domain"); manifest.domains.forEach((entry,index) => { const option=element("option",entry.label); option.value=String(index); select.append(option); });
  select.addEventListener("change",()=>loadDomain(manifest.domains[Number(select.value)])); loadDomain(manifest.domains[0]);
}).catch(error => { byId("model-title").textContent="Viewer data could not be loaded"; byId("empty-state").hidden=false; byId("empty-state").textContent=String(error); });
