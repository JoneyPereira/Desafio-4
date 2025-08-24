"""
Configurações do sistema VR/VA
"""

import os
from typing import Optional


class Settings:
    """Configurações da aplicação"""
    
    def __init__(self):
        # Configurações gerais
        self.DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # Configurações de cache
        self.CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
        self.CACHE_DIR = os.getenv('CACHE_DIR', 'data/cache')
        
        # Configurações de arquivos
        self.MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '52428800'))  # 50MB
        self.TEMP_DIR = os.getenv('TEMP_DIR', 'data/temp')
        
        # Configurações de processamento
        self.BATCH_SIZE = int(os.getenv('BATCH_SIZE', '1000'))
        self.MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
        
        # Configurações de validação
        self.VALIDATION_STRICT = os.getenv('VALIDATION_STRICT', 'True').lower() == 'true'
        self.AUTO_CORRECT = os.getenv('AUTO_CORRECT', 'False').lower() == 'true'
        
        # Configurações de benefícios
        self.DEFAULT_VR_PERCENTAGE_EMPRESA = float(os.getenv('DEFAULT_VR_PERCENTAGE_EMPRESA', '80.0'))
        self.DEFAULT_VR_PERCENTAGE_FUNCIONARIO = float(os.getenv('DEFAULT_VR_PERCENTAGE_FUNCIONARIO', '20.0'))
        
        # Configurações de feriados
        self.HOLIDAYS_FILE = os.getenv('HOLIDAYS_FILE')


# Instância global das configurações
settings = Settings()
