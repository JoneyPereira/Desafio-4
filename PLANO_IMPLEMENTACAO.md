# Plano de Implementação - Automação VR/VA com Agentes de IA

## 📋 Visão Geral do Projeto

### Objetivo
Automatizar o processo mensal de compra de VR (Vale Refeição), garantindo que cada colaborador receba o valor correto, considerando ausências, férias, datas de admissão/desligamento e calendário de feriados.

### Problema Atual
- Processo manual baseado em planilhas
- Conferência manual de datas de contrato
- Exclusão manual de colaboradores em férias
- Cálculo manual de dias úteis
- Geração manual de layout para fornecedor

### Solução Proposta
Sistema automatizado com agentes de IA e interface web para:
- Consolidação automática de múltiplas bases de dados
- Aplicação automática de regras de negócio
- Cálculo automático de benefícios
- Geração automática de relatórios
- Interface web para upload/download de arquivos

## 🏗️ Arquitetura do Sistema

### Stack Tecnológico
- **Backend**: Python 3.9+
- **Framework de Agentes**: LangChain + CrewAI
- **Interface Web**: Streamlit
- **Manipulação de Dados**: Pandas + OpenPyXL
- **Validação**: Pydantic
- **Visualização**: Plotly

### Estrutura de Agentes

#### 1. Agente Coordenador (Crew Manager)
- **Responsabilidade**: Orquestração geral do processo
- **Funções**:
  - Coordenar execução dos demais agentes
  - Gerenciar fluxo de dados entre agentes
  - Tratar erros e exceções
  - Monitorar progresso da execução

#### 2. Agente de Consolidação de Dados
- **Responsabilidade**: Unificação das bases de dados
- **Funções**:
  - Ler múltiplas planilhas Excel
  - Aplicar regras de exclusão
  - Consolidar dados em base única
  - Tratar duplicatas e inconsistências

#### 3. Agente de Validação e Limpeza
- **Responsabilidade**: Validação e correção de dados
- **Funções**:
  - Validar integridade dos dados
  - Corrigir inconsistências automáticas
  - Aplicar regras de negócio
  - Gerar relatório de validações

#### 4. Agente de Cálculo de Benefícios
- **Responsabilidade**: Cálculo de VR por colaborador
- **Funções**:
  - Calcular dias úteis por colaborador
  - Aplicar regras específicas por sindicato
  - Calcular valores de VR
  - Tratar casos especiais (férias, afastamentos)

#### 5. Agente de Geração de Relatórios
- **Responsabilidade**: Criação da planilha final
- **Funções**:
  - Gerar planilha Excel final
  - Aplicar formatação conforme modelo
  - Validar resultado final
  - Preparar arquivo para download

## 📁 Estrutura de Pastas

```
vr_automation/
├── app.py                          # Interface Streamlit principal
├── agents/
│   ├── __init__.py
│   ├── coordinator.py              # Agente coordenador
│   ├── data_consolidator.py        # Agente de consolidação
│   ├── validator.py                # Agente de validação
│   ├── calculator.py               # Agente de cálculo
│   └── reporter.py                 # Agente de relatórios
├── components/                     # Componentes Streamlit
│   ├── __init__.py
│   ├── file_upload.py              # Componente de upload
│   ├── progress_tracker.py         # Rastreador de progresso
│   ├── results_display.py          # Exibição de resultados
│   ├── analytics.py                # Análises e gráficos
│   └── validation_display.py       # Exibição de validações
├── data/
│   ├── temp/                       # Arquivos temporários
│   └── cache/                      # Cache de processamento
├── schemas/
│   ├── __init__.py
│   ├── employee.py                 # Schema de colaborador
│   ├── benefits.py                 # Schema de benefícios
│   └── validation.py               # Schema de validação
├── utils/
│   ├── __init__.py
│   ├── excel_handler.py            # Manipulação de Excel
│   ├── date_utils.py               # Utilitários de data
│   ├── business_rules.py           # Regras de negócio
│   ├── streamlit_utils.py          # Utilitários Streamlit
│   └── cache_manager.py            # Gerenciador de cache
├── config/
│   ├── __init__.py
│   └── settings.py                 # Configurações
├── pages/                          # Páginas Streamlit
│   ├── 01_upload.py                # Página de upload
│   ├── 02_processing.py            # Página de processamento
│   └── 03_results.py               # Página de resultados
├── tests/                          # Testes
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_business_rules.py
│   └── test_validation.py
├── requirements.txt                # Dependências
├── main.py                         # Script principal
├── README.md                       # Documentação
└── PLANO_IMPLEMENTACAO.md         # Este arquivo
```

## 🔄 Fluxo de Processamento

### 1. Upload de Arquivos
- Usuário faz upload das 10 planilhas necessárias
- Sistema valida formato e conteúdo dos arquivos
- Arquivos são salvos temporariamente

### 2. Consolidação de Dados
- Leitura de todas as planilhas
- Aplicação de regras de exclusão
- Consolidação em base única
- Tratamento de duplicatas

### 3. Validação e Limpeza
- Validação de integridade dos dados
- Correção automática de inconsistências
- Aplicação de regras de negócio
- Geração de relatório de validações

### 4. Cálculo de Benefícios
- Cálculo de dias úteis por colaborador
- Aplicação de regras por sindicato
- Cálculo de valores de VR
- Tratamento de casos especiais

### 5. Geração de Relatório
- Criação da planilha final
- Aplicação de formatação
- Validação do resultado
- Preparação para download

## 📊 Regras de Negócio

### Exclusões Automáticas
- Diretores
- Estagiários
- Aprendizes
- Colaboradores afastados (licença maternidade, etc.)
- Profissionais no exterior

### Regras de Desligamento
- Comunicado até dia 15: não considerar pagamento
- Comunicado após dia 15: compra proporcional

### Cálculo de Custos
- Empresa: 80% do valor total
- Funcionário: 20% descontado

### Considerações Especiais
- Férias parciais ou integrais
- Afastamentos temporários
- Feriados nacionais/estaduais/municipais
- Datas de admissão/desligamento no meio do mês

## 🎯 Cronograma de Implementação

### Fase 1: Setup e Estrutura Base (3-4 dias)
- [x] Configuração do ambiente
- [x] Criação da estrutura de pastas
- [x] Definição de schemas
- [x] Configuração de dependências

### Fase 2: Interface Web (3-4 dias)
- [ ] Implementação da interface Streamlit
- [ ] Componente de upload de arquivos
- [ ] Rastreador de progresso
- [ ] Exibição de resultados

### Fase 3: Implementação dos Agentes (5-7 dias)
- [ ] Agente coordenador
- [ ] Agente de consolidação
- [ ] Agente de validação
- [ ] Agente de cálculo
- [ ] Agente de relatórios

### Fase 4: Regras de Negócio (3-4 dias)
- [ ] Regras de exclusão
- [ ] Cálculo de dias úteis
- [ ] Regras de desligamento
- [ ] Aplicação de custos

### Fase 5: Integração e Testes (3-4 dias)
- [ ] Integração dos agentes
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Validação com dados reais

### Fase 6: Documentação e Deploy (2-3 dias)
- [ ] Documentação completa
- [ ] Scripts de execução
- [ ] Deploy da aplicação
- [ ] Treinamento de usuários

**Total Estimado: 19-26 dias**

## 🛠️ Dependências

```txt
# requirements.txt
streamlit==1.28.0
langchain==0.1.0
crewai==0.11.0
pandas==2.1.0
openpyxl==3.1.2
pydantic==2.5.0
python-dateutil==2.8.2
numpy==1.24.0
plotly==5.17.0
python-dotenv==1.0.0
```

## 🚀 Comandos de Execução

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py

# Executar em modo de desenvolvimento
streamlit run app.py --server.port 8501 --server.address localhost

# Executar testes
python -m pytest tests/

# Executar script principal
python main.py
```

## 📈 Métricas de Sucesso

### Funcionais
- Redução de 90% no tempo de processamento
- Eliminação de erros manuais
- Consistência nos cálculos
- Geração automática de relatórios

### Técnicas
- Tempo de resposta < 30 segundos
- Disponibilidade > 99%
- Taxa de erro < 1%
- Cobertura de testes > 80%

### Usuário
- Interface intuitiva
- Feedback em tempo real
- Download automático de resultados
- Validações claras

## 🔧 Configurações

### Variáveis de Ambiente
```env
# .env
DEBUG=True
LOG_LEVEL=INFO
CACHE_ENABLED=True
MAX_FILE_SIZE=50MB
TEMP_DIR=data/temp
CACHE_DIR=data/cache
```

### Configurações Streamlit
```toml
# .streamlit/config.toml
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

## 📝 Próximos Passos

1. **Validação do Plano**: Revisar com stakeholders
2. **Setup do Ambiente**: Configurar ambiente de desenvolvimento
3. **Análise das Planilhas**: Entender estrutura dos dados
4. **Implementação Iterativa**: Começar com MVP
5. **Testes e Validação**: Validar com dados reais
6. **Deploy e Treinamento**: Disponibilizar para usuários

---

**Versão**: 1.0  
**Data**: Dezembro 2024  
**Autor**: Sistema de Agentes de IA  
**Status**: Em Desenvolvimento
