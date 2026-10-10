class FrontendAI:
    def __init__(self):
        self.panel = "Earth"
        self.zoom = 1.0
        self.signal_quality = 92
        self.safe_mode = True
        self.status = "ONLINE"
        self.theme = "Cartoon"
        self.last_action = "ready"

    def set_panel(self, panel_name):
        """Switch active panel."""
        normalized = str(panel_name or "Earth").strip() or "Earth"
        self.panel = normalized
        self.last_action = "panel_change"
        return {"panel": self.panel, "status": "updated"}

    def set_zoom(self, zoom_level):
        """Adjust zoom level."""
        try:
            zoom_value = float(zoom_level)
        except (TypeError, ValueError):
            return {"zoom": self.zoom, "status": "error", "error": "invalid zoom value"}
        self.zoom = max(0.5, min(zoom_value, 3.0))
        self.last_action = "zoom_change"
        return {"zoom": self.zoom, "status": "updated"}

    def toggle_safe_mode(self, enabled):
        """Toggle safe mode."""
        self.safe_mode = bool(enabled)
        self.last_action = "safe_mode_toggle"
        return {"safe_mode": self.safe_mode, "status": "updated"}

    def get_state(self):
        """Return frontend AI state."""
        return {
            "status": self.status,
            "panel": self.panel,
            "zoom": self.zoom,
            "signal_quality": self.signal_quality,
            "safe_mode": self.safe_mode,
            "theme": self.theme,
            "last_action": self.last_action
        }


frontend_ai = FrontendAI()
