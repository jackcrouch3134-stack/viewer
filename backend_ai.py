import json
from pathlib import Path


class BackendAI:
    def __init__(self):
        self.compilations = 0
        self.updates = 0
        self.version = "1.0.0"
        self.modules = []
        self.status = "ONLINE"
        self.memory_path = Path(__file__).resolve().parent / "memory.json"
        self.number_pool = {
            "signal_quality": [88, 91, 94, 96, 89, 93, 97],
            "altitude": [420, 610, 780, 950, 1200, 840],
            "temperature": [12, 16, 19, 22, 18, 14],
            "humidity": [41, 54, 63, 48, 58, 67],
            "power": [72, 81, 86, 79, 93, 77],
            "coverage": [72, 81, 89, 93, 87, 90],
        }
        self.pool_index = {key: 0 for key in self.number_pool}
        self.memory = self._load_memory()

    def _load_memory(self):
        """Load durable learning memory from disk."""
        if not self.memory_path.exists():
            return {
                "patterns": {},
                "recent_observations": [],
            }

        try:
            with self.memory_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                return {
                    "patterns": data.get("patterns", {}),
                    "recent_observations": data.get("recent_observations", []),
                }
        except (json.JSONDecodeError, OSError):
            return {"patterns": {}, "recent_observations": []}

    def _save_memory(self):
        """Persist the learning memory so it survives restarts."""
        with self.memory_path.open("w", encoding="utf-8") as handle:
            json.dump(self.memory, handle, indent=2, sort_keys=True)

    def remember_pattern(self, name, value):
        """Record a learned pattern or behavior."""
        patterns = self.memory["patterns"]
        patterns[name] = {"value": value, "count": patterns.get(name, {}).get("count", 0) + 1}
        self.memory["recent_observations"].append({
            "name": name,
            "value": value,
        })
        self.memory["recent_observations"] = self.memory["recent_observations"][-20:]
        self._save_memory()
        return patterns[name]

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

    def compile(self, code):
        """Compile code and return module info."""
        self.compilations += 1
        module_id = f"mod_{self.compilations}"
        signal_quality = self.pull_known_number("signal_quality")
        altitude = self.pull_known_number("altitude")
        temperature = self.pull_known_number("temperature")

        self.remember_pattern("compile_signal_quality", signal_quality)
        self.remember_pattern("compile_altitude", altitude)
        self.remember_pattern("compile_temperature", temperature)

        return {
            "module_id": module_id,
            "version": self.version,
            "code": code[:50],
            "intent": "Autonomous compilation",
            "optimizations": 3,
            "signal_quality": signal_quality,
            "altitude": altitude,
            "temperature": temperature,
        }

    def get_state(self):
        """Return backend AI state."""
        return {
            "status": self.status,
            "compilations": self.compilations,
            "updates": self.updates,
            "version": self.version,
            "modules_count": len(self.modules),
            "modules": self.modules[:5],
            "known_pool": self.get_known_pool(),
            "memory": self.memory,
        }


backend_ai = BackendAI()
