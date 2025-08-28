"""
Agente de Relatórios - Especializado em geração de relatórios e análises
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from schemas import Employee, Benefit
from utils import ExcelHandler, StreamlitUtils
from config.settings import settings

logger = logging.getLogger(__name__)


class ReporterAgent:
    """
    Agente especializado em geração de relatórios e análises
    """
    
    def __init__(self):
        self.excel_handler = ExcelHandler()
        self.streamlit_utils = StreamlitUtils()
        self.report_log = []
        
    def generate_comprehensive_report(self, 
                                    employees: List[Employee],
                                    processing_month: int,
                                    processing_year: int,
                                    processing_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera relatório abrangente com análises e visualizações
        
        Args:
            employees: Lista de funcionários processados
            processing_month: Mês de processamento
            processing_year: Ano de processamento
            processing_summary: Resumo do processamento
            
        Returns:
            Dicionário com relatórios gerados
        """
        try:
            logger.info("Gerando relatório abrangente")
            
            # 1. Gerar relatório principal (Excel)
            main_report = self._generate_main_excel_report(employees, processing_month, processing_year)
            
            # 2. Gerar relatório de resumo executivo
            executive_summary = self._generate_executive_summary(employees, processing_summary)
            
            # 3. Gerar análises estatísticas
            statistical_analysis = self._generate_statistical_analysis(employees)
            
            # 4. Gerar visualizações
            visualizations = self._generate_visualizations(employees, processing_month, processing_year)
            
            # 5. Gerar relatório de validação
            validation_report = self._generate_validation_report(employees)
            
            # 6. Consolidar todos os relatórios
            consolidated_report = self._consolidate_reports(
                main_report, executive_summary, statistical_analysis, 
                visualizations, validation_report
            )
            
            self.report_log.append({
                'step': 'comprehensive_report_complete',
                'status': 'success',
                'message': 'Relatório abrangente gerado com sucesso',
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'main_report': main_report['file_path'],
                    'total_employees': len(employees),
                    'total_vr_value': sum(
                        benefit.total_value 
                        for employee in employees 
                        for benefit in employee.benefits
                    )
                }
            })
            
            return {
                'success': True,
                'reports': {
                    'main_report': main_report,
                    'executive_summary': executive_summary,
                    'statistical_analysis': statistical_analysis,
                    'visualizations': visualizations,
                    'validation_report': validation_report,
                    'consolidated_report': consolidated_report
                },
                'message': 'Relatório abrangente gerado com sucesso',
                'report_log': self.report_log
            }
            
        except Exception as e:
            logger.error(f"Erro na geração do relatório: {str(e)}")
            return {
                'success': False,
                'message': f'Erro na geração do relatório: {str(e)}',
                'error': str(e)
            }
    
    def _generate_main_excel_report(self, 
                                  employees: List[Employee],
                                  processing_month: int,
                                  processing_year: int) -> Dict[str, Any]:
        """Gera relatório principal em Excel"""
        logger.info("Gerando relatório principal Excel")
        
        try:
            # Criar DataFrame principal
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
                        'Data_Admissao': employee.admission_date,
                        'Data_Desligamento': employee.termination_date,
                        'Dias_Uteis': employee.working_days,
                        'Tipo_Beneficio': benefit.benefit_type.value,
                        'Valor_Diario': benefit.daily_value,
                        'Valor_Total': benefit.total_value,
                        'Percentual_Empresa': benefit.company_percentage,
                        'Percentual_Funcionario': benefit.employee_percentage,
                        'Valor_Empresa': benefit.total_value * (benefit.company_percentage / 100),
                        'Valor_Funcionario': benefit.total_value * (benefit.employee_percentage / 100),
                        'Motivo_Exclusao': employee.exclusion_reason or '',
                        'Inicio_Ferias': employee.vacation_start,
                        'Fim_Ferias': employee.vacation_end,
                        'Inicio_Afastamento': employee.leave_start,
                        'Fim_Afastamento': employee.leave_end
                    })
            
            main_df = pd.DataFrame(report_data)
            
            # Criar resumo por status
            status_summary = main_df.groupby('Status').agg({
                'ID_Funcionario': 'count',
                'Valor_Total': 'sum',
                'Valor_Empresa': 'sum',
                'Valor_Funcionario': 'sum'
            }).reset_index()
            status_summary.columns = ['Status', 'Quantidade', 'Valor_Total', 'Valor_Empresa', 'Valor_Funcionario']
            
            # Criar resumo por cargo
            position_summary = main_df.groupby('Cargo').agg({
                'ID_Funcionario': 'count',
                'Valor_Total': 'sum'
            }).reset_index()
            position_summary.columns = ['Cargo', 'Quantidade', 'Valor_Total']
            
            # Salvar relatório
            report_filename = f"relatorio_vr_va_{processing_year}_{processing_month:02d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            report_path = f"data/temp/{report_filename}"
            
            with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
                main_df.to_excel(writer, sheet_name='Relatório Detalhado', index=False)
                status_summary.to_excel(writer, sheet_name='Resumo por Status', index=False)
                position_summary.to_excel(writer, sheet_name='Resumo por Cargo', index=False)
            
            self.report_log.append({
                'step': 'main_excel_report',
                'status': 'success',
                'message': f'Relatório principal gerado: {report_filename}',
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'file_path': report_path,
                'filename': report_filename,
                'total_records': len(main_df),
                'total_value': main_df['Valor_Total'].sum() if not main_df.empty else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório principal: {str(e)}")
            return {
                'file_path': None,
                'filename': None,
                'error': str(e)
            }
    
    def _generate_executive_summary(self, employees: List[Employee], processing_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo executivo"""
        logger.info("Gerando resumo executivo")
        
        try:
            total_employees = len(employees)
            employees_with_benefits = [e for e in employees if e.benefits]
            excluded_employees = [e for e in employees if e.status == 'EXCLUIDO']
            
            total_vr_value = sum(
                benefit.total_value 
                for employee in employees_with_benefits 
                for benefit in employee.benefits
            )
            
            total_company_value = sum(
                benefit.total_value * (benefit.company_percentage / 100)
                for employee in employees_with_benefits 
                for benefit in employee.benefits
            )
            
            total_employee_value = sum(
                benefit.total_value * (benefit.employee_percentage / 100)
                for employee in employees_with_benefits 
                for benefit in employee.benefits
            )
            
            # Estatísticas por status
            status_stats = {}
            for employee in employees:
                status = employee.status
                if status not in status_stats:
                    status_stats[status] = 0
                status_stats[status] += 1
            
            # Top 10 funcionários por valor
            employee_values = []
            for employee in employees_with_benefits:
                for benefit in employee.benefits:
                    employee_values.append({
                        'id': employee.id,
                        'name': employee.name,
                        'position': employee.position,
                        'value': benefit.total_value
                    })
            
            top_employees = sorted(employee_values, key=lambda x: x['value'], reverse=True)[:10]
            
            executive_summary = {
                'processing_date': datetime.now().isoformat(),
                'total_employees': total_employees,
                'employees_with_benefits': len(employees_with_benefits),
                'excluded_employees': len(excluded_employees),
                'total_vr_value': total_vr_value,
                'total_company_value': total_company_value,
                'total_employee_value': total_employee_value,
                'average_vr_value': total_vr_value / len(employees_with_benefits) if employees_with_benefits else 0,
                'status_distribution': status_stats,
                'top_employees': top_employees,
                'processing_summary': processing_summary
            }
            
            self.report_log.append({
                'step': 'executive_summary',
                'status': 'success',
                'message': 'Resumo executivo gerado',
                'timestamp': datetime.now().isoformat()
            })
            
            return executive_summary
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo executivo: {str(e)}")
            return {'error': str(e)}
    
    def _generate_statistical_analysis(self, employees: List[Employee]) -> Dict[str, Any]:
        """Gera análise estatística"""
        logger.info("Gerando análise estatística")
        
        try:
            employees_with_benefits = [e for e in employees if e.benefits]
            
            if not employees_with_benefits:
                return {'error': 'Nenhum funcionário com benefícios encontrado'}
            
            # Estatísticas básicas
            vr_values = [
                benefit.total_value 
                for employee in employees_with_benefits 
                for benefit in employee.benefits
            ]
            
            working_days = [e.working_days for e in employees_with_benefits]
            
            # Análise por faixas de valor
            value_ranges = {
                '0-100': 0,
                '101-200': 0,
                '201-300': 0,
                '301-400': 0,
                '401-500': 0,
                '500+': 0
            }
            
            for value in vr_values:
                if value <= 100:
                    value_ranges['0-100'] += 1
                elif value <= 200:
                    value_ranges['101-200'] += 1
                elif value <= 300:
                    value_ranges['201-300'] += 1
                elif value <= 400:
                    value_ranges['301-400'] += 1
                elif value <= 500:
                    value_ranges['401-500'] += 1
                else:
                    value_ranges['500+'] += 1
            
            # Análise por faixas de dias úteis
            days_ranges = {
                '0-10': 0,
                '11-15': 0,
                '16-20': 0,
                '21-25': 0,
                '26-31': 0
            }
            
            for days in working_days:
                if days <= 10:
                    days_ranges['0-10'] += 1
                elif days <= 15:
                    days_ranges['11-15'] += 1
                elif days <= 20:
                    days_ranges['16-20'] += 1
                elif days <= 25:
                    days_ranges['21-25'] += 1
                else:
                    days_ranges['26-31'] += 1
            
            statistical_analysis = {
                'total_employees': len(employees_with_benefits),
                'total_vr_value': sum(vr_values),
                'average_vr_value': sum(vr_values) / len(vr_values),
                'median_vr_value': sorted(vr_values)[len(vr_values)//2],
                'min_vr_value': min(vr_values),
                'max_vr_value': max(vr_values),
                'std_vr_value': pd.Series(vr_values).std(),
                'average_working_days': sum(working_days) / len(working_days),
                'value_distribution': value_ranges,
                'days_distribution': days_ranges,
                'correlation_vr_days': pd.Series(vr_values).corr(pd.Series(working_days))
            }
            
            self.report_log.append({
                'step': 'statistical_analysis',
                'status': 'success',
                'message': 'Análise estatística gerada',
                'timestamp': datetime.now().isoformat()
            })
            
            return statistical_analysis
            
        except Exception as e:
            logger.error(f"Erro ao gerar análise estatística: {str(e)}")
            return {'error': str(e)}
    
    def _generate_visualizations(self, employees: List[Employee], month: int, year: int) -> Dict[str, Any]:
        """Gera visualizações gráficas"""
        logger.info("Gerando visualizações")
        
        try:
            employees_with_benefits = [e for e in employees if e.benefits]
            
            if not employees_with_benefits:
                return {'error': 'Nenhum funcionário com benefícios encontrado'}
            
            # Preparar dados para gráficos
            vr_values = [
                benefit.total_value 
                for employee in employees_with_benefits 
                for benefit in employee.benefits
            ]
            
            status_counts = {}
            for employee in employees_with_benefits:
                status = employee.status
                if status not in status_counts:
                    status_counts[status] = 0
                status_counts[status] += 1
            
            position_counts = {}
            for employee in employees_with_benefits:
                position = employee.position or 'Sem Cargo'
                if position not in position_counts:
                    position_counts[position] = 0
                position_counts[position] += 1
            
            # 1. Gráfico de pizza - Distribuição por status
            fig_status = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title=f'Distribuição por Status - {month}/{year}'
            )
            
            # 2. Gráfico de barras - Top 10 funcionários
            top_10_data = []
            for employee in employees_with_benefits:
                for benefit in employee.benefits:
                    top_10_data.append({
                        'Funcionário': f"{employee.name} ({employee.id})",
                        'Valor VR': benefit.total_value
                    })
            
            top_10_df = pd.DataFrame(top_10_data)
            top_10_df = top_10_df.nlargest(10, 'Valor VR')
            
            fig_top10 = px.bar(
                top_10_df,
                x='Valor VR',
                y='Funcionário',
                orientation='h',
                title=f'Top 10 Funcionários por Valor VR - {month}/{year}'
            )
            
            # 3. Histograma - Distribuição de valores VR
            fig_histogram = px.histogram(
                x=vr_values,
                nbins=20,
                title=f'Distribuição de Valores VR - {month}/{year}',
                labels={'x': 'Valor VR (R$)', 'y': 'Quantidade'}
            )
            
            # 4. Gráfico de dispersão - Valor VR vs Dias Úteis
            scatter_data = []
            for employee in employees_with_benefits:
                for benefit in employee.benefits:
                    scatter_data.append({
                        'Dias Úteis': employee.working_days,
                        'Valor VR': benefit.total_value
                    })
            
            scatter_df = pd.DataFrame(scatter_data)
            fig_scatter = px.scatter(
                scatter_df,
                x='Dias Úteis',
                y='Valor VR',
                title=f'Valor VR vs Dias Úteis - {month}/{year}'
            )
            
            # 5. Gráfico de barras - Distribuição por cargo
            fig_position = px.bar(
                x=list(position_counts.keys()),
                y=list(position_counts.values()),
                title=f'Distribuição por Cargo - {month}/{year}',
                labels={'x': 'Cargo', 'y': 'Quantidade'}
            )
            
            visualizations = {
                'status_distribution': fig_status,
                'top_10_employees': fig_top10,
                'vr_value_histogram': fig_histogram,
                'vr_vs_days_scatter': fig_scatter,
                'position_distribution': fig_position
            }
            
            self.report_log.append({
                'step': 'visualizations',
                'status': 'success',
                'message': f'{len(visualizations)} visualizações geradas',
                'timestamp': datetime.now().isoformat()
            })
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Erro ao gerar visualizações: {str(e)}")
            return {'error': str(e)}
    
    def _generate_validation_report(self, employees: List[Employee]) -> Dict[str, Any]:
        """Gera relatório de validação"""
        logger.info("Gerando relatório de validação")
        
        try:
            validation_errors = []
            validation_warnings = []
            
            for employee in employees:
                # Validar dados básicos
                if not employee.id or employee.id.strip() == '':
                    validation_errors.append(f"Funcionário sem ID: {employee.name}")
                
                if not employee.name or employee.name.strip() == '':
                    validation_errors.append(f"Funcionário sem nome: {employee.id}")
                
                # Validar benefícios
                if employee.benefits:
                    for benefit in employee.benefits:
                        if benefit.total_value < 0:
                            validation_errors.append(f"Valor negativo para {employee.id}: {benefit.total_value}")
                        
                        if benefit.daily_value < 0:
                            validation_errors.append(f"Valor diário negativo para {employee.id}: {benefit.daily_value}")
                        
                        # Verificar consistência
                        expected_total = benefit.daily_value * employee.working_days
                        if abs(benefit.total_value - expected_total) > 0.01:
                            validation_warnings.append(f"Inconsistência para {employee.id}: esperado {expected_total}, calculado {benefit.total_value}")
                
                # Validar dias úteis
                if employee.working_days < 0:
                    validation_errors.append(f"Dias úteis negativos para {employee.id}: {employee.working_days}")
                elif employee.working_days > 31:
                    validation_warnings.append(f"Dias úteis muito altos para {employee.id}: {employee.working_days}")
            
            validation_report = {
                'total_employees': len(employees),
                'total_errors': len(validation_errors),
                'total_warnings': len(validation_warnings),
                'is_valid': len(validation_errors) == 0,
                'errors': validation_errors,
                'warnings': validation_warnings,
                'validation_date': datetime.now().isoformat()
            }
            
            self.report_log.append({
                'step': 'validation_report',
                'status': 'success',
                'message': f'Relatório de validação: {len(validation_errors)} erros, {len(validation_warnings)} avisos',
                'timestamp': datetime.now().isoformat()
            })
            
            return validation_report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de validação: {str(e)}")
            return {'error': str(e)}
    
    def _consolidate_reports(self, main_report, executive_summary, statistical_analysis, visualizations, validation_report) -> Dict[str, Any]:
        """Consolida todos os relatórios"""
        logger.info("Consolidando relatórios")
        
        try:
            consolidated_report = {
                'generation_date': datetime.now().isoformat(),
                'main_report': main_report,
                'executive_summary': executive_summary,
                'statistical_analysis': statistical_analysis,
                'visualizations': visualizations,
                'validation_report': validation_report,
                'summary': {
                    'total_reports': 5,
                    'successful_reports': sum([
                        1 if main_report.get('file_path') else 0,
                        1 if executive_summary and not executive_summary.get('error') else 0,
                        1 if statistical_analysis and not statistical_analysis.get('error') else 0,
                        1 if visualizations and not visualizations.get('error') else 0,
                        1 if validation_report and not validation_report.get('error') else 0
                    ]),
                    'total_employees': executive_summary.get('total_employees', 0) if executive_summary else 0,
                    'total_vr_value': executive_summary.get('total_vr_value', 0) if executive_summary else 0
                }
            }
            
            self.report_log.append({
                'step': 'consolidate_reports',
                'status': 'success',
                'message': 'Relatórios consolidados com sucesso',
                'timestamp': datetime.now().isoformat()
            })
            
            return consolidated_report
            
        except Exception as e:
            logger.error(f"Erro ao consolidar relatórios: {str(e)}")
            return {'error': str(e)}
    
    def get_report_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos relatórios"""
        return {
            'total_steps': len(self.report_log),
            'successful_steps': len([log for log in self.report_log if log['status'] == 'success']),
            'failed_steps': len([log for log in self.report_log if log['status'] == 'error']),
            'report_log': self.report_log
        }
