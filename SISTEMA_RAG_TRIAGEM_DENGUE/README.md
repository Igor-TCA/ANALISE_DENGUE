# Sistema RAG de Triagem de Dengue v2.0

Sistema inteligente de triagem e avaliação de risco para pacientes com suspeita de dengue, utilizando **RAG (Retrieval-Augmented Generation)** e **Inteligência Artificial** treinada com dados reais do SINAN/DATASUS.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)
![Version](https://img.shields.io/badge/version-2.0-brightgreen.svg)

## Novidades da v2.0

- **Perguntas Adaptativas**: Minimização inteligente via ganho de informação
- **Guardrails de Segurança**: Abstention para casos incertos, disclaimer obrigatório
- **Citações Rastreáveis**: Cada recomendação referencia a fonte de evidência
- **Sistema de Avaliação**: Golden set com 12 casos validados, métricas formais (Recall@K, MRR, nDCG)
- **Confiança Multi-fator**: Cálculo baseado em documentos, completude e clareza clínica

## Objetivo

Auxiliar profissionais de enfermagem na triagem inicial de pacientes com suspeita de dengue, fornecendo:
- Questionário estruturado baseado em protocolos do Ministério da Saúde
- Cálculo automático de score de risco
- Análise por IA contextualizada com milhares de casos reais
- Classificação em 4 níveis de risco com recomendações de conduta
- Identificação de sinais de alarme e gravidade

## Arquitetura

```
SISTEMA_RAG_TRIAGEM_DENGUE/
│
├── backend/                          # Backend Python
│   ├── data_processor.py             # Processamento de dados do SINAN
│   ├── rag_system.py                 # Sistema RAG com segurança (v2.0)
│   ├── questionario.py               # Questionário estruturado
│   ├── perguntas_adaptativas.py      # Sistema adaptativo com ganho de informação
│   └── avaliacao.py                  # Golden set e métricas de avaliação
│
├── frontend/                         # Frontend Streamlit
│   └── app.py                        # Interface interativa completa
│
├── config/                           # Configurações
│   └── config.yaml                   # Parâmetros do sistema
│
├── data/                             # Dados processados
│   └── knowledge_base.json           # Base de conhecimento (gerada)
│
├── tests/                            # Testes automatizados
│   └── test_questionario.py          # Testes do questionário
│
├── executar.py                       # Script principal de execução
├── requirements.txt                  # Dependências Python
├── .env.example                      # Exemplo de variáveis de ambiente
├── LICENSE                           # Licença MIT (PT-BR/EN)
└── README.md                         # Este arquivo
```

## Tecnologias

- **Python 3.9+**
- **LangChain**: Framework para aplicações com LLM
- **ChromaDB**: Vector database para RAG
- **Sentence Transformers**: Embeddings semânticos
- **OpenAI GPT-4** ou **Anthropic Claude**: Modelo de linguagem
- **Streamlit**: Interface web interativa
- **Pandas**: Processamento de dados
- **Plotly**: Visualizações interativas

## Base de Conhecimento

O sistema é treinado com dados reais do SINAN (Sistema de Informação de Agravos de Notificação):

- **Fonte**: DATASUS / Ministério da Saúde
- **Período**: 2025
- **Total de registros**: 1.502.259 notificações de dengue
- **Casos graves analisados**: Hospitalizações, óbitos e dengue grave
- **Documentos no vector store**: Milhares de padrões clínicos extraídos

## Instalação

### Pré-requisitos

```bash
Python 3.9 ou superior
pip (gerenciador de pacotes Python)
```

### Passo 1: Clonar o repositório

```bash
cd ANALISE_DENGUE/SISTEMA_RAG_TRIAGEM_DENGUE
```

### Passo 2: Criar ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Passo 3: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configurar variáveis de ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env e adicionar suas chaves de API
# OPENAI_API_KEY=sua_chave_aqui
# ou
# ANTHROPIC_API_KEY=sua_chave_aqui
```

### Passo 5: Inicializar sistema

```bash
python setup.py
```

Este script irá:
1. Verificar arquivos necessários
2. Processar dados do SINAN
3. Criar base de conhecimento
4. Gerar embeddings e vector store

## Uso

### Iniciar aplicação

```bash
streamlit run frontend/app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

### Fluxo de triagem

1. **Nova Triagem**: Preencha o questionário estruturado
   - Dados demográficos
   - História da doença atual
   - Sintomas clássicos
   - Sinais de alarme
   - Sinais de gravidade
   - Comorbidades
   - Dados laboratoriais (opcional)
   - Exame físico

2. **Análise**: Sistema calcula score de risco e classifica paciente

3. **Resultado**: Visualize:
   - Classificação de risco (Baixo/Médio/Alto/Crítico)
   - Análise detalhada por IA
   - Casos similares da base de dados
   - Recomendações de conduta

4. **Ações**: Salvar, gerar PDF, ou enviar resultado

## Classificação de Risco

### BAIXO (Score < 3)
- **Característica**: Dengue sem sinais de alarme
- **Conduta**: Tratamento ambulatorial com orientações
- **Retorno**: Se piora ou não melhora em 48h

### MÉDIO (Score 3-6)
- **Característica**: Fatores de risco presentes
- **Conduta**: Monitoramento intensivo
- **Reavaliação**: Em 24h

### ALTO (Score 6-10)
- **Característica**: Sinais de alarme presentes
- **Conduta**: Avaliação médica urgente
- **Considerar**: Internação para monitoramento

### CRÍTICO (Score > 10)
- **Característica**: Dengue grave ou múltiplos sinais de alarme
- **Conduta**: ATENDIMENTO IMEDIATO
- **Ação**: Encaminhar para emergência

## Como funciona o RAG

1. **Indexação** (setup):
   - Dados do SINAN são processados
   - Casos graves são extraídos e analisados
   - Padrões clínicos são identificados
   - Documentos são convertidos em embeddings
   - Vector store é criado para busca semântica

2. **Triagem** (runtime):
   - Enfermeiro preenche questionário
   - Sistema calcula score de risco inicial
   - Dados do paciente são formatados como query

3. **Recuperação** (Retrieval):
   - Query é convertida em embedding
   - Busca por similaridade no vector store
   - Top 5 casos mais similares são recuperados

4. **Geração** (Augmented Generation):
   - Contexto dos casos similares + dados do paciente
   - LLM analisa e gera avaliação detalhada
   - Classificação final de risco
   - Recomendações de conduta

## Documentação Técnica

### Data Processor

Processa dados brutos do SINAN:
- Limpeza e normalização
- Extração de casos graves
- Criação de documentos estruturados
- Geração de padrões epidemiológicos

```python
from backend.data_processor import DengueDataProcessor

processor = DengueDataProcessor("DENGBR25.csv")
processor.load_data() \
         .clean_data() \
         .extract_severe_cases() \
         .create_knowledge_documents() \
         .save_knowledge_base("data/knowledge_base.json")
```

### RAG System

Sistema completo de RAG:

```python
from backend.rag_system import initialize_system

# Inicializar
rag = initialize_system(
    knowledge_base_path="data/knowledge_base.json",
    force_reindex=False
)

# Analisar paciente
result = rag.analyze_patient({
    'idade': 35,
    'sexo': 'F',
    'dias_sintomas': 4,
    'sintomas': ['febre', 'cefaleia', 'mialgia'],
    'sinais_alarme': ['dor_abdominal_intensa'],
    'plaquetas': 85000
})

print(f"Risco: {result['risk_level']}")
print(f"Análise: {result['analysis']}")
```

### Questionário

Sistema de perguntas estruturadas:

```python
from backend.questionario import QuestionarioTriagemDengue

q = QuestionarioTriagemDengue()

# Registrar respostas
q.registrar_resposta('idade', 45)
q.registrar_resposta('febre_presente', True)

# Calcular risco
risco = q.classificar_risco()
print(f"Nível: {risco['nivel']}")

# Gerar dados para RAG
dados = q.gerar_dados_paciente()
```

### Perguntas Adaptativas (v2.0)

Sistema que minimiza perguntas usando ganho de informação:

```python
from backend.perguntas_adaptativas import SistemaAdaptativo

sistema = SistemaAdaptativo()

# Loop de triagem adaptativa
while not sistema.triagem_completa():
    # Pegar próxima pergunta mais informativa
    pergunta = sistema.proxima_pergunta()
    print(f"[{pergunta.prioridade}] {pergunta.texto}")
    
    # Registrar resposta
    sistema.responder(pergunta.id, True)  # ou False/valor
    
    # Verificar se já podemos classificar
    if sistema.pode_classificar_com_confianca():
        break

# Resultado
resultado = sistema.classificar_risco_adaptativo()
print(f"Risco: {resultado['nivel']}")
print(f"Confiança: {resultado['confianca']:.1%}")
print(f"Perguntas feitas: {len(sistema.respostas)}")
```

### Sistema de Avaliação (v2.0)

Golden set e métricas formais:

```python
from backend.avaliacao import AvaliacaoRAG, GoldenSetDengue

# Carregar golden set com 12 casos validados
golden_set = GoldenSetDengue()
avaliacao = AvaliacaoRAG(rag_system)

# Avaliar sistema
resultados = avaliacao.avaliar_completo(golden_set.casos)

print(f"Recall@5: {resultados.recall_at_k:.2%}")
print(f"MRR: {resultados.mrr:.3f}")
print(f"nDCG: {resultados.ndcg:.3f}")
print(f"Acurácia de Classificação: {resultados.accuracy:.2%}")
```

## Aviso Importante

**Este sistema é uma ferramenta de APOIO à decisão clínica.**

- Auxilia na triagem inicial
- Identifica sinais de alarme
- Sugere conduta baseada em evidências
- **Cita fontes** para cada recomendação (v2.0)
- **Abstém-se** quando confiança é baixa (v2.0)
- NÃO substitui avaliação médica
- NÃO realiza diagnóstico definitivo
- NÃO substitui exames complementares

A avaliação presencial por profissional de saúde qualificado permanece essencial.

## Segurança e Guardrails (v2.0)

### Abstention (Abstenção)
Sistema recusa-se a classificar quando:
- Confiança < 50%
- Dados críticos ausentes (idade, sintomas principais)
- Análise estrutural incompleta

### Citações Rastreáveis
Cada análise inclui referências aos documentos fonte:
```
[DOC-001] Padrão: Adulto com sinais de alarme → Conduta X
[DOC-007] Evidência: Faixa etária 30-45 → Risco Y
```

### Disclaimer Automático
Toda resposta inclui:
```
AVISO: Esta é uma ferramenta de apoio. 
A decisão final deve ser do profissional de saúde.
```

## Validação e Qualidade

### Dados
- Fonte oficial (DATASUS)
- Dados de 2025 (atual)
- >1,5 milhões de registros
- Foco em casos graves confirmados

### Algoritmo
- Baseado em protocolo do Ministério da Saúde
- Pesos ajustados por evidência epidemiológica
- Validação com casos reais
- Identificação de sinais críticos

### IA (v2.0)
- LLM state-of-the-art (GPT-4/Claude)
- RAG com casos similares contextualizados
- Embeddings semânticos de qualidade
- Respostas explicáveis
- **Cálculo de confiança multi-fator** (NOVO)
- **Abstention para casos incertos** (NOVO)
- **Citações de fonte para rastreabilidade** (NOVO)

### Avaliação (v2.0)
- **Golden set**: 12 casos validados cobrindo todos os níveis de risco (NOVO)
- **Métricas formais**: Recall@K, MRR, nDCG, Acurácia (NOVO)
- **Testes automatizados**: Coverage de componentes críticos (NOVO)

## Configuração Avançada

### Ajustar modelo LLM

Edite `.env`:

```bash
# Para OpenAI
LLM_PROVIDER=openai
MODEL_NAME=gpt-4-turbo-preview

# Para Anthropic
LLM_PROVIDER=anthropic
MODEL_NAME=claude-3-opus-20240229
```

### Ajustar embeddings

Edite `.env`:

```bash
# Modelo local (grátis)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Modelo maior (melhor qualidade)
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

### Ajustar thresholds de risco

Edite `config/config.yaml`:

```yaml
thresholds:
  risco_baixo: 3.0
  risco_medio: 6.0
  risco_alto: 10.0
```

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Referências

- [Ministério da Saúde - Diretrizes Dengue](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/d/dengue)
- [DATASUS - SINAN](http://www2.datasus.gov.br/DATASUS/index.php?area=0203)
- [OMS - Dengue Guidelines](https://www.who.int/publications/i/item/9789241547871)
- [LangChain Documentation](https://python.langchain.com/)




```Sistema desenvolvido para auxiliar profissionais de saúde no combate à dengue utilizando tecnologias de IA.```