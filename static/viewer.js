const earthCanvas = document.getElementById('earthCanvas');
const ctx = earthCanvas.getContext('2d');

const signalBar = document.getElementById('signalBar');
const compileStatus = document.getElementById('compileStatus');
const atmosphereStatus = document.getElementById('atmosphereStatus');
const creatureStatus = document.getElementById('creatureStatus');
const signalStatus = document.getElementById('signalStatus');

function setStatusText() {
  compileStatus.textContent = 'Compiler: READY';
  atmosphereStatus.textContent = 'Atmosphere: SCANNING';
  creatureStatus.textContent = 'Creatures: TRACKED';
  signalStatus.textContent = 'Signal: RECEIVING';
}

function drawEarth() {
  const { width, height } = earthCanvas;
  ctx.clearRect(0, 0, width, height);

  const gradient = ctx.createRadialGradient(width * 0.5, height * 0.45, 30, width * 0.5, height * 0.5, width * 0.42);
  gradient.addColorStop(0, '#7fe7ff');
  gradient.addColorStop(0.45, '#3579d8');
  gradient.addColorStop(0.7, '#1a4b88');
  gradient.addColorStop(1, '#071b2b');
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(width * 0.5, height * 0.5, width * 0.28, 0, Math.PI * 2);
  ctx.fill();

  ctx.strokeStyle = 'rgba(255,255,255,0.3)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(width * 0.5, height * 0.5, width * 0.28, 0, Math.PI * 2);
  ctx.stroke();

  for (let i = 0; i < 14; i++) {
    const offset = i * 26;
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.beginPath();
    ctx.arc(width * 0.5, height * 0.5, width * 0.2 + offset * 0.3, 0, Math.PI * 2);
    ctx.stroke();
  }
}

function drawLayerCanvas(canvasId, color, label, value) {
  const canvas = document.getElementById(canvasId);
  const c = canvas.getContext('2d');
  const { width, height } = canvas;
  c.clearRect(0, 0, width, height);

  c.fillStyle = 'rgba(255,255,255,0.04)';
  c.fillRect(0, 0, width, height);

  c.fillStyle = color;
  c.fillRect(12, height * 0.54, width - 24, height * 0.18);

  c.fillStyle = 'rgba(255,255,255,0.7)';
  c.font = '12px sans-serif';
  c.fillText(label, 14, 18);
  c.fillText(`${value}%`, width - 42, 18);
}

function drawTrackingCanvas(canvasId, color) {
  const canvas = document.getElementById(canvasId);
  const c = canvas.getContext('2d');
  const { width, height } = canvas;
  c.clearRect(0, 0, width, height);

  c.strokeStyle = 'rgba(255,255,255,0.12)';
  c.beginPath();
  c.moveTo(0, height / 2);
  c.lineTo(width, height / 2);
  c.stroke();

  c.fillStyle = color;
  c.beginPath();
  c.arc(width * 0.22, height * 0.58, 7, 0, Math.PI * 2);
  c.arc(width * 0.45, height * 0.38, 7, 0, Math.PI * 2);
  c.arc(width * 0.72, height * 0.52, 7, 0, Math.PI * 2);
  c.fill();
}

function updateSignalMeter() {
  const signal = 92;
  signalBar.style.width = `${signal}%`;
  signalBar.title = `${signal}% signal quality`;
  document.getElementById('signalQuality').textContent = `${signal}%`;
}

function animate() {
  drawEarth();
  drawLayerCanvas('tropoCanvas', '#6fe7ff', 'Troposphere', 72);
  drawLayerCanvas('stratCanvas', '#ffd166', 'Stratosphere', 85);
  drawLayerCanvas('mesoCanvas', '#ff8fd3', 'Mesosphere', 18);
  drawLayerCanvas('thermoCanvas', '#7ef0bd', 'Thermosphere', 45);
  drawLayerCanvas('exoCanvas', '#9fb7ff', 'Exosphere', 88);

  drawTrackingCanvas('monarchMap', '#ff8fd3');
  drawTrackingCanvas('whaleMap', '#7ef0bd');
  drawTrackingCanvas('elephantMap', '#ffd166');

  updateSignalMeter();
  requestAnimationFrame(animate);
}

setStatusText();
requestAnimationFrame(animate);

const buttons = document.querySelectorAll('.control-btn');
buttons.forEach((button) => {
  button.addEventListener('click', () => {
    compileStatus.textContent = 'Compiler: PROCESSING';
    atmosphereStatus.textContent = 'Atmosphere: UPDATED';
    creatureStatus.textContent = 'Creatures: ACTIVE';
    signalStatus.textContent = 'Signal: LOCKED';
  });
});
