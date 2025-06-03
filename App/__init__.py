"""
AI Agent for GCP Web App Generation

An autonomous AI agent that generates complete, working GCP web applications
from natural language requirements with self-healing capabilities.
"""

__version__ = "1.0.0"
__author__ = "Your Organization"
__email__ = "dev@yourcompany.com"
__license__ = "MIT"

# Package metadata
__title__ = "gcp-ai-agent"
__description__ = "Autonomous AI agent for generating GCP web applications"
__url__ = "https://github.com/your-org/gcp-ai-agent"

# Version info tuple
VERSION = (1, 0, 0)

# Import main components for easy access
from app.main import app
from app.config.settings import get_settings
from app.core.planning_agent import PlanningAgent
from app.core.task_execution_engine import TaskExecutionEngine
from app.llm_integration.llm_manager import LLMManager

__all__ = [
    "app",
    "get_settings", 
    "PlanningAgent",
    "TaskExecutionEngine",
    "LLMManager",
    "__version__",
]
