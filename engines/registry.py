from typing import Dict, Type
from core.interfaces import BaseEngine

class EngineRegistry:
    def __init__(self):
        self._engines: Dict[str, BaseEngine] = {}
        
    def register(self, name: str, engine: BaseEngine):
        self._engines[name] = engine
        
    def get_engine(self, name: str) -> BaseEngine:
        if name not in self._engines:
            raise ValueError(f"Engine '{name}' not found in registry.")
        return self._engines[name]

registry = EngineRegistry()
