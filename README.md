# 🦟 Análise de Dengue no Brasil - 2025

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg?style=flat&logo=jupyter&logoColor=white)](https://jupyter.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458.svg?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## Sobre o Projeto

Este projeto foi desenvolvido com **fins educacionais**, com o objetivo de **estudar e praticar** análise exploratória de dados utilizando Python, Pandas e bibliotecas de visualização.

O tema escolhido foi a análise de casos de dengue notificados no Brasil em 2025, utilizando dados públicos do SINAN (Sistema de Informação de Agravos de Notificação).

## Objetivos de Aprendizado

- Praticar **manipulação de dados** com Pandas
- Aplicar **tratamento de dados** seguindo padrões oficiais (codificação SINAN)
- Criar **visualizações gráficas** com Matplotlib e Seaborn
- Gerar **mapas coropléticos** com GeoPandas
- Estruturar uma análise exploratória completa seguindo boas práticas
- Escrever **queries SQL** equivalentes às análises em Python

## Ferramentas Utilizadas

| Ferramenta | Uso |
|------------|-----|
| **Python 3.13** | Linguagem principal |
| **Pandas** | Manipulação e análise de dados |
| **NumPy** | Operações numéricas |
| **Matplotlib** | Visualização de dados |
| **Seaborn** | Visualizações estatísticas |
| **GeoPandas** | Análise geoespacial e mapas |
| **Jupyter Notebook** | Ambiente de desenvolvimento |
| **SQL** | Queries de consulta de dados |

## Conceitos Aplicados

### Análise de Dados
- Carregamento e exploração inicial de datasets
- Tratamento de valores ausentes e inconsistentes
- Conversão de tipos de dados
- Decodificação de variáveis categóricas (padrão SINAN)
- Criação de variáveis derivadas (faixas etárias, regiões)

### Visualização de Dados
- Gráficos de barras e pizza
- Heatmaps de correlação
- Dashboards com múltiplos painéis
- Mapas coropléticos
- Gráficos combinados (Combo Chart)

### Boas Práticas
- Código documentado e organizado por seções
- Uso de funções para operações repetitivas
- Separação entre tratamento, análise e visualização
- Exportação de resultados e gráficos

## Estrutura do Projeto

```
ANALISE_DENGUE/
├── analise_dengue.ipynb       # Notebook principal com análise completa
├── analise_denque_sql.sql     # Queries SQL equivalentes às análises
├── DENGBR25.csv               # Dataset de dengue do SINAN (2025)
├── CODIGO_DISTRITOS/          # Dados de referência IBGE (DTB 2024)
├── GRAFICOS/                  # Gráficos exportados da análise
├── requirements.txt           # Dependências do projeto
├── README.md                  # Este arquivo
└── RELATORIO_ANALISE.md       # Relatório completo com resultados e insights
```

## Como Executar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o Notebook

Abra o arquivo `analise_dengue.ipynb` no Jupyter Notebook ou VS Code com a extensão Jupyter.

Execute as células sequencialmente para reproduzir toda a análise.

## Seções da Análise (Notebook)

| # | Seção | Descrição |
|---|-------|-----------|
| 1 | Importação | Bibliotecas e configurações |
| 2 | Carregamento | Leitura do dataset SINAN |
| 3 | Tratamento SINAN | Conversão de tipos e decodificação |
| 4 | Faixas Etárias | Categorização por idade |
| 5 | Sintomas | Análise de sintomas por faixa etária |
| 6 | Regiões | Distribuição geográfica |
| 7 | Mortalidade | Óbitos e taxas por faixa etária |
| 8 | Geográfica | Mapas e municípios |
| 9 | Evolução Temporal | Casos por semana epidemiológica |

## Resultados

Consulte o arquivo **[RELATORIO_ANALISE.md](RELATORIO_ANALISE.md)** para:
- Resultados completos da análise
- Tabelas detalhadas de todos os indicadores
- Insights e observações
- Fontes de dados utilizadas
- Propostas de estudos futuros

## Codificação SINAN

O projeto utiliza a codificação padrão do SINAN para:

| Campo | Codificação |
|-------|-------------|
| **Idade (NU_IDADE_N)** | 4xxx=Anos, 3xxx=Meses, 2xxx=Dias, 1xxx=Horas |
| **Sintomas** | 1=Sim, 2=Não, 9=Ignorado |
| **Evolução** | 1=Cura, 2=Óbito pelo agravo, 3=Óbito por outras causas |

## Licença

Este projeto está disponível para uso educacional e de pesquisa.

---

*Projeto desenvolvido para fins de estudo e aprendizado em análise de dados.*