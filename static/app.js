class UniversalViewerSystem {
  constructor() {
    this.systemState = null;
    this.modules = [];
    this.refreshInterval = 2000;
    this.camera = {
      x: 0,
      y: 0,
      targetX: 0,
      targetY: 0,
      smoothing: 0.12,
      maxShift: 22,
    };
    this.awarenessQuestions = [
      "Is the atmospheric drift consistent with projected flight lanes?",
      "Should the observer prioritize signal stability over visual noise?",
      "Do we maintain enough separation from the thermal anomaly to proceed?",
      "What level of confidence remains in the live telemetry feed?",
      "Is the scan pattern sufficiently calm to continue tracking?",
    ];
    this.currentQuestionIndex = 0;
    this.setupEventListeners();
    this.setupCameraDrive();
    this.startAwarenessLoop();
    this.startAutoRefresh();
  }

  setupEventListeners() {
    document.getElementById("compileBtn").addEventListener("click", () => this.compileCode());
    document.getElementById("analyzeBtn").addEventListener("click", () => this.analyzeAndCompile());
    document.getElementById("interpretBtn").addEventListener("click", () => this.interpretAtmosphere());

    const awarenessBtn = document.getElementById("awarenessAnswerBtn");
    if (awarenessBtn) {
      awarenessBtn.addEventListener("click", () => this.answerAwarenessPrompt());
    }
  }

  startAwarenessLoop() {
    const questionEl = document.getElementById("awarenessQuestion");
    const mindStatusEl = document.getElementById("mindStatus");

    if (!questionEl || !mindStatusEl) {
      return;
    }

    const updateAwareness = () => {
      const nextQuestion = this.awarenessQuestions[this.currentQuestionIndex % this.awarenessQuestions.length];
      questionEl.textContent = nextQuestion;
      mindStatusEl.textContent = "Disposition: SERIOUS";
      this.currentQuestionIndex += 1;
    };

    updateAwareness();
    setInterval(updateAwareness, 9000);
  }

  answerAwarenessPrompt() {
    const questionEl = document.getElementById("awarenessQuestion");
    const mindStatusEl = document.getElementById("mindStatus");
    if (!questionEl || !mindStatusEl) {
      return;
    }

    mindStatusEl.textContent = "Disposition: FOCUSED";
    questionEl.textContent = "Acknowledged. Continuing the scan with measured discipline.";
    setTimeout(() => {
      this.currentQuestionIndex = (this.currentQuestionIndex + 1) % this.awarenessQuestions.length;
      questionEl.textContent = this.awarenessQuestions[this.currentQuestionIndex];
      mindStatusEl.textContent = "Disposition: SERIOUS";
    }, 1800);
  }

  setupCameraDrive() {
    this.cameraEl = document.querySelector(".pov-avatar");
    if (!this.cameraEl) {
      return;
    }

    const motionSignal = {
      x: 0,
      y: 0,
    };

    const updateTarget = () => {
      const driftX = Math.sin(Date.now() / 1100) * this.camera.maxShift;
      const driftY = Math.cos(Date.now() / 1400) * (this.camera.maxShift * 0.6);

      this.camera.targetX = driftX;
      this.camera.targetY = driftY;
      motionSignal.x = driftX;
      motionSignal.y = driftY;
    };

    const animateCamera = () => {
      updateTarget();
      this.camera.x += (this.camera.targetX - this.camera.x) * this.camera.smoothing;
      this.camera.y += (this.camera.targetY - this.camera.y) * this.camera.smoothing;
      this.cameraEl.style.setProperty("--camera-x", `${this.camera.x}px`);
      this.cameraEl.style.setProperty("--camera-y", `${this.camera.y}px`);
      requestAnimationFrame(animateCamera);
    };

    requestAnimationFrame(animateCamera);
  }

  async updateStatus() {
    try {
      const response = await fetch("/api/state");
      const state = await response.json();

      const backend = state.backend || {};
      const frontend = state.frontend || {};
      const ui = state.ui || {};
      const numbers = state.known_numbers || {};

      const signalQuality = numbers.signal_quality || frontend.signal_quality || 92;
      const altitude = numbers.altitude || 800;
      const coverage = numbers.coverage || 85;

      document.getElementById("compilationCount").textContent = backend.compilations || 0;
      document.getElementById("updateCount").textContent = backend.updates || 0;
      document.getElementById("versionDisplay").textContent = backend.version || "1.0.0";
      document.getElementById("moduleCount").textContent = backend.modules_count || 0;

      document.getElementById("currentPanel").textContent = frontend.panel || "Earth";
      document.getElementById("zoomLevel").textContent = `${(frontend.zoom || 1).toFixed(1)}x`;
      document.getElementById("signalQuality").textContent = `${signalQuality}%`;
      document.getElementById("altitudeValue").textContent = `${altitude} km`;
      document.getElementById("coverageValue").textContent = `${coverage}%`;
      document.getElementById("currentMode").textContent = "First Person";
      document.getElementById("observerStatus").textContent = "ACTIVE";
      document.getElementById("environmentStatus").textContent = signalQuality > 90 ? "Clear View" : "Scanning";
      document.getElementById("focusName").textContent = "Observer";

      document.getElementById("systemStatus").innerHTML = '<span class="pulse"></span> ONLINE';
      document.getElementById("backendStatus").textContent = backend.status || "ONLINE";
      document.getElementById("frontendStatus").textContent = frontend.status || "ONLINE";
      document.getElementById("userModeStatus").textContent = "OBSERVING";

      if (document.getElementById("gestureCount")) {
        document.getElementById("gestureCount").textContent = ui.gesture_history || 0;
      }
      if (document.getElementById("alertCount")) {
        document.getElementById("alertCount").textContent = ui.pending_alerts || 0;
      }
      if (document.getElementById("feedbackCount")) {
        document.getElementById("feedbackCount").textContent = (ui.pending_alerts || 0) + (ui.gesture_history || 0);
      }
      if (document.getElementById("safeMode")) {
        document.getElementById("safeMode").textContent = (frontend.safe_mode === true || ui.safe_mode === true) ? "ON" : "OFF";
      }
    } catch (err) {
      console.error("Status update failed:", err);
    }
  }

  async compileCode() {
    const code = document.getElementById("codeInput").value || "# Sample code\nprint('Compiling')";

    try {
      const response = await fetch("/api/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code })
      });

      const result = await response.json();
      const m = result.result || {};
      document.getElementById("compilerStatus").textContent = `✓ Compiled Module ${m.module_id || 'unknown'} (v${m.version || '1.0.0'})`;
      this.updateStatus();
    } catch (err) {
      document.getElementById("compilerStatus").textContent = "✕ Compile failed";
    }
  }

  async analyzeAndCompile() {
    const code = document.getElementById("codeInput").value;
    if (!code) {
      document.getElementById("compilerStatus").textContent = "Please add code to analyze.";
      return;
    }

    await this.compileCode();
  }

  async interpretAtmosphere() {
    document.getElementById("atmosphereStatus").textContent = "Interpreting...";
    setTimeout(() => {
      document.getElementById("atmosphereStatus").textContent = "✓ Complete";
    }, 800);
  }

  async refreshModules() {
    try {
      const response = await fetch("/api/state");
      const state = await response.json();
      const backend = state.backend || {};
      const list = document.getElementById("recentModules");
      const modules = backend.modules || [];

      if (!modules || modules.length === 0) {
        list.innerHTML = '<div class="activity-item">No compiled modules yet.</div>';
        return;
      }

      list.innerHTML = modules.slice(0, 5).map((m) => `
        <div class="activity-item">
          <span class="dot"></span>
          ${m.intent || 'unknown'} • v${m.version || '1.0.0'} • ${m.module_id || 'n/a'}
        </div>
      `).join('');
    } catch (err) {
      console.error("Module refresh failed:", err);
    }
  }

  startAutoRefresh() {
    setInterval(() => {
      this.updateStatus();
      this.refreshModules();
    }, this.refreshInterval);
    this.updateStatus();
    this.refreshModules();
  }
}

const viewer = new UniversalViewerSystem();
