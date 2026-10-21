"use strict";
document.getElementById("clear-filter").addEventListener("click", () => {
  const field = document.getElementById("filter");
  field.value = "";
  field.dispatchEvent(new Event("input"));
  field.focus();
});
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
  const dataUrl = document.body.dataset.reviewData || "review-data.json";
  const response = await fetch(dataUrl, {cache: "no-store"});
  if (!response.ok) throw new Error(`Review data HTTP ${response.status}`);
  const data = await response.json();
  let loaded = 0;
  let errors = 0;
  await Promise.all(data.assets.flatMap(row => ["cartoon", "original"].map(async kind => {
    const info = kind === "cartoon" ? row.selected_raw : row.original_reference;
    const url = kind === "cartoon" ? row.url : row.original_url;
    const canvas = document.querySelector(`canvas[data-key="${row.key}"][data-kind="${kind}"]`);
    if (!info || !url || !canvas) return;
    try {
      const image = new Image();
      image.src = `${url}?sha=${info.sha256}`;
      await image.decode();
      const b = info.alpha8_bounds || [0, 0, image.width, image.height];
      if (b[2] <= b[0] || b[3] <= b[1]) throw new Error("Image has no visible artwork");
      const scale = Math.min((canvas.width - 40) / (b[2] - b[0]), (canvas.height - 36) / (b[3] - b[1]));
      const ctx = canvas.getContext("2d");
      ctx.imageSmoothingEnabled = kind === "cartoon";
      ctx.drawImage(image, (canvas.width - (b[2] - b[0]) * scale) / 2 - b[0] * scale,
        (canvas.height - (b[3] - b[1]) * scale) / 2 - b[1] * scale, image.width * scale, image.height * scale);
      canvas.dataset.loaded = "true";
      loaded += 1;
    } catch (error) {
      errors += 1;
      canvas.dataset.loaded = "false";
      const note = document.createElement("p");
      note.className = "load-error";
      note.textContent = `Could not load ${kind} ${row.key}: ${error.message}`;
      canvas.parentElement.after(note);
    }
  })));
  status.textContent = `${data.summary} ${loaded} image panels loaded.${errors ? ` ${errors} panels could not load.` : ""}`;
}
render().catch(error => { status.textContent = `Could not load review data: ${error.message}`; });
