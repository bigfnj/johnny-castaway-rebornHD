"use strict";
const background = document.getElementById("background");
background.addEventListener("click", () => {
  const dark = document.body.classList.toggle("dark");
  background.setAttribute("aria-pressed", String(dark));
  background.textContent = dark ? "Use light checkerboard" : "Use dark checkerboard";
});
const status = document.getElementById("loading");
async function render() {
  const response = await fetch("review-data.json");
  if (!response.ok) throw new Error(`Review data HTTP ${response.status}`);
  const data = await response.json();
  await Promise.all(data.rows.flatMap(row => ["original", "target", "revised"].map(async kind => {
    const input = row[kind];
    const canvas = document.querySelector(`canvas[data-key="${row.key}"][data-kind="${kind}"]`);
    const image = new Image();
    image.src = input.url;
    await image.decode();
    const bounds = input.display_bounds;
    const rect = input.source_rect ?? [bounds[0], bounds[1], bounds[2] - bounds[0], bounds[3] - bounds[1]];
    const scale = Math.min((canvas.width - 40) / rect[2], (canvas.height - 40) / rect[3]);
    const ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = kind !== "original";
    const x = (canvas.width - rect[2] * scale) / 2;
    const y = (canvas.height - rect[3] * scale) / 2;
    if (input.source_rect) {
      ctx.drawImage(image, ...rect, x, y, rect[2] * scale, rect[3] * scale);
    } else {
      ctx.drawImage(image, x - rect[0] * scale, y - rect[1] * scale, image.width * scale, image.height * scale);
    }
    canvas.setAttribute("data-loaded", "true");
  })));
  status.textContent = `${data.rows.length} of ${data.rows.length} comparisons ready.`;
}
render().catch(error => { status.textContent = `Could not load comparisons: ${error.message}`; });
