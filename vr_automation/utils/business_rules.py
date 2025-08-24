"""
Utilitário para regras de negócio do sistema VR/VA
"""

import pandas as pd
import numpy as np
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Any
import logging
from dateutil.relativedelta import relativedelta
import calendar

logger = logging.getLogger(__name__)


class BusinessRules:
    """Classe para aplicar regras de negócio"""
    
    def __init__(self):
        """Inicializar regras de negócio"""
        self.exclusion_cargos = [
            'diretor', 'diretores', 'presidente', 'vice-presidente',
            'estagiário', 'estagiaria', 'estagiarios', 'estagiarias',
            'aprendiz', 'aprendizes'
        ]
        
        self.exclusion_status = [
            'licença maternidade', 'licença paternidade', 'licença médica',
            'afastamento', 'suspensão', 'demitido', 'desligado'
        ]
    
    def apply_exclusion_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplicar regras de exclusão no DataFrame
        
        Args:
            df: DataFrame com dados de colaboradores
            
        Returns:
            DataFrame filtrado
        """
        try:
            original_count = len(df)
            
            # Excluir por cargo
            if 'cargo' in df.columns:
                df = df[~df['cargo'].str.lower().isin(self.exclusion_cargos)]
            
            # Excluir por status
            if 'status' in df.columns:
                df = df[~df['status'].str.lower().isin(self.exclusion_status)]
            
            # Excluir estagiários e aprendizes
            if 'tipo_contrato' in df.columns:
                df = df[~df['tipo_contrato'].str.lower().isin(['estagiário', 'aprendiz'])]
            
            filtered_count = len(df)
            excluded_count = original_count - filtered_count
            
            logger.info(f"Exclusões aplicadas: {excluded_count} registros removidos")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao aplicar regras de exclusão: {str(e)}")
            return df
    
    def calculate_working_days(self, month: int, year: int, 
                             holidays: Optional[List[date]] = None) -> int:
        """
        Calcular dias úteis no mês
        
        Args:
            month: Mês (1-12)
            year: Ano
            holidays: Lista de feriados (opcional)
            
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
    
    def calculate_employee_working_days(self, employee_data: Dict[str, Any], 
                                      month: int, year: int) -> int:
        """
        Calcular dias úteis específicos do colaborador
        
        Args:
            employee_data: Dados do colaborador
            month: Mês de referência
            year: Ano de referência
            
        Returns:
            Dias úteis do colaborador
        """
        try:
            # Dias úteis base do mês
            base_working_days = self.calculate_working_days(month, year)
            
            # Ajustes por data de admissão
            if 'data_admissao' in employee_data:
                admission_date = employee_data['data_admissao']
                if isinstance(admission_date, str):
                    admission_date = datetime.strptime(admission_date, '%Y-%m-%d').date()
                
                if admission_date.month == month and admission_date.year == year:
                    # Calcular dias úteis a partir da admissão
                    working_days_from_admission = self.calculate_working_days_from_date(
                        admission_date, month, year
                    )
                    base_working_days = working_days_from_admission
            
            # Ajustes por data de desligamento
            if 'data_desligamento' in employee_data and employee_data['data_desligamento']:
                termination_date = employee_data['data_desligamento']
                if isinstance(termination_date, str):
                    termination_date = datetime.strptime(termination_date, '%Y-%m-%d').date()
                
                if termination_date.month == month and termination_date.year == year:
                    # Verificar regra do dia 15
                    if termination_date.day <= 15:
                        return 0  # Não considerar pagamento
                    else:
                        # Calcular dias úteis até o desligamento
                        working_days_until_termination = self.calculate_working_days_until_date(
                            termination_date, month, year
                        )
                        base_working_days = working_days_until_termination
            
            # Ajustes por férias
            if 'data_inicio_ferias' in employee_data and 'data_fim_ferias' in employee_data:
                vacation_days = self.calculate_vacation_days(
                    employee_data['data_inicio_ferias'],
                    employee_data['data_fim_ferias'],
                    month, year
                )
                base_working_days -= vacation_days
            
            # Ajustes por afastamento
            if 'data_inicio_afastamento' in employee_data and 'data_fim_afastamento' in employee_data:
                leave_days = self.calculate_leave_days(
                    employee_data['data_inicio_afastamento'],
                    employee_data['data_fim_afastamento'],
                    month, year
                )
                base_working_days -= leave_days
            
            return max(0, base_working_days)
            
        except Exception as e:
            logger.error(f"Erro ao calcular dias úteis do colaborador: {str(e)}")
            return 0
    
    def calculate_working_days_from_date(self, start_date: date, month: int, year: int) -> int:
        """Calcular dias úteis a partir de uma data"""
        try:
            # Primeiro dia do mês
            first_day = date(year, month, 1)
            
            # Último dia do mês
            last_day = date(year, month, calendar.monthrange(year, month)[1])
            
            # Ajustar data de início
            actual_start = max(start_date, first_day)
            
            # Calcular dias úteis
            working_days = 0
            current_date = actual_start
            
            while current_date <= last_day:
                if current_date.weekday() < 5:  # Segunda a sexta
                    working_days += 1
                current_date += relativedelta(days=1)
            
            return working_days
            
        except Exception as e:
            logger.error(f"Erro ao calcular dias úteis a partir da data: {str(e)}")
            return 0
    
    def calculate_working_days_until_date(self, end_date: date, month: int, year: int) -> int:
        """Calcular dias úteis até uma data"""
        try:
            # Primeiro dia do mês
            first_day = date(year, month, 1)
            
            # Ajustar data de fim
            actual_end = min(end_date, date(year, month, calendar.monthrange(year, month)[1]))
            
            # Calcular dias úteis
            working_days = 0
            current_date = first_day
            
            while current_date <= actual_end:
                if current_date.weekday() < 5:  # Segunda a sexta
                    working_days += 1
                current_date += relativedelta(days=1)
            
            return working_days
            
        except Exception as e:
            logger.error(f"Erro ao calcular dias úteis até a data: {str(e)}")
            return 0
    
    def calculate_vacation_days(self, start_date: Any, end_date: Any, 
                              month: int, year: int) -> int:
        """Calcular dias de férias no mês"""
        try:
            if not start_date or not end_date:
                return 0
            
            # Converter para date se necessário
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Verificar se as férias estão no mês de referência
            if start_date.month != month or start_date.year != year:
                return 0
            
            # Calcular dias úteis de férias
            vacation_days = 0
            current_date = start_date
            last_day = date(year, month, calendar.monthrange(year, month)[1])
            
            while current_date <= end_date and current_date <= last_day:
                if current_date.weekday() < 5:  # Segunda a sexta
                    vacation_days += 1
                current_date += relativedelta(days=1)
            
            return vacation_days
            
        except Exception as e:
            logger.error(f"Erro ao calcular dias de férias: {str(e)}")
            return 0
    
    def calculate_leave_days(self, start_date: Any, end_date: Any, 
                           month: int, year: int) -> int:
        """Calcular dias de afastamento no mês"""
        try:
            if not start_date or not end_date:
                return 0
            
            # Converter para date se necessário
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Verificar se o afastamento está no mês de referência
            if start_date.month != month or start_date.year != year:
                return 0
            
            # Calcular dias úteis de afastamento
            leave_days = 0
            current_date = start_date
            last_day = date(year, month, calendar.monthrange(year, month)[1])
            
            while current_date <= end_date and current_date <= last_day:
                if current_date.weekday() < 5:  # Segunda a sexta
                    leave_days += 1
                current_date += relativedelta(days=1)
            
            return leave_days
            
        except Exception as e:
            logger.error(f"Erro ao calcular dias de afastamento: {str(e)}")
            return 0
    
    def calculate_vr_value(self, working_days: int, daily_value: float) -> Dict[str, float]:
        """
        Calcular valor de VR
        
        Args:
            working_days: Dias úteis
            daily_value: Valor diário do VR
            
        Returns:
            Dicionário com valores calculados
        """
        try:
            total_value = working_days * daily_value
            company_value = total_value * 0.8  # 80% empresa
            employee_value = total_value * 0.2  # 20% funcionário
            
            return {
                'total_value': total_value,
                'company_value': company_value,
                'employee_value': employee_value,
                'working_days': working_days,
                'daily_value': daily_value
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular valor de VR: {str(e)}")
            return {
                'total_value': 0.0,
                'company_value': 0.0,
                'employee_value': 0.0,
                'working_days': working_days,
                'daily_value': daily_value
            }
    
    def apply_sindicato_rules(self, df: pd.DataFrame, sindicato_data: pd.DataFrame) -> pd.DataFrame:
        """
        Aplicar regras específicas por sindicato
        
        Args:
            df: DataFrame com colaboradores
            sindicato_data: DataFrame com dados dos sindicatos
            
        Returns:
            DataFrame com regras aplicadas
        """
        try:
            # Implementar regras específicas por sindicato
            # Por enquanto, retorna o DataFrame original
            return df
            
        except Exception as e:
            logger.error(f"Erro ao aplicar regras de sindicato: {str(e)}")
            return df
    
    def validate_employee_data(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar dados do colaborador
        
        Args:
            employee_data: Dados do colaborador
            
        Returns:
            Dicionário com resultados da validação
        """
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Validar campos obrigatórios
            required_fields = ['matricula', 'nome', 'data_admissao', 'cargo', 'sindicato']
            
            for field in required_fields:
                if field not in employee_data or not employee_data[field]:
                    validation_result['errors'].append(f"Campo obrigatório '{field}' não informado")
                    validation_result['valid'] = False
            
            # Validar datas
            if 'data_admissao' in employee_data:
                try:
                    if isinstance(employee_data['data_admissao'], str):
                        datetime.strptime(employee_data['data_admissao'], '%Y-%m-%d')
                except:
                    validation_result['errors'].append("Data de admissão inválida")
                    validation_result['valid'] = False
            
            if 'data_desligamento' in employee_data and employee_data['data_desligamento']:
                try:
                    if isinstance(employee_data['data_desligamento'], str):
                        datetime.strptime(employee_data['data_desligamento'], '%Y-%m-%d')
                except:
                    validation_result['errors'].append("Data de desligamento inválida")
                    validation_result['valid'] = False
            
            # Validar valores numéricos
            if 'valor_vr' in employee_data:
                try:
                    valor = float(employee_data['valor_vr'])
                    if valor < 0:
                        validation_result['warnings'].append("Valor de VR negativo")
                except:
                    validation_result['errors'].append("Valor de VR inválido")
                    validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Erro ao validar dados do colaborador: {str(e)}")
            return {
                'valid': False,
                'errors': [f"Erro na validação: {str(e)}"],
                'warnings': []
            }
