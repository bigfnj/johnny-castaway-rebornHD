"use strict";
const originals = document.getElementById("originals");
originals.addEventListener("click", () => {
  const open = originals.getAttribute("aria-pressed") !== "true";
  document.querySelectorAll("details").forEach(d => { d.open = open; });
  originals.setAttribute("aria-pressed", String(open));
  originals.textContent = open ? "Hide all originals" : "Show all originals";
});
const background = document.getElementById("background");
background.addEventListener("click", () => {
  const dark = document.body.classList.toggle("dark");
  background.setAttribute("aria-pressed", String(dark));
  background.textContent = dark ? "Use light checkerboard" : "Use dark checkerboard";
});
const status = document.getElementById("loading");
async function render() {
  const response = await fetch("review-data.json");
  if (!response.ok) throw new Error(`Review data: HTTP ${response.status}`);
  const data = await response.json();
  await Promise.all(data.assets.map(async row => {
    const canvas = document.querySelector(`canvas[data-key="${row.resource}-${row.frame}"]`);
    const im = new Image();
    im.src = row.url;
    await im.decode();
    const b = row.selected_raw.alpha8_bounds;
    const scale = Math.min((canvas.width - 52) / (b[2] - b[0]), (canvas.height - 44) / (b[3] - b[1]));
    const x = (canvas.width - (b[2] - b[0]) * scale) / 2 - b[0] * scale;
    const y = (canvas.height - (b[3] - b[1]) * scale) / 2 - b[1] * scale;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Position by visible bounds, but draw the entire unmodified RGBA image.
    ctx.drawImage(im, x, y, im.width * scale, im.height * scale);
    canvas.setAttribute("data-loaded", "true");
  }));
  status.textContent = `${data.assets.length} of ${data.assets.length} drawings ready.`;
}
render().catch(error => { status.textContent = `Could not load the review: ${error.message}`; });
