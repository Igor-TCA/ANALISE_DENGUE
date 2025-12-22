# 🦟 Dengue no Brasil (2025) — EDA com dados do DATASUS (SINAN Online)
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

- Relatório com resultados, tabelas e conclusões: [`RELATORIO_ANALISE.md`](RELATORIO_ANALISE.md)
- Notebook reprodutível (ETL + EDA): [`analise_dengue.ipynb`](analise_dengue.ipynb)
- Gráficos exportados em `GRAFICOS/` (inclui dashboard e série temporal)

![Dashboard resumo](GRAFICOS/06_dashboard_final.png)

---

## Principais análises realizadas

- **Visão geral do dataset:** volume, cobertura por UF e municípios
- **Faixa etária:** distribuição de casos notificados por grupos etários
- **Sintomas:** frequência por faixa etária (tratando campos ignorados quando aplicável)
- **Recorte territorial:** região/UF e municípios com maior volume de notificações
- **Desfechos:** leitura de gravidade via variável de evolução (quando disponível)
- **Temporal:** evolução por **semana epidemiológica** (jan–nov/2025)

---

## Fontes de dados

### Epidemiológicos (notificações)
- [DATASUS](https://datasus.saude.gov.br/  ) - Microdados de notificações de dengue (CSV, ano 2025).  
  *(utilizado como base principal do projeto: `DENGBR25.csv`)*

- [SINAN](http://sinan.saude.gov.br/) - Documentação, dicionário/legendas e codificação das variáveis (ex.: sintomas, evolução, idade).  

### Territorial e administrativa (códigos e nomes oficiais)
- [IBGE - Divisão Territorial Brasileira](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/estrutura-territorial/23701-divisao-territorial-brasileira.html) - Tabela oficial de municípios/distritos (códigos, nomes e UF), usada para padronização e junções (município ↔ UF/região).

- [IBGE - Malhas Territoriais](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html) - Geometrias oficiais (UF e municípios) para visualizações geoespaciais (mapas coropléticos).  

### Referências metodológicas
- [Ministério da Saúde - Semana Epidemiológica](https://www.gov.br/saude/)  - Referência para leitura/uso de semanas epidemiológicas e sazonalidade.  

---

## Limitações e próximos passos

**Limitações:** base de notificação (pode haver subnotificação, campos ignorados e heterogeneidade de preenchimento por localidade).

**Próximos passos recomendados (nível DS):**

- Normalização por população (IBGE) para taxas por 100 mil
- Integração com clima (INMET) para baseline de previsão e avaliação (MAE/MAPE)
- Análise de hotspots por taxa e métodos espaciais/estatísticos

---

<center>

## Feedback

<span style="color:#69b700;">

Sugestões, críticas construtivas e recomendações de estudo são muito bem-vindas.  
Sinta-se à vontade para abrir uma **Issue** ou me contatar no [LinkedIn](https://www.linkedin.com/in/igor-tca/)

</span>
<center/>
