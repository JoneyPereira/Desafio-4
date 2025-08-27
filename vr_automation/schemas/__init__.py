"""
Schemas para validação de dados do sistema VR/VA
"""

from .employee import Employee, EmployeeStatus
from .benefits import Benefit, BenefitType, BenefitCalculation
from .validation import ValidationResult, ValidationError, ValidationSeverity

__all__ = [
    'Employee',
    'EmployeeStatus', 
    'Benefit',
    'BenefitType',
    'BenefitCalculation',
    'ValidationResult',
    'ValidationError',
    'ValidationSeverity'
]
