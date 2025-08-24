"""
Schema para dados de colaboradores
"""

from datetime import date
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator


class EmployeeStatus(str, Enum):
    """Status do colaborador"""
    ACTIVE = "ativo"
    VACATION = "ferias"
    TERMINATED = "desligado"
    ON_LEAVE = "afastado"
    EXTERIOR = "exterior"
    INTERN = "estagiario"
    APPRENTICE = "aprendiz"


class Employee(BaseModel):
    """Schema para dados de colaborador"""
    
    # Identificação
    matricula: str = Field(..., description="Matrícula do colaborador")
    nome: str = Field(..., description="Nome completo do colaborador")
    cpf: Optional[str] = Field(None, description="CPF do colaborador")
    
    # Dados de contrato
    data_admissao: date = Field(..., description="Data de admissão")
    data_desligamento: Optional[date] = Field(None, description="Data de desligamento")
    cargo: str = Field(..., description="Cargo do colaborador")
    
    # Dados de benefícios
    sindicato: str = Field(..., description="Sindicato do colaborador")
    valor_vr: float = Field(0.0, description="Valor do VR por dia")
    
    # Status e exclusões
    status: EmployeeStatus = Field(EmployeeStatus.ACTIVE, description="Status atual")
    elegivel_vr: bool = Field(True, description="Se é elegível para VR")
    
    # Datas especiais
    data_inicio_ferias: Optional[date] = Field(None, description="Início das férias")
    data_fim_ferias: Optional[date] = Field(None, description="Fim das férias")
    data_inicio_afastamento: Optional[date] = Field(None, description="Início do afastamento")
    data_fim_afastamento: Optional[date] = Field(None, description="Fim do afastamento")
    
    # Cálculos
    dias_uteis: int = Field(0, description="Dias úteis no mês")
    dias_ferias: int = Field(0, description="Dias de férias no mês")
    dias_afastamento: int = Field(0, description="Dias de afastamento no mês")
    dias_efetivos: int = Field(0, description="Dias efetivos para VR")
    
    # Valores calculados
    valor_total_vr: float = Field(0.0, description="Valor total de VR")
    valor_empresa: float = Field(0.0, description="Valor pago pela empresa (80%)")
    valor_funcionario: float = Field(0.0, description="Valor descontado do funcionário (20%)")
    
    @validator('cpf')
    def validate_cpf(cls, v):
        """Validar formato do CPF"""
        if v is None:
            return v
        # Remover caracteres especiais
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf
    
    @validator('valor_vr')
    def validate_valor_vr(cls, v):
        """Validar valor do VR"""
        if v < 0:
            raise ValueError('Valor do VR não pode ser negativo')
        return v
    
    @validator('dias_efetivos')
    def calculate_dias_efetivos(cls, v, values):
        """Calcular dias efetivos automaticamente"""
        dias_uteis = values.get('dias_uteis', 0)
        dias_ferias = values.get('dias_ferias', 0)
        dias_afastamento = values.get('dias_afastamento', 0)
        
        return max(0, dias_uteis - dias_ferias - dias_afastamento)
    
    class Config:
        """Configurações do modelo"""
        use_enum_values = True
        validate_assignment = True
