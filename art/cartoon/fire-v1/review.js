'use strict';
const byId = id => document.getElementById(id);
const images = new Map();
let data, playing = true, phaseIndex = 0, elapsed = 0, lastTime = null;
const load = url => new Promise((resolve, reject) => {
  const im = new Image();
  im.onload = () => { images.set(url, im); resolve(); };
  im.onerror = () => reject(new Error(`Could not load ${url}`));
  im.src = url;
});
const cycle = () => data.cycles.find(s => s.id === byId('effect').value);
function clear(canvas) { const ctx = canvas.getContext('2d'); ctx.clearRect(0,0,canvas.width,canvas.height); return ctx; }
function drawThumbnail(canvas) {
  const a = data.assets[Number(canvas.dataset.frame)], b = a.selected_raw.alpha8_bounds;
  const ctx = clear(canvas), w=b[2]-b[0], h=b[3]-b[1], scale=Math.min((canvas.width-32)/w,(canvas.height-32)/h);
  ctx.drawImage(images.get(a.raw_url),(canvas.width-w*scale)/2-b[0]*scale,(canvas.height-h*scale)/2-b[1]*scale,a.selected_raw.canvas[0]*scale,a.selected_raw.canvas[1]*scale);
}
function render() {
  if (!data || !images.has(data.assets[0].raw_url)) return;
  const s=cycle(), phase=s.phases[phaseIndex], [cx,cy,cw,ch]=data.crop;
  for (const kind of ['source','candidate']) {
    const canvas=byId(kind), ctx=clear(canvas), z=canvas.width/cw;
    ctx.imageSmoothingEnabled=kind !== 'source';
    for (const d of phase.draws) {
      if (!byId('logs').checked && d.frame===0) continue;
      const a=data.assets[d.frame];
      if (kind==='source') {
        ctx.drawImage(images.get(a.original_url),(d.x-cx)*z,(d.y-cy)*z,a.original.canvas[0]*z,a.original.canvas[1]*z);
      } else {
        const b=a.selected_raw.alpha8_bounds, o=a.original.alpha_bounds;
        const w=b[2]-b[0], h=b[3]-b[1], scale=Math.min((o[2]-o[0])/w,(o[3]-o[1])/h);
        const x=d.x+o[0]+((o[2]-o[0])-w*scale)/2, y=d.y+o[3]-h*scale;
        ctx.drawImage(images.get(a.raw_url),(x-cx-b[0]*scale)*z,(y-cy-b[1]*scale)*z,a.selected_raw.canvas[0]*scale*z,a.selected_raw.canvas[1]*scale*z);
      }
    }
  }
  const effectFrames=phase.draws.filter(d=>d.frame!==0).map(d=>String(d.frame).padStart(3,'0')).join(', ');
  byId('status').textContent=`${s.description} | phase ${phaseIndex+1} / ${s.phases.length} | FIRE1 ${effectFrames} | ${playing?'Playing':'Paused'}`;
}
function setPlaying(value) { playing=value; elapsed=0; byId('play').textContent=playing?'Pause':'Play'; render(); }
function tick(now) {
  if (lastTime!==null && playing && data) {
    elapsed+=Math.min(now-lastTime,250)*Number(byId('speed').value);
    const s=cycle();
    while(elapsed>=s.phases[phaseIndex].nominal_duration_ms) {
      elapsed-=s.phases[phaseIndex].nominal_duration_ms;
      phaseIndex=(phaseIndex+1)%s.phases.length;
    }
    render();
  }
  lastTime=now; requestAnimationFrame(tick);
}
byId('play').addEventListener('click',()=>setPlaying(!playing));
byId('previous').addEventListener('click',()=>{if(!data)return;setPlaying(false);phaseIndex=(phaseIndex+cycle().phases.length-1)%cycle().phases.length;render();});
byId('next').addEventListener('click',()=>{if(!data)return;setPlaying(false);phaseIndex=(phaseIndex+1)%cycle().phases.length;render();});
byId('effect').addEventListener('change',()=>{phaseIndex=0;elapsed=0;render();});
byId('logs').addEventListener('change',render);
byId('originals').addEventListener('click',()=>{
  const b=byId('originals'),open=b.getAttribute('aria-pressed')!=='true';
  document.querySelectorAll('details').forEach(d=>d.open=open);b.setAttribute('aria-pressed',String(open));b.textContent=open?'Hide all originals':'Show all originals';
});
byId('background').addEventListener('click',()=>{
  const dark=document.body.classList.toggle('dark'),b=byId('background');b.setAttribute('aria-pressed',String(dark));b.textContent=dark?'Use light checkerboard':'Use dark checkerboard';
});
document.addEventListener('visibilitychange',()=>{lastTime=null;});
fetch('review-data.json').then(r=>{if(!r.ok)throw new Error('Could not load review data');return r.json();}).then(async d=>{
  await Promise.all(d.assets.flatMap(a=>[a.raw_url,a.original_url]).map(load));
  data=d; document.querySelectorAll('.thumb').forEach(drawThumbnail);
  byId('load-status').textContent='Ready: all 28 Cartoon drawings and 28 original references loaded.';
  byId('play').disabled=false;render();requestAnimationFrame(tick);
}).catch(e=>{byId('load-status').textContent=e.message;byId('status').textContent='Preview could not load.';});
