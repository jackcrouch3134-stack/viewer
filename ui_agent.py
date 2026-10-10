"""
USER INTERFACE AI OPERATOR
Manages input handling, gesture recognition, visual feedback,
rendering commands, alert/notification system, and user behavior prediction.
"""
import json
from datetime import datetime


class UIAgent:
    def __init__(self):
        self.name = "UI Agent"
        self.status = "active"
        self.user_profile = {
            "last_action": None,
            "action_frequency": {},
            "preferred_controls": "knobs",
            "interaction_style": "direct",
            "accessibility_needs": [],
        }
        self.gesture_history = []
        self.click_buffer = []
        self.active_controls = {}
        self.alerts = []
        self.notifications = []
        self.haptic_queue = []
        self.visual_feedback = {}

    def handle_click(self, control_id, x, y, button="left"):
        """Process click events and predict user intent"""
        action = {
            "timestamp": self._now(),
            "type": "click",
            "control": control_id,
            "x": x,
            "y": y,
            "button": button,
        }
        self.click_buffer.append(action)
        self._update_action_frequency(control_id)
        self._log_user_behavior(f"Clicked {control_id}")
        return self._predict_next_action(control_id)

    def handle_gesture(self, gesture_type, data):
        """Process multi-touch gestures"""
        if gesture_type == "pinch":
            return self._handle_pinch(data)
        elif gesture_type == "rotate":
            return self._handle_rotate(data)
        elif gesture_type == "swipe":
            return self._handle_swipe(data)
        elif gesture_type == "drag":
            return self._handle_drag(data)
        return {}

    def _handle_pinch(self, data):
        """Handle pinch-to-zoom gesture"""
        delta = data.get("delta", 0)
        self.gesture_history.append({"type": "pinch", "delta": delta})
        self._log_user_behavior(f"Pinch gesture: {delta}")
        self._queue_haptic("light_tap")
        return {"zoom_delta": delta * 0.1}

    def _handle_rotate(self, data):
        """Handle rotation gesture"""
        angle = data.get("angle", 0)
        self.gesture_history.append({"type": "rotate", "angle": angle})
        self._log_user_behavior(f"Rotate gesture: {angle}°")
        self._queue_haptic("medium_pulse")
        return {"rotation_delta": angle}

    def _handle_swipe(self, data):
        """Handle swipe gesture"""
        direction = data.get("direction", "unknown")
        self.gesture_history.append({"type": "swipe", "direction": direction})
        self._log_user_behavior(f"Swipe: {direction}")
        self._queue_haptic("light_tap")
        return {"swipe_direction": direction}

    def _handle_drag(self, data):
        """Handle drag/pointer movement"""
        dx = data.get("dx", 0)
        dy = data.get("dy", 0)
        self.gesture_history.append({"type": "drag", "dx": dx, "dy": dy})
        return {"drag": {"dx": dx, "dy": dy}}

    def show_alert(self, title, message, level="info"):
        """Display alert notification"""
        alert = {
            "id": len(self.alerts),
            "timestamp": self._now(),
            "title": title,
            "message": message,
            "level": level,  # info, warning, error, success
        }
        self.alerts.append(alert)
        self._queue_haptic("alert_" + level)
        self._log_user_behavior(f"Alert shown: {title}")
        return alert

    def show_notification(self, icon, text, duration=3000):
        """Display temporary notification"""
        notif = {
            "id": len(self.notifications),
            "timestamp": self._now(),
            "icon": icon,
            "text": text,
            "duration": duration,
        }
        self.notifications.append(notif)
        if len(self.notifications) > 10:
            self.notifications = self.notifications[-10:]
        return notif

    def queue_visual_feedback(self, control_id, effect="pulse"):
        """Queue visual feedback effect"""
        self.visual_feedback[control_id] = {
            "effect": effect,
            "timestamp": self._now(),
            "duration": 200,
        }
        self._log_user_behavior(f"Visual feedback queued: {control_id} ({effect})")
        return self.visual_feedback[control_id]

    def _queue_haptic(self, pattern):
        """Queue haptic/vibration feedback"""
        self.haptic_queue.append({
            "pattern": pattern,
            "timestamp": self._now(),
        })
        if len(self.haptic_queue) > 20:
            self.haptic_queue = self.haptic_queue[-20:]

    def _predict_next_action(self, current_control):
        """Predict what user will do next based on history"""
        # Simple prediction based on action frequency
        if len(self.click_buffer) < 2:
            return {"predicted_next": None}
        
        prev_action = self.click_buffer[-2] if len(self.click_buffer) > 1 else None
        curr_action = self.click_buffer[-1]
        
        predictions = []
        for ctrl, freq in self.user_profile["action_frequency"].items():
            if freq > 1:
                predictions.append({"control": ctrl, "probability": freq / 10})
        
        return {
            "predicted_next": predictions[:3],
            "confidence": 0.7 if predictions else 0.0,
        }

    def _update_action_frequency(self, control_id):
        """Track which controls user uses most"""
        freq = self.user_profile["action_frequency"]
        freq[control_id] = freq.get(control_id, 0) + 1

    def _log_user_behavior(self, description):
        """Log user interaction for analytics"""
        self.user_profile["last_action"] = {
            "timestamp": self._now(),
            "description": description,
        }

    def get_user_behavior_summary(self):
        """Return user behavior profile"""
        return {
            "most_used_controls": sorted(
                self.user_profile["action_frequency"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "gesture_count": len(self.gesture_history),
            "interaction_style": self.user_profile["interaction_style"],
            "last_action": self.user_profile["last_action"],
        }

    def get_pending_feedback(self):
        """Get all pending UI feedback (haptic, visual, alerts)"""
        return {
            "haptic_queue": self.haptic_queue,
            "visual_feedback": self.visual_feedback,
            "alerts": self.alerts[-5:],
            "notifications": self.notifications[-5:],
        }

    def clear_feedback(self):
        """Clear pending feedback after delivery"""
        self.haptic_queue = []
        self.visual_feedback = {}

    def _now(self):
        return datetime.utcnow().isoformat() + "Z"

    def get_state(self):
        return {
            "ui_agent": self.name,
            "status": self.status,
            "active_controls": len(self.active_controls),
            "gesture_history": len(self.gesture_history),
            "pending_alerts": len(self.alerts),
            "pending_notifications": len(self.notifications),
            "user_profile": self.user_profile,
        }


ui_agent = UIAgent()
