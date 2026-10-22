class FrontendAI:
    def __init__(self):
        self.panel = "Earth"
        self.zoom = 1.0
        self.signal_quality = 92
        self.safe_mode = True
        self.strict_mode = False
        self.status = "ONLINE"
        self.theme = "Cartoon"

    def set_panel(self, panel_name):
        """Switch active panel."""
        self.panel = panel_name
        return {"panel": self.panel}

    def set_zoom(self, zoom_level):
        """Adjust zoom level."""
        self.zoom = max(0.5, min(zoom_level, 3.0))
        return {"zoom": self.zoom}

    def toggle_safe_mode(self, enabled):
        """Toggle safe mode."""
        self.safe_mode = enabled
        return {"safe_mode": self.safe_mode}

    def get_state(self):
        """Return frontend AI state."""
        return {
            "status": self.status,
            "panel": self.panel,
            "zoom": self.zoom,
            "signal_quality": self.signal_quality,
            "safe_mode": self.safe_mode,
            "strict_mode": self.strict_mode,
            "theme": self.theme
        }


frontend_ai = FrontendAI()
