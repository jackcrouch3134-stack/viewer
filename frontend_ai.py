"""
FRONTEND AI OPERATOR
Handles layout logic, visual flow, component state, gesture responses,
UI communication, and interactive rendering behavior.
"""

class FrontendAI:
    def __init__(self):
        self.name = "Frontend AI"
        self.status = "online"
        self.state = {
            "theme": "cartoon",
            "zoom": 1.0,
            "rotation": 0,
            "brightness": 100,
            "contrast": 100,
            "cloud_cover": 45,
            "tilt": 0,
            "safe_mode": True,
            "strict_mode": False,
            "signal_quality": 92,
            "live": True,
            "selected_panel": "earth",
        }
        self.controllers = {}
        self.event_log = []

    def register_controller(self, name, controller):
        self.controllers[name] = controller

    def update_state(self, **changes):
        self.state.update(changes)
        self._log_event(f"UI state updated: {changes}")
        return self.state

    def set_panel(self, panel_name):
        self.state["selected_panel"] = panel_name
        self._log_event(f"Selected panel: {panel_name}")
        return self.state

    def animate_rotation(self, degrees=10):
        self.state["rotation"] = (self.state["rotation"] + degrees) % 360
        self._log_event(f"Rotation adjusted to {self.state['rotation']}°")
        return self.state["rotation"]

    def adjust_zoom(self, delta):
        self.state["zoom"] = max(0.5, min(2.5, self.state["zoom"] + delta))
        self._log_event(f"Zoom adjusted to {self.state['zoom']:.2f}x")
        return self.state["zoom"]

    def adjust_brightness(self, value):
        self.state["brightness"] = max(40, min(160, value))
        self._log_event(f"Brightness adjusted to {self.state['brightness']}")
        return self.state["brightness"]

    def adjust_contrast(self, value):
        self.state["contrast"] = max(40, min(180, value))
        self._log_event(f"Contrast adjusted to {self.state['contrast']}")
        return self.state["contrast"]

    def set_safe_mode(self, enabled):
        self.state["safe_mode"] = enabled
        self._log_event(f"Safe mode set to {enabled}")
        return self.state["safe_mode"]

    def set_strict_mode(self, enabled):
        self.state["strict_mode"] = enabled
        self._log_event(f"Strict mode set to {enabled}")
        return self.state["strict_mode"]

    def update_signal_quality(self, percent):
        self.state["signal_quality"] = max(0, min(100, percent))
        self._log_event(f"Signal quality updated to {self.state['signal_quality']}%")
        return self.state["signal_quality"]

    def handle_pointer_drag(self, dx, dy):
        self.state["rotation"] = (self.state["rotation"] + dx * 0.5) % 360
        self.state["tilt"] = max(-40, min(40, self.state["tilt"] + dy * 0.2))
        self._log_event(f"Pointer drag detected: dx={dx}, dy={dy}")
        return {"rotation": self.state["rotation"], "tilt": self.state["tilt"]}

    def _log_event(self, msg):
        self.event_log.append({"timestamp": self._now(), "message": msg})
        if len(self.event_log) > 50:
            self.event_log = self.event_log[-50:]

    def _now(self):
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

    def get_dashboard_state(self):
        return {
            "frontend_ai": self.name,
            "status": self.status,
            "theme": self.state["theme"],
            "panel": self.state["selected_panel"],
            "zoom": self.state["zoom"],
            "rotation": self.state["rotation"],
            "signal_quality": self.state["signal_quality"],
            "safe_mode": self.state["safe_mode"],
            "strict_mode": self.state["strict_mode"],
        }


frontend_ai = FrontendAI()
