import json
import re
from pathlib import Path

from learning_engine import LearningEngine


class BackendAI:
    def __init__(self):
        self.compilations = 0
        self.updates = 0
        self.version = "1.0.0"
        self.modules = []
        self.status = "ONLINE"
        self.memory_path = Path(__file__).resolve().parent / "memory.json"
        self.learning_engine = LearningEngine(self.memory_path)
        self.number_pool = {
            "signal_quality": [88, 91, 94, 96, 89, 93, 97],
            "altitude": [420, 610, 780, 950, 1200, 840],
            "temperature": [12, 16, 19, 22, 18, 14],
            "humidity": [41, 54, 63, 48, 58, 67],
            "power": [72, 81, 86, 79, 93, 77],
            "coverage": [72, 81, 89, 93, 87, 90],
        }
        self.pool_index = {key: 0 for key in self.number_pool}
        self.memory = self.learning_engine.memory

    def _load_memory(self):
        """Load durable learning memory from disk."""
        return self.learning_engine._load_memory()

    def _save_memory(self):
        """Persist the learning memory so it survives restarts."""
        self.learning_engine._save_memory()
        self.memory = self.learning_engine.memory

    def remember_pattern(self, name, value):
        """Record a learned pattern or behavior."""
        pattern = self.learning_engine.record_observation(
            context=name,
            outcome=value,
            signal_quality=value,
            coverage=value,
            altitude=value,
            confidence=0.6,
            source="backend",
        )
        self.memory = self.learning_engine.memory
        return {
            "value": value,
            "count": self.memory["patterns"].get(name, {}).get("count", 0),
            "latest": pattern,
        }

    def pull_known_number(self, key, default=0):
        """Pull the next number from a reusable internal pool."""
        values = self.number_pool.get(key, [])
        if not values:
            return default

        idx = self.pool_index.get(key, 0)
        value = values[idx % len(values)]
        self.pool_index[key] = (idx + 1) % len(values)
        return value

    def get_known_pool(self):
        """Return the complete number pool for the app to reuse."""
        return {key: list(values) for key, values in self.number_pool.items()}

    def _binary_to_readable_text(self, value):
        """Convert raw binary-like strings into a readable code-inspired narrative."""
        if not value:
            return "empty signal"

        cleaned = value.strip()
        if re.fullmatch(r"[01\s]+", cleaned):
            binary_bits = re.findall(r"[01]+", cleaned)
            chunks = []
            for chunk in binary_bits:
                if len(chunk) >= 8:
                    bytes_list = [chunk[i:i + 8] for i in range(0, len(chunk), 8)]
                    for byte in bytes_list:
                        try:
                            chunks.append(chr(int(byte, 2)))
                        except ValueError:
                            continue
            readable = "".join(chunks).strip()
            if readable:
                return readable if readable.isprintable() else "decoded signal ready"

        if len(cleaned) <= 40:
            return cleaned

        return cleaned[:40].rstrip() + "…"

    def _energy_relationship(self, code):
        """Build a lightweight signal-to-language energy model for text translation."""
        if not code:
            return {
                "motivation": "idle",
                "energy": 0.0,
                "translation": "No signal to convert.",
                "readability": 0.0,
                "signal_strength": 0.0,
            }

        normalized = code.strip()
        binary_like = bool(re.search(r"\b[01]{8,}\b", normalized) or re.fullmatch(r"[01\s]+", normalized))
        letters = sum(ch.isalpha() for ch in normalized)
        digits = sum(ch.isdigit() for ch in normalized)
        readable_ratio = min(1.0, letters / max(1, len(normalized)))
        energy = round(min(1.0, (readable_ratio * 0.7) + (0.3 if binary_like else 0.1) + (digits / max(1, len(normalized)) * 0.2)), 3)
        motivation = "stable" if energy >= 0.75 else "adaptive" if energy >= 0.5 else "rebuilding"
        translation = self._binary_to_readable_text(normalized)
        return {
            "motivation": motivation,
            "energy": energy,
            "translation": translation,
            "readability": round(readable_ratio, 3),
            "signal_strength": round(min(1.0, (energy * 0.8) + (readable_ratio * 0.2)), 3),
        }

    def compile(self, code):
        """Compile code and return module info."""
        self.compilations += 1
        module_id = f"mod_{self.compilations}"
        signal_quality = self.pull_known_number("signal_quality")
        altitude = self.pull_known_number("altitude")
        temperature = self.pull_known_number("temperature")
        energy_state = self._energy_relationship(code)

        self.remember_pattern("compile_signal_quality", signal_quality)
        self.remember_pattern("compile_altitude", altitude)
        self.remember_pattern("compile_temperature", temperature)
        self.remember_pattern("readability_bridge", energy_state["readability"])

        return {
            "module_id": module_id,
            "version": self.version,
            "code": code[:50],
            "intent": "Autonomous compilation",
            "optimizations": 3,
            "signal_quality": signal_quality,
            "altitude": altitude,
            "temperature": temperature,
            "energy_relationship": energy_state,
            "readable_translation": energy_state["translation"],
        }

    def get_state(self, period_days=7):
        """Return backend AI state."""
        self.memory = self.learning_engine.memory
        adaptive = self.learning_engine.get_adaptive_status(period_days=period_days)
        latest_module = self.modules[-1] if self.modules else {}
        energy_state = self._energy_relationship(latest_module.get("readable_translation") or latest_module.get("code") or "")
        return {
            "status": self.status,
            "compilations": self.compilations,
            "updates": self.updates,
            "version": self.version,
            "modules_count": len(self.modules),
            "modules": self.modules[:5],
            "known_pool": self.get_known_pool(),
            "memory": self.memory,
            "learning": adaptive,
            "motivation_system": {
                "name": "string motivator",
                "state": energy_state,
            },
        }


backend_ai = BackendAI()
