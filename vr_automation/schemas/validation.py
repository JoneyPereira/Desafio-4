"""
Schema para validações de dados
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ValidationSeverity(str, Enum):
    """Severidade da validação"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationError(BaseModel):
    """Schema para erro de validação"""
    
    # Identificação
    campo: str = Field(..., description="Campo com erro")
    valor: Any = Field(None, description="Valor que causou o erro")
    
    # Detalhes do erro
    mensagem: str = Field(..., description="Mensagem de erro")
    severidade: ValidationSeverity = Field(ValidationSeverity.ERROR, description="Severidade")
    
    # Contexto
    linha: Optional[int] = Field(None, description="Linha do arquivo")
    coluna: Optional[int] = Field(None, description="Coluna do arquivo")
    arquivo: Optional[str] = Field(None, description="Arquivo de origem")
    
    # Sugestões
    sugestao: Optional[str] = Field(None, description="Sugestão de correção")
    valor_correto: Optional[Any] = Field(None, description="Valor correto sugerido")
    
    # Metadados
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")
    
    class Config:
        """Configurações do modelo"""
        use_enum_values = True


class ValidationResult(BaseModel):
    """Schema para resultado de validação"""
    
    # Identificação
    arquivo: str = Field(..., description="Arquivo validado")
    tipo_validacao: str = Field(..., description="Tipo de validação")
    
    # Resultados
    valido: bool = Field(True, description="Se a validação passou")
    total_erros: int = Field(0, description="Total de erros")
    total_warnings: int = Field(0, description="Total de warnings")
    total_info: int = Field(0, description="Total de informações")
    
    # Detalhes
    erros: List[ValidationError] = Field(default_factory=list, description="Lista de erros")
    warnings: List[ValidationError] = Field(default_factory=list, description="Lista de warnings")
    info: List[ValidationError] = Field(default_factory=list, description="Lista de informações")
    
    # Estatísticas
    linhas_processadas: int = Field(0, description="Total de linhas processadas")
    linhas_com_erro: int = Field(0, description="Linhas com erro")
    percentual_erro: float = Field(0.0, description="Percentual de erro")
    
    # Metadados
    inicio_validacao: datetime = Field(default_factory=datetime.now, description="Início da validação")
    fim_validacao: Optional[datetime] = Field(None, description="Fim da validação")
    tempo_processamento: Optional[float] = Field(None, description="Tempo de processamento em segundos")
    
    def adicionar_erro(self, erro: ValidationError):
        """Adicionar erro à validação"""
        self.erros.append(erro)
        self.total_erros += 1
        self.valido = False
        return self
    
    def adicionar_warning(self, warning: ValidationError):
        """Adicionar warning à validação"""
        self.warnings.append(warning)
        self.total_warnings += 1
        return self
    
    def adicionar_info(self, info: ValidationError):
        """Adicionar informação à validação"""
        self.info.append(info)
        self.total_info += 1
        return self
    
    def finalizar_validacao(self):
        """Finalizar validação e calcular estatísticas"""
        self.fim_validacao = datetime.now()
        if self.inicio_validacao:
            self.tempo_processamento = (self.fim_validacao - self.inicio_validacao).total_seconds()
        
        # Calcular percentual de erro
        if self.linhas_processadas > 0:
            self.percentual_erro = (self.linhas_com_erro / self.linhas_processadas) * 100
        
        return self
    
    def resumo(self) -> Dict[str, Any]:
        """Retornar resumo da validação"""
        return {
            "arquivo": self.arquivo,
            "valido": self.valido,
            "total_erros": self.total_erros,
            "total_warnings": self.total_warnings,
            "total_info": self.total_info,
            "linhas_processadas": self.linhas_processadas,
            "linhas_com_erro": self.linhas_com_erro,
            "percentual_erro": self.percentual_erro,
            "tempo_processamento": self.tempo_processamento
        }
    
    class Config:
        """Configurações do modelo"""
        use_enum_values = True


class ValidationSummary(BaseModel):
    """Schema para resumo de validações"""
    
    # Identificação
    processo: str = Field(..., description="Processo de validação")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do processo")
    
    # Estatísticas gerais
    total_arquivos: int = Field(0, description="Total de arquivos processados")
    arquivos_validos: int = Field(0, description="Arquivos válidos")
    arquivos_com_erro: int = Field(0, description="Arquivos com erro")
    
    # Detalhes
    validacoes: List[ValidationResult] = Field(default_factory=list, description="Lista de validações")
    
    # Totais
    total_erros: int = Field(0, description="Total de erros")
    total_warnings: int = Field(0, description="Total de warnings")
    total_info: int = Field(0, description="Total de informações")
    
    # Performance
    tempo_total: float = Field(0.0, description="Tempo total de processamento")
    
    def adicionar_validacao(self, validacao: ValidationResult):
        """Adicionar validação ao resumo"""
        self.validacoes.append(validacao)
        self.total_arquivos += 1
        
        if validacao.valido:
            self.arquivos_validos += 1
        else:
            self.arquivos_com_erro += 1
        
        self.total_erros += validacao.total_erros
        self.total_warnings += validacao.total_warnings
        self.total_info += validacao.total_info
        
        if validacao.tempo_processamento:
            self.tempo_total += validacao.tempo_processamento
        
        return self
    
    def resumo_final(self) -> Dict[str, Any]:
        """Retornar resumo final"""
        return {
            "processo": self.processo,
            "timestamp": self.timestamp,
            "total_arquivos": self.total_arquivos,
            "arquivos_validos": self.arquivos_validos,
            "arquivos_com_erro": self.arquivos_com_erro,
            "total_erros": self.total_erros,
            "total_warnings": self.total_warnings,
            "total_info": self.total_info,
            "tempo_total": self.tempo_total,
            "percentual_sucesso": (self.arquivos_validos / self.total_arquivos * 100) if self.total_arquivos > 0 else 0
        }
    
    class Config:
        """Configurações do modelo"""
        use_enum_values = True
