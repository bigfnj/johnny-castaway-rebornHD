"use strict";
const loading = document.getElementById("loading");
const background = document.getElementById("background");
const filter = document.getElementById("filter");
const visibleCount = document.getElementById("visible-count");
const comparisons = [...document.querySelectorAll(".comparison")];

background.addEventListener("click", () => {
  const dark = document.body.classList.toggle("dark");
  background.setAttribute("aria-pressed", String(dark));
  background.textContent = dark ? "Use light checkerboard" : "Use dark checkerboard";
});

function applyFilter() {
  const tokens = filter.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
  let visible = 0;
  comparisons.forEach(row => {
    row.hidden = !tokens.every(token => row.dataset.key.toLowerCase().includes(token));
    if (!row.hidden) visible += 1;
  });
  document.querySelectorAll(".group").forEach(group => {
    group.hidden = [...group.querySelectorAll(".comparison")].every(row => row.hidden);
  });
  visibleCount.textContent = `${visible} of ${comparisons.length} rows shown`;
}
filter.addEventListener("input", applyFilter);
document.getElementById("clear-filter").addEventListener("click", () => {
  filter.value = "";
  applyFilter();
  filter.focus();
});
document.querySelectorAll("nav a[href^='#group-']").forEach(link => {
  link.addEventListener("click", () => {
    filter.value = "";
    applyFilter();
  });
});
applyFilter();

async function render() {
  const response = await fetch("review-data.json", {cache: "no-cache"});
  if (!response.ok) throw new Error(`Review data HTTP ${response.status}`);
  const data = await response.json();
  let completed = 0;
  let failed = false;
  await Promise.all(data.frames.map(async row => {
    try {
      await Promise.all(Object.entries(row.images).map(async ([kind, info]) => {
        const canvas = document.querySelector(`canvas[data-key="${row.key}"][data-kind="${kind}"]`);
        const image = new Image();
        image.src = info.url;
        await image.decode();
        const b = info.alpha8_bounds;
        const width = b[2] - b[0], height = b[3] - b[1];
        const scale = Math.min((canvas.width - 40) / width, (canvas.height - 36) / height);
        const ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = kind !== "original";
        ctx.drawImage(image, (canvas.width - width * scale) / 2 - b[0] * scale,
          (canvas.height - height * scale) / 2 - b[1] * scale,
          image.width * scale, image.height * scale);
        canvas.dataset.loaded = "true";
      }));
      completed += 1;
      if (!failed) loading.textContent = `${completed} of ${data.frames.length} comparisons ready.`;
    } catch (error) {
      failed = true;
      throw new Error(`${row.key}: ${error.message}`);
    }
  }));
}
render().catch(error => {
  loading.textContent = `Could not load comparisons: ${error.message}`;
});
