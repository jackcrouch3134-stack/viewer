import json
from datetime import datetime, timezone
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

    def summarize(self):
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

        confidence = float(latest.get("confidence", 0.0)) if latest else 0.0
        if confidence >= 0.75:
            status = "adaptive"
        elif confidence >= 0.5:
            status = "learning"
        else:
            status = "observing"

        summary = {
            "experience_count": len(experience),
            "latest_pattern": latest.get("context") if latest else "none",
            "latest_outcome": latest.get("outcome") if latest else "none",
            "confidence": round(confidence, 3),
            "status": status,
            "top_patterns": top_patterns,
            "insights": self.memory.get("insights", [])[:5],
        }
        return summary

    def get_adaptive_status(self):
        summary = self.summarize()
        base = summary.get("status", "observing")
        return {
            "status": base,
            "confidence": summary.get("confidence", 0.0),
            "latest_pattern": summary.get("latest_pattern", "none"),
            "summary": summary,
        }
