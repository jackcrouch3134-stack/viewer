class UIAgent:
    def __init__(self):
        self.gesture_history = 0
        self.pending_alerts = 0
        self.feedback_queue = []
        self.safe_mode = True
        self.status = "ONLINE"
        self.last_gesture = "idle"

    def handle_gesture(self, gesture_type, data):
        """Process user gesture."""
        if not isinstance(data, dict):
            data = {}
        self.gesture_history += 1
        self.last_gesture = str(gesture_type or "gesture").strip() or "gesture"
        return {
            "gesture": self.last_gesture,
            "count": self.gesture_history,
            "data": data,
            "status": "processed"
        }

    def show_alert(self, title, message, level="info"):
        """Create an alert notification."""
        title_text = str(title or "Alert").strip() or "Alert"
        message_text = str(message or "").strip()
        level_text = str(level or "info").strip() or "info"
        self.pending_alerts += 1
        alert = {
            "id": self.pending_alerts,
            "title": title_text,
            "message": message_text,
            "level": level_text
        }
        self.feedback_queue.append(alert)
        return alert

    def get_pending_feedback(self):
        """Get and clear pending feedback."""
        feedback = self.feedback_queue.copy()
        self.feedback_queue.clear()
        return {"feedback": feedback, "count": len(feedback), "pending_alerts": self.pending_alerts}

    def get_state(self):
        """Return UI agent state."""
        return {
            "status": self.status,
            "gesture_history": self.gesture_history,
            "pending_alerts": self.pending_alerts,
            "safe_mode": self.safe_mode,
            "last_gesture": self.last_gesture
        }


ui_agent = UIAgent()
