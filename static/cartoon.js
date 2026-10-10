const globeCanvas = document.getElementById('globeCanvas');
const ctx = globeCanvas.getContext('2d');

function drawHappyEarth() {
  const { width, height } = globeCanvas;
  ctx.clearRect(0, 0, width, height);

  const gradient = ctx.createRadialGradient(width * 0.5, height * 0.45, 30, width * 0.5, height * 0.5, width * 0.48);
  gradient.addColorStop(0, '#7be7ff');
  gradient.addColorStop(0.5, '#48a6ff');
  gradient.addColorStop(0.75, '#2d71d8');
  gradient.addColorStop(1, '#1b3d7a');

  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(width / 2, height / 2, width * 0.38, 0, Math.PI * 2);
  ctx.fill();

  ctx.strokeStyle = 'rgba(255,255,255,0.35)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(width / 2, height / 2, width * 0.38, 0, Math.PI * 2);
  ctx.stroke();

  ctx.fillStyle = 'rgba(255,255,255,0.18)';
  for (let i = 0; i < 8; i++) {
    const x = width * (0.2 + i * 0.08);
    const y = height * (0.25 + (i % 2) * 0.14);
    ctx.beginPath();
    ctx.arc(x, y, 18 + i * 3, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.fillStyle = '#ffeb8a';
  ctx.beginPath();
  ctx.arc(width * 0.62, height * 0.42, 18, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#1f3351';
  ctx.beginPath();
  ctx.arc(width * 0.54, height * 0.44, 6, 0, Math.PI * 2);
  ctx.arc(width * 0.69, height * 0.44, 6, 0, Math.PI * 2);
  ctx.fill();

  ctx.beginPath();
  ctx.arc(width * 0.62, height * 0.52, 12, 0, Math.PI);
  ctx.strokeStyle = '#1f3351';
  ctx.lineWidth = 3;
  ctx.stroke();
}

function drawTrack(canvasId, color, points) {
  const canvas = document.getElementById(canvasId);
  const c = canvas.getContext('2d');
  const { width, height } = canvas;
  c.clearRect(0, 0, width, height);

  c.strokeStyle = color;
  c.lineWidth = 3;
  c.beginPath();
  points.forEach((point, index) => {
    const x = point[0] * width;
    const y = point[1] * height;
    if (index === 0) c.moveTo(x, y);
    else c.lineTo(x, y);
  });
  c.stroke();
}

function populateData() {
  document.getElementById('locationDisplay').textContent = 'Location: Earth!';
  document.getElementById('tempDisplay').textContent = 'Temp: Varies!';
  document.getElementById('signalDisplay').textContent = 'Signal: BEEP BOOP!';
  document.getElementById('qualityDisplay').textContent = '92%';
}

setInterval(() => {
  drawHappyEarth();
  populateData();
  drawTrack('butterflyTrack', '#ff7cb8', [[0.1, 0.7],[0.3,0.4],[0.55,0.6],[0.8,0.5],[0.95,0.7]]);
  drawTrack('whaleTrack', '#4ac5ff', [[0.1,0.5],[0.3,0.6],[0.5,0.4],[0.7,0.55],[0.9,0.45]]);
  drawTrack('elephantTrack', '#ffbf69', [[0.2,0.7],[0.35,0.5],[0.6,0.5],[0.8,0.65],[0.96,0.5]]);
  drawTrack('turtleTrack', '#7adf9d', [[0.1,0.6],[0.35,0.5],[0.62,0.6],[0.82,0.55],[0.95,0.65]]);
  drawTrack('ternTrack', '#9d7cff', [[0.2,0.6],[0.45,0.35],[0.7,0.45],[0.9,0.62]]);
  drawTrack('salmonTrack', '#5de2d2', [[0.1,0.5],[0.25,0.7],[0.45,0.45],[0.7,0.6],[0.92,0.52]]);
}, 1600);

drawHappyEarth();
populateData();
