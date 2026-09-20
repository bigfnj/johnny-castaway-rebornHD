"use strict";
const status = document.getElementById("loading");
const background = document.getElementById("background");
const images = new Map();
let review;
let sceneMode = "scene";
background.addEventListener("click", () => {
  const dark = document.body.classList.toggle("dark");
  background.setAttribute("aria-pressed", String(dark));
  background.textContent = dark ? "Use light checkerboard" : "Use dark checkerboard";
});
function drawArt(canvas, info, pixelated) {
  const image = images.get(info.url), b = info.alpha8_bounds;
  const scale = Math.min((canvas.width - 40) / (b[2] - b[0]), (canvas.height - 36) / (b[3] - b[1]));
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.imageSmoothingEnabled = !pixelated;
  ctx.drawImage(image, (canvas.width - (b[2] - b[0]) * scale) / 2 - b[0] * scale,
    (canvas.height - (b[3] - b[1]) * scale) / 2 - b[1] * scale, image.width * scale, image.height * scale);
  canvas.dataset.loaded = "true";
}
function drawCrop(canvas, image, box) {
  const ctx = canvas.getContext("2d");
  ctx.imageSmoothingEnabled = false;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(image, box[0], box[1], box[2] - box[0], box[3] - box[1], 0, 0, canvas.width, canvas.height);
  canvas.dataset.loaded = "true";
}
function showFish(frame) {
  const row = review.fish.find(item => item.frame === frame);
  const capture = row[sceneMode];
  const scene = document.getElementById("scene"), image = images.get(capture.url);
  const ctx = scene.getContext("2d");
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(image, 0, 0, scene.width, scene.height);
  const b = capture.fish_bounds, sx = scene.width / image.width, sy = scene.height / image.height;
  ctx.strokeStyle = "#ffde78"; ctx.lineWidth = 3;
  ctx.strokeRect(b[0] * sx - 5, b[1] * sy - 5, (b[2] - b[0]) * sx + 10, (b[3] - b[1]) * sy + 10);
  scene.dataset.loaded = "true";
  drawCrop(document.getElementById("closeup"), image, capture.context_crop);
  drawCrop(document.getElementById("fish-crop"), image, capture.fish_crop);
  drawArt(document.getElementById("diagnostic"), row.diagnostic, true);
  drawArt(document.getElementById("cartoon"), row.cartoon, false);
  document.getElementById("cartoon-link").href = row.cartoon.url;
  document.getElementById("scene-title").textContent = `${sceneMode === "scene" ? "Current environment" : "Original-mode palette"}: fish ${frame}`;
  document.getElementById("fish-label").textContent = `Fish ${frame}`;
  document.getElementById("scene-caption").textContent = capture.caption;
  document.querySelectorAll("button[data-fish]").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.fish === frame)));
  document.body.dataset.fish = frame;
  document.body.dataset.scene = sceneMode;
}
async function render() {
  const response = await fetch("review-data.json");
  if (!response.ok) throw new Error(`Review data HTTP ${response.status}`);
  review = await response.json();
  const inputs = [...review.flag, ...review.flag_reference, ...review.fish.flatMap(row => [row.diagnostic, row.cartoon, row.scene, row.original_scene])];
  await Promise.all([...new Map(inputs.map(info => [info.url, info])).values()].map(async info => {
    const image = new Image(); image.src = info.url; await image.decode(); images.set(info.url, image);
  }));
  [...review.flag, ...review.flag_reference].forEach(info => drawArt(document.getElementById(info.id), info, info.role === "original"));
  document.querySelectorAll("button[data-fish]").forEach(button => button.addEventListener("click", () => showFish(button.dataset.fish)));
  document.querySelectorAll("button[data-scene]").forEach(button => button.addEventListener("click", () => {
    sceneMode = button.dataset.scene;
    document.querySelectorAll("button[data-scene]").forEach(other => other.setAttribute("aria-pressed", String(other === button)));
    showFish(document.body.dataset.fish);
  }));
  showFish("008");
  status.textContent = "Three fish scene views and the flag comparison ready.";
}
render().catch(error => { status.textContent = `Could not load comparisons: ${error.message}`; });
