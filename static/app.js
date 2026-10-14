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
    const clearBtn = document.getElementById("drawClearBtn");
    if (clearBtn) clearBtn.addEventListener("click", () => this.clearDrawingCanvas());
    const analyzeBtn = document.getElementById("drawAnalyzeBtn");
    if (analyzeBtn) analyzeBtn.addEventListener("click", () => this.analyzeDrawing());
    const uploadInput = document.getElementById("drawingUpload");
    const uploadBtn = document.getElementById("drawUploadBtn");
    if (uploadInput && uploadBtn) {
      uploadBtn.addEventListener("click", () => uploadInput.click());
      uploadInput.addEventListener("change", (event) => this.handleDrawingUpload(event));
    }
    const rangeSelect = document.getElementById("rangeSelect");
    if (rangeSelect) {
      rangeSelect.addEventListener("change", async () => {
        const value = Number(rangeSelect.value || 7);
        await this.fetchState(value);
      });
    }

    const translateBtn = document.getElementById("translateSignalBtn");
    if (translateBtn) {
      translateBtn.addEventListener("click", () => this.translateSignal());
    }

    const recordBtn = document.getElementById("recordExperienceBtn");
    if (recordBtn) {
      recordBtn.addEventListener("click", () => this.recordExperienceFromInput());
    }
  }

  translateSignal() {
    const input = document.getElementById("feedInput");
    if (!input) return;

    const raw = (input.value || "").trim();
    if (!raw) {
      input.focus();
      return;
    }

    const cleaned = raw.replace(/\s+/g, " ");
    const signal = cleaned.length > 72 ? cleaned.slice(0, 72) + "…" : cleaned;
    const feed = signal.length > 26 ? "patterned translation" : "direct observation";
    const imagination = signal.includes("route") || signal.includes("map")
      ? "route-aware meaning"
      : signal.includes("light") || signal.includes("signal")
        ? "signal-driven meaning"
        : "interpretive sense";
    const outcome = signal.includes("risk") || signal.includes("danger")
      ? "reposition and monitor"
      : signal.includes("goal") || signal.includes("mission")
        ? "advance with intent"
        : "keep tracking and adapt";
    const speech = signal.includes("risk") || signal.includes("danger")
      ? "Voice: caution and adjustment."
      : signal.includes("goal") || signal.includes("mission")
        ? "Voice: intent and next move."
        : "Voice: stable observation in progress.";

    const signalEl = document.getElementById("signalFlow");
    const feedEl = document.getElementById("feedFlow");
    const imaginationEl = document.getElementById("imaginationFlow");
    const outcomeEl = document.getElementById("outcomeFlow");

    if (signalEl) signalEl.textContent = signal;
    if (feedEl) feedEl.textContent = feed;
    if (imaginationEl) imaginationEl.textContent = imagination;
    if (outcomeEl) outcomeEl.textContent = `${outcome} • ${speech}`;

    const direction = `Signal → ${feed} → ${imagination} → ${outcome} → speech`;
    this.updateThoughtDirection(direction, 4);
  }

  recordExperienceFromInput() {
    const input = document.getElementById("feedInput");
    if (!input) return;

    const raw = (input.value || "").trim();
    if (!raw) {
      input.focus();
      return;
    }

    const list = document.getElementById("experienceList");
    if (!list) return;

    const summary = this.generateExperienceSummary(raw);
    const item = document.createElement("div");
    item.className = "activity-item";
    item.innerHTML = `<strong>Signal translated:</strong> ${summary}`;
    list.prepend(item);

    const items = list.querySelectorAll(".activity-item");
    while (items.length > 4) {
      list.removeChild(items[items.length - 1]);
    }

    this.updateThoughtDirection("Signal → interpretation → response", 0);
    this.translateSignal();
  }

  updateThoughtDirection(label, activeStep = 0) {
    const status = document.getElementById("thoughtDirectionStatus");
    if (status) status.textContent = label;

    const steps = document.querySelectorAll(".direction-step");
    steps.forEach((step, index) => {
      step.classList.toggle("active", index === activeStep);
    });
  }

  generateExperienceSummary(rawText) {
    const normalized = rawText.replace(/\s+/g, " ").trim();
    const hasRoute = /route|map|path|location/i.test(normalized);
    const hasRisk = /risk|threat|warning|danger/i.test(normalized);
    const hasSignal = /signal|feed|pulse|light|scan/i.test(normalized);
    const hasIntent = /goal|mission|next|plan/i.test(normalized);

    if (hasRoute && hasRisk) return "Mapped risk into a route correction and intent reset.";
    if (hasRoute && hasIntent) return "Converted a route cue into a directionally adaptive plan.";
    if (hasSignal && hasIntent) return "Merged signal context with mission intent to refine the model.";
    if (hasRisk) return "Detected warning data and translated it into cautious adaptation.";
    if (hasRoute) return "Used the map as a frame for interpretation and motion guidance.";
    if (hasSignal) return "Transformed raw signal data into a meaningful pattern.";
    return "Recorded a small interpretive cycle between feed, meaning, and outcome.";
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
      const profile = state.personal_profile || {};
      const motivator = state.motivation_system || backend.motivation_system || {};
      const motivatorState = motivator.state || {};

      const observerName = profile.observer_name || "JC";
      const identityName = profile.identity_name || "JC / Experience Network";
      const missionTitle = profile.mission_title || "Cleaner observation, stronger memory, smarter movement.";
      const missionSummary = profile.mission_summary || "The home screen is framed as a personal experience map: signal quality, learned patterns, and mission awareness stay visible while keeping the JC point of view front and center.";
      const focusLabel = profile.focus_label || "Observer";
      const modeLabel = profile.mode_label || "First Person";
      const footerLine = profile.footer_line || "JC Observer Experience System v1.0 | Personal signal intelligence";

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
      document.getElementById("currentMode").textContent = modeLabel;
      document.getElementById("observerStatus").textContent = "ACTIVE";
      document.getElementById("environmentStatus").textContent = signalQuality > 90 ? "Clear View" : "Scanning";
      document.getElementById("focusName").textContent = focusLabel;
      document.getElementById("hudModeValue").textContent = modeLabel;
      document.getElementById("hudFocusValue").textContent = focusLabel;
      document.getElementById("missionSignalValue").textContent = `${signalQuality}%`;
      document.getElementById("missionExpValue").textContent = expScore;
      document.getElementById("missionRouteValue").textContent = signalQuality > 88 ? "Stable" : "Scanning";
      document.getElementById("profileIdentity").textContent = identityName;
      document.getElementById("profileMissionTitle").textContent = missionTitle;
      document.getElementById("profileMissionSummary").textContent = missionSummary;
      document.getElementById("observerNameValue").textContent = observerName;
      document.getElementById("mapNodeJC").textContent = observerName;
      document.getElementById("footerLine").textContent = footerLine;

      document.getElementById("systemStatus").innerHTML = '<span class="pulse"></span> ONLINE';
      document.getElementById("backendStatus").textContent = backend.status || "ONLINE";
      document.getElementById("frontendStatus").textContent = frontend.status || "ONLINE";
      document.getElementById("userModeStatus").textContent = learningStatus.toUpperCase();

      if (document.getElementById("learningStatus")) {
        document.getElementById("learningStatus").textContent = `${observerName} learning status: ${learningStatus} • EXP ${expScore} • chaos ${chaosActivity} • strength ${strengthRating} • severity ${severityRating}`;
      }
      if (document.getElementById("formulaValue")) {
        document.getElementById("formulaValue").textContent = formulaDisplay;
      }

      const motivationStatus = document.getElementById("motivationStatus");
      const motivationTranslation = document.getElementById("motivationTranslation");
      if (motivationStatus) {
        const motivation = motivatorState.motivation || "adaptive";
        const energy = Number(motivatorState.energy ?? 0).toFixed(3);
        motivationStatus.textContent = `${motivation} • signal energy ${energy}`;
      }
      if (motivationTranslation) {
        motivationTranslation.textContent = motivatorState.translation || "No signal to convert.";
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

    const response = await fetch("/api/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code })
    });

    const result = await response.json();
    const message = result?.result?.energy_relationship || result?.result?.readable_translation || "Signal analyzed.";
    const statusText = typeof message === "object"
      ? `Signal translated: ${message.translation || "system ready"}`
      : `Signal translated: ${message}`;
    document.getElementById("compilerStatus").textContent = statusText;
    const motivationTranslation = document.getElementById("motivationTranslation");
    if (motivationTranslation) {
      motivationTranslation.textContent = typeof message === "object" ? (message.translation || "Signal converted.") : message;
    }
    this.updateStatus();
  }

  async interpretAtmosphere() {
    document.getElementById("atmosphereStatus").textContent = "Interpreting...";
    setTimeout(() => {
      document.getElementById("atmosphereStatus").textContent = "✓ Complete";
    }, 800);
  }

  clearDrawingCanvas() {
    const canvas = document.getElementById("drawingCanvas");
    if (!canvas) return;
    const context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = "#08171f";
    context.fillRect(0, 0, canvas.width, canvas.height);
    const summary = document.getElementById("drawingSummary");
    const lines = document.getElementById("drawingLines");
    if (summary) summary.textContent = "No drawing yet.";
    if (lines) lines.textContent = "0";
  }

  handleDrawingUpload(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    const canvas = document.getElementById("drawingCanvas");
    const summary = document.getElementById("drawingSummary");
    const image = new Image();
    const reader = new FileReader();

    reader.onload = () => {
      image.onload = () => {
        if (!canvas) return;
        const context = canvas.getContext("2d");
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.fillStyle = "#08171f";
        context.fillRect(0, 0, canvas.width, canvas.height);
        const drawWidth = Math.min(image.width, canvas.width);
        const drawHeight = Math.min(image.height, canvas.height);
        const offsetX = (canvas.width - drawWidth) / 2;
        const offsetY = (canvas.height - drawHeight) / 2;
        context.drawImage(image, offsetX, offsetY, drawWidth, drawHeight);
        if (summary) summary.textContent = `Uploaded drawing loaded: ${file.name}. Ready to analyze.`;
        this.analyzeDrawing();
      };
      image.src = reader.result;
    };

    reader.readAsDataURL(file);
  }

  analyzeDrawing() {
    const canvas = document.getElementById("drawingCanvas");
    const summary = document.getElementById("drawingSummary");
    const lines = document.getElementById("drawingLines");
    if (!canvas || !summary || !lines) return;

    const context = canvas.getContext("2d");
    const image = context.getImageData(0, 0, canvas.width, canvas.height);
    const data = image.data;
    let darkPixels = 0;
    let total = 0;
    let strokeSegments = 0;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const brightness = (r + g + b) / 3;
      if (brightness < 200) {
        darkPixels += 1;
      }
      total += 1;
    }

    const density = darkPixels / Math.max(1, total);
    const count = Math.max(6, Math.min(18, Math.round(density * 30 + 8)));
    strokeSegments = count;

    const reproduction = density > 0.1
      ? "Hand-drawn input detected. The form is being translated into stable traced contours and rebuilt as a readable visual memory."
      : "Low-density input detected. The system is preserving the sketch as a faint, low-energy trace.";

    summary.textContent = reproduction;
    lines.textContent = String(strokeSegments);

    fetch("/api/drawings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: "Hand-drawn reproduction",
        source: "canvas",
        analysis: reproduction,
        converted_lines: Array.from({ length: strokeSegments }, (_, i) => ({
          point: i + 1,
          length: Math.round(8 + (i * 2.5)),
          confidence: Number((0.5 + (density * 0.5) + (i / strokeSegments) * 0.2)).toFixed(3)
        })),
        confidence: Number(Math.min(0.99, 0.45 + density)).toFixed(3)
      })
    }).catch((err) => console.error("Drawing record failed:", err));
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
    const canvas = document.getElementById("drawingCanvas");
    if (canvas) {
      const context = canvas.getContext("2d");
      context.fillStyle = "#08171f";
      context.fillRect(0, 0, canvas.width, canvas.height);
      let drawing = false;
      const startDrawing = (event) => {
        drawing = true;
        context.beginPath();
        const point = this.getCanvasPoint(event, canvas);
        context.moveTo(point.x, point.y);
      };
      const draw = (event) => {
        if (!drawing) return;
        const point = this.getCanvasPoint(event, canvas);
        context.lineTo(point.x, point.y);
        context.strokeStyle = "#7feffc";
        context.lineWidth = 2.5;
        context.stroke();
      };
      const stopDrawing = () => {
        drawing = false;
      };
      canvas.addEventListener("pointerdown", startDrawing);
      canvas.addEventListener("pointermove", draw);
      canvas.addEventListener("pointerup", stopDrawing);
      canvas.addEventListener("pointerleave", stopDrawing);
    }

    setInterval(() => {
      this.updateStatus();
      this.refreshModules();
    }, this.refreshInterval);
    this.updateStatus();
    this.refreshModules();
  }

  getCanvasPoint(event, canvas) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    return {
      x: (event.clientX - rect.left) * scaleX,
      y: (event.clientY - rect.top) * scaleY,
    };
  }
}

const viewer = new UniversalViewerSystem();
