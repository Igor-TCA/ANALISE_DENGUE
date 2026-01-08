# 🦟 Dengue no Brasil (2025) - EDA com dados do DATASUS
<center>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg?style=flat&logo=jupyter&logoColor=white)](https://jupyter.org/)

</center>

Projeto de portfólio em **Análise Exploratória de Dados (EDA)** sobre **casos notificados de dengue no Brasil em 2025**, utilizando **microdados do SINAN disponibilizados pelo DATASUS**.  
O foco é transformar dados de notificação em um panorama analítico com **tabelas, gráficos e insights** para leitura de perfil, distribuição territorial e sazonalidade.

---

## Resultado em 30 segundos

- **Base analisada:** 1.502.259 registros (2025), 27 UFs, 5.571 municípios  
- **Perfil etário:** Adultos (23–60) concentram 56,4% dos casos notificados  
- **Distribuição regional:** Sudeste concentra 69,0% dos registros; SP representa 56,7% do total nacional  
- **Desfechos (entre casos notificados):** Idosos (60+) concentram 59,8% dos óbitos e apresentam maior proporção de óbitos (0,497%)  
- **Sazonalidade:** pico concentrado entre março e maio (semana epidemiológica)

 **Relatório completo:** [`RELATORIO_ANALISE.md`](RELATORIO_ANALISE.md)  
 **Notebook (pipeline + gráficos):** [`analise_dengue.ipynb`](analise_dengue.ipynb)

> Observação: os números acima se referem a **dados de notificação** (não necessariamente casos confirmados), conforme a base do SINAN/DATASUS.

---

## Entregáveis

### Análise Exploratória
- Relatório com resultados, tabelas e conclusões: [`RELATORIO_ANALISE.md`](RELATORIO_ANALISE.md)
- Notebook reprodutível (ETL + EDA): [`analise_dengue.ipynb`](analise_dengue.ipynb)
- **Notebook de evolução temporal**: [`analise_evolucao_temporal_dengue.ipynb`](analise_evolucao_temporal_dengue.ipynb) — análise longitudinal com delta de tempos, estratificação demográfica e features para modelos preditivos
- Gráficos exportados em `GRAFICOS/` (inclui dashboard e série temporal)

### Sistema RAG de Triagem
- **Sistema completo de triagem inteligente**: [`SISTEMA_RAG_TRIAGEM_DENGUE/`](SISTEMA_RAG_TRIAGEM_DENGUE/) — RAG com LangChain, ChromaDB e interface Streamlit
- **Documentação técnica de auditoria**: [`docs/PROJECT_AUDIT.md`](docs/PROJECT_AUDIT.md) — arquitetura, diagnóstico e roadmap de melhorias

![Dashboard resumo](GRAFICOS/06_dashboard_final.png)

---

## Principais análises realizadas

### Análise Exploratória (EDA)
- **Visão geral do dataset:** Volume, cobertura por UF e municípios
- **Faixa etária:** Distribuição de casos notificados por grupos etários
- **Sintomas:** Frequência por faixa etária (tratando campos ignorados quando aplicável)
- **Recorte territorial:** Região/UF e municípios com maior volume de notificações
- **Desfechos:** Leitura de gravidade via variável de evolução (quando disponível)
- **Temporal:** Evolução por **semana epidemiológica** (jan–nov/2025)

### Análise de Evolução Temporal (NOVO)
- **Delta de tempos:** Sintomas → Alarme → Gravidade → Óbito (quando aplicável)
- **Estratificação:** Por faixa etária, sexo e região geográfica
- **Progressão clínica:** Identificação de padrões de evolução rápida
- **Features temporais:** Exportação para integração com RAG e modelos preditivos

### Sistema RAG de Triagem (NOVO - v2.0)
- **Perguntas adaptativas:** Minimização de perguntas via ganho de informação
- **Segurança aprimorada:** Guardrails, abstention, citações com rastreabilidade
- **Avaliação estruturada:** Golden set com 12 casos validados, métricas (Recall@K, MRR, nDCG)
- **Classificação em 4 níveis:** BAIXO/MÉDIO/ALTO/CRÍTICO com recomendações de conduta

---

## Fontes de dados

### Epidemiológicos (notificações)
- [DATASUS](https://datasus.saude.gov.br/  ) - Microdados de notificações de dengue (CSV, ano 2025).  
  *(utilizado como base principal do projeto: `DENGBR25.csv`)*
  
  **Nota:** O arquivo `DENGBR25_SAMPLE.csv` é uma **amostra reduzida** da base completa (subset com menos registros), útil para testes rápidos, validação de código e exploração inicial sem necessidade de carregar o dataset completo.

- [SINAN](http://sinan.saude.gov.br/) - Documentação, dicionário/legendas e codificação das variáveis (ex.: sintomas, evolução, idade).  

### Territorial e administrativa (códigos e nomes oficiais)
- [IBGE - Divisão Territorial Brasileira](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/estrutura-territorial/23701-divisao-territorial-brasileira.html) - Tabela oficial de municípios/distritos (códigos, nomes e UF), usada para padronização e junções (município ↔ UF/região).

- [IBGE - Malhas Territoriais](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html) - Geometrias oficiais (UF e municípios) para visualizações geoespaciais (mapas coropléticos).  

### Referências metodológicas
- [Ministério da Saúde - Semana Epidemiológica](https://www.gov.br/saude/)  - Referência para leitura/uso de semanas epidemiológicas e sazonalidade.  

---

## Limitações e próximos passos

**Limitações:** Base de notificação (pode haver subnotificação, campos ignorados e heterogeneidade de preenchimento por localidade).

**Próximos passos recomendados (nível DS):**

- Normalização por população (IBGE) para taxas por 100 mil
- Integração com clima (INMET) para baseline de previsão e avaliação (MAE/MAPE)
- Análise de hotspots por taxa e métodos espaciais/estatísticos
- Integração das features temporais do notebook de evolução com modelos de ML
- Expansão do golden set do RAG com validação por especialistas

---

## Estrutura do Projeto

```
ANALISE_DENGUE/
├── analise_dengue.ipynb                    # EDA principal
├── analise_evolucao_temporal_dengue.ipynb  # Evolução temporal (NOVO)
├── DENGBR25.csv                            # Dataset completo SINAN
├── DENGBR25_SAMPLE.csv                     # Amostra para testes
├── RELATORIO_ANALISE.md                    # Relatório de EDA
├── requirements.txt                        # Dependências
├── docs/
│   └── PROJECT_AUDIT.md                    # Auditoria técnica (NOVO)
├── GRAFICOS/                               # Visualizações exportadas
├── CODIGO_DISTRITOS/                       # Dados territoriais
└── SISTEMA_RAG_TRIAGEM_DENGUE/             # Sistema de triagem inteligente
    ├── backend/
    │   ├── rag_system.py                   # Core RAG (v2.0 com segurança)
    │   ├── questionario.py                 # Questionário estruturado
    │   ├── perguntas_adaptativas.py        # Sistema adaptativo (NOVO)
    │   ├── avaliacao.py                    # Métricas e golden set (NOVO)
    │   └── data_processor.py               # Processador de dados
    ├── frontend/
    │   └── app.py                          # Interface Streamlit
    └── config/
        └── config.yaml                     # Configurações
```

---

<center>

## Feedback

<span style="color:#69b700;">

Sugestões, críticas construtivas e recomendações de estudo são muito bem-vindas.  
Sinta-se à vontade para abrir uma **Issue** ou me contatar no [LinkedIn](https://www.linkedin.com/in/igor-tca/)

</span>
<center/>
