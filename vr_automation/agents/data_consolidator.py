"""
Agente de Consolidação de Dados - Especializado em consolidar dados de múltiplos arquivos
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

from schemas import Employee
from utils import ExcelHandler, DateUtils
from config.settings import settings

logger = logging.getLogger(__name__)


class DataConsolidatorAgent:
    """
    Agente especializado em consolidação e limpeza de dados
    """
    
    def __init__(self):
        self.excel_handler = ExcelHandler()
        self.date_utils = DateUtils()
        self.consolidation_log = []
        
    def consolidate_employee_data(self, uploaded_files: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolida dados de funcionários de múltiplos arquivos
        
        Args:
            uploaded_files: Dicionário com arquivos enviados
            
        Returns:
            Dicionário com dados consolidados
        """
        try:
            logger.info("Iniciando consolidação de dados de funcionários")
            
            # 1. Consolidar funcionários ativos
            active_employees = self._consolidate_active_employees(uploaded_files)
            
            # 2. Consolidar admissões
            admission_employees = self._consolidate_admission_employees(uploaded_files)
            
            # 3. Consolidar desligamentos
            termination_employees = self._consolidate_termination_employees(uploaded_files)
            
            # 4. Aplicar dados complementares
            all_employees = active_employees + admission_employees + termination_employees
            enriched_employees = self._apply_complementary_data(all_employees, uploaded_files)
            
            # 5. Remover duplicatas
            final_employees = self._remove_duplicates(enriched_employees)
            
            # 6. Validar dados consolidados
            validation_result = self._validate_consolidated_data(final_employees)
            
            self.consolidation_log.append({
                'step': 'consolidation_complete',
                'status': 'success',
                'message': f'Consolidação concluída: {len(final_employees)} funcionários únicos',
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'active_employees': len(active_employees),
                    'admission_employees': len(admission_employees),
                    'termination_employees': len(termination_employees),
                    'final_employees': len(final_employees),
                    'validation_errors': len(validation_result.get('errors', []))
                }
            })
            
            return {
                'success': True,
                'data': final_employees,
                'message': f'Consolidação concluída: {len(final_employees)} funcionários',
                'consolidation_log': self.consolidation_log,
                'validation_summary': validation_result
            }
            
        except Exception as e:
            logger.error(f"Erro na consolidação: {str(e)}")
            return {
                'success': False,
                'message': f'Erro na consolidação: {str(e)}',
                'error': str(e)
            }
    
    def _consolidate_active_employees(self, uploaded_files: Dict[str, Any]) -> List[Employee]:
        """Consolida funcionários ativos"""
        logger.info("Consolidando funcionários ativos")
        
        employees = []
        
        try:
            if 'ativos' in uploaded_files:
                ativos_df = self.excel_handler.read_excel_file(uploaded_files['ativos'])
                
                for _, row in ativos_df.iterrows():
                    employee = self._create_employee_from_row(row, 'ATIVO')
                    employees.append(employee)
                    
                self.consolidation_log.append({
                    'step': 'active_employees',
                    'status': 'success',
                    'message': f'Funcionários ativos consolidados: {len(employees)}',
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Erro ao consolidar funcionários ativos: {str(e)}")
            self.consolidation_log.append({
                'step': 'active_employees',
                'status': 'error',
                'message': f'Erro: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        
        return employees
    
    def _consolidate_admission_employees(self, uploaded_files: Dict[str, Any]) -> List[Employee]:
        """Consolida funcionários admitidos no período"""
        logger.info("Consolidando funcionários admitidos")
        
        employees = []
        
        try:
            if 'admissao' in uploaded_files:
                admissao_df = self.excel_handler.read_excel_file(uploaded_files['admissao'])
                
                for _, row in admissao_df.iterrows():
                    employee = self._create_employee_from_row(row, 'ADMISSAO')
                    employees.append(employee)
                    
                self.consolidation_log.append({
                    'step': 'admission_employees',
                    'status': 'success',
                    'message': f'Funcionários admitidos consolidados: {len(employees)}',
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Erro ao consolidar funcionários admitidos: {str(e)}")
            self.consolidation_log.append({
                'step': 'admission_employees',
                'status': 'error',
                'message': f'Erro: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        
        return employees
    
    def _consolidate_termination_employees(self, uploaded_files: Dict[str, Any]) -> List[Employee]:
        """Consolida funcionários desligados no período"""
        logger.info("Consolidando funcionários desligados")
        
        employees = []
        
        try:
            if 'desligados' in uploaded_files:
                desligados_df = self.excel_handler.read_excel_file(uploaded_files['desligados'])
                
                for _, row in desligados_df.iterrows():
                    employee = self._create_employee_from_row(row, 'DESLIGADO')
                    employees.append(employee)
                    
                self.consolidation_log.append({
                    'step': 'termination_employees',
                    'status': 'success',
                    'message': f'Funcionários desligados consolidados: {len(employees)}',
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Erro ao consolidar funcionários desligados: {str(e)}")
            self.consolidation_log.append({
                'step': 'termination_employees',
                'status': 'error',
                'message': f'Erro: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        
        return employees
    
    def _apply_complementary_data(self, employees: List[Employee], uploaded_files: Dict[str, Any]) -> List[Employee]:
        """Aplica dados complementares (férias, afastamentos, etc.)"""
        logger.info("Aplicando dados complementares")
        
        try:
            # Aplicar dados de férias
            self._apply_vacation_data(employees, uploaded_files)
            
            # Aplicar dados de afastamentos
            self._apply_leave_data(employees, uploaded_files)
            
            # Aplicar dados de estágio
            self._apply_internship_data(employees, uploaded_files)
            
            # Aplicar dados de aprendiz
            self._apply_apprentice_data(employees, uploaded_files)
            
            # Aplicar dados de exterior
            self._apply_foreign_data(employees, uploaded_files)
            
            self.consolidation_log.append({
                'step': 'complementary_data',
                'status': 'success',
                'message': 'Dados complementares aplicados',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Erro ao aplicar dados complementares: {str(e)}")
            self.consolidation_log.append({
                'step': 'complementary_data',
                'status': 'error',
                'message': f'Erro: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        
        return employees
    
    def _apply_vacation_data(self, employees: List[Employee], uploaded_files: Dict[str, Any]):
        """Aplica dados de férias"""
        try:
            if 'ferias' in uploaded_files:
                ferias_df = self.excel_handler.read_excel_file(uploaded_files['ferias'])
                
                for _, row in ferias_df.iterrows():
                    employee_id = str(row.get('ID', ''))
                    for employee in employees:
                        if employee.id == employee_id:
                            employee.vacation_start = self.date_utils.parse_date(row.get('Inicio_Ferias'))
                            employee.vacation_end = self.date_utils.parse_date(row.get('Fim_Ferias'))
                            break
                            
        except Exception as e:
            logger.warning(f"Erro ao aplicar dados de férias: {str(e)}")
    
    def _apply_leave_data(self, employees: List[Employee], uploaded_files: Dict[str, Any]):
        """Aplica dados de afastamentos"""
        try:
            if 'afastamentos' in uploaded_files:
                afastamentos_df = self.excel_handler.read_excel_file(uploaded_files['afastamentos'])
                
                for _, row in afastamentos_df.iterrows():
                    employee_id = str(row.get('ID', ''))
                    for employee in employees:
                        if employee.id == employee_id:
                            employee.leave_start = self.date_utils.parse_date(row.get('Inicio_Afastamento'))
                            employee.leave_end = self.date_utils.parse_date(row.get('Fim_Afastamento'))
                            break
                            
        except Exception as e:
            logger.warning(f"Erro ao aplicar dados de afastamentos: {str(e)}")
    
    def _apply_internship_data(self, employees: List[Employee], uploaded_files: Dict[str, Any]):
        """Aplica dados de estágio"""
        try:
            if 'estagio' in uploaded_files:
                estagio_df = self.excel_handler.read_excel_file(uploaded_files['estagio'])
                
                for _, row in estagio_df.iterrows():
                    employee_id = str(row.get('ID', ''))
                    for employee in employees:
                        if employee.id == employee_id:
                            employee.position = 'ESTAGIÁRIO'
                            break
                            
        except Exception as e:
            logger.warning(f"Erro ao aplicar dados de estágio: {str(e)}")
    
    def _apply_apprentice_data(self, employees: List[Employee], uploaded_files: Dict[str, Any]):
        """Aplica dados de aprendiz"""
        try:
            if 'aprendiz' in uploaded_files:
                aprendiz_df = self.excel_handler.read_excel_file(uploaded_files['aprendiz'])
                
                for _, row in aprendiz_df.iterrows():
                    employee_id = str(row.get('ID', ''))
                    for employee in employees:
                        if employee.id == employee_id:
                            employee.position = 'APRENDIZ'
                            break
                            
        except Exception as e:
            logger.warning(f"Erro ao aplicar dados de aprendiz: {str(e)}")
    
    def _apply_foreign_data(self, employees: List[Employee], uploaded_files: Dict[str, Any]):
        """Aplica dados de funcionários no exterior"""
        try:
            if 'exterior' in uploaded_files:
                exterior_df = self.excel_handler.read_excel_file(uploaded_files['exterior'])
                
                for _, row in exterior_df.iterrows():
                    employee_id = str(row.get('ID', ''))
                    for employee in employees:
                        if employee.id == employee_id:
                            employee.status = 'EXTERIOR'
                            break
                            
        except Exception as e:
            logger.warning(f"Erro ao aplicar dados de exterior: {str(e)}")
    
    def _remove_duplicates(self, employees: List[Employee]) -> List[Employee]:
        """Remove funcionários duplicados baseado no ID"""
        logger.info("Removendo duplicatas")
        
        unique_employees = {}
        
        for employee in employees:
            if employee.id not in unique_employees:
                unique_employees[employee.id] = employee
            else:
                # Se já existe, manter o mais recente ou com mais informações
                existing = unique_employees[employee.id]
                if self._should_replace_employee(existing, employee):
                    unique_employees[employee.id] = employee
        
        self.consolidation_log.append({
            'step': 'remove_duplicates',
            'status': 'success',
            'message': f'Duplicatas removidas: {len(employees)} -> {len(unique_employees)}',
            'timestamp': datetime.now().isoformat()
        })
        
        return list(unique_employees.values())
    
    def _should_replace_employee(self, existing: Employee, new: Employee) -> bool:
        """Determina se deve substituir o funcionário existente pelo novo"""
        # Priorizar funcionários ativos
        if new.status == 'ATIVO' and existing.status != 'ATIVO':
            return True
        
        # Priorizar funcionários com mais informações
        existing_info = len(existing.name) + (1 if existing.admission_date else 0)
        new_info = len(new.name) + (1 if new.admission_date else 0)
        
        return new_info > existing_info
    
    def _validate_consolidated_data(self, employees: List[Employee]) -> Dict[str, Any]:
        """Valida dados consolidados"""
        logger.info("Validando dados consolidados")
        
        errors = []
        warnings = []
        
        for employee in employees:
            # Validar ID
            if not employee.id or employee.id.strip() == '':
                errors.append(f"Funcionário sem ID: {employee.name}")
            
            # Validar nome
            if not employee.name or employee.name.strip() == '':
                errors.append(f"Funcionário sem nome: {employee.id}")
            
            # Validar cargo
            if not employee.position or employee.position.strip() == '':
                warnings.append(f"Funcionário sem cargo: {employee.id} - {employee.name}")
            
            # Validar datas
            if employee.admission_date and employee.termination_date:
                if employee.admission_date > employee.termination_date:
                    errors.append(f"Data de admissão posterior à demissão: {employee.id}")
        
        self.consolidation_log.append({
            'step': 'validation',
            'status': 'success',
            'message': f'Validação concluída: {len(errors)} erros, {len(warnings)} avisos',
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'total_employees': len(employees),
            'errors': errors,
            'warnings': warnings,
            'is_valid': len(errors) == 0
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
    
    def get_consolidation_summary(self) -> Dict[str, Any]:
        """Retorna resumo da consolidação"""
        return {
            'total_steps': len(self.consolidation_log),
            'successful_steps': len([log for log in self.consolidation_log if log['status'] == 'success']),
            'failed_steps': len([log for log in self.consolidation_log if log['status'] == 'error']),
            'consolidation_log': self.consolidation_log
        }
