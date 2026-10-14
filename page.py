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
main{max-width:960px;margin:0 auto;padding:20px 16px 48px}
h1{margin:0 0 4px;font-size:1.5rem}
h2{font-size:1.05rem;margin:0 0 12px}
.sub{color:var(--muted);margin:0 0 20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin-bottom:16px}
.stats{display:flex;flex-wrap:wrap;gap:10px}
.stat{border:1px solid var(--line);border-radius:8px;padding:10px 14px;display:flex;flex-direction:column;min-width:170px}
.stat strong{color:var(--accent)}
.stat span{color:var(--muted);font-size:.9rem}
.row{display:flex;flex-wrap:wrap;gap:10px;align-items:end}
label{display:flex;flex-direction:column;font-size:.85rem;color:var(--muted);gap:4px}
input,select,button{font:inherit;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--text)}
button{background:var(--accent);color:#fff;border-color:var(--accent);cursor:pointer}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:560px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);font-size:.92rem}
th{color:var(--muted);font-weight:600}
#msg{margin-top:10px;min-height:1.2em}
.ok{color:var(--ok)}
.bad{color:var(--bad)}
.count{color:var(--muted);font-size:.9rem;margin-top:8px}
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
<thead><tr><th>Heat no</th><th>Furnace</th><th>Grade</th><th>Shift</th><th>Start</th><th>Tap temp</th><th>Power kWh</th></tr></thead>
<tbody id="rows"></tbody>
</table>
</div>
<div class="count" id="count"></div>
</section>

<section class="card">
<h2>Add a heat</h2>
<form id="form">
<div class="row">
<label>Heat no<input id="heat_no" required></label>
<label>Furnace
<select id="furnace"><option>EAF</option><option>LRF</option></select>
</label>
<label>Grade<input id="grade"></label>
<label>Shift<input id="shift" size="4"></label>
<label>Start time<input id="start_time" type="datetime-local"></label>
<label>Tap temp<input id="tap_temp" type="number" step="any"></label>
<label>Power kWh<input id="power_kwh" type="number" step="any"></label>
<button type="submit">Save heat</button>
</div>
</form>
<div id="msg"></div>
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
    [h.heat_no, h.furnace, h.grade, h.shift, start, h.tap_temp, h.power_kwh]
      .forEach(v => tr.appendChild(cell(v)));
    body.appendChild(tr);
  });
  $("count").textContent = heats.length + (heats.length === 1 ? " heat" : " heats");
}

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
    const div = document.createElement("div");
    div.className = "stat";
    const name = document.createElement("strong");
    name.textContent = s.grade || "(no grade)";
    const info = document.createElement("span");
    const avg = s.avg_tap_temp == null ? "n/a" : s.avg_tap_temp + " \u00b0C";
    info.textContent = s.heats + (s.heats === 1 ? " heat" : " heats") + ", avg tap " + avg;
    div.append(name, info);
    box.appendChild(div);
  });
}

$("apply").addEventListener("click", loadHeats);

$("form").addEventListener("submit", async e => {
  e.preventDefault();
  const msg = $("msg");
  msg.className = "";
  msg.textContent = "";
  const body = { heat_no: $("heat_no").value.trim(), furnace: $("furnace").value };
  const grade = $("grade").value.trim();
  if (grade) body.grade = grade;
  const shift = $("shift").value.trim();
  if (shift) body.shift = shift;
  if ($("start_time").value) body.start_time = $("start_time").value;
  if ($("tap_temp").value !== "") body.tap_temp = Number($("tap_temp").value);
  if ($("power_kwh").value !== "") body.power_kwh = Number($("power_kwh").value);
  const res = await fetch("/heats", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (res.ok) {
    msg.textContent = "Saved " + body.heat_no;
    msg.className = "ok";
    e.target.reset();
    loadHeats();
    loadSummary();
  } else {
    const err = await res.json();
    let text = "Error " + res.status;
    if (Array.isArray(err.detail)) {
      text += ": " + err.detail.map(d => (d.loc || []).slice(1).join(".") + " " + d.msg).join("; ");
    } else if (err.detail) {
      text += ": " + err.detail;
    }
    msg.textContent = text;
    msg.className = "bad";
  }
});

loadHeats();
loadSummary();
</script>
</body>
</html>
"""
