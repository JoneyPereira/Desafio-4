"""
Aplicação Streamlit para Automação VR/VA
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import logging

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.excel_handler import ExcelHandler
from utils.business_rules import BusinessRules
from agents import CoordinatorAgent, DataConsolidatorAgent, ValidatorAgent, CalculatorAgent, ReporterAgent
from agents.langchain_agents import CrewAIVRVAOrchestrator, LangChainVRVAAgent
from schemas.employee import Employee, EmployeeStatus
from schemas.benefits import Benefit, BenefitType
from schemas.validation import ValidationResult, ValidationError, ValidationSeverity

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar página
st.set_page_config(
    page_title="🤖 Automação VR/VA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar handlers
@st.cache_resource
def get_excel_handler():
    return ExcelHandler()

@st.cache_resource
def get_business_rules():
    return BusinessRules()

def main():
    """Função principal da aplicação"""
    
    # Header
    st.title("🤖 Automação VR/VA - Sistema Inteligente")
    st.markdown("---")
    
    # Sidebar para upload de arquivos
    with st.sidebar:
        st.header("📁 Upload de Arquivos")
        
        # Upload dos arquivos necessários
        uploaded_files = {
            'ativos': st.file_uploader("Colaboradores Ativos", type=['xlsx'], help="Planilha com colaboradores ativos"),
            'ferias': st.file_uploader("Colaboradores em Férias", type=['xlsx'], help="Planilha com colaboradores em férias"),
            'desligados': st.file_uploader("Colaboradores Desligados", type=['xlsx'], help="Planilha com colaboradores desligados"),
            'admissao': st.file_uploader("Novos Admitidos", type=['xlsx'], help="Planilha com novos admitidos"),
            'afastamentos': st.file_uploader("Afastamentos", type=['xlsx'], help="Planilha com afastamentos"),
            'sindicato': st.file_uploader("Base Sindicato x Valor", type=['xlsx'], help="Planilha com valores por sindicato"),
            'dias_uteis': st.file_uploader("Base Dias Úteis", type=['xlsx'], help="Planilha com dias úteis"),
            'estagio': st.file_uploader("Estagiários", type=['xlsx'], help="Planilha com estagiários"),
            'aprendiz': st.file_uploader("Aprendizes", type=['xlsx'], help="Planilha com aprendizes"),
            'exterior': st.file_uploader("Colaboradores Exterior", type=['xlsx'], help="Planilha com colaboradores no exterior")
        }
        
        st.markdown("---")
        
        # Configurações
        st.header("⚙️ Configurações")
        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox("Mês", range(1, 13), 4, format_func=lambda x: f"{x:02d}")
        with col2:
            year = st.selectbox("Ano", range(2024, 2027), 1)
        
        st.markdown("---")
        
        # Seleção do tipo de agente
        st.header("🤖 Tipo de Agente")
        agent_type = st.radio(
            "Escolha o tipo de processamento:",
            ["Agentes Básicos", "Agentes Avançados (LangChain/CrewAI)"],
            help="Agentes básicos são mais rápidos, agentes avançados oferecem mais recursos de IA"
        )
        
        use_advanced_agents = agent_type == "Agentes Avançados (LangChain/CrewAI)"
        
        if use_advanced_agents:
            st.info("🚀 **Agentes Avançados**: Processamento com LangChain e CrewAI para funcionalidades de IA mais avançadas")
        else:
            st.info("⚡ **Agentes Básicos**: Processamento rápido e eficiente com agentes especializados")
        
        st.markdown("---")
        
        # Botão de processamento
        process_button = st.button("🚀 Processar VR/VA", type="primary", use_container_width=True)
    
    # Área principal
    if process_button:
        # Verificar se todos os arquivos foram uploadados
        missing_files = [name for name, file in uploaded_files.items() if file is None]
        
        if missing_files:
            st.error(f"❌ Arquivos obrigatórios não encontrados: {', '.join(missing_files)}")
            st.info("ℹ️ Por favor, faça upload de todos os arquivos necessários para continuar.")
            return
        
        # Processar arquivos
        process_files(uploaded_files, month, year, use_advanced_agents)
    
    # Mostrar informações iniciais
    else:
        show_welcome_screen()

def show_welcome_screen():
    """Mostrar tela de boas-vindas"""
    
    st.markdown("""
    ## 🎯 Bem-vindo ao Sistema de Automação VR/VA
    
    Este sistema automatiza o processo de cálculo de Vale Refeição (VR/VA) para sua empresa.
    
    ### 📋 Como usar:
    
    1. **Upload de Arquivos**: No painel lateral, faça upload das 10 planilhas necessárias
    2. **Configurações**: Defina o mês e ano de referência
    3. **Processamento**: Clique em "Processar VR/VA" para iniciar a automação
    4. **Resultados**: Visualize e baixe os resultados processados
    
    ### 📊 Arquivos necessários:
    
    - **Colaboradores Ativos**: Lista de colaboradores ativos
    - **Colaboradores em Férias**: Colaboradores em período de férias
    - **Colaboradores Desligados**: Colaboradores que foram desligados
    - **Novos Admitidos**: Colaboradores admitidos no período
    - **Afastamentos**: Colaboradores afastados
    - **Base Sindicato x Valor**: Valores de VR por sindicato
    - **Base Dias Úteis**: Dias úteis por sindicato
    - **Estagiários**: Lista de estagiários
    - **Aprendizes**: Lista de aprendizes
    - **Colaboradores Exterior**: Colaboradores no exterior
    
    ### ⚡ Benefícios:
    
    - ✅ **Automatização completa** do processo manual
    - ✅ **Redução de 90%** no tempo de processamento
    - ✅ **Eliminação de erros** manuais
    - ✅ **Consistência** nos cálculos
    - ✅ **Interface intuitiva** e fácil de usar
    
    ---
    
    **🚀 Pronto para começar? Faça upload dos arquivos no painel lateral!**
    """)

def process_files(uploaded_files, month, year, use_advanced_agents=False):
    """Processar arquivos uploadados usando agentes de IA"""

    if use_advanced_agents:
        return process_files_with_crewai(uploaded_files, month, year)
    else:
        return process_files_with_basic_agents(uploaded_files, month, year)


def process_files_with_basic_agents(uploaded_files, month, year):
    """Processar arquivos usando agentes básicos (implementação original)"""

    # Inicializar agentes
    coordinator = CoordinatorAgent()
    validator = ValidatorAgent()
    consolidator = DataConsolidatorAgent()
    calculator = CalculatorAgent()
    reporter = ReporterAgent()

    # Container para progresso
    progress_container = st.container()

    with progress_container:
        st.header("🤖 Processando Dados com Agentes de IA")

        # Barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Etapa 1: Validar arquivos com agente de validação
            status_text.text("🔍 Agente de Validação: Validando arquivos...")
            progress_bar.progress(10)

            validation_result = validator.validate_uploaded_files(uploaded_files)

            if not validation_result['success']:
                st.error(f"❌ Erro na validação: {validation_result['message']}")
                return

            # Mostrar resultados de validação
            show_validation_results(validation_result['validation_result'])

            # Etapa 2: Consolidar dados com agente de consolidação
            status_text.text("📊 Agente de Consolidação: Consolidando dados...")
            progress_bar.progress(30)

            consolidation_result = consolidator.consolidate_employee_data(uploaded_files)

            if not consolidation_result['success']:
                st.error(f"❌ Erro na consolidação: {consolidation_result['message']}")
                return

            # Etapa 3: Validar dados consolidados
            status_text.text("🔍 Agente de Validação: Validando dados consolidados...")
            progress_bar.progress(50)

            employee_validation = validator.validate_employee_data(consolidation_result['data'])

            if not employee_validation['success']:
                st.warning(f"⚠️ Avisos na validação: {employee_validation['message']}")

            # Etapa 4: Calcular benefícios com agente de cálculo
            status_text.text("💰 Agente de Cálculo: Calculando benefícios...")
            progress_bar.progress(70)

            calculation_result = calculator.calculate_benefits_for_employees(
                consolidation_result['data'], month, year, uploaded_files
            )

            if not calculation_result['success']:
                st.error(f"❌ Erro no cálculo: {calculation_result['message']}")
                return

            # Etapa 5: Gerar relatórios com agente de relatórios
            status_text.text("📋 Agente de Relatórios: Gerando relatórios...")
            progress_bar.progress(90)

            report_result = reporter.generate_comprehensive_report(
                calculation_result['data'], month, year, calculation_result['summary']
            )

            if not report_result['success']:
                st.error(f"❌ Erro na geração de relatórios: {report_result['message']}")
                return

            # Etapa 6: Finalizar
            status_text.text("✅ Processamento concluído com sucesso!")
            progress_bar.progress(100)

            # Mostrar resultados
            show_results_with_agents(report_result, calculation_result, month, year)

        except Exception as e:
            st.error(f"❌ Erro durante o processamento: {str(e)}")
            logger.error(f"Erro no processamento: {str(e)}")
            return


def process_files_with_crewai(uploaded_files, month, year):
    """Processar arquivos usando agentes avançados LangChain/CrewAI"""

    # Container para progresso
    progress_container = st.container()

    with progress_container:
        st.header("🚀 Processando Dados com Agentes Avançados LangChain/CrewAI")

        # Barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Etapa 1: Inicializar orquestrador CrewAI
            status_text.text("🤖 Inicializando Agentes Avançados...")
            progress_bar.progress(10)

            orchestrator = CrewAIVRVAOrchestrator()
            orchestrator.create_agents()
            orchestrator.create_tasks(uploaded_files, month, year)

            # Etapa 2: Executar crew
            status_text.text("🔄 Executando Crew de Agentes...")
            progress_bar.progress(30)

            crew_result = orchestrator.execute_crew()

            if not crew_result['success']:
                st.error(f"❌ Erro na execução do crew: {crew_result['error']}")
                return

            # Etapa 3: Processar resultados
            status_text.text("📊 Processando Resultados...")
            progress_bar.progress(70)

            # Mostrar resultados do crew
            show_crewai_results(crew_result['result'], month, year)

            # Etapa 4: Finalizar
            status_text.text("✅ Processamento com Agentes Avançados concluído!")
            progress_bar.progress(100)

        except Exception as e:
            st.error(f"❌ Erro durante o processamento com CrewAI: {str(e)}")
            logger.error(f"Erro no processamento CrewAI: {str(e)}")
            return

def validate_uploaded_files(uploaded_files, excel_handler):
    """Validar arquivos uploadados"""
    
    validation_results = {}
    
    for file_name, uploaded_file in uploaded_files.items():
        if uploaded_file is not None:
            # Salvar arquivo temporariamente
            temp_path = f"data/temp/{uploaded_file.name}"
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Validar estrutura
            validation_result = excel_handler.validate_excel_structure(temp_path)
            validation_results[file_name] = validation_result
    
    return validation_results

def show_validation_results(validation_result):
    """Mostrar resultados de validação dos agentes"""
    
    st.subheader("🔍 Resultados da Validação - Agente de Validação")
    
    # Mostrar resumo geral
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Arquivos", len(validation_result.file_validations) if hasattr(validation_result, 'file_validations') else 0)
    with col2:
        st.metric("Total de Erros", validation_result.total_erros)
    with col3:
        st.metric("Total de Avisos", validation_result.total_warnings)
    
    # Mostrar validações por arquivo
    if hasattr(validation_result, 'file_validations'):
        for file_name, result in validation_result.file_validations.items():
            with st.expander(f"📄 {file_name.replace('_', ' ').title()}"):
                if result.get("is_valid", True):
                    st.success("✅ Arquivo válido")
                else:
                    st.error("❌ Arquivo com problemas")
                
                if result.get("errors"):
                    st.error("**Erros:**")
                    for error in result["errors"]:
                        st.write(f"- {error}")
                
                if result.get("warnings"):
                    st.warning("**Avisos:**")
                    for warning in result["warnings"]:
                        st.write(f"- {warning}")
    
    # Mostrar validação cruzada
    if hasattr(validation_result, 'cross_validation'):
        with st.expander("🔗 Validação Cruzada"):
            cross_val = validation_result.cross_validation
            if cross_val.get("errors"):
                st.error("**Erros de Validação Cruzada:**")
                for error in cross_val["errors"]:
                    st.write(f"- {error}")
            
            if cross_val.get("warnings"):
                st.warning("**Avisos de Validação Cruzada:**")
                for warning in cross_val["warnings"]:
                    st.write(f"- {warning}")
    
    # Mostrar validação de integridade
    if hasattr(validation_result, 'integrity_validation'):
        with st.expander("🔒 Validação de Integridade"):
            integrity_val = validation_result.integrity_validation
            if integrity_val.get("errors"):
                st.error("**Erros de Integridade:**")
                for error in integrity_val["errors"]:
                    st.write(f"- {error}")
            
            if integrity_val.get("warnings"):
                st.warning("**Avisos de Integridade:**")
                for warning in integrity_val["warnings"]:
                    st.write(f"- {warning}")

def consolidate_data(uploaded_files, excel_handler):
    """Consolidar dados dos arquivos"""
    
    consolidated_data = {}
    
    for file_name, uploaded_file in uploaded_files.items():
        if uploaded_file is not None:
            temp_path = f"data/temp/{uploaded_file.name}"
            df = excel_handler.read_excel_file(temp_path)
            consolidated_data[file_name] = df
    
    return consolidated_data

def apply_business_rules(consolidated_data, business_rules, month, year):
    """Aplicar regras de negócio"""
    
    # Implementar lógica de regras de negócio
    processed_data = consolidated_data.copy()
    
    # Exemplo: aplicar exclusões
    if 'ativos' in processed_data:
        processed_data['ativos'] = business_rules.apply_exclusion_rules(processed_data['ativos'])
    
    return processed_data

def calculate_benefits(processed_data, month, year):
    """Calcular benefícios"""
    
    # Implementar cálculo de benefícios
    calculated_data = processed_data.copy()
    
    # Exemplo: calcular VR
    if 'ativos' in calculated_data:
        calculated_data['ativos'] = calculate_vr_values(calculated_data['ativos'], month, year)
    
    return calculated_data

def calculate_vr_values(df, month, year):
    """Calcular valores de VR"""
    
    # Implementar cálculo específico de VR
    # Por enquanto, retorna o DataFrame original
    return df

def generate_final_report(calculated_data, month, year):
    """Gerar relatório final"""
    
    # Implementar geração do relatório final
    report = {
        'data': calculated_data,
        'month': month,
        'year': year,
        'timestamp': datetime.now(),
        'total_employees': len(calculated_data.get('ativos', pd.DataFrame())),
        'total_vr': 0.0,
        'company_cost': 0.0,
        'employee_deduction': 0.0
    }
    
    return report

def show_results(final_report, month, year):
    """Mostrar resultados finais"""
    
    st.success("✅ Processamento concluído com sucesso!")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Colaboradores", final_report['total_employees'])
    
    with col2:
        st.metric("Valor Total VR", f"R$ {final_report['total_vr']:,.2f}")
    
    with col3:
        st.metric("Custo Empresa", f"R$ {final_report['company_cost']:,.2f}")
    
    with col4:
        st.metric("Desconto Funcionários", f"R$ {final_report['employee_deduction']:,.2f}")
    
    # Download do resultado
    st.subheader("📥 Download dos Resultados")
    
    # Criar arquivo Excel para download
    excel_handler = get_excel_handler()
    
    # Converter dados para formato de download
    download_data = {}
    for key, df in final_report['data'].items():
        if isinstance(df, pd.DataFrame):
            download_data[key] = df
    
    # Gerar arquivo temporário
    output_path = f"data/temp/VR_Mensal_{month:02d}_{year}.xlsx"
    excel_handler.create_formatted_excel(download_data, output_path)
    
    # Botão de download
    with open(output_path, "rb") as file:
        st.download_button(
            label="📥 Download Planilha Final",
            data=file.read(),
            file_name=f"VR_Mensal_{month:02d}_{year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Análise dos dados
    with st.expander("📊 Análise Detalhada"):
        show_detailed_analysis(final_report)

def show_results_with_agents(report_result, calculation_result, month, year):
    """Mostrar resultados finais com agentes de IA"""
    
    st.success("✅ Processamento concluído com sucesso pelos agentes de IA!")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Colaboradores", calculation_result['summary']['total_employees'])
    
    with col2:
        st.metric("Valor Total VR", f"R$ {calculation_result['summary']['total_vr_value']:,.2f}")
    
    with col3:
        st.metric("Funcionários com Benefícios", calculation_result['summary']['employees_with_benefits'])
    
    with col4:
        st.metric("Funcionários Excluídos", calculation_result['summary']['status_distribution'].get('EXCLUIDO', 0))
    
    # Resumo executivo


def show_crewai_results(crew_result, month, year):
    """Mostrar resultados do processamento com CrewAI"""

    st.success("🚀 Processamento com Agentes Avançados concluído!")

    # Resumo dos resultados
    st.subheader("🤖 Resultados dos Agentes Avançados")
    
    # Mostrar resultados de cada agente
    if hasattr(crew_result, 'tasks_outputs'):
        for task_name, task_output in crew_result.tasks_outputs.items():
            st.info(f"**{task_name}**: {task_output}")
    
    # Mostrar resultado final
    if hasattr(crew_result, 'final_output'):
        st.subheader("📋 Resultado Final")
        st.write(crew_result.final_output)
    
    # Detalhes dos agentes CrewAI
    st.subheader("🚀 Agentes CrewAI Utilizados")
    
    crewai_agents = [
        ("🔍 Especialista em Validação", "Validou qualidade e integridade dos dados"),
        ("📊 Especialista em Consolidação", "Consolidou dados de múltiplas fontes"),
        ("💰 Especialista em Cálculos", "Calculou benefícios com regras avançadas"),
        ("📋 Especialista em Relatórios", "Gerou análises e dashboards"),
        ("🎯 Coordenador de Processos", "Orquestrou todo o fluxo de trabalho")
    ]
    
    for agent_name, description in crewai_agents:
        st.success(f"**{agent_name}**: {description}")

    # Comparação de performance
    st.subheader("⚡ Comparação de Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Agentes Básicos**")
        st.write("- Processamento sequencial")
        st.write("- Validações simples")
        st.write("- Cálculos diretos")
    
    with col2:
        st.success("**Agentes Avançados (CrewAI)**")
        st.write("- Processamento paralelo")
        st.write("- Validações inteligentes")
        st.write("- Cálculos com IA")
        st.write("- Análises avançadas")
    st.subheader("📊 Resumo Executivo - Agente de Relatórios")
    
    if 'reports' in report_result and 'executive_summary' in report_result['reports']:
        executive = report_result['reports']['executive_summary']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📈 Estatísticas Gerais:**")
            st.write(f"- Total de funcionários: {executive['total_employees']}")
            st.write(f"- Funcionários com benefícios: {executive['employees_with_benefits']}")
            st.write(f"- Funcionários excluídos: {executive['excluded_employees']}")
            st.write(f"- Valor total VR: R$ {executive['total_vr_value']:,.2f}")
            st.write(f"- Valor empresa: R$ {executive['total_company_value']:,.2f}")
            st.write(f"- Valor funcionário: R$ {executive['total_employee_value']:,.2f}")
        
        with col2:
            st.write("**🏆 Top 5 Funcionários:**")
            for i, emp in enumerate(executive['top_employees'][:5], 1):
                st.write(f"{i}. {emp['name']} - R$ {emp['value']:,.2f}")
    
    # Visualizações
    st.subheader("📈 Visualizações - Agente de Relatórios")
    
    if 'reports' in report_result and 'visualizations' in report_result['reports']:
        viz = report_result['reports']['visualizations']
        
        if not viz.get('error'):
            col1, col2 = st.columns(2)
            
            with col1:
                if 'status_distribution' in viz:
                    st.plotly_chart(viz['status_distribution'], use_container_width=True)
                
                if 'vr_value_histogram' in viz:
                    st.plotly_chart(viz['vr_value_histogram'], use_container_width=True)
            
            with col2:
                if 'top_10_employees' in viz:
                    st.plotly_chart(viz['top_10_employees'], use_container_width=True)
                
                if 'vr_vs_days_scatter' in viz:
                    st.plotly_chart(viz['vr_vs_days_scatter'], use_container_width=True)
    
    # Download do resultado
    st.subheader("📥 Download dos Resultados")
    
    if 'reports' in report_result and 'main_report' in report_result['reports']:
        main_report = report_result['reports']['main_report']
        
        if main_report.get('file_path'):
            # Botão de download
            with open(main_report['file_path'], "rb") as file:
                st.download_button(
                    label="📥 Download Relatório Completo",
                    data=file.read(),
                    file_name=main_report['filename'],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    # Análise detalhada
    with st.expander("📊 Análise Detalhada - Agentes de IA"):
        show_detailed_analysis_with_agents(report_result, calculation_result)

def show_detailed_analysis_with_agents(report_result, calculation_result):
    """Mostrar análise detalhada com agentes de IA"""
    
    st.write("### 📈 Estatísticas dos Agentes")
    
    # Estatísticas do agente de cálculo
    if 'summary' in calculation_result:
        calc_summary = calculation_result['summary']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**💰 Agente de Cálculo:**")
            st.write(f"- Total de funcionários: {calc_summary['total_employees']}")
            st.write(f"- Valor total VR: R$ {calc_summary['total_vr_value']:,.2f}")
            st.write(f"- Valor médio VR: R$ {calc_summary['average_vr_value']:,.2f}")
            
            st.write("**📊 Distribuição por Status:**")
            for status, count in calc_summary['status_distribution'].items():
                st.write(f"- {status}: {count}")
        
        with col2:
            st.write("**📊 Distribuição por Faixa de Valor:**")
            for range_name, count in calc_summary['value_distribution'].items():
                st.write(f"- {range_name}: {count}")
    
    # Estatísticas do agente de relatórios
    if 'reports' in report_result and 'statistical_analysis' in report_result['reports']:
        stats = report_result['reports']['statistical_analysis']
        
        if not stats.get('error'):
            st.write("### 📊 Análise Estatística - Agente de Relatórios")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📈 Estatísticas Descritivas:**")
                st.write(f"- Média: R$ {stats['average_vr_value']:,.2f}")
                st.write(f"- Mediana: R$ {stats['median_vr_value']:,.2f}")
                st.write(f"- Mínimo: R$ {stats['min_vr_value']:,.2f}")
                st.write(f"- Máximo: R$ {stats['max_vr_value']:,.2f}")
                st.write(f"- Desvio Padrão: R$ {stats['std_vr_value']:,.2f}")
            
            with col2:
                st.write("**📊 Distribuição por Dias Úteis:**")
                for days_range, count in stats['days_distribution'].items():
                    st.write(f"- {days_range}: {count}")
                
                st.write(f"**🔗 Correlação VR vs Dias:** {stats['correlation_vr_days']:.3f}")
    
    # Validação do agente de relatórios
    if 'reports' in report_result and 'validation_report' in report_result['reports']:
        validation = report_result['reports']['validation_report']
        
        if not validation.get('error'):
            st.write("### ✅ Validação - Agente de Relatórios")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📋 Resumo da Validação:**")
                st.write(f"- Total de funcionários: {validation['total_employees']}")
                st.write(f"- Total de erros: {validation['total_errors']}")
                st.write(f"- Total de avisos: {validation['total_warnings']}")
                st.write(f"- Válido: {'✅ Sim' if validation['is_valid'] else '❌ Não'}")
            
            with col2:
                if validation['errors']:
                    st.write("**❌ Erros Encontrados:**")
                    for error in validation['errors'][:5]:  # Mostrar apenas os primeiros 5
                        st.write(f"- {error}")
                
                if validation['warnings']:
                    st.write("**⚠️ Avisos:**")
                    for warning in validation['warnings'][:5]:  # Mostrar apenas os primeiros 5
                        st.write(f"- {warning}")

def show_detailed_analysis(final_report):
    """Mostrar análise detalhada"""
    
    st.write("### 📈 Estatísticas Gerais")
    
    # Implementar análise detalhada
    st.write("Análise detalhada será implementada aqui...")

if __name__ == "__main__":
    main()
