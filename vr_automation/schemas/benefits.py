"""
Schema para dados de benefícios
"""

from datetime import date
from typing import Optional, Dict, List
from enum import Enum
from pydantic import BaseModel, Field, validator


class BenefitType(str, Enum):
    """Tipos de benefício"""
    VR = "vale_refeicao"
    VA = "vale_alimentacao"


class Benefit(BaseModel):
    """Schema para dados de benefício"""
    
    # Identificação
    tipo: BenefitType = Field(..., description="Tipo do benefício")
    sindicato: str = Field(..., description="Sindicato associado")
    
    # Valores
    valor_diario: float = Field(..., description="Valor diário do benefício")
    valor_mensal: float = Field(0.0, description="Valor mensal calculado")
    
    # Percentuais
    percentual_empresa: float = Field(80.0, description="Percentual pago pela empresa")
    percentual_funcionario: float = Field(20.0, description="Percentual descontado do funcionário")
    
    # Valores calculados
    valor_empresa: float = Field(0.0, description="Valor pago pela empresa")
    valor_funcionario: float = Field(0.0, description="Valor descontado do funcionário")
    
    @validator('valor_diario')
    def validate_valor_diario(cls, v):
        """Validar valor diário"""
        if v < 0:
            raise ValueError('Valor diário não pode ser negativo')
        return v
    
    @validator('percentual_empresa', 'percentual_funcionario')
    def validate_percentuais(cls, v):
        """Validar percentuais"""
        if not 0 <= v <= 100:
            raise ValueError('Percentual deve estar entre 0 e 100')
        return v
    
    def calcular_valores(self, dias_efetivos: int):
        """Calcular valores baseado nos dias efetivos"""
        self.valor_mensal = self.valor_diario * dias_efetivos
        self.valor_empresa = self.valor_mensal * (self.percentual_empresa / 100)
        self.valor_funcionario = self.valor_mensal * (self.percentual_funcionario / 100)
        return self
    
    class Config:
        """Configurações do modelo"""
        use_enum_values = True
        validate_assignment = True


class BenefitCalculation(BaseModel):
    """Schema para cálculo de benefícios"""
    
    # Dados do colaborador
    matricula: str = Field(..., description="Matrícula do colaborador")
    nome: str = Field(..., description="Nome do colaborador")
    
    # Período
    mes: int = Field(..., description="Mês de referência")
    ano: int = Field(..., description="Ano de referência")
    
    # Cálculos
    dias_uteis_mes: int = Field(0, description="Dias úteis no mês")
    dias_efetivos: int = Field(0, description="Dias efetivos para benefício")
    dias_ferias: int = Field(0, description="Dias de férias")
    dias_afastamento: int = Field(0, description="Dias de afastamento")
    
    # Benefícios
    beneficios: List[Benefit] = Field(default_factory=list, description="Lista de benefícios")
    
    # Totais
    valor_total_beneficios: float = Field(0.0, description="Valor total dos benefícios")
    valor_total_empresa: float = Field(0.0, description="Valor total empresa")
    valor_total_funcionario: float = Field(0.0, description="Valor total funcionário")
    
    # Validações
    valido: bool = Field(True, description="Se o cálculo é válido")
    observacoes: List[str] = Field(default_factory=list, description="Observações do cálculo")
    
    def calcular_totais(self):
        """Calcular totais dos benefícios"""
        self.valor_total_beneficios = sum(b.valor_mensal for b in self.beneficios)
        self.valor_total_empresa = sum(b.valor_empresa for b in self.beneficios)
        self.valor_total_funcionario = sum(b.valor_funcionario for b in self.beneficios)
        return self
    
    def adicionar_observacao(self, observacao: str):
        """Adicionar observação ao cálculo"""
        self.observacoes.append(observacao)
        return self
    
    class Config:
        """Configurações do modelo"""
        use_enum_values = True
        validate_assignment = True
