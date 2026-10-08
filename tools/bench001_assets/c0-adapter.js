// Pure compatible renderer host. Native frozen renderer functions loaded first.
// No product navigation fixture, fabricated explanation, or renderer rescue.
function renderCurrent(payload) {
  const host = document.getElementById('current');
  const select = document.createElement('select');
  payload.plans.forEach((row, i) => {
    const option = document.createElement('option');
    option.value = String(i); option.textContent = row.plan.title;
    select.append(option);
  });
  const body = document.createElement('section');
  function show() {
    const row = payload.plans[Number(select.value)];
    const plan = row.plan;
    const native = strategyRenderPlan(plan, {activeContext:{domainId:'source',representationIndex:0}});
    // Metadata chrome only; no semantic body/strategy choice is changed.
    native.querySelectorAll('.strategy-badge,.learning-surface-marker').forEach(n => n.remove());
    native.querySelectorAll('.strategy-evidence p').forEach(n => n.remove());
    if (row.layout) {
      const existing = native.querySelector('.strategy-causal,.strategy-hierarchy,.strategy-sequence,.strategy-dependency,.strategy-reciprocal,.strategy-focused');
      if (!existing) throw new Error('Native structural renderer missing: no rescue');
      existing.replaceWith(diagramCanvas(row.layout, plan));
    }
    body.replaceChildren(native);
  }
  select.addEventListener('change', show); host.append(select, body); show();
}
