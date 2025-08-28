"""
Agente de Validação - Especializado em validação e qualidade de dados
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

from schemas import Employee, ValidationResult, ValidationError, ValidationSeverity
from utils import ExcelHandler, DateUtils
from config.settings import settings

logger = logging.getLogger(__name__)


class ValidatorAgent:
    """
    Agente especializado em validação e qualidade de dados
    """
    
    def __init__(self):
        self.excel_handler = ExcelHandler()
        self.date_utils = DateUtils()
        self.validation_log = []
        
    def validate_uploaded_files(self, uploaded_files: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida todos os arquivos enviados
        
        Args:
            uploaded_files: Dicionário com arquivos enviados
            
        Returns:
            Dicionário com resultados da validação
        """
        try:
            logger.info("Iniciando validação de arquivos enviados")
            
            validation_results = {}
            total_errors = 0
            total_warnings = 0
            
            # Validar cada arquivo individualmente
            for file_name, file_data in uploaded_files.items():
                file_validation = self._validate_single_file(file_name, file_data)
                validation_results[file_name] = file_validation
                
                total_errors += len(file_validation.get('errors', []))
                total_warnings += len(file_validation.get('warnings', []))
            
            # Validação cruzada entre arquivos
            cross_validation = self._cross_validate_files(uploaded_files)
            
            # Validação de integridade geral
            integrity_validation = self._validate_data_integrity(uploaded_files)
            
            # Consolidar resultados
            overall_validation = ValidationResult(
                arquivo="multiple",
                tipo_validacao="upload",
                valido=total_errors == 0,
                total_erros=total_errors,
                total_warnings=total_warnings,
                linhas_processadas=sum(result.get('total_rows', 0) for result in validation_results.values()),
                linhas_com_erro=0,
                inicio_validacao=datetime.now()
            )
            
            self.validation_log.append({
                'step': 'file_validation_complete',
                'status': 'success' if total_errors == 0 else 'error',
                'message': f'Validação concluída: {total_errors} erros, {total_warnings} avisos',
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'total_files': len(uploaded_files),
                    'total_errors': total_errors,
                    'total_warnings': total_warnings
                }
            })
            
            return {
                'success': True,
                'validation_result': overall_validation,
                'message': f'Validação concluída: {total_errors} erros, {total_warnings} avisos',
                'validation_log': self.validation_log
            }
            
        except Exception as e:
            logger.error(f"Erro na validação: {str(e)}")
            return {
                'success': False,
                'message': f'Erro na validação: {str(e)}',
                'error': str(e)
            }
    
    def validate_employee_data(self, employees: List[Employee]) -> Dict[str, Any]:
        """
        Valida dados de funcionários consolidados
        
        Args:
            employees: Lista de funcionários
            
        Returns:
            Dicionário com resultados da validação
        """
        try:
            logger.info("Validando dados de funcionários")
            
            validation_errors = []
            validation_warnings = []
            
            # Validar cada funcionário
            for employee in employees:
                employee_validation = self._validate_single_employee(employee)
                validation_errors.extend(employee_validation['errors'])
                validation_warnings.extend(employee_validation['warnings'])
            
            # Validações de negócio
            business_validation = self._validate_business_rules(employees)
            validation_errors.extend(business_validation['errors'])
            validation_warnings.extend(business_validation['warnings'])
            
            # Validações de consistência
            consistency_validation = self._validate_data_consistency(employees)
            validation_errors.extend(consistency_validation['errors'])
            validation_warnings.extend(consistency_validation['warnings'])
            
            self.validation_log.append({
                'step': 'employee_validation_complete',
                'status': 'success' if len(validation_errors) == 0 else 'error',
                'message': f'Validação de funcionários: {len(validation_errors)} erros, {len(validation_warnings)} avisos',
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'total_employees': len(employees),
                    'total_errors': len(validation_errors),
                    'total_warnings': len(validation_warnings)
                }
            })
            
            return {
                'success': True,
                'is_valid': len(validation_errors) == 0,
                'errors': validation_errors,
                'warnings': validation_warnings,
                'total_employees': len(employees),
                'message': f'Validação de funcionários: {len(validation_errors)} erros, {len(validation_warnings)} avisos'
            }
            
        except Exception as e:
            logger.error(f"Erro na validação de funcionários: {str(e)}")
            return {
                'success': False,
                'message': f'Erro na validação de funcionários: {str(e)}',
                'error': str(e)
            }
    
    def _validate_single_file(self, file_name: str, file_data: Any) -> Dict[str, Any]:
        """Valida um arquivo individual"""
        logger.info(f"Validando arquivo: {file_name}")
        
        errors = []
        warnings = []
        
        try:
            # Validar estrutura do arquivo
            structure_validation = self.excel_handler.validate_file_structure(file_data)
            if not structure_validation['valid']:
                errors.extend(structure_validation['errors'])
            
            # Validar conteúdo específico do arquivo
            content_validation = self._validate_file_content(file_name, file_data)
            errors.extend(content_validation['errors'])
            warnings.extend(content_validation['warnings'])
            
            # Validar formato de dados
            format_validation = self._validate_data_format(file_name, file_data)
            errors.extend(format_validation['errors'])
            warnings.extend(format_validation['warnings'])
            
        except Exception as e:
            errors.append(f"Erro ao validar arquivo {file_name}: {str(e)}")
        
        return {
            'file_name': file_name,
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_rows': self._count_file_rows(file_data) if file_data else 0
        }
    
    def _validate_file_content(self, file_name: str, file_data: Any) -> Dict[str, Any]:
        """Valida conteúdo específico do arquivo"""
        errors = []
        warnings = []
        
        try:
            df = self.excel_handler.read_excel_file(file_data)
            
            # Validar colunas obrigatórias baseado no tipo de arquivo
            required_columns = self._get_required_columns(file_name)
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                errors.append(f"Colunas obrigatórias ausentes: {missing_columns}")
            
            # Validar se há dados
            if df.empty:
                errors.append("Arquivo vazio")
            elif len(df) < 1:
                warnings.append("Arquivo com poucos registros")
            
            # Validar dados específicos por tipo de arquivo
            specific_validation = self._validate_specific_content(file_name, df)
            errors.extend(specific_validation['errors'])
            warnings.extend(specific_validation['warnings'])
            
        except Exception as e:
            errors.append(f"Erro ao validar conteúdo: {str(e)}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_data_format(self, file_name: str, file_data: Any) -> Dict[str, Any]:
        """Valida formato dos dados"""
        errors = []
        warnings = []
        
        try:
            df = self.excel_handler.read_excel_file(file_data)
            
            # Validar tipos de dados
            for column in df.columns:
                column_validation = self._validate_column_format(file_name, column, df[column])
                errors.extend(column_validation['errors'])
                warnings.extend(column_validation['warnings'])
            
        except Exception as e:
            errors.append(f"Erro ao validar formato: {str(e)}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_column_format(self, file_name: str, column: str, series: pd.Series) -> Dict[str, Any]:
        """Valida formato de uma coluna específica"""
        errors = []
        warnings = []
        
        # Validar IDs
        if 'ID' in column.upper():
            if series.dtype == 'object':
                # Verificar se todos os IDs são únicos
                if series.duplicated().any():
                    errors.append(f"IDs duplicados na coluna {column}")
                
                # Verificar se há IDs vazios
                if series.isna().any() or (series == '').any():
                    warnings.append(f"IDs vazios na coluna {column}")
        
        # Validar datas
        elif 'DATA' in column.upper() or 'DATE' in column.upper():
            for value in series:
                if pd.notna(value):
                    try:
                        self.date_utils.parse_date(value)
                    except:
                        errors.append(f"Data inválida na coluna {column}: {value}")
        
        # Validar valores numéricos
        elif 'VALOR' in column.upper() or 'VALUE' in column.upper():
            for value in series:
                if pd.notna(value):
                    try:
                        float(value)
                    except:
                        errors.append(f"Valor numérico inválido na coluna {column}: {value}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_specific_content(self, file_name: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Validações específicas por tipo de arquivo"""
        errors = []
        warnings = []
        
        if 'ativos' in file_name.lower():
            # Validar funcionários ativos
            if 'Status' in df.columns:
                invalid_status = df[df['Status'] != 'ATIVO']
                if not invalid_status.empty:
                    warnings.append(f"Funcionários com status diferente de ATIVO: {len(invalid_status)}")
        
        elif 'admissao' in file_name.lower():
            # Validar datas de admissão
            if 'Data_Admissao' in df.columns:
                future_dates = df[df['Data_Admissao'] > datetime.now()]
                if not future_dates.empty:
                    warnings.append(f"Datas de admissão futuras: {len(future_dates)}")
        
        elif 'desligados' in file_name.lower():
            # Validar datas de desligamento
            if 'Data_Desligamento' in df.columns:
                future_dates = df[df['Data_Desligamento'] > datetime.now()]
                if not future_dates.empty:
                    warnings.append(f"Datas de desligamento futuras: {len(future_dates)}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _get_required_columns(self, file_name: str) -> List[str]:
        """Retorna colunas obrigatórias para cada tipo de arquivo"""
        if 'ativos' in file_name.lower():
            return ['ID', 'Nome', 'Cargo', 'Status']
        elif 'admissao' in file_name.lower():
            return ['ID', 'Nome', 'Data_Admissao']
        elif 'desligados' in file_name.lower():
            return ['ID', 'Nome', 'Data_Desligamento']
        elif 'ferias' in file_name.lower():
            return ['ID', 'Inicio_Ferias', 'Fim_Ferias']
        elif 'afastamentos' in file_name.lower():
            return ['ID', 'Inicio_Afastamento', 'Fim_Afastamento']
        else:
            return ['ID']  # Mínimo obrigatório
    
    def _count_file_rows(self, file_data: Any) -> int:
        """Conta linhas de um arquivo"""
        try:
            df = self.excel_handler.read_excel_file(file_data)
            return len(df)
        except:
            return 0
    
    def _cross_validate_files(self, uploaded_files: Dict[str, Any]) -> Dict[str, Any]:
        """Validação cruzada entre arquivos"""
        logger.info("Realizando validação cruzada entre arquivos")
        
        errors = []
        warnings = []
        
        try:
            # Verificar consistência de IDs entre arquivos
            all_ids = {}
            
            for file_name, file_data in uploaded_files.items():
                try:
                    df = self.excel_handler.read_excel_file(file_data)
                    if 'ID' in df.columns:
                        file_ids = set(df['ID'].dropna().astype(str))
                        all_ids[file_name] = file_ids
                except Exception as e:
                    warnings.append(f"Erro ao ler IDs do arquivo {file_name}: {str(e)}")
            
            # Verificar IDs duplicados entre arquivos
            if len(all_ids) > 1:
                file_names = list(all_ids.keys())
                for i, file1 in enumerate(file_names):
                    for file2 in file_names[i+1:]:
                        common_ids = all_ids[file1] & all_ids[file2]
                        if common_ids:
                            warnings.append(f"IDs em comum entre {file1} e {file2}: {len(common_ids)}")
            
        except Exception as e:
            errors.append(f"Erro na validação cruzada: {str(e)}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_data_integrity(self, uploaded_files: Dict[str, Any]) -> Dict[str, Any]:
        """Valida integridade geral dos dados"""
        logger.info("Validando integridade dos dados")
        
        errors = []
        warnings = []
        
        try:
            # Verificar se todos os arquivos obrigatórios estão presentes
            required_files = [
                'ativos', 'admissao', 'desligados', 'ferias', 
                'afastamentos', 'estagio', 'aprendiz', 'exterior',
                'base_dias_uteis', 'base_sindicato_valor', 'vr_mensal'
            ]
            
            missing_files = [f for f in required_files if f not in uploaded_files]
            if missing_files:
                errors.append(f"Arquivos obrigatórios ausentes: {missing_files}")
            
            # Verificar tamanho dos arquivos
            for file_name, file_data in uploaded_files.items():
                try:
                    df = self.excel_handler.read_excel_file(file_data)
                    if len(df) > 10000:
                        warnings.append(f"Arquivo {file_name} muito grande: {len(df)} registros")
                except:
                    pass
            
        except Exception as e:
            errors.append(f"Erro na validação de integridade: {str(e)}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_single_employee(self, employee: Employee) -> Dict[str, Any]:
        """Valida um funcionário individual"""
        errors = []
        warnings = []
        
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
        
        # Validar status
        valid_statuses = ['ATIVO', 'ADMISSAO', 'DESLIGADO', 'EXTERIOR', 'EXCLUIDO']
        if employee.status not in valid_statuses:
            warnings.append(f"Status inválido: {employee.status} para {employee.id}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_business_rules(self, employees: List[Employee]) -> Dict[str, Any]:
        """Valida regras de negócio"""
        errors = []
        warnings = []
        
        # Verificar funcionários sem dias úteis
        employees_without_days = [e for e in employees if e.working_days == 0]
        if employees_without_days:
            warnings.append(f"Funcionários sem dias úteis calculados: {len(employees_without_days)}")
        
        # Verificar funcionários excluídos
        excluded_employees = [e for e in employees if e.status == 'EXCLUIDO']
        if excluded_employees:
            warnings.append(f"Funcionários excluídos: {len(excluded_employees)}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_data_consistency(self, employees: List[Employee]) -> Dict[str, Any]:
        """Valida consistência dos dados"""
        errors = []
        warnings = []
        
        # Verificar IDs duplicados
        ids = [e.id for e in employees if e.id]
        duplicate_ids = [id for id in set(ids) if ids.count(id) > 1]
        if duplicate_ids:
            errors.append(f"IDs duplicados: {duplicate_ids}")
        
        # Verificar nomes duplicados
        names = [e.name for e in employees if e.name]
        duplicate_names = [name for name in set(names) if names.count(name) > 1]
        if duplicate_names:
            warnings.append(f"Nomes duplicados: {len(duplicate_names)}")
        
        return {'errors': errors, 'warnings': warnings}
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Retorna resumo da validação"""
        return {
            'total_steps': len(self.validation_log),
            'successful_steps': len([log for log in self.validation_log if log['status'] == 'success']),
            'failed_steps': len([log for log in self.validation_log if log['status'] == 'error']),
            'validation_log': self.validation_log
        }
