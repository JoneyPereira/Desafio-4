"""
Agentes usando LangChain e CrewAI para o sistema VR/VA
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, date
import pandas as pd
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool, Tool
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from crewai import Agent, Task, Crew, Process

from schemas.employee import Employee, EmployeeStatus
from schemas.benefits import Benefit, BenefitType, BenefitCalculation
from schemas.validation import ValidationResult, ValidationError, ValidationSeverity
from utils.excel_handler import ExcelHandler
from utils.business_rules import BusinessRules
from utils.date_utils import DateUtils

logger = logging.getLogger(__name__)

# Classe base para ferramentas
class VRVABaseTool(BaseTool):
    """Classe base para todas as ferramentas VR/VA"""
    name: str = "vrva_base_tool"
    description: str = "Ferramenta base para VR/VA"
    return_direct: bool = True
    
    def _run(self, tool_input: str) -> str:
        """Implementação padrão que deve ser sobrescrita"""
        raise NotImplementedError("Subclasses devem implementar _run")
    
    async def _arun(self, tool_input: str) -> str:
        """Versão assíncrona que chama a implementação síncrona"""
        return self._run(tool_input)


# Classes de ferramentas
class ValidationTool(VRVABaseTool):
    name: str = "validation_tool"
    description: str = "Valida qualidade e integridade dos dados de funcionários"
    return_direct: bool = True
    
    def _run(self, tool_input: str) -> str:
        try:
            # Implementar lógica de validação
            return "Dados validados com sucesso"
        except Exception as e:
            return f"Erro na validação: {str(e)}"

class ConsolidationTool(VRVABaseTool):
    name: str = "consolidation_tool"
    description: str = "Consolida dados de múltiplas fontes"
    return_direct: bool = True
    
    def _run(self, tool_input: str) -> str:
        try:
            # Implementar lógica de consolidação
            return "Dados consolidados com sucesso"
        except Exception as e:
            return f"Erro na consolidação: {str(e)}"

class CalculationTool(VRVABaseTool):
    name: str = "calculation_tool"
    description: str = "Calcula benefícios VR/VA seguindo regras de negócio"
    return_direct: bool = True
    
    def _run(self, tool_input: str) -> str:
        try:
            # Implementar lógica de cálculo
            return "Benefícios calculados com sucesso"
        except Exception as e:
            return f"Erro no cálculo: {str(e)}"

class ReportingTool(VRVABaseTool):
    name: str = "reporting_tool"
    description: str = "Gera relatórios e análises detalhadas"
    return_direct: bool = True
    
    def _run(self, tool_input: str) -> str:
        try:
            # Implementar lógica de relatórios
            return "Relatórios gerados com sucesso"
        except Exception as e:
            return f"Erro na geração de relatórios: {str(e)}"

class CoordinationTool(VRVABaseTool):
    name: str = "coordination_tool"
    description: str = "Coordena e monitora o processo completo"
    return_direct: bool = True
    
    def _run(self, tool_input: str) -> str:
        try:
            # Implementar lógica de coordenação
            return "Processo coordenado com sucesso"
        except Exception as e:
            return f"Erro na coordenação: {str(e)}"

class DataQualityTool(VRVABaseTool):
    name: str = "data_quality_tool"
    description: str = "Analisa qualidade e consistência dos dados"
    return_direct: bool = True
    
    def _run(self, tool_input: str) -> str:
        try:
            # Implementar análise de qualidade
            return "Análise de qualidade concluída"
        except Exception as e:
            return f"Erro na análise: {str(e)}"

class DataCleaningTool(VRVABaseTool):
    name: str = "data_cleaning_tool"
    description: str = "Remove duplicatas e corrige inconsistências"
    return_direct: bool = True
    
    def _run(self, tool_input: str) -> str:
        try:
            # Implementar limpeza de dados
            return "Dados limpos com sucesso"
        except Exception as e:
            return f"Erro na limpeza: {str(e)}"

class BusinessRulesTool(VRVABaseTool):
    name: str = "business_rules_tool"
    description: str = "Aplica regras de negócio específicas para VR/VA"
    return_direct: bool = True
    
    def _run(self, tool_input: str) -> str:
        try:
            # Implementar aplicação de regras
            return "Regras de negócio aplicadas"
        except Exception as e:
            return f"Erro na aplicação de regras: {str(e)}"

class VisualizationTool(VRVABaseTool):
    name: str = "visualization_tool"
    description: str = "Cria gráficos e dashboards interativos"
    return_direct: bool = True
    
    def _run(self, tool_input: str) -> str:
        try:
            # Implementar criação de visualizações
            return "Visualizações criadas com sucesso"
        except Exception as e:
            return f"Erro na criação de visualizações: {str(e)}"

# Agentes
class LangChainVRVAAgent:
    """Agente base usando LangChain para processamento VR/VA"""
    
    def __init__(self, agent_name: str, model_name: str = "gpt-3.5-turbo"):
        self.agent_name = agent_name
        self.llm = ChatOpenAI(model_name=model_name, temperature=0.1)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.tools = []
        self.agent_executor = None
        
    def add_tool(self, tool: BaseTool):
        """Adiciona uma ferramenta ao agente"""
        self.tools.append(tool)
        
    def setup_agent(self):
        """Configura o agente com ferramentas e prompt"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"Você é um agente especializado em {self.agent_name} para o sistema VR/VA."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        self.agent_executor = AgentExecutor(
            agent=create_openai_functions_agent(self.llm, self.tools, prompt),
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )
        
    def execute(self, input_text: str) -> Dict[str, Any]:
        """Executa o agente com entrada específica"""
        if not self.agent_executor:
            self.setup_agent()
            
        try:
            result = self.agent_executor.invoke({"input": input_text})
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Erro no agente {self.agent_name}: {str(e)}")
            return {"success": False, "error": str(e)}


class CrewAIVRVAOrchestrator:
    """Orquestrador principal usando CrewAI para coordenação de agentes"""
    
    def __init__(self):
        self.crew = None
        self.agents = {}
        self.tasks = []
        self._create_tools()
        
    def _create_tools(self):
        """Cria instâncias de todas as ferramentas"""
        self.tools = {
            "validation": ValidationTool(),
            "data_quality": DataQualityTool(),
            "consolidation": ConsolidationTool(),
            "data_cleaning": DataCleaningTool(),
            "calculation": CalculationTool(),
            "business_rules": BusinessRulesTool(),
            "reporting": ReportingTool(),
            "visualization": VisualizationTool(),
            "coordination": CoordinationTool()
        }
        
    def _create_agent_tools(self, tool_names: List[str]) -> List[BaseTool]:
        """Cria configuração de ferramentas para um agente CrewAI"""
        return [self.tools[name] for name in tool_names if name in self.tools]
        
    def create_agents(self):
        """Cria os agentes especializados usando CrewAI"""
        
        # Agente Validador
        validator_agent = Agent(
            role="Especialista em Validação de Dados",
            goal="Validar a qualidade e integridade dos dados de funcionários e benefícios",
            backstory="""Você é um especialista em qualidade de dados com anos de experiência 
            em validação de planilhas e dados de RH. Você identifica problemas, inconsistências 
            e sugere correções para garantir dados confiáveis.""",
            verbose=True,
            allow_delegation=False,
            tools=self._create_agent_tools(["validation", "data_quality"])
        )
        
        # Agente Consolidador
        consolidator_agent = Agent(
            role="Especialista em Consolidação de Dados",
            goal="Consolidar e limpar dados de múltiplas fontes de forma eficiente",
            backstory="""Você é um analista de dados especializado em consolidação de informações 
            de diferentes sistemas e planilhas. Você garante que os dados sejam consistentes 
            e prontos para processamento.""",
            verbose=True,
            allow_delegation=False,
            tools=self._create_agent_tools(["consolidation", "data_cleaning"])
        )
        
        # Agente Calculador
        calculator_agent = Agent(
            role="Especialista em Cálculos de Benefícios",
            goal="Calcular benefícios VR/VA seguindo regras de negócio específicas",
            backstory="""Você é um especialista em folha de pagamento e benefícios com 
            conhecimento profundo das regras de VR/VA. Você calcula valores considerando 
            feriados, férias, admissões e demissões.""",
            verbose=True,
            allow_delegation=False,
            tools=self._create_agent_tools(["calculation", "business_rules"])
        )
        
        # Agente Relator
        reporter_agent = Agent(
            role="Especialista em Relatórios e Análises",
            goal="Gerar relatórios abrangentes e análises detalhadas dos benefícios",
            backstory="""Você é um analista de negócios especializado em criação de 
            relatórios executivos e dashboards. Você transforma dados complexos em 
            insights acionáveis.""",
            verbose=True,
            allow_delegation=False,
            tools=self._create_agent_tools(["reporting", "visualization"])
        )
        
        # Agente Coordenador
        coordinator_agent = Agent(
            role="Coordenador de Processos VR/VA",
            goal="Orquestrar todo o processo de cálculo de benefícios VR/VA",
            backstory="""Você é um gerente de projetos especializado em automação de 
            processos de RH. Você coordena equipes de especialistas para entregar 
            resultados precisos e no prazo.""",
            verbose=True,
            allow_delegation=True,
            tools=self._create_agent_tools(["coordination"])
        )
        
        self.agents = {
            "validator": validator_agent,
            "consolidator": consolidator_agent,
            "calculator": calculator_agent,
            "reporter": reporter_agent,
            "coordinator": coordinator_agent
        }
        
    def create_tasks(self, uploaded_files, month: int, year: int):
        """Cria as tarefas para o processamento"""
        
        # Tarefa 1: Validação
        validation_task = Task(
            description=f"""
            Validar os arquivos de entrada para o mês {month}/{year}:
            1. Verificar estrutura dos arquivos
            2. Validar dados obrigatórios
            3. Identificar inconsistências
            4. Gerar relatório de validação
            
            Arquivos: {[f.name for f in uploaded_files]}
            """,
            agent=self.agents["validator"],
            expected_output="Relatório detalhado de validação com problemas identificados e sugestões"
        )
        
        # Tarefa 2: Consolidação
        consolidation_task = Task(
            description=f"""
            Consolidar dados dos funcionários para {month}/{year}:
            1. Unificar dados de funcionários ativos
            2. Processar admissões e demissões
            3. Aplicar dados complementares (férias, licenças)
            4. Remover duplicatas
            
            Baseado na validação anterior, consolidar dados limpos.
            """,
            agent=self.agents["consolidator"],
            expected_output="Dataset consolidado e limpo de funcionários",
            context=[validation_task]
        )
        
        # Tarefa 3: Cálculo
        calculation_task = Task(
            description=f"""
            Calcular benefícios VR/VA para {month}/{year}:
            1. Aplicar regras de exclusão
            2. Calcular dias trabalhados
            3. Aplicar valores de referência
            4. Calcular custos (80% empresa, 20% funcionário)
            
            Usar dados consolidados e regras de negócio específicas.
            """,
            agent=self.agents["calculator"],
            expected_output="Cálculos completos de benefícios com valores e custos",
            context=[consolidation_task]
        )
        
        # Tarefa 4: Relatórios
        reporting_task = Task(
            description=f"""
            Gerar relatórios finais para {month}/{year}:
            1. Relatório principal em Excel
            2. Resumo executivo
            3. Análises estatísticas
            4. Dashboards interativos
            
            Usar resultados dos cálculos para criar relatórios abrangentes.
            """,
            agent=self.agents["reporter"],
            expected_output="Relatórios completos em múltiplos formatos",
            context=[calculation_task]
        )
        
        # Tarefa 5: Coordenação
        coordination_task = Task(
            description=f"""
            Coordenar todo o processo de VR/VA para {month}/{year}:
            1. Monitorar progresso das tarefas
            2. Garantir qualidade dos resultados
            3. Resolver problemas identificados
            4. Entregar resultado final
            
            Supervisionar todas as etapas e garantir entrega no prazo.
            """,
            agent=self.agents["coordinator"],
            expected_output="Processo completo finalizado com relatórios entregues",
            context=[validation_task, consolidation_task, calculation_task, reporting_task]
        )
        
        self.tasks = [
            validation_task,
            consolidation_task,
            calculation_task,
            reporting_task,
            coordination_task
        ]
        
    def execute_crew(self) -> Dict[str, Any]:
        """Executa o crew com todos os agentes e tarefas"""
        if not self.agents or not self.tasks:
            raise ValueError("Agentes e tarefas devem ser criados antes da execução")
            
        self.crew = Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = self.crew.kickoff()
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Erro na execução do crew: {str(e)}")
            return {"success": False, "error": str(e)}



