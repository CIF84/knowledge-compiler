"use strict";

const state = {
  model: null,
  representation: null,
  selectedNodeId: null,
  selectedEdgeKey: null,
  previewNodeId: null,
  previewEdgeKey: null,
  fixture: null,
  representationButtons: new Map(),
  navigation: {
    mode: "BASELINE",
    activeResolution: "PARENT",
    parentRepresentationId: null,
    focusEntityId: null,
    childRepresentationId: null,
    parentSelectionSnapshot: null,
    childSelection: null,
  },
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
    element("p", "Inspect concept context or relationship meaning and provenance."),
  );
}

function activeFixtureFor(nodeId) {
  if (state.navigation.activeResolution !== "PARENT" || !state.fixture) return null;
  if (state.navigation.mode === "BASELINE") return null;
  return state.fixture.parent_representation_id === state.representation?.id
    && state.fixture.focus_entity_id === nodeId ? state.fixture : null;
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
  const fixture = !preview ? activeFixtureFor(node.entity_id) : null;
  if (fixture) {
    const explore = element("button", `Explore ${node.label}`, "explore-action");
    explore.id = "explore-selection";
    explore.addEventListener("click", enterChildResolution);
    detail.append(
      element("p", "Increase semantic resolution while keeping selection distinct from navigation.", "explore-copy"),
      explore,
    );
  }
}

function showEdge(edge, preview) {
  const labels = Object.fromEntries(state.representation.nodes.map(node => [node.entity_id, node.label]));
  const childActive = state.navigation.activeResolution === "CHILD";
  const provenance = childActive ? state.fixture.provenance_kind : edge.provenance_status;
  const detail = byId("detail");
  detail.replaceChildren(
    element("span", preview ? "Preview · Relationship" : "Selected · Relationship", "eyebrow interaction-status"),
    element("h2", `${labels[edge.source_entity_id]} → ${labels[edge.target_entity_id]}`),
  );
  const dl = element("dl", undefined, "detail-grid");
  [["Predicate", edge.relationship_type], ["Direction", edge.direction], ["Relationship IDs", edge.relationship_ids.join(", ")], ["Provenance", provenance]].forEach(([term, value]) => {
    dl.append(element("dt", term), element("dd", value));
  });
  detail.append(dl, element("p", edge.meaning));
  if (edge.evidence.length) {
    detail.append(element("h3", "Source evidence"));
    edge.evidence.forEach(item => detail.append(
      element("blockquote", `“${item.quote}”`),
      element("small", `${item.relationship_id} · characters ${item.start_char}–${item.end_char}`),
    ));
  } else if (childActive) {
    detail.append(element("p", state.fixture.provenance_note, "fixture-note"));
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
  if (state.navigation.activeResolution === "CHILD") {
    state.navigation.childSelection = {
      selectedNodeId: state.selectedNodeId,
      selectedEdgeKey: state.selectedEdgeKey,
    };
  }
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
    const label = svgElement("text", { x: route.label_x, y: route.label_y, "text-anchor": "middle", class: "edge-label", ...data });
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
    const group = svgElement("g", { class: "node", tabindex: "0", role: "button", "aria-pressed": "false", "aria-label": node.label, "data-node-id": node.entity_id });
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

function renderParentContext() {
  const context = byId("parent-context");
  if (state.navigation.mode !== "CONTEXTUAL" || state.navigation.activeResolution !== "CHILD") {
    context.hidden = true;
    byId("context-graph").replaceChildren();
    return;
  }
  const parent = state.model.representations.find(item => item.id === state.navigation.parentRepresentationId);
  context.hidden = false;
  context.dataset.parentRepresentationId = parent.id;
  context.dataset.focusEntityId = state.navigation.focusEntityId;
  context.dataset.childRepresentationId = state.navigation.childRepresentationId;
  byId("context-title").textContent = `${state.model.title} · ${parent.title}`;
  byId("context-focus").textContent = `${state.fixture.focus_label} → deeper local model`;
  const svg = byId("context-graph");
  svg.replaceChildren();
  svg.setAttribute("viewBox", `0 0 ${parent.layout.width} ${parent.layout.height}`);
  parent.layout.edges.forEach(route => svg.append(svgElement("path", { d: pathData(route), class: "context-edge" })));
  const labels = Object.fromEntries(parent.nodes.map(node => [node.entity_id, node.label]));
  parent.layout.nodes.forEach(node => {
    const group = svgElement("g", { class: node.entity_id === state.navigation.focusEntityId ? "context-node context-focus" : "context-node", "data-context-node-id": node.entity_id });
    group.append(svgElement("rect", { x: node.x - 84, y: node.y - 30, width: "168", height: "60", rx: "8" }));
    const label = svgElement("text", { x: node.x, y: node.y + 4, "text-anchor": "middle" });
    label.textContent = labels[node.entity_id].length > 24 ? `${labels[node.entity_id].slice(0, 22)}…` : labels[node.entity_id];
    group.append(label);
    svg.append(group);
  });
}

function updateResolutionChrome() {
  const banner = byId("resolution-banner");
  banner.replaceChildren();
  if (state.navigation.activeResolution === "CHILD") {
    banner.className = "resolution-banner child-resolution";
    const copy = element("div");
    copy.append(
      element("span", "Deeper resolution · experimental fixture", "eyebrow"),
      element("strong", `Inside ${state.fixture.focus_label}`),
      element("span", ` · ${state.fixture.child_representation.title}`, "resolution-path"),
    );
    const back = element("button", `Back to ${state.model.title}`, "return-action");
    back.id = "return-to-parent";
    back.addEventListener("click", returnToParent);
    banner.append(copy, back);
  } else {
    banner.className = "resolution-banner parent-resolution";
    banner.append(
      element("span", "Parent resolution", "eyebrow"),
      element("span", state.navigation.mode === "BASELINE" ? "Select and inspect. Semantic depth remains closed in the control." : "Select an explorable concept, then use Explore."),
    );
  }
  renderParentContext();
}

function displayRepresentation(representation, { clear = true } = {}) {
  state.representation = representation;
  if (clear) {
    state.selectedNodeId = null;
    state.selectedEdgeKey = null;
  }
  state.previewNodeId = null;
  state.previewEdgeKey = null;
  byId("structure-title").textContent = representation.title;
  byId("salience").textContent = state.navigation.activeResolution === "CHILD" ? "DEEPER" : representation.salience;
  byId("structure-meta").textContent = `${representation.nodes.length} concepts · ${representation.edges.length} relationships · ${representation.layout.strategy.replaceAll("_", " ")}`;
  warningsInto(byId("structure-warnings"), representation.warnings);
  byId("empty-state").hidden = true;
  byId("graph").hidden = false;
  byId("graph").style.display = "block";
  byId("edge-list").style.display = "flex";
  renderGraph(representation);
  updateResolutionChrome();
}

function resetNavigation() {
  state.navigation.activeResolution = "PARENT";
  state.navigation.parentRepresentationId = null;
  state.navigation.focusEntityId = null;
  state.navigation.childRepresentationId = null;
  state.navigation.parentSelectionSnapshot = null;
  state.navigation.childSelection = null;
}

function selectRepresentation(representation, button) {
  resetNavigation();
  document.querySelectorAll("#representations button").forEach(item => item.classList.toggle("active", item === button));
  displayRepresentation(representation);
}

function enterChildResolution() {
  const fixture = activeFixtureFor(state.selectedNodeId);
  if (!fixture) return;
  state.navigation.parentRepresentationId = state.representation.id;
  state.navigation.focusEntityId = fixture.focus_entity_id;
  state.navigation.childRepresentationId = fixture.child_representation.id;
  state.navigation.parentSelectionSnapshot = {
    selectedNodeId: state.selectedNodeId,
    selectedEdgeKey: state.selectedEdgeKey,
  };
  state.navigation.childSelection = { selectedNodeId: null, selectedEdgeKey: null };
  state.navigation.activeResolution = "CHILD";
  displayRepresentation(fixture.child_representation);
}

function returnToParent() {
  const parent = state.model.representations.find(item => item.id === state.navigation.parentRepresentationId);
  const snapshot = state.navigation.parentSelectionSnapshot;
  resetNavigation();
  const button = state.representationButtons.get(parent.id);
  document.querySelectorAll("#representations button").forEach(item => item.classList.toggle("active", item === button));
  state.selectedNodeId = snapshot?.selectedNodeId || null;
  state.selectedEdgeKey = snapshot?.selectedEdgeKey || null;
  displayRepresentation(parent, { clear: false });
}

function selectMode(mode) {
  if (state.navigation.activeResolution === "CHILD") returnToParent();
  state.navigation.mode = mode;
  document.querySelectorAll("#modes button").forEach(button => {
    const active = button.dataset.mode === mode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  updateResolutionChrome();
  updateInteraction();
}

function renderModes(modes) {
  const labels = {
    BASELINE: "A · Baseline",
    REPLACEMENT: "B · Replacement drill-down",
    CONTEXTUAL: "C · Contextual expansion",
  };
  const container = byId("modes");
  container.replaceChildren();
  modes.forEach(mode => {
    const button = element("button", labels[mode]);
    button.dataset.mode = mode;
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => selectMode(mode));
    container.append(button);
  });
  selectMode("BASELINE");
}

async function loadDomain(entry) {
  resetNavigation();
  state.fixture = null;
  state.representationButtons = new Map();
  const requests = [fetch(entry.representation).then(response => response.json())];
  if (entry.exploration) requests.push(fetch(entry.exploration).then(response => response.json()));
  const [model, fixture] = await Promise.all(requests);
  state.model = model;
  state.fixture = fixture || null;
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
    resetDetail();
    updateResolutionChrome();
    return;
  }
  model.representations.forEach((representation, index) => {
    const button = element("button", `${representation.title} · ${representation.salience}`);
    button.addEventListener("click", () => selectRepresentation(representation, button));
    nav.append(button);
    state.representationButtons.set(representation.id, button);
    if (index === 0) selectRepresentation(representation, button);
  });
}

byId("clear-selection").addEventListener("click", clearSelection);
fetch("manifest.json").then(response => response.json()).then(manifest => {
  renderModes(manifest.modes);
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
