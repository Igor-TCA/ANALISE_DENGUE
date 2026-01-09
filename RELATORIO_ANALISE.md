# 🦟 Relatorio - Dengue no Brasil (2022-2025) | Resultados da Analise Exploratoria

<center>

## Contexto e Objetivo

</center>

Este relatorio consolida os **principais resultados** de uma **Analise Exploratoria de Dados (EDA)** sobre **casos notificados de dengue no Brasil entre 2022 e 2025**, utilizando microdados do **SINAN disponibilizados pelo DATASUS**.

O projeto nasceu de um estudo academico sobre os dados de dengue de 2025 e evoluiu para uma **analise consolidada de 4 anos** (2022-2025), gerando insights que fundamentaram o desenvolvimento de um **Sistema de Triagem Inteligente com RAG**.

Importante: os resultados abaixo refletem **dados de notificacao** (nao necessariamente casos confirmados).  
A metrica de mortalidade utilizada e a **proporcao de obitos entre casos notificados** (obitos/casos).

---

<center>

## Fonte de Dados
</center>

- **DATASUS / SINAN** - microdados de notificacoes de dengue (CSV, 2022-2025)
- **SINAN** - legenda/codificacao de variaveis (sintomas, evolucao, idade)

---

<center>

## Visao Geral do Dataset

</center>

| Metrica | Valor |
|---|---:|
| **Total de registros** | **10.998.370** |
| **Periodo** | **2022-2025** |
| **Cobertura** | **27 UFs** |
| **Arquivos processados** | **4 (DENGBR22-25.csv)** |

### Distribuicao por Ano

| Ano | Registros | Percentual |
|---|---:|---:|
| 2022 | 1.393.877 | 12,7% |
| 2023 | 1.508.653 | 13,7% |
| **2024** | **6.427.053** | **58,4%** |
| 2025 | 1.668.787 | 15,2% |

**Destaque:** O ano de 2024 concentra quase 60% de todos os casos notificados no periodo, indicando uma epidemia de grandes proporcoes.

---

<center>

## Resultados da Exploracao

### Distribuicao por Faixa Etaria (Casos Notificados)

</center>

| Faixa Etaria | Casos | Percentual |
|---|---:|---:|
| **Adultos (23-60)** | **6.104.377** | **55,5%** |
| Criancas (0-15) | 1.900.936 | 17,3% |
| Jovens (15-23) | 1.556.117 | 14,2% |
| Idosos (60+) | 1.436.940 | 13,1% |

**Resumo:** Adultos (23-60) concentram mais da metade dos casos notificados.

---

<center>

### Sintomas mais Frequentes por Faixa Etaria

</center>

**Criancas (0-15)**
| Sintoma | Frequencia |
|---|---:|
| Febre | 92,3% |
| Dor de cabeca | 69,8% |
| Dor muscular | 65,3% |
| Nausea | 37,7% |
| Vomito | 34,2% |

**Jovens (15-23)**
| Sintoma | Frequencia |
|---|---:|
| Febre | 87,4% |
| Dor de cabeca | 85,6% |
| Dor muscular | 82,9% |
| Nausea | 47,0% |
| Dor retro-orbital | 35,9% |

**Adultos (23-60)**
| Sintoma | Frequencia |
|---|---:|
| Febre | 84,9% |
| Dor muscular | 84,4% |
| Dor de cabeca | 84,0% |
| Nausea | 45,2% |
| Dor retro-orbital | 34,6% |

**Idosos (60+)**
| Sintoma | Frequencia |
|---|---:|
| Dor muscular | 80,2% |
| Febre | 77,1% |
| Dor de cabeca | 73,5% |
| Nausea | 42,6% |
| Hipertensao | 35,1% |

**Resumo clinico:**
- **Febre** e o sintoma mais frequente em todas as faixas etarias
- Em **idosos**, a presenca de **hipertensao** se destaca como comorbidade associada

---

<center>

### Distribuicao por UF (Top 10 em Volume)

</center>

| Rank | UF | Casos | Percentual |
|---:|---|---:|---:|
| 1 | **SP** | **3.772.895** | **34,3%** |
| 2 | MG | 2.319.644 | 21,1% |
| 3 | PR | 1.117.890 | 10,2% |
| 4 | GO | 695.987 | 6,3% |
| 5 | SC | 512.456 | 4,7% |
| 6 | RS | 489.234 | 4,4% |
| 7 | MS | 378.912 | 3,4% |
| 8 | DF | 267.845 | 2,4% |
| 9 | BA | 198.567 | 1,8% |
| 10 | RJ | 187.234 | 1,7% |

**Resumo:** SP e MG juntos representam mais de 55% do volume nacional de notificacoes.

---

<center>

### Obitos por Faixa Etaria

</center>

| Faixa Etaria | Obitos | Casos | Taxa de Obito |
|---|---:|---:|---:|
| **Idosos (60+)** | **7.836** | 1.436.940 | **0,545%** |
| Adultos (23-60) | 4.189 | 6.104.377 | 0,069% |
| Criancas (0-15) | 423 | 1.900.936 | 0,022% |
| Jovens (15-23) | 250 | 1.556.117 | 0,016% |

| Metrica | Valor |
|---|---:|
| **Total de obitos** | **12.698** |
| **Taxa geral (obitos/casos)** | **0,1155%** |

**Distribuicao dos Obitos:**
| Faixa Etaria | Obitos | % do Total |
|---|---:|---:|
| **Idosos (60+)** | **7.836** | **61,7%** |
| Adultos (23-60) | 4.189 | 33,0% |
| Criancas (0-15) | 423 | 3,3% |
| Jovens (15-23) | 250 | 2,0% |

**Resumo critico:** Apesar de representarem apenas 13,1% dos casos, **idosos concentram 61,7% dos obitos** e apresentam taxa de obito **34 vezes maior** que jovens.

---

<center>

## Analise de Evolucao Temporal (Dados de 2025)

</center>

A analise detalhada de evolucao temporal foi realizada com os dados de 2025 (1.668.787 registros) para identificar padroes de progressao clinica.

### Metricas de Evolucao

| Intervalo | N Casos | Media (dias) | Mediana (dias) | P90 |
|---|---:|---:|---:|---:|
| Sintomas -> Notificacao | 1.660.551 | 3,7 | 3,0 | 7,0 |
| Sintomas -> Sinais de Alarme | 36.869 | 3,7 | 3,0 | 7,0 |
| Sintomas -> Gravidade | 2.809 | 4,9 | 4,0 | 9,0 |
| Sintomas -> Obito | 2.422 | 10,8 | 7,0 | 23,0 |
| Internacao -> Obito | 1.946 | 7,0 | 3,0 | 18,0 |

### Janelas Criticas de Evolucao

| Periodo | % dos Casos Graves |
|---|---:|
| Dias 1-2 | 20,4% |
| **Dias 3-5** | **43,9%** |
| Dias 6-7 | 18,3% |
| Dias 8-14 | 12,5% |
| Dias 15+ | 4,8% |

**Insight:** A maioria das evolucoes para gravidade (64,2%) ocorre entre os **dias 3-7** apos o inicio dos sintomas.

### Evolucao por Faixa Etaria

| Faixa Etaria | N Casos | Taxa Hospitalizacao | Taxa Obito | Mediana Alarme (dias) |
|---|---:|---:|---:|---:|
| Crianca (0-14) | 252.169 | 5,2% | 0,022% | 2,0 |
| Jovem (15-22) | 229.096 | 2,9% | 0,022% | 3,0 |
| Adulto (23-59) | 950.136 | 3,5% | 0,064% | 3,0 |
| **Idoso (60+)** | **237.379** | **8,2%** | **0,461%** | **3,5** |

**Destaque:** Idosos apresentam taxa de hospitalizacao 2,8x maior que adultos e taxa de obito 7x maior.

---

<center>

## Insights para Saude Publica

</center>

### 1. Priorizacao de Risco (Idosos)

A maior proporcao de obitos entre notificados ocorre em **idosos (60+)**, sugerindo:
- Triagem e acompanhamento mais intensivos para este grupo
- Protocolos de hidratacao e observacao precoce
- Comunicacao de risco e acesso rapido a assistencia

### 2. Janela Critica de Monitoramento

O periodo entre **dias 3-7** apos inicio dos sintomas e critico:
- 64,2% das evolucoes para gravidade ocorrem nesta janela
- Sistema de triagem deve alertar para reavaliacao neste periodo
- Pacientes no dia 3-5 precisam de monitoramento intensivo

### 3. Preparacao Sazonal

O pico de casos em 2024 (58,4% do total) demonstra a necessidade de:
- Intensificar prevencao e controle vetorial antes do periodo critico
- Dimensionar estoque e capacidade assistencial para picos epidemicos
- Preparar equipes de saude com protocolos atualizados

### 4. Comorbidades como Aceleradores

Analise de sintomas mostra que em idosos:
- Hipertensao aparece entre os 5 sintomas mais frequentes
- Diabetes e hipertensao associados a evolucao mais rapida para gravidade
- Priorizar estas perguntas no questionario de triagem

---

<center>

## Aplicacao no Sistema RAG de Triagem

</center>

Os insights desta analise foram utilizados para desenvolver o **Sistema RAG de Triagem Inteligente**:

1. **Base de Conhecimento:** 56 entradas derivadas de 11M casos
2. **Pesos de Risco:** Ajustados para idade avancada (60+) e comorbidades
3. **Perguntas Adaptativas:** Priorizacao de sintomas de alta discriminacao
4. **Classificacao em 4 Niveis:** BAIXO/MEDIO/ALTO/CRITICO

O sistema utiliza os padroes temporais identificados para:
- Perguntar "Ha quantos dias comecaram os sintomas?" como pergunta-chave
- Aumentar nivel de risco para pacientes no periodo critico (dias 3-7)
- Considerar comorbidades como fatores de aceleracao

---

<center>

## Limitacoes

</center>

- Dados de **notificacao** (nao confirmados): pode haver subnotificacao
- Metrica de obitos como **obitos/casos notificados**: nao equivale a taxa de mortalidade populacional
- Analise temporal detalhada limitada a 2025 por restricoes de memoria
- Variacoes regionais podem refletir diferencas de acesso e registro

---

<center>

## Referencias

</center>

**1. Manejo Clinico e Vulnerabilidade de Idosos**  
BRASIL. Ministerio da Saude. **Dengue: diagnostico e manejo clinico: adulto e crianca**. 6. ed. Brasilia, DF: Ministerio da Saude, 2024.

**2. Sazonalidade e Vigilancia Epidemiologica**  
BRASIL. Ministerio da Saude. **Boletim Epidemiologico: Monitoramento das Arboviroses Urbanas**. Brasilia, DF: Ministerio da Saude, 2024.

**3. Diretrizes Internacionais**  
ORGANIZACAO PAN-AMERICANA DA SAUDE. **Dengue: diretrizes para diagnostico e tratamento nas Americas**. Washington, D.C.: OPAS, 2016.

**4. Metodologia de Dados**  
BRASIL. Ministerio da Saude. **Guia de Vigilancia em Saude**. 6. ed. Brasilia, DF: Ministerio da Saude, 2023.

---

*Analise realizada com dados do DATASUS (SINAN) - Ministerio da Saude*  
*Ultima atualizacao: Janeiro/2026*
