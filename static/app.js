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
    const rangeSelect = document.getElementById("rangeSelect");
    if (rangeSelect) {
      rangeSelect.addEventListener("change", async () => {
        const value = Number(rangeSelect.value || 7);
        await this.fetchState(value);
      });
    }
  }

  async fetchState(periodDays = 7) {
    const response = await fetch(`/api/state?period_days=${periodDays}`);
    return response.json();
  }

  async updateStatus() {
    try {
      const rangeSelect = document.getElementById("rangeSelect");
      const periodDays = rangeSelect ? Number(rangeSelect.value || 7) : 7;
      const response = await fetch(`/api/state?period_days=${periodDays}`);
      const state = await response.json();

      const backend = state.backend || {};
      const frontend = state.frontend || {};
      const ui = state.ui || {};
      const numbers = state.known_numbers || {};
      const learning = state.learning || {};
      const memory = state.memory || {};

      const signalQuality = numbers.signal_quality || frontend.signal_quality || 92;
      const altitude = numbers.altitude || 800;
      const coverage = numbers.coverage || 85;
      const learningStatus = learning.status || "observing";
      const learningSummary = learning.summary || {};
      const strengthRating = learning.strength_rating || learningSummary.strength_rating || "minimal";
      const severityRating = learning.severity_rating || learningSummary.severity_rating || "none";
      const expScore = Number(learning.exp_score ?? learningSummary.exp_score ?? 0).toFixed(1);
      const chaosActivity = Number(learning.chaos_activity ?? learningSummary.chaos_activity ?? 0).toFixed(3);
      const strengthValue = Number(learning.strength ?? learningSummary.strength ?? 0).toFixed(3);
      const severityValue = Number(learning.severity ?? learningSummary.severity ?? 0).toFixed(3);
      const formulaDisplay = learningSummary.formula || "EXP = (strength × 60) + (chaos × 40)";

      document.getElementById("compilationCount").textContent = backend.compilations || 0;
      document.getElementById("updateCount").textContent = backend.updates || 0;
      document.getElementById("versionDisplay").textContent = backend.version || "1.0.0";
      document.getElementById("moduleCount").textContent = backend.modules_count || 0;

      document.getElementById("currentPanel").textContent = frontend.panel || "Earth";
      document.getElementById("zoomLevel").textContent = `${(frontend.zoom || 1).toFixed(1)}x`;
      document.getElementById("signalQuality").textContent = `${signalQuality}%`;
      document.getElementById("altitudeValue").textContent = `${altitude} km`;
      document.getElementById("coverageValue").textContent = `${coverage}%`;
      document.getElementById("coverageValueSecondary").textContent = `${coverage}%`;
      document.getElementById("currentMode").textContent = "First Person";
      document.getElementById("observerStatus").textContent = "ACTIVE";
      document.getElementById("environmentStatus").textContent = signalQuality > 90 ? "Clear View" : "Scanning";
      document.getElementById("focusName").textContent = "Observer";
      document.getElementById("hudModeValue").textContent = "First Person";
      document.getElementById("hudFocusValue").textContent = "Observer";
      document.getElementById("missionSignalValue").textContent = `${signalQuality}%`;
      document.getElementById("missionExpValue").textContent = expScore;
      document.getElementById("missionRouteValue").textContent = signalQuality > 88 ? "Stable" : "Scanning";

      document.getElementById("systemStatus").innerHTML = '<span class="pulse"></span> ONLINE';
      document.getElementById("backendStatus").textContent = backend.status || "ONLINE";
      document.getElementById("frontendStatus").textContent = frontend.status || "ONLINE";
      document.getElementById("userModeStatus").textContent = learningStatus.toUpperCase();

      if (document.getElementById("learningStatus")) {
        document.getElementById("learningStatus").textContent = `Learning status: ${learningStatus} • EXP ${expScore} • chaos ${chaosActivity} • strength ${strengthRating} • severity ${severityRating}`;
      }
      if (document.getElementById("formulaValue")) {
        document.getElementById("formulaValue").textContent = formulaDisplay;
      }

      const matrixCells = document.querySelectorAll('.matrix-cell');
      matrixCells.forEach((cell, index) => {
        const tint = ["low", "mid", "high"][index % 3];
        cell.classList.remove('low', 'mid', 'high');
        cell.classList.add(tint);
      });
      if (document.getElementById("strengthValue")) {
        document.getElementById("strengthValue").textContent = strengthValue;
      }
      if (document.getElementById("severityValue")) {
        document.getElementById("severityValue").textContent = severityValue;
      }
      if (document.getElementById("chaosValue")) {
        document.getElementById("chaosValue").textContent = chaosActivity;
      }

      const trendBars = document.getElementById("trendBars");
      if (trendBars) {
        const trend = learningSummary.trend || [];
        const maxExp = trend.length ? Math.max(...trend.map((point) => Number(point.exp_score || 0))) : 1;
        const bars = trend.slice(-7).map((point) => {
          const value = Number(point.exp_score || 0);
          const height = Math.max(14, (value / maxExp) * 100);
          const label = point.date ? point.date.slice(5) : "";
          return `<div class="trend-bar" style="height:${height}%" title="${value}"><span>${label}</span></div>`;
        }).join("");
        trendBars.innerHTML = bars || '<div class="activity-item">No trend data yet.</div>';
      }

      const experienceList = document.getElementById("experienceList");
      if (experienceList) {
        const insights = learningSummary.insights || memory.recent_observations || [];
        const items = insights.slice(0, 4).map((item) => {
          const context = item.context || item.name || "pattern";
          const outcome = item.outcome || item.value || "stable";
          const confidence = item.confidence ?? 0.0;
          return `<div class="activity-item">${context}: ${outcome} (${Number(confidence).toFixed(2)})</div>`;
        });
        experienceList.innerHTML = items.length ? items.join("") : '<div class="activity-item">No learned experience yet.</div>';
      }

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

      if (rangeSelect) {
        rangeSelect.value = String(state.period_days || 7);
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
      const rangeSelect = document.getElementById("rangeSelect");
      const periodDays = rangeSelect ? Number(rangeSelect.value || 7) : 7;
      const response = await fetch(`/api/state?period_days=${periodDays}`);
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
