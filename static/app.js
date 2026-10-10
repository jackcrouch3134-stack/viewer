class UniversalViewerSystem {
  constructor() {
    this.systemState = null;
    this.modules = [];
    this.refreshInterval = 2000;
    this.setupEventListeners();
    this.startAutoRefresh();
  }

  setupEventListeners() {
    const compileBtn = document.getElementById("compileBtn");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const interpretBtn = document.getElementById("interpretBtn");

    compileBtn.addEventListener("click", () => this.compileCode());
    analyzeBtn.addEventListener("click", () => this.analyzeAndCompile());
    interpretBtn.addEventListener("click", () => this.interpretAtmosphere());
  }

  async fetchJson(url, options = {}) {
    const response = await fetch(url, options);
    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(payload.error || "Request failed");
    }

    return payload;
  }

  async updateStatus() {
    try {
      const state = await this.fetchJson("/api/state");
      const backend = state.backend || {};
      const frontend = state.frontend || {};
      const ui = state.ui || {};
      const system = state.system || {};

      document.getElementById("compilationCount").textContent = backend.compilations || 0;
      document.getElementById("updateCount").textContent = backend.updates || 0;
      document.getElementById("versionDisplay").textContent = backend.version || "1.0.0";
      document.getElementById("moduleCount").textContent = backend.modules_count || 0;

      document.getElementById("currentPanel").textContent = frontend.panel || "Earth";
      document.getElementById("zoomLevel").textContent = `${Number(frontend.zoom || 1).toFixed(1)}x`;
      document.getElementById("signalQuality").textContent = `${frontend.signal_quality || 92}%`;

      document.getElementById("gestureCount").textContent = ui.gesture_history || 0;
      document.getElementById("alertCount").textContent = ui.pending_alerts || 0;
      document.getElementById("feedbackCount").textContent = ui.pending_alerts || 0;
      document.getElementById("safeMode").textContent = (frontend.safe_mode === true || ui.safe_mode === true) ? "ON" : "OFF";

      const statusText = system.status || "ONLINE";
      document.getElementById("systemStatus").innerHTML = `<span class="pulse"></span> ${statusText}`;
      document.getElementById("backendStatus").textContent = backend.status || "ONLINE";
      document.getElementById("frontendStatus").textContent = frontend.status || "ONLINE";
      document.getElementById("uiStatus").textContent = ui.status || "ONLINE";
    } catch (err) {
      console.error("Status update failed:", err);
      document.getElementById("systemStatus").innerHTML = '<span class="pulse"></span> OFFLINE';
    }
  }

  async compileCode() {
    const codeInput = document.getElementById("codeInput");
    const code = (codeInput.value || "").trim() || "# Sample code\nprint('Compiling')";

    try {
      const result = await this.fetchJson("/api/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code })
      });

      const module = result.result || {};
      const moduleId = module.module_id || "unknown";
      const version = module.version || "1.0.0";
      document.getElementById("compilerStatus").textContent = `✓ Compiled Module ${moduleId} (v${version})`;
      this.updateStatus();
      this.refreshModules();
    } catch (err) {
      console.error("Compile failed:", err);
      document.getElementById("compilerStatus").textContent = `✕ ${err.message || "Compile failed"}`;
    }
  }

  async analyzeAndCompile() {
    const code = document.getElementById("codeInput").value;
    if (!code || !code.trim()) {
      document.getElementById("compilerStatus").textContent = "Please add code to analyze.";
      return;
    }

    await this.compileCode();
  }

  async interpretAtmosphere() {
    document.getElementById("atmosphereStatus").textContent = "Interpreting...";
    try {
      await this.fetchJson("/api/control", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ control: "panel", value: "Atmosphere" })
      });
      document.getElementById("atmosphereStatus").textContent = "✓ Complete";
    } catch (err) {
      document.getElementById("atmosphereStatus").textContent = "✕ Interpretation failed";
    }
  }

  async refreshModules() {
    try {
      const state = await this.fetchJson("/api/state");
      const backend = state.backend || {};
      const list = document.getElementById("recentModules");
      const modules = backend.modules || [];

      if (!Array.isArray(modules) || modules.length === 0) {
        list.innerHTML = '<div class="activity-item">No compiled modules yet.</div>';
        return;
      }

      list.innerHTML = modules.slice(0, 5).map((m) => `
        <div class="activity-item">
          <span class="dot"></span>
          ${m.intent || "unknown"} • v${m.version || "1.0.0"} • ${m.module_id || "n/a"}
        </div>
      `).join("");
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
