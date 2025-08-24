"""
Agentes de IA para o sistema VR/VA
"""

from .coordinator import CoordinatorAgent
from .data_consolidator import DataConsolidatorAgent
from .validator import ValidatorAgent
from .calculator import CalculatorAgent
from .reporter import ReporterAgent

__all__ = [
    'CoordinatorAgent',
    'DataConsolidatorAgent', 
    'ValidatorAgent',
    'CalculatorAgent',
    'ReporterAgent'
]
