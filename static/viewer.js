class LiveEarthViewer {
  constructor() {
    this.rotation = 0;
    this.zoom = 1.0;
    this.layersVisible = true;
    this.signalQuality = 92;
    this.canvas = document.getElementById("earthCanvas");
    this.setupControls();
    this.drawEarth();
    this.drawLayerCanvases();
    this.drawTrackingMaps();
    this.animate();
    this.startTelemetry();
  }

  setupControls() {
    document.getElementById("zoomIn").addEventListener("click", () => this.setZoom(this.zoom + 0.1));
    document.getElementById("zoomOut").addEventListener("click", () => this.setZoom(this.zoom - 0.1));
    document.getElementById("rotate").addEventListener("click", () => {
      this.rotation += 30;
      this.drawEarth();
    });
    document.getElementById("toggleLayers").addEventListener("click", () => {
      this.layersVisible = !this.layersVisible;
      document.querySelectorAll(".layer-canvas").forEach((c) => {
        c.style.visibility = this.layersVisible ? "visible" : "hidden";
      });
    });
  }

  setZoom(level) {
    this.zoom = Math.max(0.5, Math.min(level, 3.0));
    this.canvas.style.transform = `scale(${this.zoom})`;
    this.canvas.style.transition = "transform 0.25s ease";
    document.getElementById("altitudeInfo").textContent = `Altitude: ${Math.round(800 / this.zoom)} km`;
  }

  drawEarth() {
    const ctx = this.canvas.getContext("2d");
    const { width, height } = this.canvas;
    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(cx, cy) - 60;

    ctx.clearRect(0, 0, width, height);

    // Starfield
    ctx.fillStyle = "#ffffff";
    for (let i = 0; i < 90; i++) {
      const x = (i * 97) % width;
      const y = (i * 53) % height;
      ctx.globalAlpha = 0.2 + ((i * 7) % 10) / 14;
      ctx.fillRect(x, y, 1.4, 1.4);
    }
    ctx.globalAlpha = 1;

    // Earth disc
    const gradient = ctx.createRadialGradient(cx - radius * 0.3, cy - radius * 0.3, radius * 0.1, cx, cy, radius);
    gradient.addColorStop(0, "#7fd8ff");
    gradient.addColorStop(0.5, "#2b73d7");
    gradient.addColorStop(1, "#0d2242");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.fill();

    // Continents rotating
    ctx.fillStyle = "rgba(88, 240, 155, 0.75)";
    for (let i = 0; i < 7; i++) {
      const angle = ((360 / 7) * i + this.rotation) * (Math.PI / 180);
      const px = cx + Math.cos(angle) * radius * 0.5;
      const py = cy + Math.sin(angle * 1.3) * radius * 0.55;
      ctx.beginPath();
      ctx.ellipse(px, py, radius * 0.2, radius * 0.12, angle, 0, Math.PI * 2);
      ctx.fill();
    }

    // Atmosphere rim
    ctx.strokeStyle = "rgba(94, 210, 255, 0.5)";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(cx, cy, radius + 6, 0, Math.PI * 2);
    ctx.stroke();

    // Orbit path
    ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.ellipse(cx, cy, radius + 42, radius + 18, -0.4, 0, Math.PI * 2);
    ctx.stroke();

    // Satellite
    const satAngle = this.rotation * (Math.PI / 180) * 2;
    const sx = cx + Math.cos(satAngle) * (radius + 42);
    const sy = cy + Math.sin(satAngle) * (radius + 18) * 0.9;
    ctx.fillStyle = "#ffd166";
    ctx.fillRect(sx - 4, sy - 4, 8, 8);
  }

  drawLayerCanvases() {
    const layers = [
      { id: "tropoCanvas", color: "#5ed2ff" },
      { id: "stratCanvas", color: "#ffd166" },
      { id: "mesoCanvas", color: "#ef8354" },
      { id: "thermoCanvas", color: "#b388ff" },
      { id: "exoCanvas", color: "#8fb6c9" },
    ];
    layers.forEach((layer, index) => {
      const canvas = document.getElementById(layer.id);
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      const { width, height } = canvas;
      ctx.clearRect(0, 0, width, height);
      ctx.strokeStyle = layer.color;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      for (let x = 0; x <= width; x += 3) {
        const y = height / 2 + Math.sin((x / width) * Math.PI * (2 + index) + index) * (height / 3.5);
        x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.stroke();
    });
  }

  drawTrackingMaps() {
    const tracks = [
      { id: "monarchMap", color: "#e277b3" },
      { id: "whaleMap", color: "#5ed2ff" },
      { id: "elephantMap", color: "#ffd166" },
    ];
    tracks.forEach((track, index) => {
      const canvas = document.getElementById(track.id);
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      const { width, height } = canvas;
      ctx.clearRect(0, 0, width, height);
      ctx.strokeStyle = track.color;
      ctx.lineWidth = 1.5;
      ctx.setLineDash([5, 4]);
      ctx.beginPath();
      for (let x = 0; x <= width; x += 4) {
        const y = height / 2 + Math.sin((x / width) * Math.PI * 2.5 + index * 1.2) * (height / 3);
        x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.setLineDash([]);
      // Current position marker
      const markerX = (Date.now() / 50 + index * 40) % width;
      const markerY = height / 2 + Math.sin((markerX / width) * Math.PI * 2.5 + index * 1.2) * (height / 3);
      ctx.fillStyle = track.color;
      ctx.beginPath();
      ctx.arc(markerX, markerY, 3.5, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  startTelemetry() {
    setInterval(() => {
      this.signalQuality = 88 + Math.floor(Math.random() * 12);
      document.getElementById("signalQuality").textContent = `${this.signalQuality}%`;
      document.getElementById("signalBar").style.width = `${this.signalQuality}%`;
      document.getElementById("signalInfo").textContent = "Signal: 137.1 MHz";
    }, 3000);
  }

  animate() {
    this.rotation += 0.15;
    this.drawEarth();
    if (Math.floor(this.rotation) % 2 === 0) {
      this.drawTrackingMaps();
    }
    requestAnimationFrame(() => this.animate());
  }
}

const liveViewer = new LiveEarthViewer();
