from learning_engine import LearningEngine
from pathlib import Path


class ExperienceEngine:
    def __init__(self, memory_path=None):
        self.memory_path = Path(memory_path) if memory_path else Path(__file__).resolve().parent / "memory.json"
        self.engine = LearningEngine(self.memory_path)

    def record(self, context, outcome, **kwargs):
        return self.engine.record_observation(context=context, outcome=outcome, **kwargs)

    def summary(self):
        return self.engine.summarize()

    def adaptive_status(self):
        return self.engine.get_adaptive_status()
