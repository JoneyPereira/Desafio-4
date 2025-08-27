"""
Agentes de IA para o sistema VR/VA
"""
from .coordinator import CoordinatorAgent
from .data_consolidator import DataConsolidatorAgent
from .validator import ValidatorAgent
from .calculator import CalculatorAgent
from .reporter import ReporterAgent

# Placeholder para agentes básicos (serão implementados quando necessário)
class CoordinatorAgent:
    def __init__(self):
        pass

class DataConsolidatorAgent:
    def __init__(self):
        pass

class ValidatorAgent:
    def __init__(self):
        pass

class CalculatorAgent:
    def __init__(self):
        pass

class ReporterAgent:
    def __init__(self):
        pass

__all__ = [
    'CoordinatorAgent',
    'DataConsolidatorAgent',
    'ValidatorAgent',
    'CalculatorAgent',
    'ReporterAgent'
]
