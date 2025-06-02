from abc import ABC, abstractmethod
from typing import Dict, Any

class ModuleGenerator(ABC):
    """Base class for module generators"""
    
    @abstractmethod
    async def generate(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_template(self) -> str:
        pass
