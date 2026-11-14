const button = document.querySelector("#scan");
const status = document.querySelector("#status");
const container = document.querySelector("#repos");
const history = document.querySelector("#history");

function renderRepositories(rows) {
  container.replaceChildren();
  if (!rows.length) {
    const empty = document.createElement("p");
    empty.textContent = "No repositories found. Wait for the scheduled scan or ask an admin to run one.";
    container.append(empty);
    return;
  }
  for (const repo of rows) {
    const card = document.createElement("article");
    const meta = document.createElement("div");
    meta.className = "meta";
    const categories = document.createElement("span");
    categories.textContent = (repo.categories || []).join(" · ");
    const score = document.createElement("b");
    score.textContent = "Score " + repo.score;
    meta.append(categories, score);

    const title = document.createElement("h3");
    const link = document.createElement("a");
    const url = typeof repo.html_url === "string" && repo.html_url.startsWith("https://github.com/")
      ? repo.html_url : "https://github.com";
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = repo.full_name || "Unknown repository";
    title.append(link);

    const description = document.createElement("p");
    description.textContent = repo.description || "No description provided.";
    const details = document.createElement("small");
    details.textContent = "★ " + (repo.stars || 0) + " · " +
      (repo.language || "Unknown language") + " · Updated " + (repo.updated_at || "").slice(0, 10);
    const breakdown = document.createElement("small");
    breakdown.textContent = "Score details: " +
      Object.entries(repo.score_breakdown || {}).map(([key, value]) => key + " " + value).join(" · ");
    card.append(meta, title, description, details, document.createElement("br"), breakdown);
    container.append(card);
  }
}

async function loadRepositories() {
  const response = await fetch("/api/repos");
  if (!response.ok) throw new Error("Could not load repositories");
  renderRepositories(await response.json());
}

async function loadHistory() {
  const response = await fetch("/api/scans");
  if (!response.ok) throw new Error("Could not load scan history");
  const rows = await response.json();
  history.replaceChildren();
  if (!rows.length) {
    const empty = document.createElement("p");
    empty.textContent = "No saved scans yet.";
    history.append(empty);
    return;
  }
  for (const run of rows) {
    const card = document.createElement("article");
    const heading = document.createElement("h3");
    heading.textContent = "Scan #" + run.id;
    const date = document.createElement("p");
    date.textContent = new Date(run.scanned_at).toLocaleString();
    const count = document.createElement("small");
    count.textContent = run.count + " repositories";
    const detail = document.createElement("a");
    detail.href = "/api/scans/" + encodeURIComponent(run.id);
    detail.textContent = "View JSON results";
    card.append(heading, date, count, document.createElement("br"), detail);
    history.append(card);
  }
}

async function refreshDashboard() {
  await Promise.all([loadRepositories(), loadHistory()]);
}

button.addEventListener("click", async () => {
  const key = window.prompt("Admin scan key (not stored by this page):");
  if (!key) return;
  button.disabled = true;
  status.textContent = "Scanning public GitHub repositories…";
  try {
    const response = await fetch("/api/scan", {
      method: "POST",
      headers: { "X-Scan-Key": key }
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Scan failed");
    status.textContent = "Saved scan #" + data.scan_id + " · " + data.scanned + " repositories";
    await refreshDashboard();
  } catch (error) {
    status.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

refreshDashboard().catch(error => {
  container.textContent = error.message;
  history.textContent = error.message;
});
