# 🦟 Análise SQL - Dengue Brasil 2025

## Sobre esta Pasta

Esta pasta contém as **queries SQL** desenvolvidas como parte do estudo de análise de dados de dengue no Brasil.

##  Objetivo de Aprendizado

O objetivo principal foi praticar a **tradução de análises feitas em Python/Pandas para SQL**, desenvolvendo habilidades em:

- **CTEs (Common Table Expressions)**: Uso extensivo de `WITH` para organizar queries complexas
- **Funções de Janela**: Aplicação de `ROW_NUMBER()`, `SUM() OVER()` para rankings e cálculos agregados
- **CASE WHEN**: Decodificação de variáveis categóricas (padrão SINAN)
- **Agregações condicionais**: Cálculo de percentuais com `SUM(CASE WHEN...)`
- **JOINs e Subqueries**: Combinação de dados agregados
- **Tratamento de dados**: Conversão de tipos e valores nulos

## Conceitos Praticados

### Decodificação SINAN
```sql
-- Exemplo de decodificação de idade (padrão SINAN)
CASE 
    WHEN NU_IDADE_N >= 4000 AND NU_IDADE_N < 5000 THEN NU_IDADE_N - 4000  -- Anos
    WHEN NU_IDADE_N >= 3000 AND NU_IDADE_N < 4000 THEN (NU_IDADE_N - 3000) / 12.0  -- Meses
    ...
END AS IDADE_ANOS
```

### Agregações por Grupo
```sql
-- Cálculo de percentual de sintomas por faixa etária
ROUND(SUM(CASE WHEN FEBRE = 1 THEN 1 ELSE 0 END) * 100.0 / 
      NULLIF(SUM(CASE WHEN FEBRE IN (1, 2) THEN 1 ELSE 0 END), 0), 1) AS febre_pct
```

### Window Functions
```sql
-- Ranking de faixa etária mais atingida por região
ROW_NUMBER() OVER (PARTITION BY REGIAO ORDER BY casos DESC) AS rank
```

## Etapas Implementadas

| Etapa | Descrição | Status |
|-------|-----------|--------|
| 1 | Exploração inicial dos dados |  Concluído |
| 2 | Decodificação de idade (SINAN) |  Concluído |
| 3 | Criação de faixas etárias |  Concluído |
| 4 | Análise de sintomas por faixa |  Concluído |
| 5 | Análise por região |  Concluído |
| 6 | Análise de mortalidade |  Pendente |
| 7 | Análise geográfica (UF/Município) |  Pendente |
| 8 | Evolução temporal |  Pendente |

## Status

> ** TRABALHO EM ANDAMENTO**
> 
> As queries implementadas cobrem as etapas 1 a 5 da análise.
> As etapas de mortalidade, análise geográfica detalhada e evolução temporal estão pendentes de implementação.

## Referência

Para a análise completa em Python, consulte o branch `main` com o notebook `analise_dengue.ipynb`.

---

*Desenvolvido para fins de estudo em SQL e análise de dados.*
