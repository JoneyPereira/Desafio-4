"""
Agente de Cálculo - Especializado em cálculos de benefícios VR/VA
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

from schemas import Employee, Benefit, BenefitType
from utils import BusinessRules, DateUtils, ExcelHandler
from config.settings import settings

logger = logging.getLogger(__name__)


class CalculatorAgent:
    """
    Agente especializado em cálculos de benefícios VR/VA
    """
    
    def __init__(self):
        self.business_rules = BusinessRules()
        self.date_utils = DateUtils()
        self.excel_handler = ExcelHandler()
        self.calculation_log = []
        
    def calculate_benefits_for_employees(self, 
                                       employees: List[Employee],
                                       processing_month: int,
                                       processing_year: int,
                                       uploaded_files: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula benefícios VR/VA para todos os funcionários
        
        Args:
            employees: Lista de funcionários
            processing_month: Mês de processamento
            processing_year: Ano de processamento
            uploaded_files: Arquivos enviados para obter dados de referência
            
        Returns:
            Dicionário com resultados dos cálculos
        """
        try:
            logger.info(f"Iniciando cálculo de benefícios para {len(employees)} funcionários")
            
            # 1. Carregar dados de referência
            reference_data = self._load_reference_data(uploaded_files)
            
            # 2. Aplicar regras de exclusão
            filtered_employees = self._apply_exclusion_rules(employees)
            
            # 3. Calcular dias úteis
            employees_with_days = self._calculate_working_days(
                filtered_employees, processing_month, processing_year, reference_data
            )
            
            # 4. Calcular valores VR/VA
            employees_with_benefits = self._calculate_vr_va_values(
                employees_with_days, reference_data
            )
            
            # 5. Aplicar regras específicas
            final_employees = self._apply_specific_rules(
                employees_with_benefits, processing_month, processing_year
            )
            
            # 6. Gerar resumo dos cálculos
            calculation_summary = self._generate_calculation_summary(final_employees)
            
            self.calculation_log.append({
                'step': 'calculation_complete',
                'status': 'success',
                'message': f'Cálculos concluídos: {len(final_employees)} funcionários processados',
                'timestamp': datetime.now().isoformat(),
                'details': calculation_summary
            })
            
            return {
                'success': True,
                'data': final_employees,
                'summary': calculation_summary,
                'message': f'Cálculos concluídos: {len(final_employees)} funcionários processados',
                'calculation_log': self.calculation_log
            }
            
        except Exception as e:
            logger.error(f"Erro nos cálculos: {str(e)}")
            return {
                'success': False,
                'message': f'Erro nos cálculos: {str(e)}',
                'error': str(e)
            }
    
    def _load_reference_data(self, uploaded_files: Dict[str, Any]) -> Dict[str, Any]:
        """Carrega dados de referência para cálculos"""
        logger.info("Carregando dados de referência")
        
        reference_data = {}
        
        try:
            # Carregar base de dias úteis
            if 'base_dias_uteis' in uploaded_files:
                dias_uteis_df = self.excel_handler.read_excel_file(uploaded_files['base_dias_uteis'])
                reference_data['working_days'] = dias_uteis_df
            
            # Carregar base de sindicato x valor
            if 'base_sindicato_valor' in uploaded_files:
                sindicato_df = self.excel_handler.read_excel_file(uploaded_files['base_sindicato_valor'])
                reference_data['union_values'] = sindicato_df
            
            # Carregar VR mensal
            if 'vr_mensal' in uploaded_files:
                vr_mensal_df = self.excel_handler.read_excel_file(uploaded_files['vr_mensal'])
                reference_data['monthly_vr'] = vr_mensal_df
            
            self.calculation_log.append({
                'step': 'load_reference_data',
                'status': 'success',
                'message': f'Dados de referência carregados: {len(reference_data)} bases',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados de referência: {str(e)}")
            self.calculation_log.append({
                'step': 'load_reference_data',
                'status': 'error',
                'message': f'Erro: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        
        return reference_data
    
    def _apply_exclusion_rules(self, employees: List[Employee]) -> List[Employee]:
        """Aplica regras de exclusão"""
        logger.info("Aplicando regras de exclusão")
        
        filtered_employees = []
        excluded_count = 0
        
        for employee in employees:
            if self.business_rules.should_exclude_employee(employee):
                employee.status = 'EXCLUIDO'
                employee.exclusion_reason = self._get_exclusion_reason(employee)
                excluded_count += 1
            else:
                filtered_employees.append(employee)
        
        self.calculation_log.append({
            'step': 'exclusion_rules',
            'status': 'success',
            'message': f'Regras de exclusão aplicadas: {excluded_count} excluídos',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'total_employees': len(employees),
                'excluded_employees': excluded_count,
                'filtered_employees': len(filtered_employees)
            }
        })
        
        return filtered_employees
    
    def _get_exclusion_reason(self, employee: Employee) -> str:
        """Determina motivo da exclusão"""
        exclusion_reasons = []
        
        # Verificar cargo
        if employee.position:
            position_lower = employee.position.lower()
            if 'diretor' in position_lower or 'presidente' in position_lower:
                exclusion_reasons.append("Cargo de direção")
            elif 'estagiário' in position_lower or 'estagiario' in position_lower:
                exclusion_reasons.append("Estagiário")
            elif 'aprendiz' in position_lower:
                exclusion_reasons.append("Aprendiz")
        
        # Verificar status
        if employee.status == 'EXTERIOR':
            exclusion_reasons.append("Funcionário no exterior")
        
        return "; ".join(exclusion_reasons) if exclusion_reasons else "Regra de exclusão aplicada"
    
    def _calculate_working_days(self, 
                              employees: List[Employee],
                              month: int,
                              year: int,
                              reference_data: Dict[str, Any]) -> List[Employee]:
        """Calcula dias úteis para cada funcionário"""
        logger.info("Calculando dias úteis")
        
        for employee in employees:
            try:
                working_days = self.business_rules.calculate_employee_working_days(
                    employee, month, year
                )
                employee.working_days = working_days
                
            except Exception as e:
                logger.warning(f"Erro ao calcular dias úteis para {employee.id}: {str(e)}")
                employee.working_days = 0
        
        self.calculation_log.append({
            'step': 'working_days_calculation',
            'status': 'success',
            'message': f'Dias úteis calculados para {len(employees)} funcionários',
            'timestamp': datetime.now().isoformat()
        })
        
        return employees
    
    def _calculate_vr_va_values(self, 
                               employees: List[Employee],
                               reference_data: Dict[str, Any]) -> List[Employee]:
        """Calcula valores VR/VA para cada funcionário"""
        logger.info("Calculando valores VR/VA")
        
        total_vr_value = 0
        employees_with_benefits = []
        
        for employee in employees:
            try:
                # Calcular VR
                vr_calculation = self._calculate_vr_value(employee, reference_data)
                
                if vr_calculation:
                    benefit = Benefit(
                        employee_id=employee.id,
                        benefit_type=BenefitType.VR,
                        daily_value=vr_calculation['daily_value'],
                        working_days=employee.working_days,
                        total_value=vr_calculation['total_value'],
                        company_percentage=settings.DEFAULT_VR_PERCENTAGE_EMPRESA,
                        employee_percentage=settings.DEFAULT_VR_PERCENTAGE_FUNCIONARIO
                    )
                    
                    employee.benefits = [benefit]
                    total_vr_value += benefit.total_value
                    employees_with_benefits.append(employee)
                
            except Exception as e:
                logger.warning(f"Erro ao calcular VR para {employee.id}: {str(e)}")
        
        self.calculation_log.append({
            'step': 'vr_va_calculation',
            'status': 'success',
            'message': f'Valores VR/VA calculados: R$ {total_vr_value:.2f}',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'total_vr_value': total_vr_value,
                'employees_with_benefits': len(employees_with_benefits)
            }
        })
        
        return employees_with_benefits
    
    def _calculate_vr_value(self, employee: Employee, reference_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calcula valor VR para um funcionário específico"""
        try:
            # Obter valor diário baseado no sindicato
            daily_value = self._get_daily_vr_value(employee, reference_data)
            
            if daily_value is None:
                # Usar valor padrão
                daily_value = 25.0  # Valor padrão
            
            # Calcular valor total
            total_value = daily_value * employee.working_days
            
            return {
                'daily_value': daily_value,
                'total_value': total_value,
                'working_days': employee.working_days
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular VR para {employee.id}: {str(e)}")
            return None
    
    def _get_daily_vr_value(self, employee: Employee, reference_data: Dict[str, Any]) -> Optional[float]:
        """Obtém valor diário VR baseado no sindicato"""
        try:
            if 'union_values' in reference_data:
                union_df = reference_data['union_values']
                
                # Buscar valor baseado no cargo/sindicato do funcionário
                if 'Cargo' in union_df.columns and 'Valor_Diario' in union_df.columns:
                    for _, row in union_df.iterrows():
                        if employee.position and row['Cargo'].lower() in employee.position.lower():
                            return float(row['Valor_Diario'])
                
                # Se não encontrar, usar valor padrão da tabela
                if 'Valor_Diario' in union_df.columns:
                    return float(union_df['Valor_Diario'].iloc[0])
            
            return None
            
        except Exception as e:
            logger.warning(f"Erro ao obter valor diário VR: {str(e)}")
            return None
    
    def _apply_specific_rules(self, 
                             employees: List[Employee],
                             month: int,
                             year: int) -> List[Employee]:
        """Aplica regras específicas de negócio"""
        logger.info("Aplicando regras específicas")
        
        for employee in employees:
            try:
                # Aplicar regras específicas do funcionário
                employee = self.business_rules.apply_specific_rules(employee, month, year)
                
                # Ajustar benefícios se necessário
                if employee.benefits:
                    for benefit in employee.benefits:
                        # Aplicar limites máximos
                        if benefit.total_value > 1000:  # Limite exemplo
                            benefit.total_value = 1000
                            benefit.daily_value = 1000 / employee.working_days if employee.working_days > 0 else 0
                        
                        # Aplicar valores mínimos
                        if benefit.total_value < 10:  # Valor mínimo exemplo
                            benefit.total_value = 10
                            benefit.daily_value = 10 / employee.working_days if employee.working_days > 0 else 0
                
            except Exception as e:
                logger.warning(f"Erro ao aplicar regras específicas para {employee.id}: {str(e)}")
        
        self.calculation_log.append({
            'step': 'specific_rules',
            'status': 'success',
            'message': f'Regras específicas aplicadas para {len(employees)} funcionários',
            'timestamp': datetime.now().isoformat()
        })
        
        return employees
    
    def _generate_calculation_summary(self, employees: List[Employee]) -> Dict[str, Any]:
        """Gera resumo dos cálculos"""
        total_employees = len(employees)
        total_vr_value = sum(
            benefit.total_value 
            for employee in employees 
            for benefit in employee.benefits
        )
        
        # Estatísticas por status
        status_stats = {}
        for employee in employees:
            status = employee.status
            if status not in status_stats:
                status_stats[status] = 0
            status_stats[status] += 1
        
        # Estatísticas por faixa de valor
        value_ranges = {
            '0-100': 0,
            '101-200': 0,
            '201-300': 0,
            '301+': 0
        }
        
        for employee in employees:
            for benefit in employee.benefits:
                value = benefit.total_value
                if value <= 100:
                    value_ranges['0-100'] += 1
                elif value <= 200:
                    value_ranges['101-200'] += 1
                elif value <= 300:
                    value_ranges['201-300'] += 1
                else:
                    value_ranges['301+'] += 1
        
        return {
            'total_employees': total_employees,
            'total_vr_value': total_vr_value,
            'average_vr_value': total_vr_value / total_employees if total_employees > 0 else 0,
            'status_distribution': status_stats,
            'value_distribution': value_ranges,
            'employees_with_benefits': len([e for e in employees if e.benefits]),
            'employees_without_benefits': len([e for e in employees if not e.benefits])
        }
    
    def validate_calculations(self, employees: List[Employee]) -> Dict[str, Any]:
        """Valida os cálculos realizados"""
        logger.info("Validando cálculos")
        
        errors = []
        warnings = []
        
        for employee in employees:
            # Validar dias úteis
            if employee.working_days < 0:
                errors.append(f"Dias úteis negativos para {employee.id}: {employee.working_days}")
            elif employee.working_days > 31:
                warnings.append(f"Dias úteis muito altos para {employee.id}: {employee.working_days}")
            
            # Validar benefícios
            if employee.benefits:
                for benefit in employee.benefits:
                    if benefit.total_value < 0:
                        errors.append(f"Valor total negativo para {employee.id}: {benefit.total_value}")
                    
                    if benefit.daily_value < 0:
                        errors.append(f"Valor diário negativo para {employee.id}: {benefit.daily_value}")
                    
                    # Verificar consistência
                    expected_total = benefit.daily_value * employee.working_days
                    if abs(benefit.total_value - expected_total) > 0.01:
                        warnings.append(f"Inconsistência no cálculo para {employee.id}: esperado {expected_total}, calculado {benefit.total_value}")
        
        self.calculation_log.append({
            'step': 'calculation_validation',
            'status': 'success' if len(errors) == 0 else 'error',
            'message': f'Validação concluída: {len(errors)} erros, {len(warnings)} avisos',
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_employees_validated': len(employees)
        }
    
    def get_calculation_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos cálculos"""
        return {
            'total_steps': len(self.calculation_log),
            'successful_steps': len([log for log in self.calculation_log if log['status'] == 'success']),
            'failed_steps': len([log for log in self.calculation_log if log['status'] == 'error']),
            'calculation_log': self.calculation_log
        }
