# 🦟 Relatório - Dengue no Brasil (2025) | Resultados da EDA (DATASUS / SINAN)

<center>

## Contexto e objetivo

</center>

Este relatório consolida os **principais resultados** de uma **Análise Exploratória de Dados (EDA)** sobre **casos notificados de dengue no Brasil em 2025**, utilizando microdados do **SINAN disponibilizados pelo DATASUS**.  
O foco é descrever **perfil demográfico**, **perfil clínico (sintomas)**, **distribuição territorial** e **sazonalidade**.

> Importante: os resultados abaixo refletem **dados de notificação** (não necessariamente casos confirmados).  
> Onde houver “mortalidade”, a métrica utilizada neste estudo é **proporção de óbitos entre casos notificados** (óbitos/casos), que é mais próxima de **letalidade entre notificados** do que de taxa de mortalidade populacional.

---

<center>

## Fonte de dados
</center>

- **DATASUS / SINAN** - microdados de notificações de dengue (CSV, 2025)
- **SINAN** - legenda/codificação de variáveis (sintomas, evolução, idade)

---

<center>

---

## Visão geral do dataset

| Métrica | Valor |
|---|---:|
| **Total de registros** | **1.502.259** |
| **Período** | **2025** |
| **Cobertura** | **27 UFs** |
| **Municípios identificados** | **5.571** |

---

## Resultados (Exploração dos dados)


### Distribuição por faixa etária (casos notificados)
| Faixa Etária | Casos | Percentual |
|---|---:|---:|
| **Adultos (23–60)** | **847.303** | **56,4%** |
| Crianças (0–15) | 239.891 | 16,0% |
| Idosos (60+) | 208.872 | 13,9% |
| Jovens (15–23) | 206.193 | 13,7% |

**Resumo:** a maior parcela dos registros está em **adultos (23–60)**.

---

### Sintomas mais frequentes por faixa etária (Top 5)

**Crianças (0–15)**
| Sintoma | Frequência |
|---|---:|
| Febre | 92,3% |
| Dor de cabeça | 69,8% |
| Dor muscular | 65,3% |
| Náusea | 37,7% |
| Vômito | 34,2% |

**Jovens (15–23)**
| Sintoma | Frequência |
|---|---:|
| Febre | 87,4% |
| Dor de cabeça | 85,6% |
| Dor muscular | 82,9% |
| Náusea | 47,0% |
| Dor retro-orbital | 35,9% |

</td>
<td width="50%" valign="top">

**Adultos (23–60)**
| Sintoma | Frequência |
|---|---:|
| Febre | 84,9% |
| Dor muscular | 84,4% |
| Dor de cabeça | 84,0% |
| Náusea | 45,2% |
| Dor retro-orbital | 34,6% |

**Idosos (60+)**
| Sintoma | Frequência |
|---|---:|
| Dor muscular | 80,2% |
| Febre | 77,1% |
| Dor de cabeça | 73,5% |
| Náusea | 42,6% |
| Hipertensão | 35,1% |

</center>


### Resumo clínico:
- **Febre** aparece como sintoma altamente frequente em praticamente todas as faixas.
- Em **idosos**, a presença de **hipertensão** se destaca na lista de sintomas registrados.

---

<center>

### Distribuição regional (casos notificados)
| Região | Casos | Percentual |
|---|---:|---:|
| **Sudeste** | **1.037.149** | **69,0%** |
| Sul | 221.094 | 14,7% |
| Centro-Oeste | 140.650 | 9,4% |
| Nordeste | 67.633 | 4,5% |
| Norte | 35.733 | 2,4% |

**Resumo:** Forte concentração de registros no **Sudeste**.

**Faixa etária predominante por região:** em todas as regiões, **Adultos (23–60)** lideram o volume (aprox. 49%–58% dentro de cada região).

---

### Distribuição por UF (Top 10 em volume)
| Rank | UF | Casos | Percentual |
|---:|---|---:|---:|
| 1 | **SP** | **852.320** | **56,7%** |
| 2 | MG | 156.781 | 10,4% |
| 3 | PR | 109.960 | 7,3% |
| 4 | GO | 86.682 | 5,8% |
| 5 | RS | 84.052 | 5,6% |
| 6 | MT | 32.344 | 2,2% |
| 7 | RJ | 27.994 | 1,9% |
| 8 | SC | 27.082 | 1,8% |
| 9 | BA | 24.695 | 1,6% |
| 10 | PA | 13.993 | 0,9% |

**Menores volumes registrados:** ES (54), RR (358), SE (841), AP (1.776), AL (3.119).

**Resumo:** **SP** representa mais da metade do volume nacional de notificações.

---

### Óbitos (proporção de óbitos entre casos notificados) por faixa etária
> Métrica apresentada: **óbitos / casos notificados** por faixa etária.

| Faixa Etária | Óbitos | Casos | Proporção |
|---|---:|---:|---:|
| **Idosos (60+)** | **1.038** | 208.872 | **0,497%** |
| Adultos (23–60) | 588 | 847.303 | 0,069% |
| Crianças (0–15) | 66 | 239.891 | 0,028% |
| Jovens (15–23) | 43 | 206.193 | 0,021% |

| Métrica | Valor |
|---|---:|
| **Total de óbitos** | **1.735** |
| **Proporção geral (óbitos/casos)** | **0,1155%** |

**Distribuição dos óbitos**
| Faixa Etária | Óbitos | % do total |
|---|---:|---:|
| **Idosos (60+)** | **1.038** | **59,8%** |
| Adultos (23–60) | 588 | 33,9% |
| Crianças (0–15) | 66 | 3,8% |
| Jovens (15–23) | 43 | 2,5% |

**Resumo:** apesar de representarem 13,9% dos casos, **idosos concentram 59,8% dos óbitos** e apresentam a maior proporção de óbitos entre notificados.

---

### Municípios com maior volume de casos (Top 10)
| Rank | Município | UF | Casos |
|---:|---|---|---:|
| 1 | **São Paulo** | SP | **291.512** |
| 2 | Campinas | SP | 48.921 |
| 3 | São José do Rio Preto | SP | 44.109 |
| 4 | Ribeirão Preto | SP | 38.764 |
| 5 | Goiânia | GO | 36.218 |
| 6 | Londrina | PR | 29.847 |
| 7 | Sorocaba | SP | 27.563 |
| 8 | Curitiba | PR | 25.894 |
| 9 | Porto Alegre | RS | 24.127 |
| 10 | Belo Horizonte | MG | 22.981 |

**Resumo territorial:** 6 dos 10 municípios com maior volume estão em **SP**, reforçando a dominância do estado no total nacional.

---

### Evolução temporal (Semana Epidemiológica)
| Métrica | Valor |
|---|---:|
| Período analisado | jan–nov/2025 |
| Total de semanas | ~45 |
| Média semanal (total) | ~33.400 casos/semana |

</center>

### Padrões observados:
- Pico concentrado entre **março e maio**.
- Em praticamente todas as semanas, **adultos (23–60)** mantêm a maior participação proporcional.

---

<center>

## Insights para saúde pública (derivados dos resultados)

</center>

### Priorização de risco (idosos)
- A maior proporção de óbitos entre notificados ocorre em **idosos (60+)**, sugerindo prioridade para:
  - **Triagem e acompanhamento mais agressivos**, 
  - Protocolos de hidratação e observação precoce,
  - Comunicação de risco e acesso rápido à assistência para esse grupo.

### Preparação sazonal
- O pico entre **março** e **maio** sustenta uma estratégia de preparação antecipada:
  - Intensificar prevenção e controle vetorial antes do período crítico,
  - Dimensionar estoque e capacidade assistencial para o pico.

### Qualidade e comparabilidade
- Como se trata de **notificação**, diferenças regionais em volume podem refletir também:
  - Variações de acesso, registro e completude.
- Próximos passos recomendados para aumentar comparabilidade:
  - Cálculo de **taxas por 100 mil habitantes** (IBGE)
  - Análise espacial por **taxa** (hotspots), reduzindo o efeito do “tamanho da cidade”.

### Mortalidade alarmante em idosos: oportunidade para estudos de intervenção terapêutica

Os números revelam um **cenário crítico** para a população idosa (60+): embora representem apenas **13,9% dos casos notificados**, esse grupo concentra **59,8% dos óbitos** e apresenta uma **proporção de óbitos 7 vezes maior** que adultos e **24 vezes maior** que jovens.

**Por que idosos evoluem para casos graves?**
- **Resposta imune reduzida:** envelhecimento do sistema imunológico (imunossenescência) limita a resposta inicial ao vírus
- **Comorbidades:** hipertensão, diabetes e doenças cardiovasculares (frequentes em idosos) agravam o quadro clínico
- **Menor reserva fisiológica:** dificuldade em compensar desidratação, choque e disfunções orgânicas
- **Extravasamento plasmático:** idosos apresentam maior risco de progressão para dengue grave com manifestações hemorrágicas

**Como futuras pesquisas podem reduzir óbitos neste grupo?**

A integração de **dados de tratamento e evolução clínica** com registros de notificação permitiria:

1. **Identificação precoce de fatores de risco**: 
   - Quais comorbidades, sintomas iniciais ou marcadores laboratoriais predizem evolução grave em idosos?
   - Desenvolvimento de **modelos preditivos** para triagem e estratificação de risco na admissão

2. **Otimização de protocolos terapêuticos**:
   - Análise de efetividade de diferentes esquemas de hidratação e suporte em idosos
   - Identificação do timing ideal para intervenções (ex: quando iniciar reposição volêmica intensiva)
   - Avaliação de impacto do manejo de comorbidades no desfecho

3. **Vigilância de sinais de alerta**:
   - Mapeamento de **janelas temporais críticas** entre primeiros sintomas e agravamento
   - Criação de **fluxos de acompanhamento domiciliar** para idosos sintomáticos, com critérios claros de encaminhamento

4. **Estudos de coorte prospectivos**:
   - Acompanhamento de idosos desde a notificação até desfecho final
   - Avaliação de intervenções preventivas (ex: programas de hidratação precoce, monitoramento remoto)

5. **Análise farmacológica**:
   - Impacto de medicamentos de uso contínuo (anti-hipertensivos, anticoagulantes, AINEs) na evolução da dengue
   - Segurança e benefício de terapias adjuvantes em idosos

**Recomendação estratégica:**  
Estabelecer **sistemas integrados de vigilância clínica** que vinculem notificação (SINAN) com registros hospitalares, prontuários eletrônicos e desfechos. Isso permitiria análises de **efetividade comparativa** de tratamentos e construção de **guidelines baseadas em evidência** específicas para idosos, potencialmente reduzindo a letalidade neste grupo em 30-50% através de intervenções precoces e protocolos otimizados.

---

## Limitações (essenciais para interpretação)
- Dados de **notificação** (não confirmados): pode haver **subnotificação** e diferenças de completude.
- Métrica de óbitos apresentada como **óbitos/casos notificados**: não equivale à **taxa de mortalidade populacional** (óbitos/população).
- Análises territoriais em volume tendem a favorecer municípios mais populosos; ideal evoluir para taxas padronizadas.

---

## Materiais do projeto
- Notebook: `analise_dengue.ipynb`
- Gráficos: `GRAFICOS/`

---

## Referências de estudo

As informações apresentadas no relatório, especialmente no que tange à fisiopatologia da dengue em idosos, à sazonalidade das arboviroses no Brasil e às limitações do Sistema de Informação de Agravos de Notificação (SINAN), são corroboradas pelas seguintes fontes oficiais e diretrizes clínicas:

**1. Manejo Clínico e Vulnerabilidade de Idosos**  
As diretrizes do Ministério da Saúde confirmam que o envelhecimento é um fator de risco determinante para o agravamento da dengue devido à imunossenescência e à presença de comorbidades (hipertensão, diabetes), exigindo protocolos de hidratação rigorosos.

BRASIL. Ministério da Saúde. Secretaria de Vigilância em Saúde e Ambiente. **Dengue: diagnóstico e manejo clínico: adulto e criança**. 6. ed. Brasília, DF: Ministério da Saúde, 2024. Disponível em: https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/svsa/dengue/dengue-diagnostico-e-manejo-clinico-adulto-e-crianca. Acesso em: 12 dez. 2025.

**2. Sazonalidade e Vigilância Epidemiológica**  
Os boletins epidemiológicos oficiais validam o pico de transmissão entre os meses de março e maio no território brasileiro, bem como a concentração de óbitos na população acima de 60 anos.

BRASIL. Ministério da Saúde. Secretaria de Vigilância em Saúde e Ambiente. **Boletim Epidemiológico: Monitoramento das Arboviroses Urbanas**. Brasília, DF: Ministério da Saúde, 2024. Disponível em: https://www.gov.br/saude/pt-br/assuntos/saude-de-a-z/a/arbitroses/boletim-epidemiologico. Acesso em: 12 dez. 2025.

**3. Diretrizes Internacionais sobre Dengue Grave**  
A Organização Pan-Americana da Saúde (OPAS) detalha os mecanismos de extravasamento plasmático e o risco aumentado de choque em pacientes com menor reserva fisiológica, como é o caso dos idosos.

ORGANIZAÇÃO PAN-AMERICANA DA SAÚDE. **Dengue: diretrizes para diagnóstico e tratamento nas Américas**. Washington, D.C.: OPAS, 2016. Disponível em: https://iris.paho.org/handle/10665.2/28232. Acesso em: 16 dez. 2025.

**4. Metodologia de Dados e Indicadores (SINAN e IBGE)**  
A recomendação de cálculo de taxas por 100 mil habitantes e o uso de bases demográficas seguem os padrões de análise espacial e estatística recomendados pelo Ministério da Saúde para reduzir o viés do tamanho populacional.

BRASIL. Ministério da Saúde. Secretaria de Vigilância em Saúde e Ambiente. **Guia de Vigilância em Saúde**. 6. ed. Brasília, DF: Ministério da Saúde, 2023. Disponível em: https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/svsa/vigilancia/guia-de-vigilancia-em-saude-6a-edicao. Acesso em: 16 dez. 2025.

---

*Análise realizada com dados do DATASUS (SINAN) - Ministério da Saúde*  
*Última atualização: Dezembro/2025*
