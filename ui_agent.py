class UIAgent:
    def __init__(self):
        self.gesture_history = 0
        self.pending_alerts = 0
        self.feedback_queue = []
        self.safe_mode = True
        self.strict_mode = False
        self.status = "ONLINE"

    def handle_gesture(self, gesture_type, data):
        """Process user gesture."""
        self.gesture_history += 1
        return {
            "gesture": gesture_type,
            "count": self.gesture_history,
            "data": data
        }

    def show_alert(self, title, message, level="info"):
        """Create an alert notification."""
        self.pending_alerts += 1
        alert = {
            "id": self.pending_alerts,
            "title": title,
            "message": message,
            "level": level
        }
        self.feedback_queue.append(alert)
        return alert

    def get_pending_feedback(self):
        """Get and clear pending feedback."""
        feedback = self.feedback_queue.copy()
        self.feedback_queue.clear()
        self.pending_alerts -= len(feedback)
        return {"feedback": feedback, "count": len(feedback)}

    def get_state(self):
        """Return UI agent state."""
        return {
            "status": self.status,
            "gesture_history": self.gesture_history,
            "pending_alerts": self.pending_alerts,
            "feedback_count": len(self.feedback_queue),
            "safe_mode": self.safe_mode,
            "strict_mode": self.strict_mode,
        }


ui_agent = UIAgent()
