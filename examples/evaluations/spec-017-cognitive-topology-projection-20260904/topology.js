"use strict";

let topology;
let conceptById;
let assertionById;
let relationshipById;
let neighborhoodById;
let selectedConceptId = null;
let selectedRelationshipId = null;
let visibleIds = new Set();
const svgNS = "http://www.w3.org/2000/svg";
const escapeHtml = value => String(value).replace(/[&<>'"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[char]));

async function start() {
  const manifest = await fetch("manifest.json").then(response => response.json());
  topology = await fetch(manifest.topology).then(response => response.json());
  conceptById = new Map(topology.concepts.map(item => [item.id, item]));
  assertionById = new Map(topology.grounded_assertions.map(item => [item.id, item]));
  relationshipById = new Map(topology.canonical_relationships.map(item => [item.id, item]));
  neighborhoodById = new Map(topology.neighborhoods.map(item => [item.focus_concept_id, item]));
  document.getElementById("reset").addEventListener("click", resetOverview);
  document.getElementById("search-toggle").addEventListener("click", toggleSearch);
  document.getElementById("search").addEventListener("input", renderSearch);
  resetOverview();
}

function svgElement(name, attributes = {}) {
  const element = document.createElementNS(svgNS, name);
  for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
  return element;
}

function resetOverview() {
  selectedConceptId = null;
  selectedRelationshipId = null;
  visibleIds = new Set(topology.initial_state.visible_concept_ids);
  document.getElementById("topology").setAttribute("viewBox", "0 0 1160 680");
  document.getElementById("inspector").hidden = true;
  document.getElementById("search-panel").hidden = true;
  document.getElementById("search-toggle").setAttribute("aria-expanded", "false");
  render();
}

function render() {
  renderFields();
  renderAffinityGuides();
  renderRelationships();
  renderNodes();
}

function renderFields() {
  const group = document.getElementById("fields");
  group.replaceChildren();
  [...visibleIds].map(id => conceptById.get(id)).sort((a, b) => b.presentation_salience - a.presentation_salience || a.id.localeCompare(b.id)).slice(0, 3).forEach(concept => {
    group.append(svgElement("circle", {class: "field-halo", cx: concept.position.x, cy: concept.position.y, r: 95 + Math.min(45, concept.assertion_degree * 7)}));
  });
}

function renderAffinityGuides() {
  const group = document.getElementById("affinity-guides");
  group.replaceChildren();
  if (!selectedConceptId) return;
  const neighborhood = neighborhoodById.get(selectedConceptId);
  if (!neighborhood) return;
  const source = conceptById.get(selectedConceptId).position;
  neighborhood.member_concept_ids.slice(1).forEach(id => {
    const target = conceptById.get(id).position;
    group.append(svgElement("line", {class: "affinity-guide", x1: source.x, y1: source.y, x2: target.x, y2: target.y, "aria-label": "presentation proximity; not a semantic relationship"}));
  });
}

function renderRelationships() {
  const group = document.getElementById("canonical-edges");
  group.replaceChildren();
  topology.canonical_relationships.filter(item => visibleIds.has(item.source_entity_id) && visibleIds.has(item.target_entity_id)).forEach(item => {
    const source = conceptById.get(item.source_entity_id).position;
    const target = conceptById.get(item.target_entity_id).position;
    group.append(svgElement("line", {class: "canonical-underlay", x1: source.x, y1: source.y, x2: target.x, y2: target.y}));
    const edge = svgElement("line", {class: `canonical-edge ${selectedRelationshipId === item.id ? "selected" : ""}`, x1: source.x, y1: source.y, x2: target.x, y2: target.y, tabindex: 0, role: "button", "aria-label": `${item.relationship_type}: ${item.statement}`});
    edge.addEventListener("click", event => { event.stopPropagation(); inspectRelationship(item.id); });
    edge.addEventListener("keydown", event => { if (event.key === "Enter" || event.key === " ") inspectRelationship(item.id); });
    group.append(edge);
    const label = svgElement("text", {class: "edge-label", x: (source.x + target.x) / 2, y: (source.y + target.y) / 2 - 7, "text-anchor": "middle"});
    label.textContent = item.relationship_type.replaceAll("_", " ");
    group.append(label);
  });
}

function renderNodes() {
  const group = document.getElementById("nodes");
  group.replaceChildren();
  const maxSalience = Math.max(...topology.concepts.map(item => item.presentation_salience));
  topology.concepts.filter(item => visibleIds.has(item.id)).forEach(concept => {
    const isFocal = topology.initial_state.visible_concept_ids.slice(0, 3).includes(concept.id);
    const node = svgElement("g", {class: `concept ${isFocal ? "focal" : ""} ${selectedConceptId === concept.id ? "selected" : ""}`, transform: `translate(${concept.position.x} ${concept.position.y})`, tabindex: 0, role: "button", "aria-label": concept.label});
    const radius = 7 + 8 * concept.presentation_salience / maxSalience;
    node.append(svgElement("circle", {class: "node-ring", r: radius + 8}));
    node.append(svgElement("circle", {class: "node-dot", r: radius}));
    const label = svgElement("foreignObject", {x: -75, y: radius + 10, width: 150, height: 42});
    const labelBody = document.createElement("div");
    labelBody.className = "concept-label";
    labelBody.textContent = concept.label;
    label.append(labelBody);
    node.append(label);
    node.addEventListener("click", () => focusConcept(concept.id, false));
    node.addEventListener("keydown", event => { if (event.key === "Enter" || event.key === " ") focusConcept(concept.id, false); });
    group.append(node);
  });
}

function focusConcept(id, recenter) {
  selectedConceptId = id;
  selectedRelationshipId = null;
  const neighborhood = neighborhoodById.get(id);
  visibleIds = new Set(topology.initial_state.visible_concept_ids);
  if (neighborhood) neighborhood.member_concept_ids.forEach(item => visibleIds.add(item));
  visibleIds.add(id);
  if (recenter) {
    const point = conceptById.get(id).position;
    document.getElementById("topology").setAttribute("viewBox", `${point.x - 420} ${point.y - 245} 840 490`);
  }
  document.getElementById("search-panel").hidden = true;
  document.getElementById("search-toggle").setAttribute("aria-expanded", "false");
  showConceptInspector(id);
  render();
}

function showConceptInspector(id) {
  const concept = conceptById.get(id);
  const assertionIds = topology.grounded_assertions.filter(item => item.participant_entity_ids.includes(id)).map(item => item.id);
  const inspector = document.getElementById("inspector");
  inspector.hidden = false;
  inspector.innerHTML = `<button class="close" type="button" aria-label="Close details">×</button><span class="level">LOCAL TOPOLOGY</span><h2>${escapeHtml(concept.label)}</h2><p>${escapeHtml(concept.description)}</p><p class="meta">${assertionIds.length} source-backed explanation${assertionIds.length === 1 ? "" : "s"} available</p>${assertionIds.length ? `<button id="explain" type="button">Explain</button>` : ""}`;
  inspector.querySelector(".close").addEventListener("click", closeInspector);
  inspector.querySelector("#explain")?.addEventListener("click", () => showExplanationChooser(id, assertionIds));
}

function showExplanationChooser(conceptId, assertionIds) {
  const inspector = document.getElementById("inspector");
  inspector.innerHTML = `<button class="close" type="button" aria-label="Close details">×</button><span class="level">EXPLANATION</span><h2>${escapeHtml(conceptById.get(conceptId).label)}</h2><div class="explanation-list">${assertionIds.map((id, index) => `<button type="button" data-assertion="${escapeHtml(id)}" aria-label="Open explanation ${index + 1}">${index + 1}</button>`).join("")}</div><div id="explanation-slot" class="explanation"><p>Choose one explanation.</p></div>`;
  inspector.querySelector(".close").addEventListener("click", closeInspector);
  inspector.querySelectorAll("[data-assertion]").forEach(button => button.addEventListener("click", () => showExplanation(button.dataset.assertion)));
  showExplanation(assertionIds[0]);
}

function showExplanation(id) {
  const assertion = assertionById.get(id);
  const slot = document.getElementById("explanation-slot");
  slot.innerHTML = `<p>${escapeHtml(assertion.statement)}</p><button type="button" id="evidence">Show source evidence</button>`;
  slot.querySelector("#evidence").addEventListener("click", () => showEvidence(assertion));
}

function showEvidence(item) {
  const slot = document.getElementById("explanation-slot") || document.getElementById("relationship-slot");
  slot.insertAdjacentHTML("beforeend", `<div class="evidence"><span class="level">SOURCE EVIDENCE</span>${item.evidence.map(span => `<blockquote>${escapeHtml(span.quote)}</blockquote><p class="meta">characters ${span.start_char}–${span.end_char}</p>`).join("")}</div>`);
  slot.querySelector("#evidence")?.remove();
}

function inspectRelationship(id) {
  selectedRelationshipId = id;
  const item = relationshipById.get(id);
  const source = conceptById.get(item.source_entity_id);
  const target = conceptById.get(item.target_entity_id);
  const inspector = document.getElementById("inspector");
  inspector.hidden = false;
  inspector.innerHTML = `<button class="close" type="button" aria-label="Close details">×</button><span class="level">ESTABLISHED RELATIONSHIP</span><h2>${escapeHtml(source.label)} → ${escapeHtml(target.label)}</h2><div id="relationship-slot" class="relationship-detail"><p><b>${escapeHtml(item.relationship_type.replaceAll("_", " "))}</b> — ${escapeHtml(item.predicate_meaning)}</p><p>${escapeHtml(item.statement)}</p><button type="button" id="evidence">Show source evidence</button></div>`;
  inspector.querySelector(".close").addEventListener("click", closeInspector);
  inspector.querySelector("#evidence").addEventListener("click", () => showEvidence(item));
  render();
}

function closeInspector() {
  selectedConceptId = null;
  selectedRelationshipId = null;
  document.getElementById("inspector").hidden = true;
  visibleIds = new Set(topology.initial_state.visible_concept_ids);
  document.getElementById("topology").setAttribute("viewBox", "0 0 1160 680");
  render();
}

function toggleSearch() {
  const panel = document.getElementById("search-panel");
  panel.hidden = !panel.hidden;
  document.getElementById("search-toggle").setAttribute("aria-expanded", String(!panel.hidden));
  if (!panel.hidden) { document.getElementById("search").focus(); renderSearch(); }
}

function renderSearch() {
  const query = document.getElementById("search").value.trim().toLocaleLowerCase();
  const results = query ? topology.concepts.filter(item => `${item.label} ${item.aliases.join(" ")}`.toLocaleLowerCase().includes(query)) : [];
  document.getElementById("search-results").innerHTML = results.map(item => `<button type="button" class="search-result" data-result="${escapeHtml(item.id)}">${escapeHtml(item.label)}</button>`).join("");
  document.querySelectorAll("[data-result]").forEach(button => button.addEventListener("click", () => focusConcept(button.dataset.result, true)));
}

start().catch(error => {
  document.getElementById("stage").innerHTML = `<section class="inspector"><h2>Viewer could not load</h2><p>${escapeHtml(error.message)}</p></section>`;
});
