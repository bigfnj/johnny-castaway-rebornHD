"use strict";
const data = JSON.parse(document.getElementById("review-data").textContent);
const byId = id => document.getElementById(id);
const entries = [];
let loaded = 0, failed = 0, active = null;
const dialog = byId("detail");
function text(tag, value, cls) {
  const node = document.createElement(tag);
  node.textContent = value;
  if (cls) node.className = cls;
  return node;
}
function paint(canvas, img, stage, large = false) {
  const wanted = Number(byId("zoom").value);
  const maxW = Math.max(1, stage.clientWidth - 28), maxH = Math.max(1, stage.clientHeight - 28);
  const scale = Math.max(1, Math.min(large ? Math.max(8, wanted) : wanted,
    Math.floor(maxW / img.naturalWidth), Math.floor(maxH / img.naturalHeight)));
  canvas.width = img.naturalWidth * scale;
  canvas.height = img.naturalHeight * scale;
  const ctx = canvas.getContext("2d");
  ctx.imageSmoothingEnabled = false;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  canvas.dataset.loaded = "true";
}
function updateLoad() {
  byId("loaded").textContent = failed
    ? loaded + " of " + data.count + " originals loaded; " + failed + " failed"
    : loaded + " of " + data.count + " originals loaded";
}
function openDetail(entry) {
  if (!entry.img.complete || !entry.img.naturalWidth) return;
  active = entry;
  byId("detail-title").textContent = entry.row.id;
  byId("detail-description").textContent = entry.row.description;
  byId("detail-status").textContent = entry.row.status_label + ". " + entry.row.status_detail;
  byId("detail-original").href = entry.row.url;
  dialog.showModal();
  requestAnimationFrame(() => paint(byId("detail-canvas"), entry.img, byId("detail-stage"), true));
}
for (const row of data.rows) {
  const card = document.createElement("article"); card.className = "card"; card.dataset.id = row.id;
  const top = document.createElement("div"); top.className = "card-top";
  const heading = document.createElement("div"); heading.append(text("h3", row.id, "frame-id"));
  heading.append(text("span", row.canvas[0] + " x " + row.canvas[1] + " original pixels; unchanged alpha", "dimensions"));
  top.append(heading, text("span", row.status_label, "badge " + row.status));
  const stage = document.createElement("button"); stage.type = "button"; stage.className = "stage";
  stage.setAttribute("aria-label", "Enlarge original " + row.id);
  const canvas = document.createElement("canvas"); canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", row.id + ": " + row.description); stage.append(canvas);
  const copy = document.createElement("div"); copy.className = "card-copy";
  copy.append(text("p", row.description, "description"), text("p", row.status_detail, "status-detail"));
  const links = document.createElement("div"); links.className = "card-links";
  const original = text("a", "Full original"); original.href = row.url; original.target = "_blank"; original.rel = "noopener";
  links.append(original);
  const details = document.createElement("details"); details.className = "detail-toggle";
  details.append(text("summary", "Original source details"));
  details.append(text("p", "Archive member: " + row.archive_member));
  details.append(text("p", "PNG SHA256: " + row.original.sha256));
  if (row.static_source_actions.length) {
    details.append(text("p", "Static script context: " + row.static_source_actions.map(a => a.ttm + " tag " + a.tag + ": " + a.description).join("; ")));
  } else details.append(text("p", "No unique-slot static action is recorded for this frame."));
  copy.append(links, details); card.append(top, stage, copy);
  const img = new Image(), entry = {row, card, canvas, img, stage}; entries.push(entry);
  stage.addEventListener("click", () => openDetail(entry));
  img.onload = () => { loaded++; paint(canvas, img, stage); updateLoad(); };
  img.onerror = () => { failed++; canvas.dataset.loaded = "false"; stage.append(text("span", "Original failed to load")); updateLoad(); };
  byId(row.resource === "SSUZY1.BMP" ? "ssuzy-grid" : "sbreakup-grid").append(card);
  img.src = row.url;
}
function filter() {
  const q = byId("search").value.toLowerCase().replace(/\.?bmp/g, "").replace(/[^a-z0-9]/g, "");
  const status = byId("status").value;
  let visible = 0;
  for (const entry of entries) {
    const haystack = entry.row.id.toLowerCase().replace(/\.?bmp/g, "").replace(/[^a-z0-9]/g, "");
    const show = (!q || haystack.includes(q)) && (status === "all" || status === entry.row.status);
    entry.card.hidden = !show; if (show) visible++;
  }
  for (const item of [["ssuzy", "SSUZY1.BMP"], ["sbreakup", "SBREAKUP.BMP"]]) {
    byId(item[0]).hidden = !entries.some(e => e.row.resource === item[1] && !e.card.hidden);
  }
  byId("empty").hidden = visible > 0;
  repaint();
}
function repaint() {
  for (const e of entries) if (!e.card.hidden && e.img.naturalWidth) paint(e.canvas, e.img, e.stage);
  if (dialog.open && active) paint(byId("detail-canvas"), active.img, byId("detail-stage"), true);
}
byId("search").addEventListener("input", filter);
byId("status").addEventListener("change", filter);
byId("clear").addEventListener("click", () => { byId("search").value = ""; byId("status").value = "all"; filter(); });
byId("zoom").addEventListener("change", repaint);
byId("backdrop").addEventListener("change", () => {
  const colors = {light:["#eef2f5","#e4eaf0"],sea:["#6ab2c9","#6ab2c9"],dark:["#253d4e","#304957"]}[byId("backdrop").value];
  document.documentElement.style.setProperty("--tile", colors[0]);
  document.documentElement.style.setProperty("--tile-alt", colors[1]);
});
byId("close").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", e => { if (e.target === dialog) { const r = dialog.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close(); } });
window.addEventListener("resize", () => requestAnimationFrame(repaint));
updateLoad();
