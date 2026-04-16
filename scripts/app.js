const timelineConfig = [
  { key: "pr", title: "Purchase Requisition", code: "ME51N" },
  { key: "rfq", title: "Request for Quotation", code: "ME41" },
  { key: "quotation", title: "Vendor Quotation", code: "ME47" },
  { key: "po", title: "Purchase Order", code: "ME21N" },
  { key: "gr", title: "Goods Receipt", code: "MIGO" },
  { key: "invoice", title: "Invoice Verification", code: "MIRO" },
  { key: "payment", title: "Vendor Payment", code: "F-53" },
];

const state = {
  snapshot: null,
};

function readUiStateFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return {
    section: params.get("section") || "overview",
    txn: params.get("txn") || "pr",
  };
}

function currency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));
}

function formatDate(value) {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function setBanner(message, type = "neutral") {
  const el = document.getElementById("systemBanner");
  el.textContent = message;
  el.className = `system-banner ${type}`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    throw new Error(payload?.error || `Request failed with status ${response.status}`);
  }

  return payload;
}

function renderDataGrid(elementId, entries) {
  const container = document.getElementById(elementId);
  container.innerHTML = "";
  entries.forEach(([label, value]) => {
    const card = document.createElement("article");
    card.className = "data-card";
    card.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
    container.appendChild(card);
  });
}

function renderTimeline() {
  const processData = state.snapshot.processData;
  const container = document.getElementById("timeline");
  const template = document.getElementById("timelineItemTemplate");
  container.innerHTML = "";

  timelineConfig.forEach((step) => {
    const node = template.content.firstElementChild.cloneNode(true);
    const doc = processData[step.key];
    node.querySelector("h4").textContent = step.title;
    node.querySelector(".timeline-code").textContent = step.code;

    const statusEl = node.querySelector(".timeline-status");
    const metaEl = node.querySelector(".timeline-meta");
    if (doc) {
      statusEl.textContent = "Completed";
      statusEl.className = "timeline-status status-pill success";
      metaEl.textContent = `${doc.number} created on ${formatDate(doc.createdOn)}${doc.statusNote ? ` | ${doc.statusNote}` : ""}`;
    } else {
      statusEl.textContent = "Pending";
      statusEl.className = "timeline-status status-pill neutral";
      metaEl.textContent = "No document posted yet.";
    }
    container.appendChild(node);
  });
}

function renderDocuments() {
  const body = document.getElementById("documentsTable");
  body.innerHTML = "";
  const documents = state.snapshot.documents;

  if (!documents.length) {
    body.innerHTML = `<tr><td colspan="6">No documents generated yet.</td></tr>`;
    return;
  }

  documents.forEach((doc) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${doc.type.toUpperCase()}</td>
      <td>${doc.number}</td>
      <td>${doc.reference}</td>
      <td>${doc.status}</td>
      <td>${formatDate(doc.createdOn)}</td>
      <td>${currency(doc.value)}</td>
    `;
    body.appendChild(row);
  });
}

function renderPostings() {
  const body = document.getElementById("postingsTable");
  body.innerHTML = "";
  const postings = state.snapshot.postings;

  if (!postings.length) {
    body.innerHTML = `<tr><td colspan="5">No FI postings generated yet.</td></tr>`;
    return;
  }

  postings.forEach((entry) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${entry.fiDoc}<br /><span class="label">${entry.docNumber}</span></td>
      <td>40 / 50</td>
      <td>${entry.debit}</td>
      <td>${entry.credit}</td>
      <td>${currency(entry.amount)}</td>
    `;
    body.appendChild(row);
  });
}

function renderOverview() {
  const metrics = state.snapshot.metrics;
  const controls = state.snapshot.controls;
  document.getElementById("overviewPoQty").textContent = controls.quantities.po;
  document.getElementById("overviewGrQty").textContent = controls.quantities.gr;
  document.getElementById("overviewInvoiceQty").textContent = controls.quantities.invoice;
  document.getElementById("docCount").textContent = metrics.docCount;
  document.getElementById("inventoryValue").textContent = currency(metrics.inventoryValue);
  document.getElementById("vendorLiability").textContent = currency(metrics.vendorLiability);
  document.getElementById("paymentStatus").textContent = metrics.paymentStatus;

  const completed = timelineConfig.filter((step) => state.snapshot.processData[step.key]).length;
  const percent = Math.round((completed / timelineConfig.length) * 100);
  document.getElementById("completionBadge").textContent = `${percent}% complete`;

  const matchStatus = document.getElementById("overviewMatchStatus");
  matchStatus.textContent = controls.match.label;
  matchStatus.className = `status-pill ${controls.match.status}`;
}

function renderControls() {
  const controls = state.snapshot.controls;
  const controlContainer = document.getElementById("controlsCard");
  const alertContainer = document.getElementById("alertsPanel");
  const comparisonBody = document.getElementById("comparisonTable");

  controlContainer.innerHTML = "";
  alertContainer.innerHTML = "";
  comparisonBody.innerHTML = "";

  controls.controlRows.forEach((item) => {
    const row = document.createElement("article");
    row.className = "control-row";
    row.innerHTML = `<h4>${item.title}</h4><p>${item.description}</p><p class="label">${item.status}</p>`;
    controlContainer.appendChild(row);
  });

  controls.alerts.forEach((item) => {
    const card = document.createElement("article");
    card.className = "alert-card";
    card.innerHTML = `<h4>${item.title}</h4><p>${item.description}</p><p class="status-pill ${item.level}">${item.level.toUpperCase()}</p>`;
    alertContainer.appendChild(card);
  });

  if (!state.snapshot.comparisonRows.length) {
    comparisonBody.innerHTML = `<tr><td colspan="6">No quotation available yet for comparison.</td></tr>`;
    return;
  }

  state.snapshot.comparisonRows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.vendor}</td>
      <td>${currency(row.value)}</td>
      <td>${currency(row.freight)}</td>
      <td>${row.leadTime} days</td>
      <td>${row.rank}</td>
      <td>${row.decision}</td>
    `;
    comparisonBody.appendChild(tr);
  });
}

function applyLatestDocumentDefaults() {
  const data = state.snapshot.processData;
  const poNumber = data.po?.number || "";
  const invoiceOpenAmount = data.invoice ? Number(data.invoice.amount) + Number(data.invoice.tax) : 59000;

  const grPo = document.querySelector('#form-gr input[name="poNumber"]');
  const invoicePo = document.querySelector('#form-invoice input[name="poNumber"]');
  const paymentAmount = document.querySelector('#form-payment input[name="amount"]');

  grPo.placeholder = poNumber ? `Latest PO: ${poNumber}` : "Auto uses latest PO if left blank";
  invoicePo.placeholder = poNumber ? `Latest PO: ${poNumber}` : "Auto uses latest PO if left blank";
  paymentAmount.value = invoiceOpenAmount;
}

function renderAll() {
  renderDataGrid("orgData", state.snapshot.masterData.organization);
  renderDataGrid("masterData", state.snapshot.masterData.core);
  renderTimeline();
  renderDocuments();
  renderPostings();
  renderOverview();
  renderControls();
  applyLatestDocumentDefaults();
}

async function refreshState(message = "System synchronized with backend.") {
  state.snapshot = await api("/api/state");
  renderAll();
  setBanner(message, "success");
}

function activateSection(id) {
  document.querySelectorAll(".nav-link").forEach((button) => {
    button.classList.toggle("active", button.dataset.section === id);
  });
  document.querySelectorAll(".section").forEach((section) => {
    section.classList.toggle("active", section.id === id);
  });
}

function activateTxn(id) {
  document.querySelectorAll(".txn-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.txn === id);
  });
  document.querySelectorAll(".txn-form").forEach((form) => {
    form.classList.toggle("active", form.id === `form-${id}`);
  });
}

function formToJson(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  Object.keys(data).forEach((key) => {
    if (data[key] === "") {
      delete data[key];
    }
  });
  return data;
}

async function submitTransaction(type, form) {
  try {
    setBanner(`Posting ${type.toUpperCase()} transaction to backend...`, "neutral");
    const snapshot = await api(`/api/transactions/${type}`, {
      method: "POST",
      body: JSON.stringify(formToJson(form)),
    });
    state.snapshot = snapshot;
    renderAll();
    form.reset();
    applyLatestDocumentDefaults();
    setBanner(`${type.toUpperCase()} transaction posted successfully.`, "success");
  } catch (error) {
    setBanner(error.message, "danger");
  }
}

async function loadGuidedDemo() {
  try {
    setBanner("Loading guided demo dataset...", "neutral");
    state.snapshot = await api("/api/seed", { method: "POST", body: "{}" });
    renderAll();
    setBanner("Guided demo loaded from backend.", "success");
  } catch (error) {
    setBanner(error.message, "danger");
  }
}

async function resetDemoData() {
  try {
    setBanner("Resetting backend data...", "neutral");
    state.snapshot = await api("/api/reset", { method: "POST", body: "{}" });
    renderAll();
    setBanner("All transactional data has been reset.", "warning");
  } catch (error) {
    setBanner(error.message, "danger");
  }
}

async function exportSnapshot() {
  try {
    const payload = await api("/api/export");
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "buildright-p2p-snapshot.json";
    link.click();
    URL.revokeObjectURL(url);
    setBanner("Snapshot exported from backend.", "success");
  } catch (error) {
    setBanner(error.message, "danger");
  }
}

function bindEvents() {
  document.querySelectorAll(".nav-link").forEach((button) => {
    button.addEventListener("click", () => activateSection(button.dataset.section));
  });

  document.querySelectorAll(".txn-tab").forEach((button) => {
    button.addEventListener("click", () => activateTxn(button.dataset.txn));
  });

  document.getElementById("form-pr").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitTransaction("pr", event.currentTarget);
  });
  document.getElementById("form-rfq").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitTransaction("rfq", event.currentTarget);
  });
  document.getElementById("form-quotation").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitTransaction("quotation", event.currentTarget);
  });
  document.getElementById("form-po").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitTransaction("po", event.currentTarget);
  });
  document.getElementById("form-gr").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitTransaction("gr", event.currentTarget);
  });
  document.getElementById("form-invoice").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitTransaction("invoice", event.currentTarget);
  });
  document.getElementById("form-payment").addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitTransaction("payment", event.currentTarget);
  });

  document.getElementById("seedButton").addEventListener("click", loadGuidedDemo);
  document.getElementById("resetButton").addEventListener("click", resetDemoData);
  document.getElementById("exportButton").addEventListener("click", exportSnapshot);
}

async function bootstrap() {
  bindEvents();
  try {
    const uiState = readUiStateFromUrl();
    activateSection(uiState.section);
    activateTxn(uiState.txn);
    setBanner("Connecting to backend...", "neutral");
    await refreshState("Backend connected. Ready for transactions.");
  } catch (error) {
    setBanner(error.message, "danger");
  }
}

bootstrap();
