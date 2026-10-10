"""
AGENT COORDINATOR
Orchestrates communication between BackendAI, FrontendAI, and UIAgent
Routes requests, syncs state, and manages inter-agent communication
"""
from datetime import datetime


class AgentCoordinator:
    def __init__(self, backend_ai, frontend_ai, ui_agent):
        self.name = "Agent Coordinator"
        self.backend = backend_ai
        self.frontend = frontend_ai
        self.ui = ui_agent
        self.status = "online"
        self.message_queue = []
        self.state_sync_log = []

    def route_compile_request(self, code):
        """User → UI → Frontend → Backend → compile"""
        # UI captures the request
        self.ui.queue_visual_feedback("compile_btn", "pulse")
        
        # Backend compiles autonomously
        module = self.backend.compile_autonomous(code)
        
        # Frontend updates UI state
        self.frontend.update_state(selected_panel="compiler")
        
        # UI shows success
        self.ui.show_notification("✅", f"Compiled: {module['module_id']}", 3000)
        
        return module

    def route_load_image(self, image_data):
        """User → UI → Frontend updates with image"""
        self.ui.queue_visual_feedback("load_btn", "spin")
        self.frontend.update_state(selected_panel="picture")
        self.ui.show_notification("🖼️", "Image loaded", 2000)
        return {"status": "loaded", "size": len(image_data)}

    def route_gesture(self, gesture_type, data):
        """User gesture → UI → Frontend updates controls"""
        feedback = self.ui.handle_gesture(gesture_type, data)
        
        if gesture_type == "pinch":
            zoom_delta = feedback.get("zoom_delta", 0)
            self.frontend.adjust_zoom(zoom_delta)
        elif gesture_type == "rotate":
            rot_delta = feedback.get("rotation_delta", 0)
            self.frontend.animate_rotation(rot_delta)
        elif gesture_type == "drag":
            dx = feedback.get("drag", {}).get("dx", 0)
            dy = feedback.get("drag", {}).get("dy", 0)
            self.frontend.handle_pointer_drag(dx, dy)
        
        return self.frontend.state

    def route_slider_change(self, slider_id, value):
        """Slider → UI → Frontend → visual update"""
        self.ui.handle_click(slider_id, value, 0)
        
        if slider_id == "brightness":
            self.frontend.adjust_brightness(value)
        elif slider_id == "contrast":
            self.frontend.adjust_contrast(value)
        elif slider_id == "zoom":
            self.frontend.adjust_zoom(value)
        
        return {"control": slider_id, "value": value}

    def route_safety_toggle(self, safe_mode, strict_mode):
        """Safety controls → UI → Frontend"""
        self.frontend.set_safe_mode(safe_mode)
        self.frontend.set_strict_mode(strict_mode)
        self.ui.show_notification("🛡️", f"Safe mode: {'ON' if safe_mode else 'OFF'}")
        return {"safe_mode": safe_mode, "strict_mode": strict_mode}

    def sync_all_state(self):
        """Synchronize state across all three agents"""
        sync = {
            "timestamp": self._now(),
            "backend": self.backend.get_state(),
            "frontend": self.frontend.get_dashboard_state(),
            "ui": self.ui.get_state(),
        }
        self.state_sync_log.append(sync)
        if len(self.state_sync_log) > 50:
            self.state_sync_log = self.state_sync_log[-50:]
        return sync

    def get_unified_state(self):
        """Return complete unified system state"""
        return {
            "coordinator": self.name,
            "status": self.status,
            "backend": self.backend.get_state(),
            "frontend": self.frontend.get_dashboard_state(),
            "ui": self.ui.get_state(),
            "timestamp": self._now(),
        }

    def predict_user_intent(self):
        """Predict what user will do next"""
        behavior = self.ui.get_user_behavior_summary()
        most_used = [c[0] for c in behavior["most_used_controls"][:3]]
        
        predictions = []
        for control in most_used:
            if control.startswith("knob_"):
                predictions.append({"type": "adjustment", "control": control})
            elif control.startswith("btn_"):
                predictions.append({"type": "action", "control": control})
        
        return {
            "predictions": predictions,
            "confidence": 0.6,
            "interaction_style": behavior["interaction_style"],
        }

    def handle_user_error(self, error_msg):
        """Handle user mistakes gracefully"""
        self.ui.show_alert(
            "⚠️ Oops!",
            error_msg,
            level="warning"
        )
        self.ui.queue_visual_feedback("error", "shake")
        self.ui._queue_haptic("error_buzz")

    def _now(self):
        return datetime.utcnow().isoformat() + "Z"

    def get_message_log(self):
        """Get all inter-agent communications"""
        return self.state_sync_log[-20:]
