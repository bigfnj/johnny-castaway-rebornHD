"use strict";
const status = document.getElementById("loading");
const background = document.getElementById("background");
background.addEventListener("click", () => {
  const dark = document.body.classList.toggle("dark");
  background.setAttribute("aria-pressed", String(dark));
  background.textContent = dark ? "Use light checkerboard" : "Use dark checkerboard";
});
const originals = document.getElementById("originals");
originals.addEventListener("click", () => {
  const hide = originals.textContent === "Hide all originals";
  document.querySelectorAll("details").forEach(el => { el.open = !hide; });
  originals.textContent = hide ? "Show all originals" : "Hide all originals";
});
document.getElementById("filter").addEventListener("input", event => {
  const q = event.target.value.trim().toLowerCase();
  document.querySelectorAll("figure[data-filter]").forEach(el => { el.hidden = !el.dataset.filter.toLowerCase().includes(q); });
  document.querySelectorAll("section").forEach(el => { el.hidden = !el.querySelector("figure:not([hidden])"); });
});
async function render() {
  const response = await fetch("review-data.json");
  if (!response.ok) throw new Error(`Review data HTTP ${response.status}`);
  const data = await response.json();
  await Promise.all(data.assets.flatMap(row => ["cartoon", "original"].map(async kind => {
    const info = kind === "cartoon" ? row.selected_raw : row.original_reference;
    const canvas = document.querySelector(`canvas[data-key="${row.key}"][data-kind="${kind}"]`);
    const image = new Image();
    image.src = kind === "cartoon" ? row.url : row.original_url;
    await image.decode();
    const b = info.alpha8_bounds;
    const scale = Math.min((canvas.width - 40) / (b[2] - b[0]), (canvas.height - 36) / (b[3] - b[1]));
    const ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = kind === "cartoon";
    ctx.drawImage(image, (canvas.width - (b[2] - b[0]) * scale) / 2 - b[0] * scale,
      (canvas.height - (b[3] - b[1]) * scale) / 2 - b[1] * scale, image.width * scale, image.height * scale);
    canvas.dataset.loaded = "true";
  })));
  status.textContent = `${data.assets.length} of ${data.assets.length} comparisons ready.`;
}
render().catch(error => { status.textContent = `Could not load comparisons: ${error.message}`; });
