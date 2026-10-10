from __future__ import annotations

from datetime import datetime
from threading import Lock


class RuntimeStateStore:
    def __init__(self):
        self._lock = Lock()
        self.app_name = "Earth-Aware Satellite Intelligence Platform"
        self.version = "1.1.0"
        self.status = "ONLINE"
        self.started_at = datetime.utcnow().isoformat() + "Z"
        self.events = []
        self.alerts = []
        self.metrics = {
            "requests": 0,
            "compiles": 0,
            "gestures": 0,
            "alerts": 0,
        }

    def record_event(self, event_type, message, details=None):
        entry = {
            "type": event_type,
            "message": message,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        with self._lock:
            self.events.insert(0, entry)
            self.events = self.events[:25]
        return entry

    def get_snapshot(self):
        with self._lock:
            return {
                "app_name": self.app_name,
                "version": self.version,
                "status": self.status,
                "started_at": self.started_at,
                "events": self.events[:10],
                "alerts": self.alerts[:10],
                "metrics": dict(self.metrics),
            }

    def update_metrics(self, **kwargs):
        with self._lock:
            for key, value in kwargs.items():
                if key in self.metrics:
                    self.metrics[key] = value

    def increment_metric(self, key, delta=1):
        with self._lock:
            if key not in self.metrics:
                return
            self.metrics[key] = self.metrics.get(key, 0) + delta

    def set_status(self, status):
        with self._lock:
            self.status = status

    def add_alert(self, title, message, level="info"):
        alert = {"title": title, "message": message, "level": level, "timestamp": datetime.utcnow().isoformat() + "Z"}
        with self._lock:
            self.alerts.insert(0, alert)
            self.alerts = self.alerts[:10]
            self.metrics["alerts"] = len(self.alerts)
        return alert

    def get_event_feed(self):
        with self._lock:
            return list(self.events[:10])
