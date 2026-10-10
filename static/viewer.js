class ImaginationViewer {
  constructor() {
    this.frames = [
      {
        id: 'earth-core',
        title: 'Earth Core',
        summary: 'Planetary focus with global atmospheric continuity and live orbital awareness.',
        narrative: 'The system locks onto the living planet: oceanic motion, atmospheric rhythm, and tectonic pulse converge into a single coherent Earth-intent.'
      },
      {
        id: 'atmosphere-surge',
        title: 'Atmosphere Surge',
        summary: 'A layered atmospheric focus with cloud formation and thermal movement in motion.',
        narrative: 'The atmosphere rises into view as a living membrane, guiding the intelligence toward cloud, wind, and signal logic in continuous exchange.'
      },
      {
        id: 'biosphere-shift',
        title: 'Biosphere Shift',
        summary: 'Migration, habitat, and life-pattern awareness become the central attention field.',
        narrative: 'Intent drifts toward living systems, where species movement and environmental cues become the primary frame of meaning.'
      },
      {
        id: 'signal-echo',
        title: 'Signal Echo',
        summary: 'The imagery narrows to transmission fidelity, resonance, and directional clarity.',
        narrative: 'The channel becomes a listening surface, where signal strength and pattern recognition guide the imagination toward precise focus.'
      }
    ];

    this.activeFrameIndex = 0;
    this.canvas = document.getElementById('earthCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.rotation = 0;

    this.bindUI();
    this.renderFrameBank();
    this.renderFocusNarrative();
    this.drawEarth();
    this.startLoop();
  }

  bindUI() {
    document.getElementById('toggleLayers').addEventListener('click', () => this.toggleLayerDisplay());
    document.getElementById('zoomIn').addEventListener('click', () => this.zoom(1.1));
    document.getElementById('zoomOut').addEventListener('click', () => this.zoom(0.9));
    document.getElementById('rotate').addEventListener('click', () => this.rotateScene());
    document.getElementById('focusNext').addEventListener('click', () => this.advanceFocus());
  }

  renderFrameBank() {
    const frameBank = document.getElementById('frameBank');
    frameBank.innerHTML = this.frames.map((frame, index) => `
      <button class="frame-card ${index === this.activeFrameIndex ? 'active' : ''}" data-index="${index}">
        <h3>${frame.title}</h3>
        <p>${frame.summary}</p>
      </button>
    `).join('');

    frameBank.querySelectorAll('.frame-card').forEach((button) => {
      button.addEventListener('click', () => {
        this.activeFrameIndex = Number(button.dataset.index);
        this.renderFrameBank();
        this.renderFocusNarrative();
      });
    });
  }

  renderFocusNarrative() {
    const frame = this.frames[this.activeFrameIndex];
    const focusTitle = document.getElementById('focusTitle');
    const focusNarrative = document.getElementById('focusNarrative');
    focusTitle.textContent = frame.title;
    focusNarrative.textContent = frame.narrative;
  }

  toggleLayerDisplay() {
    const elements = document.querySelectorAll('.layer-display');
    elements.forEach((el) => {
      const hidden = el.style.opacity === '0.25';
      el.style.opacity = hidden ? '1' : '0.25';
    });
  }

  zoom(scale) {
    const currentScale = Number(this.canvas.dataset.scale || '1');
    const next = Math.min(1.9, Math.max(0.8, currentScale * scale));
    this.canvas.dataset.scale = String(next);
    this.drawEarth();
  }

  rotateScene() {
    this.rotation = (this.rotation + 0.35) % (Math.PI * 2);
    this.drawEarth();
  }

  drawEarth() {
    const ctx = this.ctx;
    const { width, height } = this.canvas;
    const scale = Number(this.canvas.dataset.scale || '1');

    ctx.clearRect(0, 0, width, height);

    const gradient = ctx.createRadialGradient(
      width * 0.5,
      height * 0.5,
      25,
      width * 0.5,
      height * 0.5,
      width * 0.5
    );
    gradient.addColorStop(0, 'rgba(124, 213, 255, 0.9)');
    gradient.addColorStop(0.2, 'rgba(62, 112, 185, 0.8)');
    gradient.addColorStop(0.6, 'rgba(24, 61, 93, 0.9)');
    gradient.addColorStop(1, 'rgba(4, 11, 16, 1)');

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(width, height) * 0.28 * scale;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(this.rotation);

    ctx.beginPath();
    ctx.fillStyle = '#63d6ff';
    ctx.arc(0, 0, radius, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.fillStyle = 'rgba(34, 154, 92, 0.9)';
    ctx.arc(0, 0, radius * 0.9, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.fillStyle = 'rgba(25, 118, 161, 0.7)';
    ctx.arc(0, 0, radius * 0.73, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.strokeStyle = 'rgba(167, 232, 255, 0.6)';
    ctx.lineWidth = 2;
    for (let i = 0; i < 8; i++) {
      ctx.beginPath();
      ctx.ellipse(0, 0, radius * (0.72 + i * 0.12), radius * 0.38, this.rotation, 0, Math.PI * 2);
      ctx.stroke();
    }

    ctx.restore();

    const currentFrame = this.frames[this.activeFrameIndex];
    const frameText = currentFrame.title.toUpperCase();
    ctx.fillStyle = 'rgba(255,255,255,0.8)';
    ctx.font = '600 20px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(frameText, width / 2, height - 38);
  }

  advanceFocus() {
    this.activeFrameIndex = (this.activeFrameIndex + 1) % this.frames.length;
    this.renderFrameBank();
    this.renderFocusNarrative();
    this.drawEarth();
  }

  startLoop() {
    setInterval(() => {
      this.advanceFocus();
    }, 5000);
  }
}

new ImaginationViewer();
