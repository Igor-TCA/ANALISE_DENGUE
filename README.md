# 🦟 Analise de Dengue no Brasil - EDA e Sistema RAG de Triagem
<center>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg?style=flat&logo=jupyter&logoColor=white)](https://jupyter.org/)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-green.svg?style=flat)](https://langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Interface-red.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)

</center>

## Origem do Projeto

Este projeto nasceu de uma **Analise Exploratoria de Dados (EDA)** para estudo dos dados de dengue no Brasil, utilizando **microdados do SINAN disponibilizados pelo DATASUS**. A analise inicial focou nos dados de **2025**, buscando entender perfis demograficos, distribuicao territorial, sazonalidade e fatores de risco.

Durante a exploracao dos dados, identificamos padroes relevantes sobre a **evolucao temporal da doenca** e os **grupos de maior risco**. A partir desses insights, surgiu a ideia de implementar um **Sistema de Triagem Inteligente com RAG (Retrieval-Augmented Generation)**, utilizando os dados historicos de dengue (2022-2025) como base de conhecimento para auxiliar na classificacao de risco de pacientes.

O projeto evoluiu, portanto, de uma analise exploratoria academica para uma **solucao pratica de apoio a decisao clinica**, demonstrando como dados publicos de saude podem ser transformados em ferramentas uteis para profissionais e pacientes.

---

## Resultado em 30 segundos

- **Base consolidada:** 10.998.370 registros (2022-2025), 27 UFs
- **Perfil etario:** Adultos (23-60) concentram 55,5% dos casos notificados  
- **Distribuicao regional:** SP (34,3%), MG (21,1%), PR (10,2%) lideram em volume
- **Desfechos criticos:** Idosos (60+) concentram 61,7% dos obitos com taxa de 0,543%
- **Total de obitos:** 12.698 casos (0,1155% do total)
- **Sistema RAG:** Triagem inteligente com 4 niveis de risco (BAIXO/MEDIO/ALTO/CRITICO)

**Relatorio completo:** [RELATORIO_ANALISE.md](RELATORIO_ANALISE.md)  
**Notebook principal:** [analise_dengue.ipynb](analise_dengue.ipynb)

Nota: Os numeros referem-se a dados de notificacao (nao necessariamente casos confirmados), conforme a base do SINAN/DATASUS.

---

## Entregaveis

### Fase 1: Analise Exploratoria de Dados
A primeira etapa do projeto focou em compreender os dados epidemiologicos:

- **Relatorio de resultados:** [RELATORIO_ANALISE.md](RELATORIO_ANALISE.md) - consolidacao de metricas e insights
- **Notebook de EDA:** [analise_dengue.ipynb](analise_dengue.ipynb) - pipeline reprodutivel de analise
- **Notebook de evolucao temporal:** [analise_evolucao_temporal_dengue.ipynb](analise_evolucao_temporal_dengue.ipynb) - analise de progressao clinica e janelas criticas
- **Graficos:** pasta `GRAFICOS/` com visualizacoes exportadas

### Fase 2: Sistema RAG de Triagem Inteligente
Com os insights da EDA, desenvolvemos um sistema de apoio a triagem:

- **Sistema completo:** [SISTEMA_RAG_TRIAGEM_DENGUE/](SISTEMA_RAG_TRIAGEM_DENGUE/) - aplicacao RAG com interface Streamlit
- **Base de conhecimento:** gerada a partir de ~11 milhoes de casos do SINAN (2022-2025)
- **Classificacao de risco:** 4 niveis (BAIXO/MEDIO/ALTO/CRITICO) com recomendacoes de conduta

![Dashboard resumo](GRAFICOS/06_dashboard_final.png)

---

## Principais Analises Realizadas

### Analise Exploratoria (EDA)
- **Visao geral:** 10.998.370 registros de 2022 a 2025
- **Perfil demografico:** Distribuicao por faixa etaria e sexo
- **Perfil clinico:** Frequencia de sintomas por grupo
- **Distribuicao territorial:** Analise por regiao, UF e municipio
- **Desfechos:** Taxa de obitos por faixa etaria
- **Sazonalidade:** Evolucao por semana epidemiologica

### Analise de Evolucao Temporal
- **Delta de tempos:** Sintomas -> Alarme -> Gravidade -> Obito
- **Janelas criticas:** 64,2% dos casos graves evoluem entre dias 3-7
- **Estratificacao:** Idosos evoluem mais rapido para gravidade (mediana: 4 dias)
- **Features para RAG:** Metricas temporais exportadas para o sistema de triagem

### Sistema RAG de Triagem
- **Questionario adaptativo:** Perguntas dinamicas baseadas em ganho de informacao
- **Base de conhecimento:** 56 entradas de conhecimento derivadas de 11M casos
- **Classificacao de risco:** Score ponderado com fatores demograficos e clinicos
- **Recomendacoes:** Condutas especificas para cada nivel de risco

---

## Fontes de Dados

### Dados Epidemiologicos
- [DATASUS](https://datasus.saude.gov.br/) - Microdados de notificacoes de dengue (CSV, 2022-2025)
  - `DENGBR22.csv`: 1.393.877 registros
  - `DENGBR23.csv`: 1.508.653 registros
  - `DENGBR24.csv`: 6.427.053 registros
  - `DENGBR25.csv`: 1.668.787 registros
  
- [SINAN](http://sinan.saude.gov.br/) - Documentacao, dicionario e codificacao das variaveis

### Dados Territoriais
- [IBGE - Divisao Territorial](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/estrutura-territorial/23701-divisao-territorial-brasileira.html) - Codigos e nomes de municipios/UFs

### Referencias Metodologicas
- [Ministerio da Saude - Semana Epidemiologica](https://www.gov.br/saude/) - Referencia para analise temporal  

---

## Limitacoes e Proximos Passos

**Limitacoes:**
- Base de notificacao (pode haver subnotificacao e heterogeneidade de preenchimento)
- Analise temporal detalhada limitada a 2025 por restricoes de memoria
- Sistema RAG sem validacao por especialistas clinicos

**Proximos passos:**
- Normalizacao por populacao (IBGE) para taxas por 100 mil habitantes
- Integracao com dados climaticos (INMET) para modelos preditivos
- Expansao do golden set do RAG com validacao por profissionais de saude
- Deploy do sistema RAG em ambiente de producao

---

## Estrutura do Projeto

```
ANALISE_DENGUE/
├── analise_dengue.ipynb                    # EDA principal (11M registros)
├── analise_evolucao_temporal_dengue.ipynb  # Analise de progressao clinica
├── RELATORIO_ANALISE.md                    # Relatorio consolidado
├── README.md                               # Este arquivo
├── requirements.txt                        # Dependencias Python
├── streamlit_graph.py                      # Visualizacao interativa
├── LINKEDIN.md                             # Post para divulgacao
│
├── BASE DE DADOS/                          # Dados do SINAN (2022-2025)
│   ├── DENGBR22.csv
│   ├── DENGBR23.csv
│   ├── DENGBR24.csv
│   └── DENGBR25.csv
│
├── GRAFICOS/                               # Visualizacoes exportadas
│
└── SISTEMA_RAG_TRIAGEM_DENGUE/             # Sistema de triagem inteligente
    ├── executar.py                         # Script de execucao
    ├── gerar_base_conhecimento.py          # Gerador da base RAG
    ├── requirements.txt                    # Dependencias do RAG
    ├── backend/
    │   ├── rag_system.py                   # Core RAG com ChromaDB
    │   ├── questionario.py                 # Questionario estruturado
    │   ├── perguntas_adaptativas.py        # Sistema adaptativo
    │   ├── avaliacao.py                    # Metricas e validacao
    │   ├── local_analyzer.py               # Analisador local
    │   └── data_processor.py               # Processador de dados
    ├── frontend/
    │   └── app.py                          # Interface Streamlit
    ├── config/
    │   └── config.yaml                     # Configuracoes
    └── data/
        ├── base_conhecimento_dengue.csv    # Base de conhecimento
        └── knowledge_base.json             # Base vetorizada
```

---

## Como Executar

### Analise Exploratoria
```bash
# Instalar dependencias
pip install -r requirements.txt

# Abrir notebooks no Jupyter
jupyter notebook analise_dengue.ipynb
jupyter notebook analise_evolucao_temporal_dengue.ipynb
```

### Sistema RAG de Triagem
```bash
cd SISTEMA_RAG_TRIAGEM_DENGUE

# Instalar dependencias
pip install -r requirements.txt

# Executar interface
python executar.py
# ou
streamlit run frontend/app.py
```

---

<center>

## Feedback

Sugestoes, criticas construtivas e recomendacoes de estudo sao muito bem-vindas.  
Sinta-se a vontade para abrir uma **Issue** ou me contatar no [LinkedIn](https://www.linkedin.com/in/igor-tca/)

</center>
