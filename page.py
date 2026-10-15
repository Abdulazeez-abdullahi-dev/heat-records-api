PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Heat Records</title>
<style>
:root{--bg:#f6f7f9;--card:#ffffff;--text:#1d2530;--muted:#6a7584;--line:#dde2e8;--accent:#c2410c;--ok:#15803d;--bad:#b91c1c}
@media (prefers-color-scheme:dark){:root{--bg:#14181d;--card:#1d232b;--text:#e8ecf1;--muted:#97a3b3;--line:#2d3641;--accent:#fb923c;--ok:#4ade80;--bad:#f87171}}
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
table{border-collapse:collapse;width:100%;min-width:940px}
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
.note{color:var(--muted);font-size:.85rem;margin:0 0 8px}
</style>
</head>
<body>
<main>
<h1>Heat Records</h1>
<p class="sub">Sample data only. API docs are at <a href="/docs">/docs</a>.</p>

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
</div>
<div class="scroll" style="margin-top:12px">
<table>
<thead><tr><th>Heat no</th><th>Furnace</th><th>Grade</th><th>Shift</th><th>Start</th><th>Tap temp</th><th>Size (t)</th><th>Power kWh</th><th>Oxygen Nm&sup3;</th><th>Lime kg</th><th>Carbon kg</th><th></th></tr></thead>
<tbody id="rows"></tbody>
</table>
</div>
<div class="count" id="count"></div>
</section>

<section class="card">
<h2>Tap temperature by heat</h2>
<p class="note">Follows the furnace and grade filter above. Hover over a dot to see the heat.</p>
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
</main>

<script>
const $ = id => document.getElementById(id);

function cell(value) {
  const td = document.createElement("td");
  td.textContent = value == null ? "" : value;
  return td;
}

async function loadHeats() {
  const params = new URLSearchParams();
  if ($("f-furnace").value) params.set("furnace", $("f-furnace").value);
  if ($("f-grade").value.trim()) params.set("grade", $("f-grade").value.trim());
  const res = await fetch("/heats?" + params.toString());
  const heats = await res.json();
  const body = $("rows");
  body.replaceChildren();
  heats.forEach(h => {
    const tr = document.createElement("tr");
    const start = h.start_time ? h.start_time.replace("T", " ") : "";
    [h.heat_no, h.furnace, h.grade, h.shift, start, h.tap_temp, h.tap_weight_t, h.power_kwh, h.oxygen_nm3, h.lime_kg, h.carbon_kg]
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
  const d = pts.map((p, i) => (i ? "L" : "M") + x(i).toFixed(1) + " " + y(p.tap_temp).toFixed(1)).join(" ");
  svg.appendChild(svgEl("path", { d: d, class: "line" }));
  const step = Math.ceil(pts.length / 10);
  pts.forEach((p, i) => {
    const dot = svgEl("circle", { cx: x(i), cy: y(p.tap_temp), r: 4, class: "dot" });
    dot.appendChild(svgEl("title", {}, p.heat_no + ": " + p.tap_temp + " \u00b0C"));
    svg.appendChild(dot);
    if (i % step === 0) {
      svg.appendChild(svgEl("text", { x: x(i), y: H - B + 18, class: "tick", "text-anchor": "middle" }, p.heat_no));
    }
  });
  svg.appendChild(svgEl("text", { x: 14, y: H / 2, class: "tick", "text-anchor": "middle", transform: "rotate(-90 14 " + (H / 2) + ")" }, "Tap temp (\u00b0C)"));
  box.appendChild(svg);
}

const METRICS = [
  ["avg_tap_temp", "Avg tap temp", " \u00b0C"],
  ["avg_heat_size_t", "Avg heat size", " t"],
  ["avg_power_kwh", "Avg power", " kWh"],
  ["avg_carbon_kg", "Avg carbon injection", " kg"],
  ["avg_oxygen_nm3", "Avg oxygen", " Nm\u00b3"],
  ["avg_lime_kg", "Avg lime", " kg"]
];

async function loadSummary() {
  const res = await fetch("/summary");
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
    METRICS.forEach(m => {
      const row = document.createElement("div");
      row.className = "metric";
      const label = document.createElement("span");
      label.textContent = m[1];
      const value = document.createElement("span");
      value.textContent = s[m[0]] == null ? "n/a" : s[m[0]] + m[2];
      row.append(label, value);
      card.appendChild(row);
    });
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
  return fetch(url, {
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
  const res = await fetch("/heats/" + encodeURIComponent(name), {
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
  const res = await fetch("/heats/" + encodeURIComponent(name), { method: "DELETE" });
  if (await showResult(res, msg, "Deleted " + name)) {
    endEdit();
    loadHeats();
    loadSummary();
  }
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

loadHeats();
loadSummary();
</script>
</body>
</html>
"""
