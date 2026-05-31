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

function renderDatasets() {
  const datasets = document.querySelector("#dataset-table");
  datasets.innerHTML = (state.architecture.datasets || [])
    .map(
      (dataset) => `
        <tr>
          <td>
            <strong>${dataset.title}</strong>
            <small>${dataset.dataset_id}</small>
          </td>
          <td>${dataset.dataset_type}</td>
          <td>${dataset.classification}</td>
          <td>${dataset.access_mode}</td>
          <td>${dataset.dmp_id}</td>
          <td>
            <button type="button" data-action="zenodo-export" data-dataset-id="${dataset.dataset_id}">
              Draft
            </button>
          </td>
        </tr>
      `,
    )
    .join("");

  const zenodoPolicy = document.querySelector("#zenodo-export-policy");
  zenodoPolicy.innerHTML = (state.architecture.zenodo_export_policy || [])
    .map((control) => pill(control.id, control.status))
    .join("");

  const dmps = document.querySelector("#dmp-table");
  dmps.innerHTML = (state.architecture.data_management_plans || [])
    .map(
      (dmp) => `
        <tr>
          <td>
            <strong>${dmp.dmp_id}</strong>
            <small>${dmp.owner}</small>
          </td>
          <td>${dmp.project_id}</td>
          <td>${pill(dmp.status, dmp.status)}</td>
          <td>${dmp.access_policy}</td>
          <td>${dmp.retention_policy}</td>
        </tr>
      `,
    )
    .join("");

  const controls = document.querySelector("#dmp-control-list");
  controls.innerHTML = (state.architecture.dmp_controls || [])
    .map(
      (control) => `
        <article class="control">
          <h3>${control.id}</h3>
          <p>${control.control}</p>
          <div class="meta">
            ${pill(control.status, control.status)}
            ${pill(control.evidence)}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderIntermediation() {
  const flow = document.querySelector("#intermediation-flow");
  flow.innerHTML = state.architecture.intermediation_flow
    .map(
      (step) => `
        <article class="item">
          <h3>${step.step}. ${step.name}</h3>
          <p>${step.control}</p>
          <div class="meta">${pill(step.source)}</div>
        </article>
      `,
    )
    .join("");

  const profiles = document.querySelector("#consumer-profile-table");
  profiles.innerHTML = state.architecture.consumer_profiles
    .map(
      (profile) => `
        <tr>
          <td>
            <strong>${profile.name}</strong>
            <small>${profile.profile_id}</small>
          </td>
          <td>${profile.consumer_type}</td>
          <td>${profile.default_access.join(", ")}</td>
          <td>${profile.raw_access}</td>
        </tr>
      `,
    )
    .join("");
}

function renderDataAct() {
  const journey = document.querySelector("#data-act-journey");
  journey.innerHTML = (state.architecture.data_act_user_journey || [])
    .map(
      (step) => `
        <article class="item">
          <h3>${step.step}. ${step.name}</h3>
          <p>${step.control}</p>
          <div class="meta">${pill(step.evidence)}</div>
        </article>
      `,
    )
    .join("");

  const products = document.querySelector("#data-act-product-table");
  products.innerHTML = (state.architecture.data_act_connected_products || [])
    .map(
      (product) => `
        <tr>
          <td>
            <strong>${product.connected_product}</strong>
            <small>${product.product_id}</small>
          </td>
          <td>${product.generated_data.join(", ")}</td>
          <td>${product.default_access}</td>
          <td>${product.third_party_sharing}</td>
        </tr>
      `,
    )
    .join("");

  const channels = document.querySelector("#data-act-channel-table");
  channels.innerHTML = (state.architecture.data_act_access_channels || [])
    .map(
      (channel) => `
        <tr>
          <td>
            <strong>${channel.name}</strong>
            <small>${channel.channel_id}</small>
          </td>
          <td>${channel.consumer}</td>
          <td>${channel.delivery}</td>
          <td>${channel.evidence_topics.join(", ")}</td>
        </tr>
      `,
    )
    .join("");

  const obligations = document.querySelector("#data-act-obligation-list");
  obligations.innerHTML = (state.architecture.data_act_obligations || [])
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

function renderSecurityResilience() {
  const scope = document.querySelector("#security-scope-list");
  scope.innerHTML = [
    "NIS2: secteur, taille et transposition nationale a confirmer",
    "DORA: applicable si perimetre financier ou fournisseur ICT finance",
    "CRA: applicable aux produits avec elements numeriques mis sur le marche UE",
  ]
    .map((item) => pill(item))
    .join("");

  const gates = document.querySelector("#security-gate-list");
  gates.innerHTML = (state.architecture.security_resilience_gates || [])
    .map(
      (gate) => `
        <article class="item">
          <h3>${gate.gate}</h3>
          <p>${gate.control}</p>
          <div class="meta">
            ${pill(gate.status, gate.status)}
            ${pill(gate.evidence)}
          </div>
        </article>
      `,
    )
    .join("");

  const controls = document.querySelector("#security-control-table");
  controls.innerHTML = (state.architecture.security_resilience_controls || [])
    .map(
      (control) => `
        <tr>
          <td>
            <strong>${control.id}</strong>
            <small>${control.control}</small>
          </td>
          <td>${control.regulation}</td>
          <td>${control.domain}</td>
          <td>
            ${control.evidence_topic}
            <small>${pill(control.status, control.status)}</small>
          </td>
        </tr>
      `,
    )
    .join("");

  const topics = document.querySelector("#security-topic-table");
  topics.innerHTML = (state.architecture.topics || [])
    .filter(
      (topic) =>
        topic.name.startsWith("security.") ||
        topic.name.startsWith("resilience.") ||
        topic.name.startsWith("compliance.") ||
        topic.name.startsWith("cra."),
    )
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
  const readiness = document.querySelector("#compliance-readiness-table");
  readiness.innerHTML = (state.architecture.compliance_readiness || [])
    .map(
      (item) => `
        <tr>
          <td>
            <strong>${item.regulation}</strong>
            <small>${item.technical_status}</small>
          </td>
          <td>${pill(item.readiness, item.readiness)}</td>
          <td>${item.blocking_gap}</td>
          <td>${item.next_action}</td>
        </tr>
      `,
    )
    .join("");

  const scope = document.querySelector("#compliance-scope-table");
  scope.innerHTML = (state.architecture.compliance_scope_decisions || [])
    .map(
      (item) => `
        <tr>
          <td>
            <strong>${item.regulation}</strong>
            <small>${item.basis}</small>
          </td>
          <td>${pill(item.scope_status, item.scope_status)}</td>
          <td>${item.owner}</td>
          <td>${item.evidence_topic}</td>
        </tr>
      `,
    )
    .join("");

  const reporting = document.querySelector("#compliance-reporting-table");
  reporting.innerHTML = (state.architecture.compliance_reporting_channels || [])
    .map(
      (item) => `
        <tr>
          <td><strong>${item.regulation}</strong></td>
          <td>${item.trigger}</td>
          <td>${pill(item.channel_status, item.channel_status)}</td>
          <td>${item.evidence_topic}</td>
        </tr>
      `,
    )
    .join("");

  const additionalLegislation = document.querySelector("#additional-legislation-table");
  additionalLegislation.innerHTML = (state.architecture.additional_legislation || [])
    .map(
      (item) => `
        <tr>
          <td>
            <strong>${item.regulation}</strong>
            <small>${item.evidence_topic}</small>
          </td>
          <td>${pill(item.applicability, item.applicability)}</td>
          <td>${item.reason}</td>
          <td>${item.architecture_action}</td>
        </tr>
      `,
    )
    .join("");

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
  renderDatasets();
  renderIntermediation();
  renderDataAct();
  renderResearch();
  renderDga();
  renderSecurityResilience();
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

async function exportDatasetToZenodo(datasetId) {
  const result = document.querySelector("#zenodo-export-result");
  result.textContent = "Export Zenodo en cours...";
  const payload = await fetchJson("/api/datasets/zenodo/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId }),
  });
  result.textContent = `Draft Zenodo cree pour ${payload.dataset_id}: ${payload.record_url || "-"}`;
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
  if (event.target.matches('[data-action="zenodo-export"]')) {
    exportDatasetToZenodo(event.target.dataset.datasetId).catch((error) => {
      document.querySelector("#zenodo-export-result").textContent = error.message;
    });
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
