"""
Demonstração da integração LangChain/CrewAI com o sistema VR/VA
"""

import sys
import os
import logging
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.langchain_agents import CrewAIVRVAOrchestrator, LangChainVRVAAgent
from utils.excel_handler import ExcelHandler
from utils.business_rules import BusinessRules

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_langchain_agent():
    """Testar agente LangChain básico"""
    
    print("🧪 Testando Agente LangChain...")
    
    try:
        # Criar agente de validação
        validator_agent = LangChainVRVAAgent("Validação de Dados")
        
        # Testar execução
        result = validator_agent.execute("Validar estrutura de dados de funcionários")
        
        if result['success']:
            print("✅ Agente LangChain funcionando corretamente!")
            print(f"Resultado: {result['result']}")
        else:
            print(f"❌ Erro no agente LangChain: {result['error']}")
            
    except Exception as e:
        print(f"❌ Erro ao testar agente LangChain: {str(e)}")


def test_crewai_orchestrator():
    """Testar orquestrador CrewAI"""
    
    print("\n🚀 Testando Orquestrador CrewAI...")
    
    try:
        # Criar orquestrador
        orchestrator = CrewAIVRVAOrchestrator()
        
        # Criar agentes
        print("📋 Criando agentes...")
        orchestrator.create_agents()
        
        # Simular arquivos de entrada
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        mock_files = [
            MockFile("colaboradores_ativos.xlsx"),
            MockFile("ferias.xlsx"),
            MockFile("desligados.xlsx")
        ]
        
        # Criar tarefas
        print("📝 Criando tarefas...")
        orchestrator.create_tasks(mock_files, 5, 2024)
        
        print("✅ Orquestrador CrewAI configurado com sucesso!")
        print(f"Agentes criados: {len(orchestrator.agents)}")
        print(f"Tarefas criadas: {len(orchestrator.tasks)}")
        
        # Listar agentes
        print("\n🤖 Agentes disponíveis:")
        for agent_name, agent in orchestrator.agents.items():
            print(f"  - {agent_name}: {agent.role}")
        
        # Listar tarefas
        print("\n📋 Tarefas configuradas:")
        for i, task in enumerate(orchestrator.tasks, 1):
            print(f"  {i}. {task.agent.role}")
            print(f"     Descrição: {task.description[:100]}...")
        
    except Exception as e:
        print(f"❌ Erro ao testar orquestrador CrewAI: {str(e)}")


def test_integration():
    """Testar integração completa"""
    
    print("\n🔗 Testando Integração Completa...")
    
    try:
        # Testar componentes básicos
        print("📊 Testando componentes básicos...")
        
        excel_handler = ExcelHandler()
        business_rules = BusinessRules()
        
        print("✅ Componentes básicos funcionando!")
        
        # Testar agentes LangChain
        test_langchain_agent()
        
        # Testar orquestrador CrewAI
        test_crewai_orchestrator()
        
        print("\n🎉 Integração completa testada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na integração: {str(e)}")


def show_architecture():
    """Mostrar arquitetura dos agentes"""
    
    print("\n🏗️ Arquitetura dos Agentes LangChain/CrewAI")
    print("=" * 60)
    
    print("""
    🤖 Agentes LangChain:
    ├── LangChainVRVAAgent (Base)
    │   ├── ChatOpenAI (LLM)
    │   ├── ConversationBufferMemory
    │   └── AgentExecutor
    │
    🚀 Orquestrador CrewAI:
    ├── CrewAIVRVAOrchestrator
    │   ├── Agent (Validador)
    │   ├── Agent (Consolidador)
    │   ├── Agent (Calculador)
    │   ├── Agent (Relator)
    │   └── Agent (Coordenador)
    │
    🛠️ Ferramentas:
    ├── ValidationTool
    ├── ConsolidationTool
    ├── CalculationTool
    ├── ReportingTool
    ├── CoordinationTool
    ├── DataQualityTool
    ├── DataCleaningTool
    ├── BusinessRulesTool
    └── VisualizationTool
    """)


def show_benefits():
    """Mostrar benefícios da integração"""
    
    print("\n💡 Benefícios da Integração LangChain/CrewAI")
    print("=" * 60)
    
    benefits = [
        ("🧠 Inteligência Avançada", "Processamento com LLMs para análises mais sofisticadas"),
        ("🔄 Processamento Paralelo", "Múltiplos agentes trabalhando simultaneamente"),
        ("📊 Análises Inteligentes", "Detecção automática de padrões e anomalias"),
        ("🔍 Validação Avançada", "Validação contextual e inteligente dos dados"),
        ("📈 Relatórios Dinâmicos", "Geração de insights personalizados"),
        ("⚡ Escalabilidade", "Arquitetura modular para crescimento futuro"),
        ("🎯 Especialização", "Cada agente focado em uma tarefa específica"),
        ("🛡️ Confiabilidade", "Múltiplas validações e verificações automáticas")
    ]
    
    for benefit, description in benefits:
        print(f"✅ {benefit}: {description}")


def main():
    """Função principal"""
    
    print("🚀 Demonstração da Integração LangChain/CrewAI - Sistema VR/VA")
    print("=" * 70)
    
    # Mostrar arquitetura
    show_architecture()
    
    # Mostrar benefícios
    show_benefits()
    
    # Testar integração
    test_integration()
    
    print("\n" + "=" * 70)
    print("✅ Demonstração concluída!")
    print("\n📝 Próximos passos:")
    print("1. Configure as variáveis de ambiente (OPENAI_API_KEY)")
    print("2. Execute o Streamlit app: streamlit run app.py")
    print("3. Escolha 'Agentes Avançados' na interface")
    print("4. Faça upload dos arquivos e processe!")


if __name__ == "__main__":
    main()
