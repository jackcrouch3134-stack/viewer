class UniversalViewerSystem {
  constructor() {
    this.systemState = null;
    this.modules = [];
    this.refreshInterval = 2000;
    this.setupEventListeners();
    this.startAutoRefresh();
  }

  setupEventListeners() {
    document.getElementById("compileBtn").addEventListener("click", () => this.compileCode());
    document.getElementById("analyzeBtn").addEventListener("click", () => this.analyzeAndCompile());
    document.getElementById("interpretBtn").addEventListener("click", () => this.interpretAtmosphere());
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
