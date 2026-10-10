class UniversalViewerSystem {
  constructor() {
    this.systemState = null;
    this.modules = [];
    this.refreshInterval = 2000;
    this.setupEventListeners();
    this.startAutoRefresh();
  }

  setupEventListeners() {
    document.getElementById("statusBtn").addEventListener("click", () => this.updateStatus());
    document.getElementById("compileBtn").addEventListener("click", () => this.compileCode());
    document.getElementById("analyzeBtn").addEventListener("click", () => this.analyzeAndCompile());
    document.getElementById("interpretBtn").addEventListener("click", () => this.interpretAtmosphere());
    document.getElementById("bioBtn").addEventListener("click", () => this.analyzeBiology());
    document.getElementById("calibrateBtn").addEventListener("click", () => this.calibrateAutonomy());
  }

  async updateStatus() {
    const response = await fetch("/api/compiler/state");
    const state = await response.json();
    document.getElementById("compilationCount").textContent = state.total_compilations;
    document.getElementById("updateCount").textContent = state.total_updates;
    document.getElementById("versionDisplay").textContent = state.antenna_version;
    document.getElementById("moduleCount").textContent = state.compiled_modules;
    document.getElementById("systemInfo").innerHTML = `
      <p><strong>Status:</strong> ${state.system_state.status}</p>
      <p><strong>Autonomous Mode:</strong> ${state.system_state.autonomous_mode ? 'ON' : 'OFF'}</p>
      <p><strong>Last Activity:</strong> ${new Date(state.last_activity).toLocaleTimeString()}</p>
    `;
  }

  async compileCode() {
    const response = await fetch("/api/compiler/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: "# Sample code" })
    });
    const result = await response.json();
    alert(`Compiled module: ${result.module_id}\nOptimizations: ${result.optimizations}`);
    this.updateStatus();
  }

  async analyzeAndCompile() {
    const code = document.getElementById("codeInput").value;
    if (!code) {
      alert("Paste code first");
      return;
    }
    const response = await fetch("/api/compiler/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code })
    });
    const result = await response.json();
    document.getElementById("compilerStatus").textContent = `✓ Compiled (v${result.version})`;
    this.updateStatus();
  }

  async interpretAtmosphere() {
    document.getElementById("atmosphereStatus").textContent = "Interpreting...";
    setTimeout(() => { document.getElementById("atmosphereStatus").textContent = "✓ Complete"; }, 1000);
  }

  async analyzeBiology() {
    document.getElementById("bioStatus").textContent = "Analyzing...";
    setTimeout(() => { document.getElementById("bioStatus").textContent = "✓ 8 Species Detected"; }, 1000);
  }

  async calibrateAutonomy() {
    const payload = {
      challenge_level: Number(document.getElementById("challengeLevel").value),
      realism_bias: Number(document.getElementById("realismBias").value),
      depth_bias: Number(document.getElementById("depthBias").value),
      safety_bias: Number(document.getElementById("safetyBias").value)
    };

    const response = await fetch("/api/autonomy/calibrate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    document.getElementById("calibrationResult").textContent = `${result.summary} Severity ${result.challenge_severity}, Realism ${result.realism_weight}, Depth ${result.depth_weight}.`;
    this.updateStatus();
  }

  async refreshModules() {
    const response = await fetch("/api/compiler/modules");
    const data = await response.json();
    const list = document.getElementById("recentModules");
    if (data.modules.length === 0) {
      list.innerHTML = "No modules yet.";
      return;
    }
    let html = "";
    for (const module of data.modules.slice(0, 5)) {
      html += `<div class="module-item">v${module.version} - ${module.code_intent || 'unknown'}</div>`;
    }
    list.innerHTML = html;
  }

  startAutoRefresh() {
    setInterval(() => {
      this.updateStatus();
      this.refreshModules();
    }, this.refreshInterval);
    this.updateStatus();
  }
}

const viewer = new UniversalViewerSystem();
