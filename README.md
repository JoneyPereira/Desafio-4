# 🤖 Automação VR/VA - Sistema Inteligente

Sistema automatizado para cálculo de Vale Refeição (VR/VA) com interface web intuitiva e processamento inteligente de dados.

## 🎯 Objetivo

Automatizar o processo mensal de compra de VR (Vale Refeição), garantindo que cada colaborador receba o valor correto, considerando ausências, férias, datas de admissão/desligamento e calendário de feriados.

## ✨ Funcionalidades

- **📁 Upload Inteligente**: Interface drag & drop para múltiplas planilhas
- **🔍 Validação Automática**: Verificação de integridade dos dados
- **⚖️ Regras de Negócio**: Aplicação automática de regras específicas
- **🧮 Cálculo Automático**: Processamento inteligente de benefícios
- **📊 Relatórios**: Geração automática de planilhas formatadas
- **📈 Análises**: Visualizações e métricas em tempo real

## 🏗️ Arquitetura

### Diagrama da Arquitetura

```mermaid
graph TB
    %% Interface do Usuário
    subgraph "🎨 Interface do Usuário"
        UI[Streamlit Interface]
        Upload[Upload de Arquivos]
        Config[Configurações]
        Results[Resultados]
    end

    %% Camada de Agentes
    subgraph "🤖 Camada de Agentes"
        subgraph "Agentes Básicos"
            BA[Agentes Básicos]
            BA --> Validator[Validador]
            BA --> Consolidator[Consolidador]
            BA --> Calculator[Calculador]
            BA --> Reporter[Relator]
        end
        
        subgraph "Agentes Avançados"
            AA[Agentes LangChain/CrewAI]
            AA --> LangChain[LangChain Agent]
            AA --> CrewAI[CrewAI Orchestrator]
            
            subgraph "CrewAI Agents"
                CA1[Validador IA]
                CA2[Consolidador IA]
                CA3[Calculador IA]
                CA4[Relator IA]
                CA5[Coordenador IA]
            end
            
            CrewAI --> CA1
            CrewAI --> CA2
            CrewAI --> CA3
            CrewAI --> CA4
            CrewAI --> CA5
        end
    end

    %% Camada de Processamento
    subgraph "⚙️ Camada de Processamento"
        Excel[Excel Handler]
        Business[Business Rules]
        Validation[Validation Engine]
        Calculation[Calculation Engine]
        Reporting[Reporting Engine]
    end

    %% Camada de Dados
    subgraph "💾 Camada de Dados"
        Schemas[Pydantic Schemas]
        Cache[Cache Manager]
        Temp[Temp Files]
        Output[Output Files]
    end

    %% Camada de IA
    subgraph "🧠 Camada de IA"
        LLM[OpenAI GPT]
        Memory[Conversation Memory]
        Tools[CrewAI Tools]
        Chain[LangChain Chain]
    end

    %% Fluxo de Dados
    UI --> Upload
    Upload --> Excel
    Excel --> Validation
    Validation --> Business
    Business --> Calculation
    Calculation --> Reporting
    Reporting --> Results

    %% Integração com IA
    UI --> AA
    AA --> LLM
    LLM --> Memory
    Memory --> Chain
    Chain --> Tools
    Tools --> CA1
    Tools --> CA2
    Tools --> CA3
    Tools --> CA4
    Tools --> CA5

    %% Schemas e Cache
    Validation --> Schemas
    Calculation --> Cache
    Reporting --> Temp
    Results --> Output

    %% Estilo
    classDef uiClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef agentClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef processClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef dataClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef aiClass fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    class UI,Upload,Config,Results uiClass
    class BA,AA,Validator,Consolidator,Calculator,Reporter,LangChain,CrewAI,CA1,CA2,CA3,CA4,CA5 agentClass
    class Excel,Business,Validation,Calculation,Reporting processClass
    class Schemas,Cache,Temp,Output dataClass
    class LLM,Memory,Tools,Chain aiClass
```

### Stack Tecnológico
- **Backend**: Python 3.9+
- **Interface Web**: Streamlit
- **Manipulação de Dados**: Pandas + OpenPyXL
- **Validação**: Pydantic
- **Visualização**: Plotly
- **IA**: LangChain + CrewAI + OpenAI GPT

### Estrutura do Projeto
```
vr_automation/
├── app.py                          # Interface Streamlit principal
├── agents/                         # Agentes de IA
│   ├── __init__.py                # Agentes básicos
│   └── langchain_agents.py        # Agentes LangChain/CrewAI
├── components/                     # Componentes Streamlit
├── data/                          # Dados temporários e cache
├── schemas/                       # Schemas de validação
├── utils/                         # Utilitários
├── config/                        # Configurações
├── pages/                         # Páginas Streamlit
├── tests/                         # Testes
├── demo_langchain_crewai.py       # Demonstração IA
└── requirements.txt               # Dependências
```

### Modalidades de Processamento

#### 🔄 Fluxo de Processamento Básico
```mermaid
sequenceDiagram
    participant U as Usuário
    participant UI as Interface
    participant V as Validador
    participant C as Consolidador
    participant Calc as Calculador
    participant R as Relator

    U->>UI: Upload arquivos
    UI->>V: Validar dados
    V->>UI: Resultado validação
    UI->>C: Consolidar dados
    C->>UI: Dados consolidados
    UI->>Calc: Calcular benefícios
    Calc->>UI: Cálculos realizados
    UI->>R: Gerar relatórios
    R->>UI: Relatórios prontos
    UI->>U: Download resultados
```

#### 🚀 Fluxo de Processamento Avançado (IA)
```mermaid
sequenceDiagram
    participant U as Usuário
    participant UI as Interface
    participant O as Orchestrator
    participant CA1 as Validador IA
    participant CA2 as Consolidador IA
    participant CA3 as Calculador IA
    participant CA4 as Relator IA
    participant CA5 as Coordenador IA
    participant LLM as OpenAI GPT

    U->>UI: Upload arquivos + IA
    UI->>O: Inicializar CrewAI
    O->>LLM: Configurar LLM
    O->>CA1: Tarefa: Validar dados
    CA1->>LLM: Análise inteligente
    LLM->>CA1: Validação contextual
    CA1->>O: Dados validados
    O->>CA2: Tarefa: Consolidar dados
    CA2->>LLM: Consolidação inteligente
    LLM->>CA2: Dados consolidados
    CA2->>O: Dados prontos
    O->>CA3: Tarefa: Calcular benefícios
    CA3->>LLM: Cálculos avançados
    LLM->>CA3: Benefícios calculados
    CA3->>O: Cálculos prontos
    O->>CA4: Tarefa: Gerar relatórios
    CA4->>LLM: Análises inteligentes
    LLM->>CA4: Relatórios dinâmicos
    CA4->>O: Relatórios prontos
    O->>CA5: Tarefa: Coordenar processo
    CA5->>O: Processo finalizado
    O->>UI: Resultados com IA
    UI->>U: Download resultados avançados
```

## 🚀 Instalação

### Pré-requisitos
- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd vr_automation
```

2. **Crie um ambiente virtual (recomendado)**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação**
```bash
streamlit run app.py
```

## 📖 Como Usar

### 1. Acesso à Interface
Após executar o comando `streamlit run app.py`, a aplicação estará disponível em:
```
http://localhost:8501
```

### 2. Seleção do Tipo de Processamento
O sistema oferece duas modalidades de processamento:

#### 🔄 **Agentes Básicos** (Recomendado para início)
- Processamento rápido e eficiente
- Validações e cálculos diretos
- Ideal para processamento em lote
- Não requer configuração de API

#### 🚀 **Agentes Avançados (LangChain/CrewAI)** (Recomendado para análise avançada)
- Processamento com inteligência artificial
- Validações contextuais e inteligentes
- Análises avançadas e insights personalizados
- Requer configuração de `OPENAI_API_KEY`

### 3. Upload de Arquivos
No painel lateral, faça upload das seguintes planilhas:
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

### 3. Configurações
Defina o mês e ano de referência para o processamento.

### 4. Processamento
Clique em "🚀 Processar VR/VA" para iniciar a automação.

### 5. Resultados
Visualize os resultados e faça download da planilha final.

## 📊 Regras de Negócio

### Exclusões Automáticas
- Diretores
- Estagiários
- Aprendizes
- Colaboradores afastados (licença maternidade, etc.)
- Profissionais no exterior

### Regras de Desligamento
- **Comunicado até dia 15**: Não considerar pagamento
- **Comunicado após dia 15**: Compra proporcional

### Cálculo de Custos
- **Empresa**: 80% do valor total
- **Funcionário**: 20% descontado

### Considerações Especiais
- Férias parciais ou integrais
- Afastamentos temporários
- Feriados nacionais/estaduais/municipais
- Datas de admissão/desligamento no meio do mês

## 🔧 Configuração

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações Gerais
DEBUG=True
LOG_LEVEL=INFO
CACHE_ENABLED=True
MAX_FILE_SIZE=50MB
TEMP_DIR=data/temp
CACHE_DIR=data/cache

# Configuração OpenAI (para Agentes Avançados)
OPENAI_API_KEY=sua_chave_api_openai_aqui
OPENAI_MODEL=gpt-3.5-turbo
```

### Configurações Streamlit
Crie um arquivo `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = "localhost"

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## 🧪 Testes e Demonstrações

### Executar Testes
```bash
python -m pytest tests/
```

### Cobertura de Testes
```bash
python -m pytest --cov=. tests/
```

### Demonstração dos Agentes IA
Para testar a integração LangChain/CrewAI:

```bash
cd vr_automation
python demo_langchain_crewai.py
```

Este script demonstra:
- Arquitetura dos agentes
- Benefícios da integração
- Testes de funcionalidade
- Configuração do sistema

## 📈 Métricas de Sucesso

### Funcionais
- ✅ Redução de 90% no tempo de processamento
- ✅ Eliminação de erros manuais
- ✅ Consistência nos cálculos
- ✅ Geração automática de relatórios

### Técnicas
- ✅ Tempo de resposta < 30 segundos
- ✅ Disponibilidade > 99%
- ✅ Taxa de erro < 1%
- ✅ Cobertura de testes > 80%

## 🤝 Contribuição

### Como Contribuir

1. **Fork o projeto**
2. **Crie uma branch para sua feature**
```bash
git checkout -b feature/nova-funcionalidade
```

3. **Faça commit das mudanças**
```bash
git commit -m 'Adiciona nova funcionalidade'
```

4. **Push para a branch**
```bash
git push origin feature/nova-funcionalidade
```

5. **Abra um Pull Request**

### Padrões de Código

- Use **Black** para formatação
- Use **Flake8** para linting
- Siga as convenções PEP 8
- Documente funções e classes
- Escreva testes para novas funcionalidades

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para dúvidas, sugestões ou problemas:

- **Email**: suporte@empresa.com
- **Issues**: [GitHub Issues](https://github.com/empresa/vr-automation/issues)
- **Documentação**: [Wiki do Projeto](https://github.com/empresa/vr-automation/wiki)

## 🔄 Changelog

### v1.1.0 (2024-12-XX) - Integração IA
- ✅ Integração LangChain/CrewAI
- ✅ Agentes de IA especializados
- ✅ Processamento com OpenAI GPT
- ✅ Validações inteligentes
- ✅ Análises avançadas
- ✅ Relatórios dinâmicos
- ✅ Interface dual (Básico/Avançado)

### v1.0.0 (2024-12-XX) - Versão Base
- ✅ Interface Streamlit completa
- ✅ Upload de múltiplas planilhas
- ✅ Validação automática de dados
- ✅ Aplicação de regras de negócio
- ✅ Cálculo automático de benefícios
- ✅ Geração de relatórios
- ✅ Download de resultados

---

**Desenvolvido com ❤️ pela equipe de Automação**
