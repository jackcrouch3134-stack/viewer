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
        return {
            "backend": self.backend.get_state(),
            "frontend": self.frontend.get_state(),
            "ui": self.ui.get_state(),
            "system": {
                "status": "ONLINE",
                "timestamp": self.get_timestamp(),
                "safe_mode": self.frontend.safe_mode or self.ui.safe_mode,
            },
            "timestamp": self.get_timestamp()
        }

    def route_compile_request(self, code):
        """Route compilation request through backend."""
        if not isinstance(code, str):
            raise ValueError("Code payload must be a string.")
        normalized_code = code.strip()
        if not normalized_code:
            raise ValueError("Code payload cannot be empty.")
        result = self.backend.compile(normalized_code)
        self.backend.record_module(result)
        self.ui.show_alert("Compilation", f"Compiled module {result['module_id']}", "success")
        self.frontend.last_action = "compile"
        return result

    def route_gesture(self, gesture_type, data):
        """Route gesture through UI agent."""
        if not isinstance(data, dict):
            data = {}
        gesture = self.ui.handle_gesture(gesture_type, data)
        self.frontend.last_action = "gesture"
        return gesture

    def route_slider_change(self, control, value):
        """Route slider/control changes through frontend."""
        if control == "zoom":
            result = self.frontend.set_zoom(value)
            self.ui.show_alert("Control", f"Zoom updated to {result.get('zoom')}", "info")
            return result
        if control == "panel":
            result = self.frontend.set_panel(value)
            self.ui.show_alert("Control", f"Panel changed to {result.get('panel')}", "info")
            return result
        raise ValueError(f"Unsupported control: {control}")

    def route_safety_toggle(self, safe_mode, strict_mode):
        """Route safety mode toggles."""
        self.frontend.toggle_safe_mode(safe_mode)
        self.ui.safe_mode = bool(safe_mode)
        return {
            "safe_mode": bool(safe_mode),
            "strict_mode": bool(strict_mode),
            "status": "updated"
        }

    def get_timestamp(self):
        """Return current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


coordinator = AgentCoordinator(backend_ai, frontend_ai, ui_agent)
