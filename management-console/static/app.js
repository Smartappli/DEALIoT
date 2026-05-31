const state = {
  architecture: null,
  healthById: new Map(),
  activePlane: "all",
};

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { Accept: "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`${url} returned ${response.status}`);
  }
  return response.json();
}

function text(value) {
  return value === null || value === undefined || value === "" ? "-" : String(value);
}

function pill(label, className = "") {
  return `<span class="pill ${className}">${text(label)}</span>`;
}

function renderMetrics() {
  const components = state.architecture?.components || [];
  const summary = [...state.healthById.values()].reduce((acc, item) => {
    acc[item.status] = (acc[item.status] || 0) + 1;
    return acc;
  }, {});

  document.querySelector("#metric-services").textContent = components.length;
  document.querySelector("#metric-healthy").textContent = summary.healthy || 0;
  document.querySelector("#metric-unreachable").textContent = summary.unreachable || 0;
  document.querySelector("#metric-topics").textContent = state.architecture?.topics.length || 0;
}

function renderPlaneFilter() {
  const select = document.querySelector("#plane-filter");
  const planes = [...new Set(state.architecture.components.map((item) => item.plane))].sort();
  select.innerHTML = [
    '<option value="all">Tous les plans</option>',
    ...planes.map((plane) => `<option value="${plane}">${plane}</option>`),
  ].join("");
  select.value = state.activePlane;
}

function renderComponents() {
  const container = document.querySelector("#component-grid");
  const components = state.architecture.components.filter(
    (item) => state.activePlane === "all" || item.plane === state.activePlane,
  );

  container.innerHTML = components
    .map((component) => {
      const health = state.healthById.get(component.id) || {
        status: "unknown",
        detail: "not checked",
      };
      const links = component.ui
        ? `<a class="link-button" href="${component.ui}" target="_blank" rel="noreferrer">Ouvrir</a>`
        : "";
      return `
        <article class="component">
          <h3>${component.name}</h3>
          <p>${component.role}</p>
          <div class="meta">
            ${pill(component.plane)}
            ${pill(health.status, health.status)}
            ${pill(`risk ${component.risk}`, component.risk)}
          </div>
          <small>${component.data_scope}</small>
          <footer>${links}</footer>
        </article>
      `;
    })
    .join("");
}

function renderTopics() {
  const table = document.querySelector("#topic-table");
  table.innerHTML = state.architecture.topics
    .map(
      (topic) => `
        <tr>
          <td><strong>${topic.name}</strong></td>
          <td>${topic.plane}</td>
          <td>${topic.classification}</td>
          <td>${topic.retention}</td>
        </tr>
      `,
    )
    .join("");
}

function renderResearch() {
  const context = state.architecture.research_context;
  const contextContainer = document.querySelector("#research-context");
  contextContainer.innerHTML = `
    <article class="item">
      <h3>${context.primary_purpose}</h3>
      <p>${context.dga_mode}</p>
      <div class="meta">
        ${context.general_interest_objectives.map((objective) => pill(objective)).join("")}
      </div>
    </article>
  `;

  const projects = document.querySelector("#research-project-list");
  projects.innerHTML = state.architecture.research_projects
    .map(
      (project) => `
        <article class="component">
          <h3>${project.title}</h3>
          <p>${project.objective}</p>
          <div class="meta">
            ${pill(project.permission_model)}
            ${pill(project.ethics_review_status, project.ethics_review_status)}
          </div>
          <small>${project.sharing_layer}</small>
        </article>
      `,
    )
    .join("");

  const controls = document.querySelector("#research-control-list");
  controls.innerHTML = state.architecture.research_controls
    .map(
      (control) => `
        <article class="control">
          <h3>${control.id}</h3>
          <p>${control.control}</p>
          <div class="meta">${pill(control.status, control.status)}</div>
        </article>
      `,
    )
    .join("");
}

function renderDga() {
  const principles = document.querySelector("#dga-principles");
  principles.innerHTML = state.architecture.dga_obligations
    ? state.architecture.dga_obligations
        .filter((item) => item.status === "implemented")
        .map((item) => pill(item.article, item.status))
        .join("")
    : "";

  const products = document.querySelector("#data-product-table");
  products.innerHTML = state.architecture.data_products
    .map(
      (product) => `
        <tr>
          <td>
            <strong>${product.title}</strong>
            <small>${product.product_id}</small>
          </td>
          <td>${product.data_category}</td>
          <td>${product.access_mode}</td>
          <td>${product.dga_gate}</td>
        </tr>
      `,
    )
    .join("");

  const obligations = document.querySelector("#dga-obligation-list");
  obligations.innerHTML = state.architecture.dga_obligations
    .map(
      (obligation) => `
        <article class="control">
          <h3>${obligation.article}</h3>
          <p>${obligation.control}</p>
          <div class="meta">${pill(obligation.status, obligation.status)}</div>
        </article>
      `,
    )
    .join("");
}

function renderOperations() {
  const container = document.querySelector("#operations-list");
  container.innerHTML = state.architecture.operations
    .map((operation) => {
      const action =
        operation.id === "refresh-health"
          ? '<button type="button" data-action="refresh">Executer</button>'
          : "";
      return `
        <article class="item">
          <h3>${operation.name}</h3>
          <p>${operation.description}</p>
          <div class="meta">
            ${pill(operation.method)}
            ${pill(operation.scope)}
          </div>
          <footer>${action}</footer>
        </article>
      `;
    })
    .join("");
}

function renderRunbooks() {
  const container = document.querySelector("#runbook-list");
  container.innerHTML = state.architecture.runbooks
    .map(
      (runbook) => `
        <article class="item">
          <h3>${runbook.name}</h3>
          <p>${runbook.scope}</p>
          <div class="meta">${pill(runbook.path)}</div>
        </article>
      `,
    )
    .join("");
}

function renderCompliance() {
  const container = document.querySelector("#compliance-list");
  container.innerHTML = state.architecture.compliance_controls
    .map(
      (control) => `
        <article class="control">
          <h3>${control.regulation}</h3>
          <p>${control.control}</p>
          <div class="meta">${pill(control.status, control.status)}</div>
        </article>
      `,
    )
    .join("");
}

function renderAll() {
  renderMetrics();
  renderPlaneFilter();
  renderComponents();
  renderTopics();
  renderResearch();
  renderDga();
  renderOperations();
  renderRunbooks();
  renderCompliance();
}

async function refreshHealth() {
  const health = await fetchJson("/api/health");
  state.healthById = new Map(health.checks.map((item) => [item.id, item]));
  renderMetrics();
  renderComponents();
}

async function init() {
  state.architecture = await fetchJson("/api/architecture");
  renderAll();
  await refreshHealth();
}

document.addEventListener("click", (event) => {
  if (event.target.matches("#refresh-health") || event.target.matches('[data-action="refresh"]')) {
    refreshHealth().catch((error) => console.error(error));
  }
});

document.addEventListener("change", (event) => {
  if (event.target.matches("#plane-filter")) {
    state.activePlane = event.target.value;
    renderComponents();
  }
});

init().catch((error) => {
  document.body.innerHTML = `<main class="fatal"><h1>Console indisponible</h1><p>${error.message}</p></main>`;
});
