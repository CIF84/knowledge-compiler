"use strict";

let model;
let selectedId = null;
const byId = values => new Map(values.map(value => [value.id, value]));
const escapeHtml = value => String(value).replace(/[&<>'"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[char]));

async function start() {
  const manifest = await fetch("manifest.json").then(response => response.json());
  model = await fetch(manifest.representation).then(response => response.json());
  model.conceptById = byId(model.concepts);
  model.assertionById = byId(model.grounded_assertions);
  model.relationshipById = byId(model.canonical_relationships);
  model.propositionById = byId(model.structured_propositions);
  model.neighborhoodByEntity = new Map(model.neighborhoods.map(item => [item.anchor_entity_id, item]));
  document.getElementById("concept-search").addEventListener("input", renderBrowser);
  document.getElementById("overview-button").addEventListener("click", renderOverview);
  renderBrowser();
  renderOverview();
}

function renderBrowser() {
  const query = document.getElementById("concept-search").value.trim().toLowerCase();
  const items = model.concepts.filter(item => `${item.name} ${item.description} ${item.aliases.join(" ")}`.toLowerCase().includes(query));
  document.getElementById("browser-count").textContent = `${items.length} of ${model.concepts.length} source concepts`;
  document.getElementById("concept-list").innerHTML = items.map(item => `
    <button type="button" class="concept-button ${selectedId === item.id ? "selected" : ""}" data-concept="${escapeHtml(item.id)}">
      ${escapeHtml(item.name)}<small>${item.assertion_degree} explanation${item.assertion_degree === 1 ? "" : "s"}</small>
    </button>`).join("");
  document.querySelectorAll("[data-concept]").forEach(button => {
    button.addEventListener("click", () => renderFocus(button.dataset.concept));
    button.addEventListener("mouseenter", () => previewConcept(button.dataset.concept));
  });
}

function renderOverview() {
  selectedId = null;
  renderBrowser();
  document.getElementById("focus-view").hidden = true;
  document.getElementById("overview-grid").hidden = false;
  document.getElementById("view-heading").innerHTML = `<h2>Begin with six connected ideas</h2><p>This is a bounded orientation, not a ranking of scientific importance. Select one to unfold its source-backed neighborhood.</p>`;
  const assertionIds = model.overview.initial_assertion_ids;
  document.getElementById("overview-grid").innerHTML = model.overview.initial_entity_ids.map((entityId, index) => {
    const concept = model.conceptById.get(entityId);
    const assertion = model.assertionById.get(assertionIds[index]);
    return `<button class="neighborhood-card" type="button" data-overview="${escapeHtml(entityId)}">
      <span class="tier-tag">Concept neighborhood</span><h3>${escapeHtml(concept.name)}</h3>
      <p class="description">${escapeHtml(concept.description)}</p>
      <div class="signal-row"><span class="signal">${concept.assertion_degree} explanations</span><span class="signal">${concept.canonical_relationship_degree} established links</span></div>
      ${assertion ? `<p class="preview">${escapeHtml(assertion.statement)}</p>` : ""}
    </button>`;
  }).join("");
  document.querySelectorAll("[data-overview]").forEach(button => {
    button.addEventListener("click", () => renderFocus(button.dataset.overview));
    button.addEventListener("mouseenter", () => previewConcept(button.dataset.overview));
  });
  document.getElementById("detail-panel").innerHTML = `<p class="eyebrow">INSPECT</p><h2>Select an idea</h2><p>Click an idea to keep its neighborhood open. Hover for a quick preview.</p>`;
}

function renderFocus(entityId) {
  selectedId = entityId;
  renderBrowser();
  const concept = model.conceptById.get(entityId);
  const neighborhood = model.neighborhoodByEntity.get(entityId) || {assertion_ids: [], canonical_relationship_ids: [], proposition_ids: []};
  document.getElementById("overview-grid").hidden = true;
  const focus = document.getElementById("focus-view");
  focus.hidden = false;
  document.getElementById("view-heading").innerHTML = "";
  focus.innerHTML = `<div class="focus-hero"><p class="eyebrow">CONCEPT NEIGHBORHOOD</p><h2>${escapeHtml(concept.name)}</h2><p>${escapeHtml(concept.description)}</p></div>
    ${tierSection("Established relationships", "relationship", neighborhood.canonical_relationship_ids.map(id => model.relationshipById.get(id)))}
    ${tierSection("Structured conditions / events", "proposition", neighborhood.proposition_ids.map(id => model.propositionById.get(id)))}
    ${tierSection("Source-backed explanations", "assertion", neighborhood.assertion_ids.map(id => model.assertionById.get(id)))}
  `;
  focus.querySelectorAll("[data-item]").forEach(button => {
    button.addEventListener("click", () => inspect(button.dataset.kind, button.dataset.item));
    button.addEventListener("mouseenter", () => inspect(button.dataset.kind, button.dataset.item, true));
  });
  showConcept(concept);
}

function tierSection(title, kind, items) {
  const cards = items.length ? items.map(item => itemCard(kind, item)).join("") : `<p class="empty-tier">No ${title.toLowerCase()} are admitted for this concept.</p>`;
  return `<section class="tier-section"><h3>${escapeHtml(title)}</h3>${cards}</section>`;
}

function itemCard(kind, item) {
  const symbols = kind === "assertion" ? item.participant_entity_ids.map(id => model.conceptById.get(id)?.name || id)
    : kind === "relationship" ? [model.conceptById.get(item.source_entity_id).name, item.relationship_type, model.conceptById.get(item.target_entity_id).name]
    : item.role_bindings.map(binding => `${binding.role}: ${model.conceptById.get(binding.entity_id).name}`);
  return `<button type="button" class="item-card ${kind}" data-kind="${kind}" data-item="${escapeHtml(item.id)}">
    <span class="tier-tag">${escapeHtml(item.tier_label)}</span>${escapeHtml(item.statement)}
    <span class="participant-row">${symbols.map(label => `<span class="participant">${escapeHtml(label)}</span>`).join("")}</span>
  </button>`;
}

function previewConcept(entityId) {
  if (selectedId) return;
  const concept = model.conceptById.get(entityId);
  document.getElementById("detail-panel").innerHTML = `<p class="eyebrow">PREVIEW</p><h2>${escapeHtml(concept.name)}</h2><p>${escapeHtml(concept.description)}</p><p class="detail-meta">${concept.assertion_degree} source-backed explanations · ${concept.canonical_relationship_degree} established relationships</p>`;
}

function showConcept(concept) {
  document.getElementById("detail-panel").innerHTML = `<p class="eyebrow">SELECTED CONCEPT</p><h2>${escapeHtml(concept.name)}</h2><p>${escapeHtml(concept.description)}</p><p class="detail-meta">Its neighborhood groups existing source material for presentation only. Grouping does not create a semantic relationship.</p>`;
}

function inspect(kind, id, hoverOnly = false) {
  const item = kind === "assertion" ? model.assertionById.get(id) : kind === "relationship" ? model.relationshipById.get(id) : model.propositionById.get(id);
  const evidence = item.evidence.map(span => `<blockquote>${escapeHtml(span.quote)}</blockquote><p class="detail-meta">Source characters ${span.start_char}–${span.end_char} · ${escapeHtml(span.document_id)}</p>`).join("");
  document.getElementById("detail-panel").innerHTML = `<p class="eyebrow">${hoverOnly ? "PREVIEW" : "SELECTED"}</p><h2>${escapeHtml(item.tier_label)}</h2><p>${escapeHtml(item.statement)}</p><h3>Source evidence</h3>${evidence}<p class="detail-meta">${kind === "assertion" ? "Participant chips are presentation attachments, not inferred pairwise edges." : "This item is preserved from the accepted semantic model."}</p>`;
}

start().catch(error => {
  document.body.innerHTML = `<main class="map-panel"><h1>Viewer could not load</h1><pre>${escapeHtml(error.message)}</pre></main>`;
});
