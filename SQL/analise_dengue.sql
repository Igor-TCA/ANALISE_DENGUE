-- =============================================================================
-- ETAPA 1: CARREGAMENTO E EXPLORAÇÃO DOS DADOS
-- =============================================================================

-- 1.1 Contar total de registros
SELECT COUNT(*) AS total_registros FROM notificacoes;

-- 1.2 Visualizar primeiros registros
SELECT * FROM notificacoes LIMIT 10;

-- =============================================================================
-- ETAPA 2: TRATAMENTO DE DADOS - DECODIFICAÇÃO DA IDADE
-- Padrão SINAN: 4xxx=Anos, 3xxx=Meses, 2xxx=Dias, 1xxx=Horas
-- =============================================================================

-- 2.1 Decodificar idade em anos
WITH idade_decodificada AS (
    SELECT 
        *,
        CASE 
            WHEN NU_IDADE_N >= 4000 AND NU_IDADE_N < 5000 THEN NU_IDADE_N - 4000
            WHEN NU_IDADE_N >= 3000 AND NU_IDADE_N < 4000 THEN (NU_IDADE_N - 3000) / 12.0
            WHEN NU_IDADE_N >= 2000 AND NU_IDADE_N < 3000 THEN (NU_IDADE_N - 2000) / 365.0
            WHEN NU_IDADE_N >= 1000 AND NU_IDADE_N < 2000 THEN (NU_IDADE_N - 1000) / (365.0 * 24)
            ELSE NU_IDADE_N
        END AS IDADE_ANOS
    FROM notificacoes
)
SELECT * FROM idade_decodificada LIMIT 10;

-- 2.2 Verificar distribuição por unidade de tempo original
SELECT 
    CASE 
        WHEN NU_IDADE_N >= 4000 AND NU_IDADE_N < 5000 THEN 'Anos'
        WHEN NU_IDADE_N >= 3000 AND NU_IDADE_N < 4000 THEN 'Meses'
        WHEN NU_IDADE_N >= 2000 AND NU_IDADE_N < 3000 THEN 'Dias'
        WHEN NU_IDADE_N >= 1000 AND NU_IDADE_N < 2000 THEN 'Horas'
        ELSE 'Outro'
    END AS unidade_idade,
    COUNT(*) AS quantidade
FROM notificacoes
GROUP BY 1
ORDER BY quantidade DESC;

-- =============================================================================
-- ETAPA 3: FAIXAS ETÁRIAS
-- Crianças (0-15), Jovens (15-23), Adultos (23-60), Idosos (60+)
-- =============================================================================

-- 3.1 Classificar por faixa etária

WITH dados_com_faixa AS (
    SELECT 
        *,
        CASE 
            WHEN NU_IDADE_N >= 4000 AND NU_IDADE_N < 5000 THEN NU_IDADE_N - 4000
            WHEN NU_IDADE_N >= 3000 AND NU_IDADE_N < 4000 THEN (NU_IDADE_N - 3000) / 12.0
            WHEN NU_IDADE_N >= 2000 AND NU_IDADE_N < 3000 THEN (NU_IDADE_N - 2000) / 365.0
            WHEN NU_IDADE_N >= 1000 AND NU_IDADE_N < 2000 THEN (NU_IDADE_N - 1000) / (365.0 * 24)
            ELSE NU_IDADE_N
        END AS IDADE_ANOS
    FROM notificacoes
),
faixas_etarias AS (
    SELECT 
        *,
        CASE 
            WHEN IDADE_ANOS IS NULL OR IDADE_ANOS < 0 THEN 'Nao informado'
            WHEN IDADE_ANOS <= 15 THEN 'Criancas (0-15)'
            WHEN IDADE_ANOS <= 23 THEN 'Jovens (15-23)'
            WHEN IDADE_ANOS <= 60 THEN 'Adultos (23-60)'
            ELSE 'Idosos (60+)'
        END AS FAIXA_ETARIA
    FROM dados_com_faixa
)
SELECT * FROM faixas_etarias LIMIT 10;

-- 3.2 Contagem por faixa etária
WITH dados_com_faixa AS (
    SELECT 
        CASE 
            WHEN NU_IDADE_N >= 4000 AND NU_IDADE_N < 5000 THEN NU_IDADE_N - 4000
            WHEN NU_IDADE_N >= 3000 AND NU_IDADE_N < 4000 THEN (NU_IDADE_N - 3000) / 12.0
            WHEN NU_IDADE_N >= 2000 AND NU_IDADE_N < 3000 THEN (NU_IDADE_N - 2000) / 365.0
            WHEN NU_IDADE_N >= 1000 AND NU_IDADE_N < 2000 THEN (NU_IDADE_N - 1000) / (365.0 * 24)
            ELSE NU_IDADE_N
        END AS IDADE_ANOS
    FROM notificacoes
),
faixas AS (
    SELECT 
        CASE 
            WHEN IDADE_ANOS IS NULL OR IDADE_ANOS < 0 THEN 'Nao informado'
            WHEN IDADE_ANOS <= 15 THEN 'Criancas (0-15)'
            WHEN IDADE_ANOS <= 23 THEN 'Jovens (15-23)'
            WHEN IDADE_ANOS <= 60 THEN 'Adultos (23-60)'
            ELSE 'Idosos (60+)'
        END AS FAIXA_ETARIA
    FROM dados_com_faixa
)
SELECT 
    FAIXA_ETARIA,
    COUNT(*) AS casos,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentual
FROM faixas
GROUP BY FAIXA_ETARIA
ORDER BY 
    CASE FAIXA_ETARIA
        WHEN 'Criancas (0-15)' THEN 1
        WHEN 'Jovens (15-23)' THEN 2
        WHEN 'Adultos (23-60)' THEN 3
        WHEN 'Idosos (60+)' THEN 4
        ELSE 5
    END;

-- =============================================================================
-- ETAPA 4: ANÁLISE DE SINTOMAS POR FAIXA ETÁRIA
-- =============================================================================

-- 4.1 Frequência de cada sintoma por faixa etária

WITH dados_completos AS (
    SELECT 
        *,
        CASE 
            WHEN NU_IDADE_N >= 4000 AND NU_IDADE_N < 5000 THEN NU_IDADE_N - 4000
            WHEN NU_IDADE_N >= 3000 AND NU_IDADE_N < 4000 THEN (NU_IDADE_N - 3000) / 12.0
            WHEN NU_IDADE_N >= 2000 AND NU_IDADE_N < 3000 THEN (NU_IDADE_N - 2000) / 365.0
            WHEN NU_IDADE_N >= 1000 AND NU_IDADE_N < 2000 THEN (NU_IDADE_N - 1000) / (365.0 * 24)
            ELSE NU_IDADE_N
        END AS IDADE_ANOS
    FROM notificacoes
),
dados_com_faixa AS (
    SELECT 
        *,
        CASE 
            WHEN IDADE_ANOS IS NULL OR IDADE_ANOS < 0 THEN 'Nao informado'
            WHEN IDADE_ANOS <= 15 THEN 'Criancas (0-15)'
            WHEN IDADE_ANOS <= 23 THEN 'Jovens (15-23)'
            WHEN IDADE_ANOS <= 60 THEN 'Adultos (23-60)'
            ELSE 'Idosos (60+)'
        END AS FAIXA_ETARIA
    FROM dados_completos
)
SELECT 
    FAIXA_ETARIA,
    -- Febre
    ROUND(SUM(CASE WHEN FEBRE = 1 THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN FEBRE IN (1, 2) THEN 1 ELSE 0 END), 0), 1) AS febre_pct,
    -- Mialgia (Dor muscular)
    ROUND(SUM(CASE WHEN MIALGIA = 1 THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN MIALGIA IN (1, 2) THEN 1 ELSE 0 END), 0), 1) AS mialgia_pct,
    -- Cefaleia (Dor de cabeça)
    ROUND(SUM(CASE WHEN CEFALEIA = 1 THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN CEFALEIA IN (1, 2) THEN 1 ELSE 0 END), 0), 1) AS cefaleia_pct,
    -- Náusea
    ROUND(SUM(CASE WHEN NAUSEA = 1 THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN NAUSEA IN (1, 2) THEN 1 ELSE 0 END), 0), 1) AS nausea_pct,
    -- Vômito
    ROUND(SUM(CASE WHEN VOMITO = 1 THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN VOMITO IN (1, 2) THEN 1 ELSE 0 END), 0), 1) AS vomito_pct,
    -- Dor retro-orbital
    ROUND(SUM(CASE WHEN DOR_RETRO = 1 THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN DOR_RETRO IN (1, 2) THEN 1 ELSE 0 END), 0), 1) AS dor_retro_pct,
    -- Hipertensão
    ROUND(SUM(CASE WHEN HIPERTENSA = 1 THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN HIPERTENSA IN (1, 2) THEN 1 ELSE 0 END), 0), 1) AS hipertensao_pct,
    -- Exantema (Manchas na pele)
    ROUND(SUM(CASE WHEN EXANTEMA = 1 THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN EXANTEMA IN (1, 2) THEN 1 ELSE 0 END), 0), 1) AS exantema_pct,
    -- Artralgia (Dor nas articulações)
    ROUND(SUM(CASE WHEN ARTRALGIA = 1 THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN ARTRALGIA IN (1, 2) THEN 1 ELSE 0 END), 0), 1) AS artralgia_pct
FROM dados_com_faixa
WHERE FAIXA_ETARIA != 'Nao informado'
GROUP BY FAIXA_ETARIA
ORDER BY 
    CASE FAIXA_ETARIA
        WHEN 'Criancas (0-15)' THEN 1
        WHEN 'Jovens (15-23)' THEN 2
        WHEN 'Adultos (23-60)' THEN 3
        WHEN 'Idosos (60+)' THEN 4
    END;

-- 4.2 Top 5 sintomas - Crianças
WITH dados_completos AS (
    SELECT 
        *,
        CASE 
            WHEN NU_IDADE_N >= 4000 AND NU_IDADE_N < 5000 THEN NU_IDADE_N - 4000
            WHEN NU_IDADE_N >= 3000 AND NU_IDADE_N < 4000 THEN (NU_IDADE_N - 3000) / 12.0
            WHEN NU_IDADE_N >= 2000 AND NU_IDADE_N < 3000 THEN (NU_IDADE_N - 2000) / 365.0
            WHEN NU_IDADE_N >= 1000 AND NU_IDADE_N < 2000 THEN (NU_IDADE_N - 1000) / (365.0 * 24)
            ELSE NU_IDADE_N
        END AS IDADE_ANOS
    FROM notificacoes
),
criancas AS (
    SELECT * FROM dados_completos
    WHERE IDADE_ANOS <= 15 AND IDADE_ANOS >= 0
),
sintomas_criancas AS (
    SELECT 'Febre' AS sintoma, 
           ROUND(SUM(CASE WHEN FEBRE = 1 THEN 1 ELSE 0 END) * 100.0 / 
                 NULLIF(SUM(CASE WHEN FEBRE IN (1, 2) THEN 1 ELSE 0 END), 0), 1) AS percentual
    FROM criancas
    UNION ALL
    SELECT 'Dor muscular', 
           ROUND(SUM(CASE WHEN MIALGIA = 1 THEN 1 ELSE 0 END) * 100.0 / 
                 NULLIF(SUM(CASE WHEN MIALGIA IN (1, 2) THEN 1 ELSE 0 END), 0), 1)
    FROM criancas
    UNION ALL
    SELECT 'Dor de cabeca', 
           ROUND(SUM(CASE WHEN CEFALEIA = 1 THEN 1 ELSE 0 END) * 100.0 / 
                 NULLIF(SUM(CASE WHEN CEFALEIA IN (1, 2) THEN 1 ELSE 0 END), 0), 1)
    FROM criancas
    UNION ALL
    SELECT 'Nausea', 
           ROUND(SUM(CASE WHEN NAUSEA = 1 THEN 1 ELSE 0 END) * 100.0 / 
                 NULLIF(SUM(CASE WHEN NAUSEA IN (1, 2) THEN 1 ELSE 0 END), 0), 1)
    FROM criancas
    UNION ALL
    SELECT 'Vomito', 
           ROUND(SUM(CASE WHEN VOMITO = 1 THEN 1 ELSE 0 END) * 100.0 / 
                 NULLIF(SUM(CASE WHEN VOMITO IN (1, 2) THEN 1 ELSE 0 END), 0), 1)
    FROM criancas
    UNION ALL
    SELECT 'Dor retro-orbital', 
           ROUND(SUM(CASE WHEN DOR_RETRO = 1 THEN 1 ELSE 0 END) * 100.0 / 
                 NULLIF(SUM(CASE WHEN DOR_RETRO IN (1, 2) THEN 1 ELSE 0 END), 0), 1)
    FROM criancas
)
SELECT 'Criancas (0-15)' AS faixa_etaria, sintoma, percentual
FROM sintomas_criancas
WHERE percentual IS NOT NULL
ORDER BY percentual DESC
LIMIT 5;

-- =============================================================================
-- ETAPA 5: ANÁLISE POR REGIÃO E FAIXA ETÁRIA
-- UF: Norte (11-17), Nordeste (21-29), Sudeste (31-35), Sul (41-43), Centro-Oeste (50-53)
-- =============================================================================

-- 5.1 Mapeamento de UF para Região

WITH dados_completos AS (
    SELECT 
        *,
        CASE 
            WHEN NU_IDADE_N >= 4000 AND NU_IDADE_N < 5000 THEN NU_IDADE_N - 4000
            WHEN NU_IDADE_N >= 3000 AND NU_IDADE_N < 4000 THEN (NU_IDADE_N - 3000) / 12.0
            WHEN NU_IDADE_N >= 2000 AND NU_IDADE_N < 3000 THEN (NU_IDADE_N - 2000) / 365.0
            WHEN NU_IDADE_N >= 1000 AND NU_IDADE_N < 2000 THEN (NU_IDADE_N - 1000) / (365.0 * 24)
            ELSE NU_IDADE_N
        END AS IDADE_ANOS,
        CASE 
            WHEN SG_UF_NOT BETWEEN 11 AND 17 THEN 'Norte'
            WHEN SG_UF_NOT BETWEEN 21 AND 29 THEN 'Nordeste'
            WHEN SG_UF_NOT BETWEEN 31 AND 35 THEN 'Sudeste'
            WHEN SG_UF_NOT BETWEEN 41 AND 43 THEN 'Sul'
            WHEN SG_UF_NOT BETWEEN 50 AND 53 THEN 'Centro-Oeste'
            ELSE 'Nao identificado'
        END AS REGIAO
    FROM notificacoes
),
dados_com_faixa AS (
    SELECT 
        *,
        CASE 
            WHEN IDADE_ANOS IS NULL OR IDADE_ANOS < 0 THEN 'Nao informado'
            WHEN IDADE_ANOS <= 15 THEN 'Criancas (0-15)'
            WHEN IDADE_ANOS <= 23 THEN 'Jovens (15-23)'
            WHEN IDADE_ANOS <= 60 THEN 'Adultos (23-60)'
            ELSE 'Idosos (60+)'
        END AS FAIXA_ETARIA
    FROM dados_completos
)
SELECT * FROM dados_com_faixa LIMIT 10;

-- 5.2 Contagem de casos por Região
WITH dados_completos AS (
    SELECT 
        CASE 
            WHEN SG_UF_NOT BETWEEN 11 AND 17 THEN 'Norte'
            WHEN SG_UF_NOT BETWEEN 21 AND 29 THEN 'Nordeste'
            WHEN SG_UF_NOT BETWEEN 31 AND 35 THEN 'Sudeste'
            WHEN SG_UF_NOT BETWEEN 41 AND 43 THEN 'Sul'
            WHEN SG_UF_NOT BETWEEN 50 AND 53 THEN 'Centro-Oeste'
            ELSE 'Nao identificado'
        END AS REGIAO
    FROM notificacoes
)
SELECT 
    REGIAO,
    COUNT(*) AS casos,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentual
FROM dados_completos
WHERE REGIAO != 'Nao identificado'
GROUP BY REGIAO
ORDER BY casos DESC;

-- 5.3 Tabela cruzada: Casos por Região E Faixa Etária
WITH dados_completos AS (
    SELECT 
        CASE 
            WHEN NU_IDADE_N >= 4000 AND NU_IDADE_N < 5000 THEN NU_IDADE_N - 4000
            WHEN NU_IDADE_N >= 3000 AND NU_IDADE_N < 4000 THEN (NU_IDADE_N - 3000) / 12.0
            WHEN NU_IDADE_N >= 2000 AND NU_IDADE_N < 3000 THEN (NU_IDADE_N - 2000) / 365.0
            WHEN NU_IDADE_N >= 1000 AND NU_IDADE_N < 2000 THEN (NU_IDADE_N - 1000) / (365.0 * 24)
            ELSE NU_IDADE_N
        END AS IDADE_ANOS,
        CASE 
            WHEN SG_UF_NOT BETWEEN 11 AND 17 THEN 'Norte'
            WHEN SG_UF_NOT BETWEEN 21 AND 29 THEN 'Nordeste'
            WHEN SG_UF_NOT BETWEEN 31 AND 35 THEN 'Sudeste'
            WHEN SG_UF_NOT BETWEEN 41 AND 43 THEN 'Sul'
            WHEN SG_UF_NOT BETWEEN 50 AND 53 THEN 'Centro-Oeste'
            ELSE 'Nao identificado'
        END AS REGIAO
    FROM notificacoes
),
dados_com_faixa AS (
    SELECT 
        REGIAO,
        CASE 
            WHEN IDADE_ANOS IS NULL OR IDADE_ANOS < 0 THEN 'Nao informado'
            WHEN IDADE_ANOS <= 15 THEN 'Criancas (0-15)'
            WHEN IDADE_ANOS <= 23 THEN 'Jovens (15-23)'
            WHEN IDADE_ANOS <= 60 THEN 'Adultos (23-60)'
            ELSE 'Idosos (60+)'
        END AS FAIXA_ETARIA
    FROM dados_completos
)
SELECT 
    REGIAO,
    SUM(CASE WHEN FAIXA_ETARIA = 'Criancas (0-15)' THEN 1 ELSE 0 END) AS criancas,
    SUM(CASE WHEN FAIXA_ETARIA = 'Jovens (15-23)' THEN 1 ELSE 0 END) AS jovens,
    SUM(CASE WHEN FAIXA_ETARIA = 'Adultos (23-60)' THEN 1 ELSE 0 END) AS adultos,
    SUM(CASE WHEN FAIXA_ETARIA = 'Idosos (60+)' THEN 1 ELSE 0 END) AS idosos,
    COUNT(*) AS total
FROM dados_com_faixa
WHERE REGIAO != 'Nao identificado' AND FAIXA_ETARIA != 'Nao informado'
GROUP BY REGIAO
ORDER BY total DESC;

-- 5.4 Faixa etária mais atingida em cada região
WITH dados_completos AS (
    SELECT 
        CASE 
            WHEN NU_IDADE_N >= 4000 AND NU_IDADE_N < 5000 THEN NU_IDADE_N - 4000
            WHEN NU_IDADE_N >= 3000 AND NU_IDADE_N < 4000 THEN (NU_IDADE_N - 3000) / 12.0
            WHEN NU_IDADE_N >= 2000 AND NU_IDADE_N < 3000 THEN (NU_IDADE_N - 2000) / 365.0
            WHEN NU_IDADE_N >= 1000 AND NU_IDADE_N < 2000 THEN (NU_IDADE_N - 1000) / (365.0 * 24)
            ELSE NU_IDADE_N
        END AS IDADE_ANOS,
        CASE 
            WHEN SG_UF_NOT BETWEEN 11 AND 17 THEN 'Norte'
            WHEN SG_UF_NOT BETWEEN 21 AND 29 THEN 'Nordeste'
            WHEN SG_UF_NOT BETWEEN 31 AND 35 THEN 'Sudeste'
            WHEN SG_UF_NOT BETWEEN 41 AND 43 THEN 'Sul'
            WHEN SG_UF_NOT BETWEEN 50 AND 53 THEN 'Centro-Oeste'
            ELSE 'Nao identificado'
        END AS REGIAO
    FROM notificacoes
),
dados_com_faixa AS (
    SELECT 
        REGIAO,
        CASE 
            WHEN IDADE_ANOS IS NULL OR IDADE_ANOS < 0 THEN 'Nao informado'
            WHEN IDADE_ANOS <= 15 THEN 'Criancas (0-15)'
            WHEN IDADE_ANOS <= 23 THEN 'Jovens (15-23)'
            WHEN IDADE_ANOS <= 60 THEN 'Adultos (23-60)'
            ELSE 'Idosos (60+)'
        END AS FAIXA_ETARIA
    FROM dados_completos
),
contagem AS (
    SELECT 
        REGIAO,
        FAIXA_ETARIA,
        COUNT(*) AS casos
    FROM dados_com_faixa
    WHERE REGIAO != 'Nao identificado' AND FAIXA_ETARIA != 'Nao informado'
    GROUP BY REGIAO, FAIXA_ETARIA
),
ranking AS (
    SELECT 
        REGIAO,
        FAIXA_ETARIA,
        casos,
        ROW_NUMBER() OVER (PARTITION BY REGIAO ORDER BY casos DESC) AS rank
    FROM contagem
)
SELECT 
    REGIAO,
    FAIXA_ETARIA AS faixa_mais_atingida,
    casos,
    ROUND(casos * 100.0 / SUM(casos) OVER (PARTITION BY REGIAO), 1) AS percentual_da_regiao
FROM ranking
WHERE rank = 1
ORDER BY casos DESC;

-- 5.5 Distribuição percentual por faixa etária em cada região
WITH dados_completos AS (
    SELECT 
        CASE 
            WHEN NU_IDADE_N >= 4000 AND NU_IDADE_N < 5000 THEN NU_IDADE_N - 4000
            WHEN NU_IDADE_N >= 3000 AND NU_IDADE_N < 4000 THEN (NU_IDADE_N - 3000) / 12.0
            WHEN NU_IDADE_N >= 2000 AND NU_IDADE_N < 3000 THEN (NU_IDADE_N - 2000) / 365.0
            WHEN NU_IDADE_N >= 1000 AND NU_IDADE_N < 2000 THEN (NU_IDADE_N - 1000) / (365.0 * 24)
            ELSE NU_IDADE_N
        END AS IDADE_ANOS,
        CASE 
            WHEN SG_UF_NOT BETWEEN 11 AND 17 THEN 'Norte'
            WHEN SG_UF_NOT BETWEEN 21 AND 29 THEN 'Nordeste'
            WHEN SG_UF_NOT BETWEEN 31 AND 35 THEN 'Sudeste'
            WHEN SG_UF_NOT BETWEEN 41 AND 43 THEN 'Sul'
            WHEN SG_UF_NOT BETWEEN 50 AND 53 THEN 'Centro-Oeste'
            ELSE 'Nao identificado'
        END AS REGIAO
    FROM notificacoes
),
dados_com_faixa AS (
    SELECT 
        REGIAO,
        CASE 
            WHEN IDADE_ANOS IS NULL OR IDADE_ANOS < 0 THEN 'Nao informado'
            WHEN IDADE_ANOS <= 15 THEN 'Criancas (0-15)'
            WHEN IDADE_ANOS <= 23 THEN 'Jovens (15-23)'
            WHEN IDADE_ANOS <= 60 THEN 'Adultos (23-60)'
            ELSE 'Idosos (60+)'
        END AS FAIXA_ETARIA
    FROM dados_completos
),
totais_regiao AS (
    SELECT REGIAO, COUNT(*) AS total_regiao
    FROM dados_com_faixa
    WHERE REGIAO != 'Nao identificado' AND FAIXA_ETARIA != 'Nao informado'
    GROUP BY REGIAO
)
SELECT 
    d.REGIAO,
    d.FAIXA_ETARIA,
    COUNT(*) AS casos,
    ROUND(COUNT(*) * 100.0 / t.total_regiao, 1) AS percentual
FROM dados_com_faixa d
JOIN totais_regiao t ON d.REGIAO = t.REGIAO
WHERE d.REGIAO != 'Nao identificado' AND d.FAIXA_ETARIA != 'Nao informado'
GROUP BY d.REGIAO, d.FAIXA_ETARIA, t.total_regiao
ORDER BY 
    CASE d.REGIAO
        WHEN 'Sudeste' THEN 1
        WHEN 'Sul' THEN 2
        WHEN 'Centro-Oeste' THEN 3
        WHEN 'Nordeste' THEN 4
        WHEN 'Norte' THEN 5
    END,
    CASE d.FAIXA_ETARIA
        WHEN 'Criancas (0-15)' THEN 1
        WHEN 'Jovens (15-23)' THEN 2
        WHEN 'Adultos (23-60)' THEN 3
        WHEN 'Idosos (60+)' THEN 4
    END;

-- =============================================================================
-- AUXILIAR: MAPEAMENTO UF → NOME DO ESTADO
-- =============================================================================
SELECT 
    SG_UF_NOT AS codigo_uf,
    CASE SG_UF_NOT
        WHEN 11 THEN 'Rondonia'
        WHEN 12 THEN 'Acre'
        WHEN 13 THEN 'Amazonas'
        WHEN 14 THEN 'Roraima'
        WHEN 15 THEN 'Para'
        WHEN 16 THEN 'Amapa'
        WHEN 17 THEN 'Tocantins'
        WHEN 21 THEN 'Maranhao'
        WHEN 22 THEN 'Piaui'
        WHEN 23 THEN 'Ceara'
        WHEN 24 THEN 'Rio Grande do Norte'
        WHEN 25 THEN 'Paraiba'
        WHEN 26 THEN 'Pernambuco'
        WHEN 27 THEN 'Alagoas'
        WHEN 28 THEN 'Sergipe'
        WHEN 29 THEN 'Bahia'
        WHEN 31 THEN 'Minas Gerais'
        WHEN 32 THEN 'Espirito Santo'
        WHEN 33 THEN 'Rio de Janeiro'
        WHEN 35 THEN 'Sao Paulo'
        WHEN 41 THEN 'Parana'
        WHEN 42 THEN 'Santa Catarina'
        WHEN 43 THEN 'Rio Grande do Sul'
        WHEN 50 THEN 'Mato Grosso do Sul'
        WHEN 51 THEN 'Mato Grosso'
        WHEN 52 THEN 'Goias'
        WHEN 53 THEN 'Distrito Federal'
        ELSE 'Desconhecido'
    END AS nome_estado,
    COUNT(*) AS casos
FROM notificacoes
GROUP BY SG_UF_NOT
ORDER BY casos DESC;
