from backend_ai import backend_ai
from frontend_ai import frontend_ai
from ui_agent import ui_agent


class AgentCoordinator:
    def __init__(self, backend, frontend, ui):
        self.backend = backend
        self.frontend = frontend
        self.ui = ui

    def get_unified_state(self):
        """Return combined state from all three agents."""
        backend_state = self.backend.get_state()
        frontend_state = self.frontend.get_state()
        memory = backend_state.get("memory", {})
        recent = memory.get("recent_observations", [])
        learning = backend_state.get("learning", {})
        return {
            "backend": backend_state,
            "frontend": frontend_state,
            "ui": self.ui.get_state(),
            "timestamp": self.get_timestamp(),
            "known_numbers": {
                "signal_quality": self.backend.pull_known_number("signal_quality", 92),
                "altitude": self.backend.pull_known_number("altitude", 800),
                "temperature": self.backend.pull_known_number("temperature", 18),
                "humidity": self.backend.pull_known_number("humidity", 52),
                "power": self.backend.pull_known_number("power", 80),
                "coverage": self.backend.pull_known_number("coverage", 85),
            },
            "memory": memory,
            "learning": learning,
            "last_learned": recent[-1] if recent else None,
        }

    def route_compile_request(self, code):
        """Route compilation request through backend."""
        result = self.backend.compile(code)
        self.backend.modules.append(result)
        self.ui.show_alert("Compilation", f"Compiled module {result['module_id']}", "success")
        return result

    def route_gesture(self, gesture_type, data):
        """Route gesture through UI agent."""
        gesture = self.ui.handle_gesture(gesture_type, data)
        return gesture

    def route_slider_change(self, control, value):
        """Route slider/control changes through frontend."""
        if control == "zoom":
            return self.frontend.set_zoom(value)
        elif control == "panel":
            return self.frontend.set_panel(value)
        return {"control": control, "value": value}

    def route_safety_toggle(self, safe_mode, strict_mode):
        """Route safety mode toggles."""
        self.frontend.toggle_safe_mode(safe_mode)
        self.ui.safe_mode = safe_mode
        return {
            "safe_mode": safe_mode,
            "strict_mode": strict_mode
        }

    def get_timestamp(self):
        """Return current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


coordinator = AgentCoordinator(backend_ai, frontend_ai, ui_agent)
