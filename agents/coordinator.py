"""
Agente Coordenador - Orquestra o processamento VR/VA
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

from ..schemas import Employee, Benefit, ValidationResult
from ..utils import ExcelHandler, BusinessRules, DateUtils, CacheManager
from ..config.settings import settings

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    Agente coordenador que orquestra todo o processo de VR/VA
    """
    
    def __init__(self):
        self.excel_handler = ExcelHandler()
        self.business_rules = BusinessRules()
        self.date_utils = DateUtils()
        self.cache_manager = CacheManager()
        self.processing_log = []
        
    def process_vr_va_request(self, 
                            uploaded_files: Dict[str, Any],
                            processing_month: int,
                            processing_year: int,
                            **kwargs) -> Dict[str, Any]:
        """
        Processa uma solicitação completa de VR/VA
        
        Args:
            uploaded_files: Dicionário com arquivos enviados
            processing_month: Mês de processamento
            processing_year: Ano de processamento
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dicionário com resultados do processamento
        """
        try:
            logger.info(f"Iniciando processamento VR/VA para {processing_month}/{processing_year}")
            
            # 1. Validação inicial
            validation_result = self._validate_input_files(uploaded_files)
            if not validation_result['success']:
                return validation_result
            
            # 2. Consolidação de dados
            consolidated_data = self._consolidate_data(uploaded_files)
            if not consolidated_data['success']:
                return consolidated_data
            
            # 3. Aplicação de regras de negócio
            processed_data = self._apply_business_rules(
                consolidated_data['data'], 
                processing_month, 
                processing_year
            )
            if not processed_data['success']:
                return processed_data
            
            # 4. Cálculo de benefícios
            benefits_result = self._calculate_benefits(processed_data['data'])
            if not benefits_result['success']:
                return benefits_result
            
            # 5. Geração de relatório
            report_result = self._generate_report(benefits_result['data'])
            if not report_result['success']:
                return report_result
            
            # 6. Log de sucesso
            self._log_processing_success(processing_month, processing_year)
            
            return {
                'success': True,
                'message': 'Processamento concluído com sucesso',
                'data': {
                    'processed_employees': len(benefits_result['data']),
                    'total_vr_value': benefits_result['total_vr_value'],
                    'report_file': report_result['report_file'],
                    'processing_time': datetime.now().isoformat(),
                    'validation_summary': validation_result['summary']
                },
                'processing_log': self.processing_log
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento: {str(e)}")
            return {
                'success': False,
                'message': f'Erro no processamento: {str(e)}',
                'error': str(e)
            }
    
    def _validate_input_files(self, uploaded_files: Dict[str, Any]) -> Dict[str, Any]:
        """Valida os arquivos de entrada"""
        logger.info("Iniciando validação de arquivos")
        
        required_files = [
            'ativos', 'admissao', 'desligados', 'ferias', 
            'afastamentos', 'estagio', 'aprendiz', 'exterior',
            'base_dias_uteis', 'base_sindicato_valor', 'vr_mensal'
        ]
        
        missing_files = []
        validation_errors = []
        
        for file_name in required_files:
            if file_name not in uploaded_files:
                missing_files.append(file_name)
            else:
                # Validação básica do arquivo
                file_validation = self.excel_handler.validate_file_structure(
                    uploaded_files[file_name]
                )
                if not file_validation['valid']:
                    validation_errors.extend(file_validation['errors'])
        
        if missing_files:
            return {
                'success': False,
                'message': f'Arquivos obrigatórios não encontrados: {missing_files}',
                'missing_files': missing_files
            }
        
        if validation_errors:
            return {
                'success': False,
                'message': 'Erros de validação encontrados',
                'validation_errors': validation_errors
            }
        
        self.processing_log.append({
            'step': 'validation',
            'status': 'success',
            'message': f'Validação concluída: {len(required_files)} arquivos válidos',
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'success': True,
            'message': 'Validação concluída com sucesso',
            'summary': {
                'total_files': len(required_files),
                'valid_files': len(required_files),
                'errors': 0
            }
        }
    
    def _consolidate_data(self, uploaded_files: Dict[str, Any]) -> Dict[str, Any]:
        """Consolida dados de todos os arquivos"""
        logger.info("Iniciando consolidação de dados")
        
        try:
            consolidated_employees = []
            
            # Processar arquivo de ativos
            ativos_df = self.excel_handler.read_excel_file(uploaded_files['ativos'])
            for _, row in ativos_df.iterrows():
                employee = self._create_employee_from_row(row, 'ATIVO')
                consolidated_employees.append(employee)
            
            # Processar admissões
            admissao_df = self.excel_handler.read_excel_file(uploaded_files['admissao'])
            for _, row in admissao_df.iterrows():
                employee = self._create_employee_from_row(row, 'ADMISSAO')
                consolidated_employees.append(employee)
            
            # Processar desligamentos
            desligados_df = self.excel_handler.read_excel_file(uploaded_files['desligados'])
            for _, row in desligados_df.iterrows():
                employee = self._create_employee_from_row(row, 'DESLIGADO')
                consolidated_employees.append(employee)
            
            # Aplicar dados de férias e afastamentos
            self._apply_leave_data(consolidated_employees, uploaded_files)
            
            self.processing_log.append({
                'step': 'consolidation',
                'status': 'success',
                'message': f'Consolidação concluída: {len(consolidated_employees)} funcionários',
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'data': consolidated_employees,
                'message': f'Consolidação concluída: {len(consolidated_employees)} funcionários'
            }
            
        except Exception as e:
            logger.error(f"Erro na consolidação: {str(e)}")
            return {
                'success': False,
                'message': f'Erro na consolidação: {str(e)}'
            }
    
    def _apply_business_rules(self, 
                            employees: List[Employee], 
                            month: int, 
                            year: int) -> Dict[str, Any]:
        """Aplica regras de negócio aos funcionários"""
        logger.info("Aplicando regras de negócio")
        
        try:
            processed_employees = []
            
            for employee in employees:
                # Verificar exclusões
                if self.business_rules.should_exclude_employee(employee):
                    employee.status = 'EXCLUIDO'
                    employee.exclusion_reason = 'Regra de exclusão aplicada'
                    processed_employees.append(employee)
                    continue
                
                # Calcular dias úteis
                working_days = self.business_rules.calculate_employee_working_days(
                    employee, month, year
                )
                employee.working_days = working_days
                
                # Aplicar regras específicas
                employee = self.business_rules.apply_specific_rules(employee, month, year)
                
                processed_employees.append(employee)
            
            self.processing_log.append({
                'step': 'business_rules',
                'status': 'success',
                'message': f'Regras aplicadas: {len(processed_employees)} funcionários',
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'data': processed_employees,
                'message': f'Regras de negócio aplicadas: {len(processed_employees)} funcionários'
            }
            
        except Exception as e:
            logger.error(f"Erro na aplicação de regras: {str(e)}")
            return {
                'success': False,
                'message': f'Erro na aplicação de regras: {str(e)}'
            }
    
    def _calculate_benefits(self, employees: List[Employee]) -> Dict[str, Any]:
        """Calcula benefícios VR/VA para cada funcionário"""
        logger.info("Calculando benefícios VR/VA")
        
        try:
            total_vr_value = 0
            employees_with_benefits = []
            
            for employee in employees:
                if employee.status == 'EXCLUIDO':
                    continue
                
                # Calcular VR
                vr_calculation = self.business_rules.calculate_vr_value(employee)
                
                benefit = Benefit(
                    employee_id=employee.id,
                    benefit_type='VR',
                    daily_value=vr_calculation['daily_value'],
                    working_days=employee.working_days,
                    total_value=vr_calculation['total_value'],
                    company_percentage=settings.DEFAULT_VR_PERCENTAGE_EMPRESA,
                    employee_percentage=settings.DEFAULT_VR_PERCENTAGE_FUNCIONARIO
                )
                
                employee.benefits = [benefit]
                total_vr_value += benefit.total_value
                employees_with_benefits.append(employee)
            
            self.processing_log.append({
                'step': 'benefits_calculation',
                'status': 'success',
                'message': f'Benefícios calculados: R$ {total_vr_value:.2f}',
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'data': employees_with_benefits,
                'total_vr_value': total_vr_value,
                'message': f'Benefícios calculados: R$ {total_vr_value:.2f}'
            }
            
        except Exception as e:
            logger.error(f"Erro no cálculo de benefícios: {str(e)}")
            return {
                'success': False,
                'message': f'Erro no cálculo de benefícios: {str(e)}'
            }
    
    def _generate_report(self, employees: List[Employee]) -> Dict[str, Any]:
        """Gera relatório final"""
        logger.info("Gerando relatório final")
        
        try:
            # Criar DataFrame para relatório
            report_data = []
            
            for employee in employees:
                if not employee.benefits:
                    continue
                    
                for benefit in employee.benefits:
                    report_data.append({
                        'ID_Funcionario': employee.id,
                        'Nome': employee.name,
                        'Cargo': employee.position,
                        'Status': employee.status,
                        'Dias_Uteis': employee.working_days,
                        'Valor_Diario_VR': benefit.daily_value,
                        'Valor_Total_VR': benefit.total_value,
                        'Percentual_Empresa': benefit.company_percentage,
                        'Percentual_Funcionario': benefit.employee_percentage,
                        'Valor_Empresa': benefit.total_value * (benefit.company_percentage / 100),
                        'Valor_Funcionario': benefit.total_value * (benefit.employee_percentage / 100)
                    })
            
            report_df = pd.DataFrame(report_data)
            
            # Salvar relatório
            report_filename = f"relatorio_vr_va_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            report_path = f"data/temp/{report_filename}"
            
            self.excel_handler.save_dataframe_to_excel(
                report_df, 
                report_path, 
                sheet_name='Relatório VR/VA'
            )
            
            self.processing_log.append({
                'step': 'report_generation',
                'status': 'success',
                'message': f'Relatório gerado: {report_filename}',
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'report_file': report_path,
                'message': f'Relatório gerado: {report_filename}'
            }
            
        except Exception as e:
            logger.error(f"Erro na geração do relatório: {str(e)}")
            return {
                'success': False,
                'message': f'Erro na geração do relatório: {str(e)}'
            }
    
    def _create_employee_from_row(self, row: pd.Series, source: str) -> Employee:
        """Cria objeto Employee a partir de uma linha do DataFrame"""
        return Employee(
            id=str(row.get('ID', '')),
            name=str(row.get('Nome', '')),
            position=str(row.get('Cargo', '')),
            status=source,
            admission_date=self.date_utils.parse_date(row.get('Data_Admissao')),
            termination_date=self.date_utils.parse_date(row.get('Data_Desligamento')),
            working_days=0,
            benefits=[],
            exclusion_reason=None
        )
    
    def _apply_leave_data(self, employees: List[Employee], uploaded_files: Dict[str, Any]):
        """Aplica dados de férias e afastamentos"""
        try:
            # Processar férias
            ferias_df = self.excel_handler.read_excel_file(uploaded_files['ferias'])
            for _, row in ferias_df.iterrows():
                employee_id = str(row.get('ID', ''))
                for employee in employees:
                    if employee.id == employee_id:
                        employee.vacation_start = self.date_utils.parse_date(row.get('Inicio_Ferias'))
                        employee.vacation_end = self.date_utils.parse_date(row.get('Fim_Ferias'))
                        break
            
            # Processar afastamentos
            afastamentos_df = self.excel_handler.read_excel_file(uploaded_files['afastamentos'])
            for _, row in afastamentos_df.iterrows():
                employee_id = str(row.get('ID', ''))
                for employee in employees:
                    if employee.id == employee_id:
                        employee.leave_start = self.date_utils.parse_date(row.get('Inicio_Afastamento'))
                        employee.leave_end = self.date_utils.parse_date(row.get('Fim_Afastamento'))
                        break
                        
        except Exception as e:
            logger.warning(f"Erro ao aplicar dados de férias/afastamentos: {str(e)}")
    
    def _log_processing_success(self, month: int, year: int):
        """Registra sucesso do processamento"""
        logger.info(f"Processamento VR/VA concluído com sucesso para {month}/{year}")
        
        # Salvar no cache
        cache_key = f"processing_log_{year}_{month}"
        self.cache_manager.set(cache_key, {
            'processing_log': self.processing_log,
            'timestamp': datetime.now().isoformat(),
            'month': month,
            'year': year
        })
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Retorna status do processamento"""
        return {
            'total_steps': len(self.processing_log),
            'completed_steps': len([log for log in self.processing_log if log['status'] == 'success']),
            'failed_steps': len([log for log in self.processing_log if log['status'] == 'error']),
            'current_step': self.processing_log[-1] if self.processing_log else None,
            'processing_log': self.processing_log
        }
