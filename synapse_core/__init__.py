"""
Synapse Core - Agente Autónomo de Propósito General
"""

__version__ = "1.0.0"
__author__ = "Synapse Team"

from .config import Config
from .memory import MemoryManager
from .agents import AgentManager

__all__ = ['Config', 'MemoryManager', 'AgentManager']