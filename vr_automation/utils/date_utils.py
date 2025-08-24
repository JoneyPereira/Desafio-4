"""
Utilitário para manipulação de datas
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
import calendar
import logging

logger = logging.getLogger(__name__)


class DateUtils:
    """Classe para utilitários de data"""
    
    @staticmethod
    def parse_date(date_str: str, format: str = "%Y-%m-%d") -> Optional[date]:
        """
        Converter string para date
        
        Args:
            date_str: String com a data
            format: Formato da data
            
        Returns:
            Objeto date ou None se inválido
        """
        try:
            return datetime.strptime(date_str, format).date()
        except (ValueError, TypeError):
            logger.warning(f"Data inválida: {date_str}")
            return None
    
    @staticmethod
    def format_date(date_obj: date, format: str = "%Y-%m-%d") -> str:
        """
        Formatar date para string
        
        Args:
            date_obj: Objeto date
            format: Formato desejado
            
        Returns:
            String formatada
        """
        try:
            return date_obj.strftime(format)
        except (AttributeError, TypeError):
            logger.warning(f"Objeto date inválido: {date_obj}")
            return ""
    
    @staticmethod
    def get_month_range(year: int, month: int) -> Tuple[date, date]:
        """
        Obter primeiro e último dia do mês
        
        Args:
            year: Ano
            month: Mês (1-12)
            
        Returns:
            Tupla com primeiro e último dia
        """
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        return first_day, last_day
    
    @staticmethod
    def get_working_days_in_month(year: int, month: int, 
                                holidays: Optional[List[date]] = None) -> int:
        """
        Calcular dias úteis no mês
        
        Args:
            year: Ano
            month: Mês (1-12)
            holidays: Lista de feriados
            
        Returns:
            Número de dias úteis
        """
        try:
            # Obter calendário do mês
            cal = calendar.monthcalendar(year, month)
            
            # Contar dias úteis (segunda a sexta)
            working_days = 0
            for week in cal:
                for day in week[0:5]:  # Segunda a sexta
                    if day != 0:
                        working_days += 1
            
            # Remover feriados
            if holidays:
                for holiday in holidays:
                    if holiday.month == month and holiday.year == year:
                        # Verificar se é dia útil
                        if holiday.weekday() < 5:  # Segunda a sexta
                            working_days -= 1
            
            return working_days
            
        except Exception as e:
            logger.error(f"Erro ao calcular dias úteis: {str(e)}")
            return 0
    
    @staticmethod
    def get_working_days_between(start_date: date, end_date: date,
                               holidays: Optional[List[date]] = None) -> int:
        """
        Calcular dias úteis entre duas datas
        
        Args:
            start_date: Data de início
            end_date: Data de fim
            holidays: Lista de feriados
            
        Returns:
            Número de dias úteis
        """
        try:
            working_days = 0
            current_date = start_date
            
            while current_date <= end_date:
                # Verificar se é dia útil (segunda a sexta)
                if current_date.weekday() < 5:
                    # Verificar se não é feriado
                    if not holidays or current_date not in holidays:
                        working_days += 1
                
                current_date += timedelta(days=1)
            
            return working_days
            
        except Exception as e:
            logger.error(f"Erro ao calcular dias úteis entre datas: {str(e)}")
            return 0
    
    @staticmethod
    def is_working_day(check_date: date, holidays: Optional[List[date]] = None) -> bool:
        """
        Verificar se uma data é dia útil
        
        Args:
            check_date: Data para verificar
            holidays: Lista de feriados
            
        Returns:
            True se for dia útil
        """
        try:
            # Verificar se é fim de semana
            if check_date.weekday() >= 5:  # Sábado ou domingo
                return False
            
            # Verificar se é feriado
            if holidays and check_date in holidays:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar dia útil: {str(e)}")
            return False
    
    @staticmethod
    def get_next_working_day(start_date: date, 
                           holidays: Optional[List[date]] = None) -> date:
        """
        Obter próximo dia útil
        
        Args:
            start_date: Data de início
            holidays: Lista de feriados
            
        Returns:
            Próximo dia útil
        """
        try:
            current_date = start_date + timedelta(days=1)
            
            while not DateUtils.is_working_day(current_date, holidays):
                current_date += timedelta(days=1)
            
            return current_date
            
        except Exception as e:
            logger.error(f"Erro ao obter próximo dia útil: {str(e)}")
            return start_date
    
    @staticmethod
    def get_previous_working_day(start_date: date,
                               holidays: Optional[List[date]] = None) -> date:
        """
        Obter dia útil anterior
        
        Args:
            start_date: Data de início
            holidays: Lista de feriados
            
        Returns:
            Dia útil anterior
        """
        try:
            current_date = start_date - timedelta(days=1)
            
            while not DateUtils.is_working_day(current_date, holidays):
                current_date -= timedelta(days=1)
            
            return current_date
            
        except Exception as e:
            logger.error(f"Erro ao obter dia útil anterior: {str(e)}")
            return start_date
    
    @staticmethod
    def get_month_name(month: int, language: str = "pt_BR") -> str:
        """
        Obter nome do mês
        
        Args:
            month: Mês (1-12)
            language: Idioma
            
        Returns:
            Nome do mês
        """
        try:
            if language == "pt_BR":
                month_names = [
                    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
                ]
            else:
                month_names = [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]
            
            if 1 <= month <= 12:
                return month_names[month - 1]
            else:
                return f"Mês {month}"
                
        except Exception as e:
            logger.error(f"Erro ao obter nome do mês: {str(e)}")
            return f"Mês {month}"
    
    @staticmethod
    def get_quarter(month: int) -> int:
        """
        Obter trimestre do mês
        
        Args:
            month: Mês (1-12)
            
        Returns:
            Trimestre (1-4)
        """
        try:
            return (month - 1) // 3 + 1
        except Exception as e:
            logger.error(f"Erro ao obter trimestre: {str(e)}")
            return 1
    
    @staticmethod
    def is_same_month(date1: date, date2: date) -> bool:
        """
        Verificar se duas datas são do mesmo mês
        
        Args:
            date1: Primeira data
            date2: Segunda data
            
        Returns:
            True se forem do mesmo mês
        """
        try:
            return date1.year == date2.year and date1.month == date2.month
        except Exception as e:
            logger.error(f"Erro ao verificar mesmo mês: {str(e)}")
            return False
    
    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """
        Obter número de dias no mês
        
        Args:
            year: Ano
            month: Mês (1-12)
            
        Returns:
            Número de dias
        """
        try:
            return calendar.monthrange(year, month)[1]
        except Exception as e:
            logger.error(f"Erro ao obter dias no mês: {str(e)}")
            return 30
