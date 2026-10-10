class BackendAI:
    def __init__(self):
        self.compilations = 0
        self.updates = 0
        self.version = "1.0.0"
        self.modules = []
        self.status = "ONLINE"
        self.last_operation = "idle"

    def compile(self, code):
        """Compile code and return module info."""
        code_text = (code or "").strip()
        self.compilations += 1
        self.updates += 1
        self.last_operation = "compile"
        module_id = f"mod_{self.compilations}"
        return {
            "module_id": module_id,
            "version": self.version,
            "code": code_text[:50],
            "intent": "Autonomous compilation",
            "optimizations": 3,
            "status": "compiled"
        }

    def record_module(self, module):
        """Persist a module in the recent history list."""
        if not isinstance(module, dict):
            return
        self.modules.insert(0, module)
        self.modules = self.modules[:10]

    def get_state(self):
        """Return backend AI state."""
        return {
            "status": self.status,
            "compilations": self.compilations,
            "updates": self.updates,
            "version": self.version,
            "modules_count": len(self.modules),
            "modules": self.modules[:5],
            "last_operation": self.last_operation
        }


backend_ai = BackendAI()
