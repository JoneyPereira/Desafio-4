"""
Gerenciador de cache para o sistema VR/VA
"""

import os
import json
import pickle
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Gerenciador de cache para otimizar performance"""
    
    def __init__(self, cache_dir: str = "data/cache", max_age_hours: int = 24):
        """
        Inicializar gerenciador de cache
        
        Args:
            cache_dir: Diretório de cache
            max_age_hours: Idade máxima do cache em horas
        """
        self.cache_dir = cache_dir
        self.max_age = timedelta(hours=max_age_hours)
        
        # Criar diretório de cache se não existir
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_key(self, key: str) -> str:
        """Gerar chave de cache"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """Obter caminho do arquivo de cache"""
        cache_key = self._get_cache_key(key)
        return os.path.join(self.cache_dir, f"{cache_key}.cache")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Verificar se cache é válido"""
        try:
            if not os.path.exists(cache_path):
                return False
            
            # Verificar idade do arquivo
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
            age = datetime.now() - file_time
            
            return age < self.max_age
            
        except Exception as e:
            logger.warning(f"Erro ao verificar validade do cache: {str(e)}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obter valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor em cache ou None se não encontrado/inválido
        """
        try:
            cache_path = self._get_cache_path(key)
            
            if not self._is_cache_valid(cache_path):
                return None
            
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            logger.debug(f"Cache hit: {key}")
            return data
            
        except Exception as e:
            logger.warning(f"Erro ao ler cache {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Definir valor no cache
        
        Args:
            key: Chave do cache
            value: Valor para armazenar
            
        Returns:
            True se sucesso
        """
        try:
            cache_path = self._get_cache_path(key)
            
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            
            logger.debug(f"Cache set: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao escrever cache {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Deletar valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            True se sucesso
        """
        try:
            cache_path = self._get_cache_path(key)
            
            if os.path.exists(cache_path):
                os.remove(cache_path)
                logger.debug(f"Cache deleted: {key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao deletar cache {key}: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """
        Limpar todo o cache
        
        Returns:
            True se sucesso
        """
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
            
            logger.info("Cache limpo com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obter estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            stats = {
                'total_files': 0,
                'valid_files': 0,
                'expired_files': 0,
                'total_size': 0,
                'cache_dir': self.cache_dir
            }
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    stats['total_files'] += 1
                    stats['total_size'] += os.path.getsize(file_path)
                    
                    if self._is_cache_valid(file_path):
                        stats['valid_files'] += 1
                    else:
                        stats['expired_files'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {str(e)}")
            return {}
    
    def cleanup_expired(self) -> int:
        """
        Limpar arquivos de cache expirados
        
        Returns:
            Número de arquivos removidos
        """
        try:
            removed_count = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    
                    if not self._is_cache_valid(file_path):
                        os.remove(file_path)
                        removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Removidos {removed_count} arquivos de cache expirados")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache expirado: {str(e)}")
            return 0
