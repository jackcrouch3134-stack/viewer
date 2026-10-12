import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


class LearningEngine:
    def __init__(self, memory_path):
        self.memory_path = Path(memory_path)
        self.memory = self._load_memory()

    def _default_memory(self):
        return {
            "patterns": {},
            "experience": [],
            "recent_observations": [],
            "insights": [],
        }

    def _load_memory(self):
        if not self.memory_path.exists():
            return self._default_memory()

        try:
            with self.memory_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                merged = self._default_memory()
                merged["patterns"] = data.get("patterns", {})
                merged["experience"] = data.get("experience", [])
                merged["recent_observations"] = data.get("recent_observations", [])
                merged["insights"] = data.get("insights", [])
                return merged
        except (json.JSONDecodeError, OSError):
            return self._default_memory()

    def _save_memory(self):
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        with self.memory_path.open("w", encoding="utf-8") as handle:
            json.dump(self.memory, handle, indent=2, sort_keys=True)

    def record_observation(self, context, outcome, signal_quality=None, altitude=None, coverage=None, confidence=0.5, source="system"):
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = {
            "context": str(context),
            "outcome": str(outcome),
            "signal_quality": signal_quality,
            "altitude": altitude,
            "coverage": coverage,
            "confidence": float(confidence),
            "source": str(source),
            "timestamp": timestamp,
        }

        self.memory.setdefault("experience", [])
        self.memory.setdefault("recent_observations", [])
        self.memory.setdefault("patterns", {})
        self.memory.setdefault("insights", [])

        self.memory["experience"].append(entry)
        self.memory["experience"] = self.memory["experience"][-25:]

        self.memory["recent_observations"].append(entry)
        self.memory["recent_observations"] = self.memory["recent_observations"][-20:]

        pattern = self.memory["patterns"].setdefault(context, {
            "count": 0,
            "confidence": 0.0,
            "last_outcome": None,
            "last_seen": timestamp,
        })
        previous_count = max(pattern.get("count", 0), 0)
        previous_confidence = float(pattern.get("confidence", 0.0))
        new_count = previous_count + 1
        pattern["count"] = new_count
        pattern["confidence"] = round(((previous_confidence * previous_count) + float(confidence)) / new_count, 3)
        pattern["last_outcome"] = str(outcome)
        pattern["last_seen"] = timestamp

        if confidence >= 0.7:
            self.memory["insights"] = [
                {
                    "context": str(context),
                    "outcome": str(outcome),
                    "confidence": float(confidence),
                    "timestamp": timestamp,
                }
            ] + self.memory["insights"][:4]

        self._save_memory()
        return entry

    def _parse_time(self, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _rating_for_value(self, value):
        if value is None:
            return "none"
        if value >= 0.85:
            return "high"
        if value >= 0.65:
            return "medium"
        if value >= 0.4:
            return "low"
        return "minimal"

    def _chaos_activity(self, records):
        if not records:
            return 0.0
        import math

        total = 0.0
        previous = None
        for index, record in enumerate(records):
            confidence = float(record.get("confidence", 0.0) or 0.0)
            signal = float(record.get("signal_quality", 0.0) or 0.0) / 100.0
            coverage = float(record.get("coverage", 0.0) or 0.0) / 100.0
            altitude = float(record.get("altitude", 0.0) or 0.0) / 1000.0
            stamp = self._parse_time(record.get("timestamp"))
            phase = 0.0
            if stamp is not None:
                phase = (stamp.microsecond / 1_000_000) + (index + 1)
            volatility = conf = confidence
            if previous is not None:
                volatility += abs(confidence - previous)
            volatility += signal + coverage + altitude
            wave = abs(math.sin((index + 1.0) * 1.618 + phase))
            total += (volatility / 4.0) * (0.5 + wave)
            previous = confidence
        return round(min(1.0, total / max(1, len(records) * 2.5)), 3)

    def summarize(self, period_days=7):
        experience = self.memory.get("experience", [])
        patterns = self.memory.get("patterns", {})
        latest = experience[-1] if experience else None

        top_patterns = []
        for name, data in sorted(patterns.items(), key=lambda item: item[1].get("confidence", 0), reverse=True)[:3]:
            top_patterns.append({
                "context": name,
                "confidence": float(data.get("confidence", 0.0)),
                "count": int(data.get("count", 0)),
                "last_outcome": data.get("last_outcome"),
            })

        window_start = datetime.now(timezone.utc) - timedelta(days=period_days)
        windowed = []
        for record in experience:
            stamp = self._parse_time(record.get("timestamp"))
            if stamp and stamp >= window_start:
                windowed.append(record)

        if windowed:
            avg_confidence = sum(float(item.get("confidence", 0.0)) for item in windowed) / len(windowed)
            chaos_activity = self._chaos_activity(windowed)
            strength = float(avg_confidence)
            severity = min(1.0, strength * 0.9 + chaos_activity * 0.6)
            exp_score = round(min(100.0, max(0.0, (strength * 60.0) + (chaos_activity * 40.0))), 2)
            experience_strength = self._rating_for_value(strength)
            experience_severity = self._rating_for_value(severity)
            experience_count = len(windowed)
        else:
            avg_confidence = 0.0
            strength = 0.0
            severity = 0.0
            chaos_activity = 0.0
            exp_score = 0.0
            experience_strength = "minimal"
            experience_severity = "none"
            experience_count = 0

        confidence = float(latest.get("confidence", 0.0)) if latest else 0.0
        if confidence >= 0.75:
            status = "adaptive"
        elif confidence >= 0.5:
            status = "learning"
        else:
            status = "observing"

        summary = {
            "experience_count": len(experience),
            "window_count": experience_count,
            "latest_pattern": latest.get("context") if latest else "none",
            "latest_outcome": latest.get("outcome") if latest else "none",
            "confidence": round(confidence, 3),
            "status": status,
            "strength": round(strength, 3),
            "strength_rating": experience_strength,
            "severity": round(severity, 3),
            "severity_rating": experience_severity,
            "exp_score": exp_score,
            "chaos_activity": chaos_activity,
            "period_days": period_days,
            "top_patterns": top_patterns,
            "insights": self.memory.get("insights", [])[:5],
        }
        return summary

    def get_adaptive_status(self, period_days=7):
        summary = self.summarize(period_days=period_days)
        base = summary.get("status", "observing")
        return {
            "status": base,
            "confidence": summary.get("confidence", 0.0),
            "latest_pattern": summary.get("latest_pattern", "none"),
            "strength": summary.get("strength", 0.0),
            "strength_rating": summary.get("strength_rating", "minimal"),
            "severity": summary.get("severity", 0.0),
            "severity_rating": summary.get("severity_rating", "none"),
            "exp_score": summary.get("exp_score", 0.0),
            "chaos_activity": summary.get("chaos_activity", 0.0),
            "summary": summary,
        }
