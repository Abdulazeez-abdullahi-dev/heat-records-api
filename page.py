PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Heat Records</title>
<style>
:root{--bg:#f6f7f9;--card:#ffffff;--text:#1d2530;--muted:#6a7584;--line:#dde2e8;--accent:#c2410c;--accent2:#2563eb;--ok:#15803d;--bad:#b91c1c}
@media (prefers-color-scheme:dark){:root{--bg:#14181d;--card:#1d232b;--text:#e8ecf1;--muted:#97a3b3;--line:#2d3641;--accent:#fb923c;--accent2:#60a5fa;--ok:#4ade80;--bad:#f87171}}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--text);line-height:1.4}
main{max-width:1000px;margin:0 auto;padding:20px 16px 48px}
h1{margin:0 0 4px;font-size:1.5rem}
h2{font-size:1.05rem;margin:0 0 12px}
.sub{color:var(--muted);margin:0 0 20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin-bottom:16px}
.stats{display:flex;flex-wrap:wrap;gap:10px}
.stat{border:1px solid var(--line);border-radius:8px;padding:10px 14px;display:flex;flex-direction:column;min-width:240px;flex:1}
.stat strong{color:var(--accent);font-size:1.05rem}
.stat .heats{color:var(--muted);font-size:.9rem;margin-bottom:6px}
.metric{display:flex;justify-content:space-between;gap:12px;font-size:.9rem;padding:3px 0;border-top:1px solid var(--line)}
.metric span:first-child{color:var(--muted)}
.row{display:flex;flex-wrap:wrap;gap:10px;align-items:end}
label{display:flex;flex-direction:column;font-size:.85rem;color:var(--muted);gap:4px}
input,select,button{font:inherit;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--text)}
button{background:var(--accent);color:#fff;border-color:var(--accent);cursor:pointer}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:1400px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);font-size:.92rem}
th{color:var(--muted);font-weight:600}
.msg{margin-top:10px;min-height:1.2em}
.ok{color:var(--ok)}
.bad{color:var(--bad)}
.count{color:var(--muted);font-size:.9rem;margin-top:8px}
.chart{width:100%;height:auto;display:block}
.grid{stroke:var(--line);stroke-width:1}
.tick{fill:var(--muted);font-size:12px}
.line{fill:none;stroke:var(--accent);stroke-width:2}
.dot{fill:var(--accent)}
.line2{fill:none;stroke:var(--accent2);stroke-width:2}
.dot2{fill:var(--accent2)}
.legend{display:flex;gap:16px;font-size:.85rem;color:var(--muted);margin-bottom:6px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}
.group{color:var(--muted);font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;margin:10px 0 2px}
table.totals{min-width:520px}
input[type=checkbox]{padding:0;width:18px;height:18px}
.note{color:var(--muted);font-size:.85rem;margin:0 0 8px}
</style>
</head>
<body>
<main>
<h1>Heat Records</h1>
<p class="sub">Sample data only. API docs are at <a href="/docs">/docs</a>.</p>

<section class="card" id="login" style="display:none">
<h2>API key</h2>
<p class="note">Enter the API key saved in api_key.txt, in the folder where the app runs.</p>
<form id="login-form">
<div class="row">
<label>Key<input id="key-input" type="password" autocomplete="off"></label>
<label style="flex-direction:row;align-items:center;gap:6px"><input id="key-remember" type="checkbox"> Remember on this computer</label>
<button type="submit">Unlock</button>
</div>
</form>
<div class="msg bad" id="login-msg"></div>
</section>

<div id="app" style="display:none">
<div style="text-align:right;margin-bottom:8px"><button id="lock" type="button" style="background:transparent;color:var(--text);border-color:var(--line)">Lock</button></div>

<section class="card">
<h2>Summary by grade</h2>
<div class="stats" id="summary"></div>
</section>

<section class="card">
<h2>Heats</h2>
<div class="row">
<label>Furnace
<select id="f-furnace"><option value="">All</option><option>EAF</option><option>LRF</option></select>
</label>
<label>Grade
<input id="f-grade" placeholder="e.g. SAE1018">
</label>
<button id="apply" type="button">Filter</button>
<button id="export" type="button" style="background:transparent;color:var(--text);border-color:var(--line)">Download CSV</button>
</div>
<div class="scroll" style="margin-top:12px">
<table>
<thead><tr><th><input type="checkbox" id="select-all" title="Tick all shown heats"></th><th>Heat no</th><th>Furnace</th><th>Grade</th><th>Shift</th><th>Start</th><th>Tap temp</th><th>Size (t)</th><th>Power kWh</th><th>Oxygen Nm&sup3;</th><th>Lime kg</th><th>Carbon kg</th><th>kWh/t</th><th>Carbon kg/t</th><th>Oxygen Nm&sup3;/t</th><th>Lime kg/t</th><th></th></tr></thead>
<tbody id="rows"></tbody>
</table>
</div>
<div class="count" id="count"></div>
</section>

<section class="card">
<h2>Totals and per tonne</h2>
<p class="note" id="totals-note"></p>
<div class="scroll">
<table class="totals">
<thead><tr><th>Parameter</th><th>Total</th><th>Per tonne</th><th>Heats counted</th></tr></thead>
<tbody id="totals"></tbody>
</table>
</div>
</section>

<section class="card">
<h2>Tap temperature by heat</h2>
<p class="note">Follows the furnace and grade filter above. EAF and LRF are drawn as separate lines. Hover over a dot to see the heat.</p>
<div id="chart"></div>
</section>

<section class="card">
<h2 id="form-title">Add a heat</h2>
<form id="form">
<div class="row">
<label>Heat no<input id="heat_no" required></label>
<label>Furnace
<select id="furnace"><option>EAF</option><option>LRF</option></select>
</label>
<label>Grade<input id="grade"></label>
<label>Shift<input id="shift" size="4"></label>
<label>Start time<input id="start_time" type="datetime-local"></label>
</div>
<div class="row" style="margin-top:10px">
<label>Tap temp (&deg;C)<input id="tap_temp" type="number" step="any"></label>
<label>Heat size (t)<input id="tap_weight_t" type="number" step="any"></label>
<label>Power (kWh)<input id="power_kwh" type="number" step="any"></label>
<label>Oxygen (Nm&sup3;)<input id="oxygen_nm3" type="number" step="any"></label>
<label>Lime (kg)<input id="lime_kg" type="number" step="any"></label>
<label>Carbon injection (kg)<input id="carbon_kg" type="number" step="any"></label>
<button type="submit" id="save-btn">Save heat</button>
<button type="button" id="cancel-edit" style="display:none;background:transparent;color:var(--text);border-color:var(--line)">Cancel</button>
<button type="button" id="delete-btn" style="display:none;background:var(--bad);border-color:var(--bad)">Delete heat</button>
</div>
</form>
<div class="msg" id="msg"></div>
</section>

<section class="card">
<h2>Add a chemistry sample</h2>
<p class="note">Samples are stored with the heat. They are not used in the summary averages.</p>
<form id="sample-form">
<div class="row">
<label>Heat no<input id="s_heat_no" required></label>
<label>Sample time<input id="s_time" type="datetime-local" required></label>
<label>C %<input id="s_c" type="number" step="any" size="6"></label>
<label>Mn %<input id="s_mn" type="number" step="any" size="6"></label>
<label>Si %<input id="s_si" type="number" step="any" size="6"></label>
<label>S %<input id="s_s" type="number" step="any" size="6"></label>
<label>P %<input id="s_p" type="number" step="any" size="6"></label>
<button type="submit">Save sample</button>
</div>
</form>
<div class="msg" id="smsg"></div>
</section>
</div>
</main>

<script>
const $ = id => document.getElementById(id);

const KEY_NAME = "heatApiKey";

function getKey() {
  return sessionStorage.getItem(KEY_NAME) || localStorage.getItem(KEY_NAME) || "";
}

function storeKey(key, remember) {
  sessionStorage.removeItem(KEY_NAME);
  localStorage.removeItem(KEY_NAME);
  (remember ? localStorage : sessionStorage).setItem(KEY_NAME, key);
}

function clearKey() {
  sessionStorage.removeItem(KEY_NAME);
  localStorage.removeItem(KEY_NAME);
}

function showLogin(message) {
  $("login").style.display = "";
  $("app").style.display = "none";
  $("login-msg").textContent = message || "";
}

function showApp() {
  $("login").style.display = "none";
  $("app").style.display = "";
}

async function api(url, options) {
  const opts = Object.assign({}, options);
  opts.headers = Object.assign({}, opts.headers, { "X-API-Key": getKey() });
  const hadKey = getKey() !== "";
  const res = await fetch(url, opts);
  if (res.status === 401) {
    clearKey();
    showLogin(hadKey ? "That key was not accepted. Try again." : "Enter the API key to continue.");
  }
  return res;
}

function cell(value) {
  const td = document.createElement("td");
  td.textContent = value == null ? "" : value;
  return td;
}

let currentHeats = [];
let rowBoxes = [];
const selected = new Set();
const TOTAL_FIELDS = [
  ["power_kwh", "Power", "kWh"],
  ["oxygen_nm3", "Oxygen", "Nm\u00b3"],
  ["carbon_kg", "Carbon injection", "kg"],
  ["lime_kg", "Lime", "kg"]
];

function fmt(value, digits) {
  const f = Math.pow(10, digits);
  return String(Math.round(value * f) / f);
}

function sumOf(list, getter) {
  return list.reduce((acc, h) => acc + getter(h), 0);
}

function addTotalRow(body, name, total, perTonne, counted) {
  const tr = document.createElement("tr");
  [name, total, perTonne, counted].forEach(v => tr.appendChild(cell(v)));
  body.appendChild(tr);
}

function plural(n, word) {
  return n + " " + word + (n === 1 ? "" : "s");
}

function renderTotals() {
  const picked = selected.size > 0;
  const chosen = picked ? currentHeats.filter(h => selected.has(h.heat_no)) : currentHeats;
  const body = $("totals");
  body.replaceChildren();
  if (chosen.length === 0) {
    $("totals-note").textContent = "No heats to calculate.";
    return;
  }
  $("totals-note").textContent = picked
    ? "Calculated for the " + plural(chosen.length, "heat") + " you ticked. Per tonne = total \u00f7 total heat size, using only heats that have both values."
    : "Calculated for all " + plural(chosen.length, "heat") + " shown. Tick heats in the table to calculate for just those. Per tonne = total \u00f7 total heat size, using only heats that have both values.";
  const sized = chosen.filter(h => h.tap_weight_t != null);
  addTotalRow(body, "Heat size",
    sized.length ? fmt(sumOf(sized, h => h.tap_weight_t), 1) + " t" : "n/a",
    "", sized.length + " of " + chosen.length);
  TOTAL_FIELDS.forEach(f => {
    const key = f[0];
    const have = chosen.filter(h => h[key] != null);
    const both = have.filter(h => h.tap_weight_t != null && h.tap_weight_t > 0);
    const tonnes = sumOf(both, h => h.tap_weight_t);
    const used = sumOf(both, h => h[key]);
    addTotalRow(body, f[1],
      have.length ? fmt(sumOf(have, h => h[key]), 1) + " " + f[2] : "n/a",
      both.length ? fmt(used / tonnes, 2) + " " + f[2] + "/t" : "n/a",
      both.length + " of " + chosen.length);
  });
}

function updateSelectAll() {
  $("select-all").checked = currentHeats.length > 0 && currentHeats.every(h => selected.has(h.heat_no));
}

function perTonne(h, field) {
  if (h[field] == null || h.tap_weight_t == null || h.tap_weight_t <= 0) return null;
  return Math.round(h[field] / h.tap_weight_t * 100) / 100;
}

function filterParams() {
  const params = new URLSearchParams();
  if ($("f-furnace").value) params.set("furnace", $("f-furnace").value);
  if ($("f-grade").value.trim()) params.set("grade", $("f-grade").value.trim());
  return params;
}

async function loadHeats() {
  const res = await api("/heats?" + filterParams().toString());
  if (!res.ok) return;
  const heats = await res.json();
  const body = $("rows");
  body.replaceChildren();
  rowBoxes = [];
  heats.forEach(h => {
    const tr = document.createElement("tr");
    const boxCell = document.createElement("td");
    const box = document.createElement("input");
    box.type = "checkbox";
    box.checked = selected.has(h.heat_no);
    box.addEventListener("change", () => {
      if (box.checked) selected.add(h.heat_no); else selected.delete(h.heat_no);
      updateSelectAll();
      renderTotals();
    });
    rowBoxes.push([h.heat_no, box]);
    boxCell.appendChild(box);
    tr.appendChild(boxCell);
    const start = h.start_time ? h.start_time.replace("T", " ") : "";
    [h.heat_no, h.furnace, h.grade, h.shift, start, h.tap_temp, h.tap_weight_t, h.power_kwh, h.oxygen_nm3, h.lime_kg, h.carbon_kg,
     perTonne(h, "power_kwh"), perTonne(h, "carbon_kg"), perTonne(h, "oxygen_nm3"), perTonne(h, "lime_kg")]
      .forEach(v => tr.appendChild(cell(v)));
    const editCell = document.createElement("td");
    const editBtn = document.createElement("button");
    editBtn.type = "button";
    editBtn.textContent = "Edit";
    editBtn.addEventListener("click", () => startEdit(h));
    editCell.appendChild(editBtn);
    tr.appendChild(editCell);
    body.appendChild(tr);
  });
  $("count").textContent = heats.length + (heats.length === 1 ? " heat" : " heats");
  currentHeats = heats;
  Array.from(selected).forEach(n => {
    if (!heats.some(h => h.heat_no === n)) selected.delete(n);
  });
  updateSelectAll();
  renderTotals();
  drawChart(heats);
}

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(name, attrs, text) {
  const el = document.createElementNS(SVG_NS, name);
  for (const key in attrs) el.setAttribute(key, attrs[key]);
  if (text != null) el.textContent = text;
  return el;
}

function drawChart(heats) {
  const box = $("chart");
  box.replaceChildren();
  const pts = heats
    .filter(h => h.tap_temp != null && h.start_time)
    .sort((a, b) => a.start_time.localeCompare(b.start_time));
  if (pts.length < 2) {
    box.textContent = "Add at least two heats with a start time and tap temperature to see the chart.";
    return;
  }
  const W = 800, H = 280, L = 56, R = 16, T = 16, B = 44;
  const temps = pts.map(p => p.tap_temp);
  let lo = Math.min(...temps), hi = Math.max(...temps);
  if (hi - lo < 20) {
    const mid = (hi + lo) / 2;
    lo = mid - 10;
    hi = mid + 10;
  }
  const pad = (hi - lo) * 0.1;
  lo -= pad;
  hi += pad;
  const x = i => L + (W - L - R) * (i / (pts.length - 1));
  const y = v => T + (H - T - B) * (1 - (v - lo) / (hi - lo));
  const svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": "Tap temperature by heat" });
  svg.setAttribute("class", "chart");
  for (let i = 0; i <= 4; i++) {
    const v = lo + (hi - lo) * i / 4;
    const yy = y(v);
    svg.appendChild(svgEl("line", { x1: L, x2: W - R, y1: yy, y2: yy, class: "grid" }));
    svg.appendChild(svgEl("text", { x: L - 8, y: yy + 4, class: "tick", "text-anchor": "end" }, Math.round(v)));
  }
  const present = [];
  [["EAF", "line", "dot"], ["LRF", "line2", "dot2"]].forEach(sr => {
    const idx = [];
    pts.forEach((p, i) => { if (p.furnace === sr[0]) idx.push(i); });
    if (idx.length === 0) return;
    present.push(sr[0]);
    if (idx.length > 1) {
      const d = idx.map((i, k) => (k ? "L" : "M") + x(i).toFixed(1) + " " + y(pts[i].tap_temp).toFixed(1)).join(" ");
      svg.appendChild(svgEl("path", { d: d, class: sr[1] }));
    }
    idx.forEach(i => {
      const dot = svgEl("circle", { cx: x(i), cy: y(pts[i].tap_temp), r: 4, class: sr[2] });
      dot.appendChild(svgEl("title", {}, pts[i].heat_no + " (" + sr[0] + "): " + pts[i].tap_temp + " \u00b0C"));
      svg.appendChild(dot);
    });
  });
  const step = Math.ceil(pts.length / 10);
  pts.forEach((p, i) => {
    if (i % step === 0) {
      svg.appendChild(svgEl("text", { x: x(i), y: H - B + 18, class: "tick", "text-anchor": "middle" }, p.heat_no));
    }
  });
  svg.appendChild(svgEl("text", { x: 14, y: H / 2, class: "tick", "text-anchor": "middle", transform: "rotate(-90 14 " + (H / 2) + ")" }, "Tap temp (\u00b0C)"));
  const legend = document.createElement("div");
  legend.className = "legend";
  present.forEach(name => {
    const item = document.createElement("span");
    const swatch = document.createElement("i");
    swatch.style.background = name === "EAF" ? "var(--accent)" : "var(--accent2)";
    item.append(swatch, name);
    legend.appendChild(item);
  });
  box.appendChild(legend);
  box.appendChild(svg);
}

const AVERAGES = [
  ["avg_tap_temp", "Tap temp", " \u00b0C"],
  ["avg_heat_size_t", "Heat size", " t"],
  ["avg_power_kwh", "Power", " kWh"],
  ["avg_carbon_kg", "Carbon injection", " kg"],
  ["avg_oxygen_nm3", "Oxygen", " Nm\u00b3"],
  ["avg_lime_kg", "Lime", " kg"]
];

const PER_TONNE = [
  ["power_kwh_per_t", "Power", " kWh/t"],
  ["carbon_kg_per_t", "Carbon injection", " kg/t"],
  ["oxygen_nm3_per_t", "Oxygen", " Nm\u00b3/t"],
  ["lime_kg_per_t", "Lime", " kg/t"]
];

function addGroup(card, title) {
  const g = document.createElement("div");
  g.className = "group";
  g.textContent = title;
  card.appendChild(g);
}

function addRows(card, s, list) {
  list.forEach(m => {
    const row = document.createElement("div");
    row.className = "metric";
    const label = document.createElement("span");
    label.textContent = m[1];
    const value = document.createElement("span");
    value.textContent = s[m[0]] == null ? "n/a" : s[m[0]] + m[2];
    row.append(label, value);
    card.appendChild(row);
  });
}

async function loadSummary() {
  const res = await api("/summary");
  if (!res.ok) return;
  const data = await res.json();
  const box = $("summary");
  box.replaceChildren();
  if (data.length === 0) {
    box.textContent = "No heats yet.";
    return;
  }
  data.forEach(s => {
    const card = document.createElement("div");
    card.className = "stat";
    const name = document.createElement("strong");
    name.textContent = s.grade || "(no grade)";
    const heats = document.createElement("div");
    heats.className = "heats";
    heats.textContent = s.heats + (s.heats === 1 ? " heat" : " heats");
    card.append(name, heats);
    addRows(card, s, [["total_heat_size_t", "Total heat size", " t"]]);
    addGroup(card, "Average per heat");
    addRows(card, s, AVERAGES);
    addGroup(card, "Per tonne of steel");
    addRows(card, s, PER_TONNE);
    box.appendChild(card);
  });
}

async function showResult(res, msg, okText) {
  if (res.ok) {
    msg.textContent = okText;
    msg.className = "msg ok";
    return true;
  }
  let text = "Error " + res.status;
  try {
    const err = await res.json();
    if (Array.isArray(err.detail)) {
      text += ": " + err.detail.map(d => (d.loc || []).slice(1).join(".") + " " + d.msg).join("; ");
    } else if (err.detail) {
      text += ": " + err.detail;
    }
  } catch (e) {}
  msg.textContent = text;
  msg.className = "msg bad";
  return false;
}

function addNumbers(body, pairs) {
  pairs.forEach(p => {
    const v = $(p[0]).value;
    if (v !== "") body[p[1]] = Number(v);
  });
}

async function postJson(url, body) {
  return api(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
}

let editingHeat = null;
const NUM_FIELDS = ["tap_temp", "tap_weight_t", "power_kwh", "oxygen_nm3", "lime_kg", "carbon_kg"];

function startEdit(h) {
  editingHeat = h.heat_no;
  $("heat_no").value = h.heat_no;
  $("heat_no").readOnly = true;
  $("furnace").value = h.furnace;
  $("furnace").disabled = true;
  $("grade").value = h.grade || "";
  $("shift").value = h.shift || "";
  $("start_time").value = h.start_time ? h.start_time.slice(0, 16) : "";
  NUM_FIELDS.forEach(f => { $(f).value = h[f] == null ? "" : h[f]; });
  $("form-title").textContent = "Edit heat " + h.heat_no;
  $("save-btn").textContent = "Update heat";
  $("cancel-edit").style.display = "";
  $("delete-btn").style.display = "";
  $("msg").textContent = "";
  $("form").scrollIntoView({ behavior: "smooth", block: "center" });
}

function endEdit() {
  editingHeat = null;
  $("form").reset();
  $("heat_no").readOnly = false;
  $("furnace").disabled = false;
  $("form-title").textContent = "Add a heat";
  $("save-btn").textContent = "Save heat";
  $("cancel-edit").style.display = "none";
  $("delete-btn").style.display = "none";
}

async function saveEdit(msg) {
  const name = editingHeat;
  const body = {
    grade: $("grade").value.trim() || null,
    shift: $("shift").value.trim() || null,
    start_time: $("start_time").value || null
  };
  NUM_FIELDS.forEach(f => {
    const v = $(f).value;
    body[f] = v === "" ? null : Number(v);
  });
  const res = await api("/heats/" + encodeURIComponent(name), {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (await showResult(res, msg, "Updated " + name)) {
    endEdit();
    loadHeats();
    loadSummary();
  }
}

$("cancel-edit").addEventListener("click", () => {
  endEdit();
  $("msg").textContent = "";
});

$("delete-btn").addEventListener("click", async () => {
  if (!editingHeat) return;
  const name = editingHeat;
  if (!confirm("Delete heat " + name + " and all its events? This cannot be undone.")) return;
  const msg = $("msg");
  const res = await api("/heats/" + encodeURIComponent(name), { method: "DELETE" });
  if (await showResult(res, msg, "Deleted " + name)) {
    endEdit();
    loadHeats();
    loadSummary();
  }
});

$("select-all").addEventListener("change", e => {
  currentHeats.forEach(h => {
    if (e.target.checked) selected.add(h.heat_no); else selected.delete(h.heat_no);
  });
  rowBoxes.forEach(pair => { pair[1].checked = selected.has(pair[0]); });
  renderTotals();
});

$("export").addEventListener("click", async () => {
  const res = await api("/export.csv?" + filterParams().toString());
  if (!res.ok) return;
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "heats.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
});

$("apply").addEventListener("click", loadHeats);

$("form").addEventListener("submit", async e => {
  e.preventDefault();
  const msg = $("msg");
  msg.textContent = "";
  if (editingHeat) {
    await saveEdit(msg);
    return;
  }
  const body = { heat_no: $("heat_no").value.trim(), furnace: $("furnace").value };
  const grade = $("grade").value.trim();
  if (grade) body.grade = grade;
  const shift = $("shift").value.trim();
  if (shift) body.shift = shift;
  if ($("start_time").value) body.start_time = $("start_time").value;
  addNumbers(body, [
    ["tap_temp", "tap_temp"], ["tap_weight_t", "tap_weight_t"], ["power_kwh", "power_kwh"],
    ["oxygen_nm3", "oxygen_nm3"], ["lime_kg", "lime_kg"], ["carbon_kg", "carbon_kg"]
  ]);
  const res = await postJson("/heats", body);
  if (await showResult(res, msg, "Saved " + body.heat_no)) {
    e.target.reset();
    loadHeats();
    loadSummary();
  }
});

$("sample-form").addEventListener("submit", async e => {
  e.preventDefault();
  const msg = $("smsg");
  msg.textContent = "";
  const heatNo = $("s_heat_no").value.trim();
  const body = { timestamp: $("s_time").value, kind: "sample" };
  addNumbers(body, [["s_c", "c"], ["s_mn", "mn"], ["s_si", "si"], ["s_s", "s"], ["s_p", "p"]]);
  const res = await postJson("/heats/" + encodeURIComponent(heatNo) + "/events", body);
  if (await showResult(res, msg, "Saved sample for " + heatNo)) {
    e.target.reset();
    loadSummary();
  }
});

$("login-form").addEventListener("submit", e => {
  e.preventDefault();
  const key = $("key-input").value.trim();
  if (!key) return;
  storeKey(key, $("key-remember").checked);
  $("key-input").value = "";
  showApp();
  loadHeats();
  loadSummary();
});

$("lock").addEventListener("click", () => {
  clearKey();
  showLogin("Locked.");
});

if (getKey() === "") {
  showLogin("");
} else {
  showApp();
  loadHeats();
  loadSummary();
}
</script>
</body>
</html>
"""
