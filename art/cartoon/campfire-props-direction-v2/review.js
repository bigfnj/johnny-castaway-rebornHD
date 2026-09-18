"use strict";
const background = document.getElementById("background");
background.addEventListener("click", () => {
  const dark = document.body.classList.toggle("dark");
  background.setAttribute("aria-pressed", String(dark));
  background.textContent = dark ? "Use light checkerboard" : "Use dark checkerboard";
});
const earlier = document.getElementById("earlier");
earlier.addEventListener("click", () => {
  const hidden = document.body.classList.toggle("hide-earlier");
  earlier.setAttribute("aria-pressed", String(hidden));
  earlier.textContent = hidden ? "Show earlier Cartoon" : "Hide earlier Cartoon";
});
const status = document.getElementById("loading");
async function render() {
  const response = await fetch("review-data.json");
  if (!response.ok) throw new Error(`Review data HTTP ${response.status}`);
  const data = await response.json();
  await Promise.all(data.rows.flatMap(row => ["original", "earlier", "revised"].map(async kind => {
    const input = row[kind];
    const canvas = document.querySelector(`canvas[data-key="${row.key}"][data-kind="${kind}"]`);
    const im = new Image();
    im.src = input.url;
    await im.decode();
    const b = input.display_bounds;
    const scale = Math.min((canvas.width - 54) / (b[2] - b[0]), (canvas.height - 48) / (b[3] - b[1]));
    const ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = kind !== "original";
    ctx.drawImage(im, (canvas.width - (b[2] - b[0]) * scale) / 2 - b[0] * scale,
      (canvas.height - (b[3] - b[1]) * scale) / 2 - b[1] * scale, im.width * scale, im.height * scale);
    canvas.setAttribute("data-loaded", "true");
  })));
  status.textContent = `${data.rows.length} of ${data.rows.length} comparisons ready.`;
}
render().catch(error => { status.textContent = `Could not load comparisons: ${error.message}`; });
