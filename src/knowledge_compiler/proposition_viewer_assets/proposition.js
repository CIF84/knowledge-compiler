"use strict";

const propositionElement = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};

function propositionExpression(card) {
  const roles = Object.fromEntries(card.roles.map(item => [item.role, item.label]));
  if (card.proposition_type === "COMPARISON_CONDITION") {
    return `${roles.LEFT_OPERAND} > ${roles.RIGHT_OPERAND} → CAUSES → ${roles.OUTCOME}`;
  }
  return `${roles.EVENT}: ${roles.OBJECT} → TRANSFERS TO → ${roles.DESTINATION}`;
}

function renderPropositionCards(model) {
  const target = document.getElementById("proposition-cards");
  target.replaceChildren();
  (model.proposition_cards || []).forEach(card => {
    const article = propositionElement("article", undefined, "proposition-card");
    article.append(
      propositionElement("span", card.proposition_type.replaceAll("_", " "), "eyebrow"),
      propositionElement("h3", card.statement),
      propositionElement("p", propositionExpression(card), "proposition-expression"),
    );
    const roles = propositionElement("dl", undefined, "proposition-roles");
    card.roles.forEach(binding => roles.append(
      propositionElement("dt", binding.role.replaceAll("_", " ")),
      propositionElement("dd", binding.label),
    ));
    article.append(roles, propositionElement(
      "p",
      card.comparison_operator
        ? `${card.comparison_operator.replaceAll("_", " ")} → ${card.relationship_type}`
        : card.relationship_type,
      "proposition-semantics",
    ));
    card.evidence.forEach(item => article.append(
      propositionElement("blockquote", `“${item.quote}”`),
      propositionElement("small", `${card.provenance_status} · characters ${item.start_char}–${item.end_char}`),
    ));
    target.append(article);
  });
}

fetch("manifest.json").then(response => response.json()).then(manifest => {
  const select = document.getElementById("domain");
  const load = index => fetch(manifest.domains[index].representation)
    .then(response => response.json()).then(renderPropositionCards);
  select.addEventListener("change", () => load(Number(select.value)));
  load(0);
});
