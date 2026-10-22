class CartoonEarthViewer {
  constructor() {
    this.rotation = 0;
    this.zoom = 1.0;
    this.animating = true;
    this.globeCanvas = document.getElementById("globeCanvas");
    this.setupControls();
    this.drawGlobe();
    this.drawTracks();
    this.animate();
  }

  setupControls() {
    document.getElementById("rotateBtn").addEventListener("click", () => {
      this.rotation += 45;
      this.drawGlobe();
    });
    document.getElementById("zoomInBtn").addEventListener("click", () => this.setZoom(this.zoom + 0.2));
    document.getElementById("zoomOutBtn").addEventListener("click", () => this.setZoom(this.zoom - 0.2));
    document.getElementById("refreshBtn").addEventListener("click", () => this.refresh());
    document.getElementById("animateBtn").addEventListener("click", (event) => {
      this.animating = !this.animating;
      event.target.textContent = this.animating ? "▶️ ANIMATE" : "⏸️ PAUSED";
    });
  }

  setZoom(level) {
    this.zoom = Math.max(0.6, Math.min(level, 2.0));
    this.globeCanvas.style.transform = `scale(${this.zoom})`;
    this.globeCanvas.style.transition = "transform 0.25s ease";
  }

  drawGlobe() {
    const ctx = this.globeCanvas.getContext("2d");
    const { width, height } = this.globeCanvas;
    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(cx, cy) - 20;

    ctx.clearRect(0, 0, width, height);

    // Ocean
    ctx.fillStyle = "#3b9be0";
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.fill();

    // Wobbly cartoon continents rotating with the globe
    ctx.fillStyle = "#7ed491";
    const continents = 6;
    for (let i = 0; i < continents; i++) {
      const angle = ((360 / continents) * i + this.rotation) * (Math.PI / 180);
      const px = cx + Math.cos(angle) * radius * 0.45;
      const py = cy + Math.sin(angle * 1.4) * radius * 0.5;
      ctx.beginPath();
      ctx.ellipse(px, py, radius * 0.22, radius * 0.14, angle, 0, Math.PI * 2);
      ctx.fill();
    }

    // Cloud swirl
    ctx.strokeStyle = "rgba(255,255,255,0.85)";
    ctx.lineWidth = 5;
    ctx.lineCap = "round";
    for (let i = 0; i < 4; i++) {
      const y = cy - radius * 0.5 + i * radius * 0.33;
      ctx.beginPath();
      ctx.arc(cx, y, radius * 0.5, Math.PI * 0.15, Math.PI * 0.85);
      ctx.stroke();
    }

    // Smiley terminator line for charm
    ctx.strokeStyle = "#23405e";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.stroke();
  }

  drawTracks() {
    const ids = ["butterflyTrack", "whaleTrack", "elephantTrack", "turtleTrack", "ternTrack", "salmonTrack"];
    ids.forEach((id, index) => {
      const canvas = document.getElementById(id);
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      const { width, height } = canvas;
      ctx.clearRect(0, 0, width, height);
      ctx.strokeStyle = ["#e277b3", "#3b9be0", "#c98a4b", "#2e9e5b", "#e2b13b", "#e2633b"][index % 6];
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 3]);
      ctx.beginPath();
      for (let x = 0; x <= width; x += 4) {
        const y = height / 2 + Math.sin((x / width) * Math.PI * 2 + index) * (height / 3);
        x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.setLineDash([]);
    });
  }

  refresh() {
    const quality = 85 + Math.floor(Math.random() * 15);
    document.getElementById("qualityDisplay").textContent = `${quality}%`;
    document.getElementById("locationDisplay").textContent = "Location: Earth!";
    document.getElementById("signalDisplay").textContent = "Signal: BEEP BOOP!";
    this.drawTracks();
  }

  animate() {
    if (this.animating) {
      this.rotation += 0.4;
      this.drawGlobe();
    }
    requestAnimationFrame(() => this.animate());
  }
}

const cartoonViewer = new CartoonEarthViewer();
