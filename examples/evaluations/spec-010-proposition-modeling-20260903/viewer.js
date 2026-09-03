"use strict";

const state = {
  model: null,
  representation: null,
  selectedNodeId: null,
  selectedEdgeKey: null,
  previewNodeId: null,
  previewEdgeKey: null,
};
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

function effectiveSelection() {
  if (state.previewEdgeKey) return { kind: "edge", id: state.previewEdgeKey, preview: true };
  if (state.previewNodeId) return { kind: "node", id: state.previewNodeId, preview: true };
  if (state.selectedEdgeKey) return { kind: "edge", id: state.selectedEdgeKey, preview: false };
  if (state.selectedNodeId) return { kind: "node", id: state.selectedNodeId, preview: false };
  return null;
}

function resetDetail() {
  byId("detail").replaceChildren(
    element("span", "Detail", "eyebrow"),
    element("h2", "Select a node or relationship"),
    element("p", "Inspect concept context or relationship meaning and source evidence."),
  );
}

function showNode(node, preview) {
  const detail = byId("detail");
  detail.replaceChildren(
    element("span", preview ? "Preview · Concept" : "Selected · Concept", "eyebrow interaction-status"),
    element("h2", node.label),
  );
  const dl = element("dl", undefined, "detail-grid");
  [["Type", node.entity_type], ["Entity ID", node.entity_id]].forEach(([term, value]) => {
    dl.append(element("dt", term), element("dd", value));
  });
  detail.append(dl, element("p", node.description || "No description was provided."));
}

function showEdge(edge, preview) {
  const labels = Object.fromEntries(state.representation.nodes.map(node => [node.entity_id, node.label]));
  const detail = byId("detail");
  detail.replaceChildren(
    element("span", preview ? "Preview · Relationship" : "Selected · Relationship", "eyebrow interaction-status"),
    element("h2", `${labels[edge.source_entity_id]} → ${labels[edge.target_entity_id]}`),
  );
  const dl = element("dl", undefined, "detail-grid");
  [["Predicate", edge.relationship_type], ["Direction", edge.direction], ["Relationship IDs", edge.relationship_ids.join(", ")], ["Provenance", edge.provenance_status]].forEach(([term, value]) => {
    dl.append(element("dt", term), element("dd", value));
  });
  detail.append(dl, element("p", edge.meaning));
  if (edge.evidence.length) {
    detail.append(element("h3", "Source evidence"));
    edge.evidence.forEach(item => detail.append(
      element("blockquote", `“${item.quote}”`),
      element("small", `${item.relationship_id} · characters ${item.start_char}–${item.end_char}`),
    ));
  } else {
    detail.append(element("p", "This relationship is inferred and has no source evidence.", "warning"));
  }
}

function updateInteraction() {
  const effective = effectiveSelection();
  document.querySelectorAll("[data-node-id]").forEach(node => {
    const matches = effective?.kind === "node" && node.dataset.nodeId === effective.id;
    node.classList.toggle("is-selected", matches && !effective.preview);
    node.classList.toggle("is-preview", matches && effective.preview);
    node.classList.toggle("is-unrelated", Boolean(effective) && !matches);
    if (node.getAttribute("role") === "button") node.setAttribute("aria-pressed", String(matches));
  });
  document.querySelectorAll("[data-edge-key]").forEach(node => {
    const matches = effective?.kind === "edge" && node.dataset.edgeKey === effective.id;
    node.classList.toggle("is-selected", matches && !effective.preview);
    node.classList.toggle("is-preview", matches && effective.preview);
    node.classList.toggle("is-unrelated", Boolean(effective) && !matches);
    if (node.getAttribute("role") === "button" || node.tagName === "BUTTON") {
      node.setAttribute("aria-pressed", String(matches));
    }
  });
  byId("clear-selection").disabled = !(state.selectedNodeId || state.selectedEdgeKey);
  if (!effective || !state.representation) {
    resetDetail();
    return;
  }
  if (effective.kind === "node") {
    showNode(state.representation.nodes.find(node => node.entity_id === effective.id), effective.preview);
  } else {
    showEdge(state.representation.edges.find(edge => edge.edge_key === effective.id), effective.preview);
  }
}

function clearSelection() {
  state.selectedNodeId = null;
  state.selectedEdgeKey = null;
  state.previewNodeId = null;
  state.previewEdgeKey = null;
  updateInteraction();
}

function selectNode(nodeId) {
  state.selectedNodeId = nodeId;
  state.selectedEdgeKey = null;
  state.previewNodeId = null;
  state.previewEdgeKey = null;
  updateInteraction();
}

function selectEdge(edgeKey) {
  state.selectedEdgeKey = edgeKey;
  state.selectedNodeId = null;
  state.previewNodeId = null;
  state.previewEdgeKey = null;
  updateInteraction();
}

function previewNode(nodeId) {
  state.previewNodeId = nodeId;
  state.previewEdgeKey = null;
  updateInteraction();
}

function previewEdge(edgeKey) {
  state.previewEdgeKey = edgeKey;
  state.previewNodeId = null;
  updateInteraction();
}

function clearPreview() {
  state.previewNodeId = null;
  state.previewEdgeKey = null;
  updateInteraction();
}

function keyboardSelect(event, callback) {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    callback();
  }
}

function pathData(route) {
  const points = route.points;
  if (route.path_kind === "LINE") return `M ${points[0].x} ${points[0].y} L ${points[1].x} ${points[1].y}`;
  if (route.path_kind === "QUADRATIC") return `M ${points[0].x} ${points[0].y} Q ${points[1].x} ${points[1].y} ${points[2].x} ${points[2].y}`;
  return `M ${points[0].x} ${points[0].y} C ${points[1].x} ${points[1].y} ${points[2].x} ${points[2].y} ${points[3].x} ${points[3].y}`;
}

function appendArrowMarker(defs, id, color) {
  const marker = svgElement("marker", { id, viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" });
  marker.append(svgElement("path", { d: "M 0 0 L 10 5 L 0 10 z", fill: color }));
  defs.append(marker);
}

function renderGraph(representation) {
  const svg = byId("graph");
  svg.replaceChildren();
  const edgeList = byId("edge-list");
  edgeList.replaceChildren();
  const layout = representation.layout;
  svg.setAttribute("viewBox", `0 0 ${layout.width} ${layout.height}`);
  svg.dataset.layoutStrategy = layout.strategy;
  const defs = svgElement("defs");
  appendArrowMarker(defs, "arrow", "#697870");
  appendArrowMarker(defs, "arrow-selected", "#176b50");
  appendArrowMarker(defs, "arrow-preview", "#9a5f10");
  svg.append(defs);

  const positions = Object.fromEntries(layout.nodes.map(node => [node.entity_id, node]));
  const routes = Object.fromEntries(layout.edges.map(route => [route.edge_key, route]));
  const nodeLabels = Object.fromEntries(representation.nodes.map(node => [node.entity_id, node.label]));

  representation.edges.forEach(edge => {
    const route = routes[edge.edge_key];
    const data = { "data-edge-key": edge.edge_key };
    const line = svgElement("path", { d: pathData(route), class: "edge-line", ...data });
    const hit = svgElement("path", {
      d: pathData(route), class: "edge-hit", tabindex: "0", role: "button", "aria-pressed": "false",
      "aria-label": `${nodeLabels[edge.source_entity_id]} ${edge.relationship_label} ${nodeLabels[edge.target_entity_id]}`,
      ...data,
    });
    hit.addEventListener("click", () => selectEdge(edge.edge_key));
    hit.addEventListener("keydown", event => keyboardSelect(event, () => selectEdge(edge.edge_key)));
    hit.addEventListener("mouseenter", () => previewEdge(edge.edge_key));
    hit.addEventListener("mouseleave", clearPreview);
    const label = svgElement("text", {
      x: route.label_x, y: route.label_y, "text-anchor": "middle", class: "edge-label", ...data,
    });
    label.textContent = edge.relationship_label;
    svg.append(line, hit, label);

    const edgeButton = element("button", `${nodeLabels[edge.source_entity_id]} — ${edge.relationship_label} → ${nodeLabels[edge.target_entity_id]}`);
    edgeButton.dataset.edgeKey = edge.edge_key;
    edgeButton.setAttribute("aria-pressed", "false");
    edgeButton.addEventListener("click", () => selectEdge(edge.edge_key));
    edgeButton.addEventListener("mouseenter", () => previewEdge(edge.edge_key));
    edgeButton.addEventListener("mouseleave", clearPreview);
    edgeList.append(edgeButton);
  });

  representation.nodes.forEach(node => {
    const position = positions[node.entity_id];
    const group = svgElement("g", {
      class: "node", tabindex: "0", role: "button", "aria-pressed": "false", "aria-label": node.label,
      "data-node-id": node.entity_id,
    });
    group.append(svgElement("rect", { x: position.x - 84, y: position.y - 30, width: "168", height: "60", rx: "8" }));
    const label = svgElement("text", { x: position.x, y: position.y + 4, "text-anchor": "middle" });
    label.textContent = node.label.length > 24 ? `${node.label.slice(0, 22)}…` : node.label;
    group.append(label);
    group.addEventListener("click", () => selectNode(node.entity_id));
    group.addEventListener("keydown", event => keyboardSelect(event, () => selectNode(node.entity_id)));
    group.addEventListener("mouseenter", () => previewNode(node.entity_id));
    group.addEventListener("mouseleave", clearPreview);
    svg.append(group);
  });
  svg.addEventListener("click", event => { if (event.target === svg) clearSelection(); });
  updateInteraction();
}

function selectRepresentation(representation, button) {
  state.representation = representation;
  state.selectedNodeId = null;
  state.selectedEdgeKey = null;
  state.previewNodeId = null;
  state.previewEdgeKey = null;
  document.querySelectorAll("#representations button").forEach(item => item.classList.toggle("active", item === button));
  byId("structure-title").textContent = representation.title;
  byId("salience").textContent = representation.salience;
  byId("structure-meta").textContent = `${representation.nodes.length} concepts · ${representation.edges.length} relationships · ${representation.layout.strategy.replaceAll("_", " ")}`;
  warningsInto(byId("structure-warnings"), representation.warnings);
  byId("empty-state").hidden = true;
  byId("graph").hidden = false;
  byId("graph").style.display = "block";
  byId("edge-list").style.display = "flex";
  renderGraph(representation);
}

async function loadDomain(entry) {
  state.representation = null;
  state.selectedNodeId = null;
  state.selectedEdgeKey = null;
  state.previewNodeId = null;
  state.previewEdgeKey = null;
  const model = await fetch(entry.representation).then(response => response.json());
  state.model = model;
  byId("model-title").textContent = model.title;
  warningsInto(byId("global-warnings"), model.warnings);
  const nav = byId("representations");
  nav.replaceChildren();
  if (!model.representations.length) {
    byId("structure-title").textContent = "No detected representation";
    byId("salience").textContent = "EMPTY";
    byId("structure-meta").textContent = "0 structures";
    byId("structure-warnings").replaceChildren();
    byId("graph").replaceChildren();
    byId("graph").hidden = true;
    byId("graph").style.display = "none";
    byId("edge-list").replaceChildren();
    byId("edge-list").style.display = "none";
    const empty = byId("empty-state");
    empty.hidden = false;
    empty.textContent = model.empty_state;
    byId("clear-selection").disabled = true;
    byId("detail").replaceChildren(
      element("span", "Detail", "eyebrow"),
      element("h2", "No structure to inspect"),
      element("p", "This domain has no supported higher-order representation."),
    );
    return;
  }
  model.representations.forEach((representation, index) => {
    const button = element("button", `${representation.title} · ${representation.salience}`);
    button.addEventListener("click", () => selectRepresentation(representation, button));
    nav.append(button);
    if (index === 0) selectRepresentation(representation, button);
  });
}

byId("clear-selection").addEventListener("click", clearSelection);
fetch("manifest.json").then(response => response.json()).then(manifest => {
  const select = byId("domain");
  manifest.domains.forEach((entry, index) => {
    const option = element("option", entry.label);
    option.value = String(index);
    select.append(option);
  });
  select.addEventListener("change", () => loadDomain(manifest.domains[Number(select.value)]));
  loadDomain(manifest.domains[0]);
}).catch(error => {
  byId("model-title").textContent = "Viewer data could not be loaded";
  byId("empty-state").hidden = false;
  byId("empty-state").textContent = String(error);
});
