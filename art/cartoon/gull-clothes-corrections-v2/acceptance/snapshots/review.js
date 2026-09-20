"use strict";
const status = document.getElementById("loading");
const background = document.getElementById("background");
background.addEventListener("click", () => {
  const dark = document.body.classList.toggle("dark");
  background.setAttribute("aria-pressed", String(dark));
  background.textContent = dark ? "Use light checkerboard" : "Use dark checkerboard";
});
async function render() {
  const response = await fetch("review-data.json");
  if (!response.ok) throw new Error(`Review data HTTP ${response.status}`);
  const data = await response.json();
  await Promise.all(data.frames.flatMap(row => Object.entries(row.images).map(async ([kind, info]) => {
    const canvas = document.querySelector(`canvas[data-frame="${row.frame}"][data-kind="${kind}"]`);
    const image = new Image();
    image.src = info.url;
    await image.decode();
    const b = info.alpha8_bounds;
    const scale = Math.min((canvas.width - 40) / (b[2] - b[0]), (canvas.height - 36) / (b[3] - b[1]));
    const ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = kind !== "original";
    ctx.drawImage(image, (canvas.width - (b[2] - b[0]) * scale) / 2 - b[0] * scale,
      (canvas.height - (b[3] - b[1]) * scale) / 2 - b[1] * scale, image.width * scale, image.height * scale);
    canvas.dataset.loaded = "true";
  })));
  status.textContent = `${data.frames.length} of ${data.frames.length} comparisons ready.`;
}
render().catch(error => { status.textContent = `Could not load comparisons: ${error.message}`; });
