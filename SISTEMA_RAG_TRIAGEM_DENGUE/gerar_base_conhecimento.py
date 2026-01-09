"""
Gerador de Base de Conhecimento para Sistema RAG de Triagem de Dengue
Processa dados reais do SINAN e cria base estruturada para consulta
Suporta múltiplos arquivos CSV (DENGBR*.csv) de diferentes anos
"""

import pandas as pd
import numpy as np
import json
import csv
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def encontrar_arquivos_dengue():
    """
    Busca automaticamente todos os arquivos CSV de dengue nas pastas conhecidas.
    Procura por arquivos com padrão DENGBR*.csv
    """
    arquivos_encontrados = []
    
    # Pastas onde procurar
    pastas_busca = [
        Path(".."),                      # Pasta pai
        Path("../BASE DE DADOS"),        # Pasta específica de dados
        Path("../base de dados"),        # Case insensitive
        Path("../dados"),                # Alternativa
        Path("."),                       # Pasta atual
    ]
    
    # Padrões de arquivo para buscar
    padroes = ["DENGBR*.csv", "dengbr*.csv", "DENG*.csv"]
    
    for pasta in pastas_busca:
        if pasta.exists():
            for padrao in padroes:
                arquivos = list(pasta.glob(padrao))
                for arq in arquivos:
                    if arq.resolve() not in [a.resolve() for a in arquivos_encontrados]:
                        arquivos_encontrados.append(arq)
    
    # Ordenar por nome (ano)
    arquivos_encontrados.sort(key=lambda x: x.name)
    
    return arquivos_encontrados


def carregar_multiplos_csvs(arquivos: list) -> pd.DataFrame:
    """
    Carrega e concatena múltiplos arquivos CSV em um único DataFrame
    """
    dataframes = []
    total_registros = 0
    
    for arquivo in arquivos:
        try:
            print(f"      Carregando: {arquivo.name}...", end=" ")
            df = pd.read_csv(arquivo, low_memory=False, encoding='latin-1')
            
            # Adicionar coluna de origem
            df['_ARQUIVO_ORIGEM'] = arquivo.name
            df['_ANO_ARQUIVO'] = arquivo.name.replace('DENGBR', '').replace('.csv', '')
            
            registros = len(df)
            total_registros += registros
            print(f"{registros:,} registros")
            
            dataframes.append(df)
        except Exception as e:
            print(f"ERRO: {e}")
            continue
    
    if not dataframes:
        return None
    
    # Concatenar todos os DataFrames
    print(f"\n      Concatenando {len(dataframes)} arquivos...")
    df_final = pd.concat(dataframes, ignore_index=True)
    print(f"      Total combinado: {len(df_final):,} registros")
    
    return df_final


def processar_dados_sinan():
    """Processa os dados do SINAN para criar base de conhecimento completa"""
    
    print("=" * 70)
    print("GERAÇÃO DE BASE DE CONHECIMENTO PARA SISTEMA RAG")
    print("=" * 70)
    
    # Buscar todos os arquivos automaticamente
    print("\n[1/7] Buscando arquivos de dados...")
    arquivos = encontrar_arquivos_dengue()
    
    if not arquivos:
        print("[ERRO] Nenhum arquivo DENGBR*.csv encontrado!")
        print("       Certifique-se de que os arquivos estão na pasta correta.")
        return None
    
    print(f"      Encontrados {len(arquivos)} arquivo(s):")
    for arq in arquivos:
        print(f"        - {arq}")
    
    # Carregar todos os arquivos
    print("\n[2/7] Carregando dados...")
    df = carregar_multiplos_csvs(arquivos)
    
    if df is None or len(df) == 0:
        print("[ERRO] Não foi possível carregar os dados.")
        return None
    
    # ===== PROCESSAMENTO =====
    print("\n[3/7] Processando variáveis...")
    
    # Calcular idade em anos
    def calcular_idade(nu_idade_n):
        if pd.isna(nu_idade_n):
            return None
        try:
            codigo = str(int(nu_idade_n))
            if len(codigo) != 4:
                return None
            tipo = int(codigo[0])
            valor = int(codigo[1:])
            if tipo == 4:
                return valor
            elif tipo == 3:
                return valor / 12
            elif tipo == 2:
                return valor / 365
        except:
            return None
        return None
    
    df['IDADE_ANOS'] = df['NU_IDADE_N'].apply(calcular_idade)
    
    # Faixa etária
    def classificar_faixa(idade):
        if pd.isna(idade):
            return 'Desconhecida'
        if idade < 2:
            return 'Lactente (0-2)'
        elif idade < 15:
            return 'Criança (2-14)'
        elif idade < 23:
            return 'Jovem (15-22)'
        elif idade < 60:
            return 'Adulto (23-59)'
        else:
            return 'Idoso (60+)'
    
    df['FAIXA_ETARIA'] = df['IDADE_ANOS'].apply(classificar_faixa)
    
    # ===== IDENTIFICAR CASOS GRAVES =====
    print("\n[4/7] Identificando casos por gravidade...")
    
    obitos = df[df['EVOLUCAO'] == 2]
    dengue_alarme = df[df['CLASSI_FIN'] == 2]  # Dengue com sinais de alarme
    dengue_grave = df[df['CLASSI_FIN'] == 3]   # Dengue grave
    hospitalizados = df[df['HOSPITALIZ'] == 1]
    curados = df[df['EVOLUCAO'] == 1]
    
    print(f"      Óbitos: {len(obitos):,}")
    print(f"      Dengue com alarme: {len(dengue_alarme):,}")
    print(f"      Dengue grave: {len(dengue_grave):,}")
    print(f"      Hospitalizados: {len(hospitalizados):,}")
    print(f"      Curados: {len(curados):,}")
    
    # ===== CRIAR BASE DE CONHECIMENTO =====
    print("\n[5/7] Criando base de conhecimento estruturada...")
    
    knowledge_entries = []
    
    # ----- CATEGORIA: CLASSIFICAÇÃO DE RISCO -----
    
    # Por faixa etária
    for faixa in df['FAIXA_ETARIA'].unique():
        if faixa == 'Desconhecida':
            continue
            
        df_faixa = df[df['FAIXA_ETARIA'] == faixa]
        n_total = len(df_faixa)
        
        if n_total > 100:
            n_hosp = (df_faixa['HOSPITALIZ'] == 1).sum()
            n_obito = (df_faixa['EVOLUCAO'] == 2).sum()
            n_grave = df_faixa['CLASSI_FIN'].isin([2, 3]).sum()
            
            taxa_hosp = n_hosp / n_total * 100
            taxa_obito = n_obito / n_total * 100
            taxa_grave = n_grave / n_total * 100
            
            # Determinar nível de risco
            if taxa_obito > 0.3:
                risco = "ALTO"
            elif taxa_obito > 0.05:
                risco = "MÉDIO"
            else:
                risco = "BAIXO"
            
            knowledge_entries.append({
                'categoria': 'classificacao_risco',
                'subcategoria': 'faixa_etaria',
                'pergunta': f'Qual o risco para pacientes da faixa {faixa}?',
                'resposta': f'Faixa {faixa}: Risco {risco}. Taxa de hospitalização: {taxa_hosp:.2f}%. Taxa de óbito: {taxa_obito:.3f}%. Taxa de casos graves: {taxa_grave:.2f}%. Total de casos analisados: {n_total:,}.',
                'fonte': 'SINAN/DATASUS 2025',
                'dados': json.dumps({
                    'faixa_etaria': faixa,
                    'n_casos': n_total,
                    'taxa_hospitalizacao': round(taxa_hosp, 2),
                    'taxa_obito': round(taxa_obito, 3),
                    'taxa_casos_graves': round(taxa_grave, 2),
                    'nivel_risco': risco
                })
            })
    
    # ----- CATEGORIA: SINAIS DE ALARME -----
    
    sinais_alarme_map = {
        'ALRM_HIPOT': ('hipotensão postural', 'Queda da pressão ao levantar'),
        'ALRM_PLAQ': ('queda de plaquetas', 'Trombocitopenia'),
        'ALRM_VOM': ('vômitos persistentes', 'Vômitos que não cessam'),
        'ALRM_SANG': ('sangramento de mucosas', 'Sangramento gengival, nasal ou outros'),
        'ALRM_HEMAT': ('aumento do hematócrito', 'Hemoconcentração'),
        'ALRM_ABDOM': ('dor abdominal intensa', 'Dor abdominal contínua'),
        'ALRM_LETAR': ('letargia', 'Sonolência excessiva ou irritabilidade'),
        'ALRM_HEPAT': ('hepatomegalia dolorosa', 'Fígado aumentado e doloroso'),
        'ALRM_LIQ': ('acúmulo de líquidos', 'Derrame pleural ou ascite'),
    }
    
    casos_graves_all = pd.concat([obitos, dengue_alarme, dengue_grave]).drop_duplicates()
    
    for col, (nome, descricao) in sinais_alarme_map.items():
        if col in df.columns:
            # Em casos graves
            if col in casos_graves_all.columns:
                freq_graves = (casos_graves_all[col] == 1).sum()
                total_graves = len(casos_graves_all)
                pct_graves = freq_graves / total_graves * 100 if total_graves > 0 else 0
                
                # Em todos os casos
                freq_total = (df[col] == 1).sum()
                pct_total = freq_total / len(df) * 100
                
                # Calcular risco relativo
                casos_com_sinal = df[df[col] == 1]
                if len(casos_com_sinal) > 0:
                    taxa_obito_com = (casos_com_sinal['EVOLUCAO'] == 2).sum() / len(casos_com_sinal) * 100
                else:
                    taxa_obito_com = 0
                
                knowledge_entries.append({
                    'categoria': 'sinais_alarme',
                    'subcategoria': nome,
                    'pergunta': f'O que significa {nome} como sinal de alarme?',
                    'resposta': f'{nome.upper()}: {descricao}. Presente em {pct_graves:.1f}% dos casos graves. Pacientes com este sinal têm taxa de óbito de {taxa_obito_com:.3f}%. Este é um sinal de alarme que requer ATENÇÃO IMEDIATA e reavaliação médica urgente.',
                    'fonte': 'SINAN/DATASUS 2025 + Protocolo MS',
                    'dados': json.dumps({
                        'sinal': nome,
                        'frequencia_casos_graves': round(pct_graves, 1),
                        'frequencia_geral': round(pct_total, 1),
                        'taxa_obito_associada': round(taxa_obito_com, 3)
                    })
                })
    
    # ----- CATEGORIA: SINAIS DE GRAVIDADE -----
    
    sinais_gravidade_map = {
        'GRAV_PULSO': ('pulso fraco ou ausente', 'Indica choque'),
        'GRAV_CONV': ('convulsões', 'Comprometimento neurológico'),
        'GRAV_ENCH': ('enchimento capilar lento', 'Maior que 2 segundos'),
        'GRAV_INSUF': ('insuficiência respiratória', 'Desconforto respiratório grave'),
        'GRAV_TAQUI': ('taquicardia', 'Frequência cardíaca elevada'),
        'GRAV_EXTRE': ('extremidades frias', 'Hipoperfusão periférica'),
        'GRAV_HIPOT': ('hipotensão arterial', 'Pressão arterial baixa'),
        'GRAV_HEMAT': ('hematócrito elevado', 'Hemoconcentração grave'),
        'GRAV_MELEN': ('melena', 'Sangue nas fezes'),
        'GRAV_SANG': ('sangramento grave', 'Hemorragia importante'),
        'GRAV_CONSC': ('alteração de consciência', 'Confusão, torpor ou coma'),
        'GRAV_ORGAO': ('comprometimento de órgãos', 'Falência orgânica'),
    }
    
    for col, (nome, descricao) in sinais_gravidade_map.items():
        if col in df.columns:
            freq_obitos = (obitos[col] == 1).sum() if col in obitos.columns else 0
            total_obitos = len(obitos)
            pct_obitos = freq_obitos / total_obitos * 100 if total_obitos > 0 else 0
            
            knowledge_entries.append({
                'categoria': 'sinais_gravidade',
                'subcategoria': nome,
                'pergunta': f'O que significa {nome} como sinal de gravidade?',
                'resposta': f'{nome.upper()}: {descricao}. Presente em {pct_obitos:.1f}% dos casos que evoluíram para óbito. Este é um SINAL DE GRAVIDADE que indica DENGUE GRAVE (Grupo D) e requer INTERNAÇÃO IMEDIATA em UTI ou unidade de emergência.',
                'fonte': 'SINAN/DATASUS 2025 + Protocolo MS',
                'dados': json.dumps({
                    'sinal': nome,
                    'frequencia_obitos': round(pct_obitos, 1),
                    'classificacao': 'GRUPO D - DENGUE GRAVE'
                })
            })
    
    # ----- CATEGORIA: SINTOMAS -----
    
    sintomas_map = {
        'FEBRE': 'febre',
        'MIALGIA': 'dor muscular (mialgia)',
        'CEFALEIA': 'cefaleia (dor de cabeça)',
        'EXANTEMA': 'exantema (manchas na pele)',
        'VOMITO': 'vômito',
        'NAUSEA': 'náusea',
        'DOR_COSTAS': 'dor nas costas',
        'CONJUNTVIT': 'conjuntivite',
        'ARTRITE': 'artrite',
        'ARTRALGIA': 'artralgia (dor nas articulações)',
        'DOR_RETRO': 'dor retro-orbital',
    }
    
    for col, nome in sintomas_map.items():
        if col in df.columns:
            freq_geral = (df[col] == 1).sum()
            pct_geral = freq_geral / len(df) * 100
            
            freq_graves = (casos_graves_all[col] == 1).sum() if col in casos_graves_all.columns else 0
            pct_graves = freq_graves / len(casos_graves_all) * 100 if len(casos_graves_all) > 0 else 0
            
            knowledge_entries.append({
                'categoria': 'sintomas',
                'subcategoria': nome,
                'pergunta': f'Qual a relevância de {nome} na dengue?',
                'resposta': f'{nome.upper()}: Presente em {pct_geral:.1f}% de todos os casos e em {pct_graves:.1f}% dos casos graves. A presença isolada deste sintoma não indica gravidade, mas deve ser monitorada junto com outros sinais.',
                'fonte': 'SINAN/DATASUS 2025',
                'dados': json.dumps({
                    'sintoma': nome,
                    'frequencia_geral': round(pct_geral, 1),
                    'frequencia_graves': round(pct_graves, 1)
                })
            })
    
    # ----- CATEGORIA: COMORBIDADES -----
    
    comorbidades_map = {
        'DIABETES': 'diabetes mellitus',
        'HEMATOLOG': 'doença hematológica',
        'HEPATOPAT': 'hepatopatia',
        'RENAL': 'doença renal crônica',
        'HIPERTENSA': 'hipertensão arterial',
        'ACIDO_PEPT': 'doença ácido-péptica',
        'AUTO_IMUNE': 'doença autoimune',
    }
    
    for col, nome in comorbidades_map.items():
        if col in df.columns:
            casos_com = df[df[col] == 1]
            casos_sem = df[df[col] != 1]
            
            if len(casos_com) > 50:
                taxa_obito_com = (casos_com['EVOLUCAO'] == 2).sum() / len(casos_com) * 100
                taxa_obito_sem = (casos_sem['EVOLUCAO'] == 2).sum() / len(casos_sem) * 100 if len(casos_sem) > 0 else 0
                
                taxa_hosp_com = (casos_com['HOSPITALIZ'] == 1).sum() / len(casos_com) * 100
                
                risco_relativo = taxa_obito_com / taxa_obito_sem if taxa_obito_sem > 0 else 0
                
                knowledge_entries.append({
                    'categoria': 'comorbidades',
                    'subcategoria': nome,
                    'pergunta': f'Qual o impacto de {nome} na evolução da dengue?',
                    'resposta': f'Pacientes com {nome.upper()} têm taxa de óbito de {taxa_obito_com:.3f}% (vs {taxa_obito_sem:.3f}% sem a comorbidade). Taxa de hospitalização: {taxa_hosp_com:.2f}%. Risco relativo de óbito: {risco_relativo:.1f}x. Pacientes com esta comorbidade devem ser classificados como GRUPO B ou superior.',
                    'fonte': 'SINAN/DATASUS 2025',
                    'dados': json.dumps({
                        'comorbidade': nome,
                        'n_casos': len(casos_com),
                        'taxa_obito': round(taxa_obito_com, 3),
                        'taxa_hospitalizacao': round(taxa_hosp_com, 2),
                        'risco_relativo': round(risco_relativo, 1)
                    })
                })
    
    # ----- CATEGORIA: CONDUTAS/TRATAMENTOS -----
    
    condutas = [
        {
            'categoria': 'conduta',
            'subcategoria': 'grupo_a',
            'pergunta': 'Qual a conduta para paciente Grupo A (dengue sem sinais de alarme)?',
            'resposta': 'GRUPO A - DENGUE SEM SINAIS DE ALARME: Atendimento ambulatorial. Hidratação oral: 60-80ml/kg/dia (1/3 soro de reidratação + 2/3 líquidos). Sintomáticos: Paracetamol ou Dipirona. NÃO usar AAS, Ibuprofeno ou outros AINEs. Retorno em 24-48h ou imediatamente se sinais de alarme. Orientar paciente sobre sinais de alarme.',
            'fonte': 'Protocolo MS 2024',
            'dados': json.dumps({'grupo': 'A', 'local': 'ambulatorial', 'internacao': False})
        },
        {
            'categoria': 'conduta',
            'subcategoria': 'grupo_b',
            'pergunta': 'Qual a conduta para paciente Grupo B (condições especiais)?',
            'resposta': 'GRUPO B - CONDIÇÕES ESPECIAIS (gestantes, idosos >65, crianças <2, comorbidades): Unidade com leito de observação. Hidratação oral supervisionada: 80ml/kg/dia. Hemograma com plaquetas obrigatório. Reavaliação diária até 48h após febre. Orientar sinais de alarme para retorno imediato.',
            'fonte': 'Protocolo MS 2024',
            'dados': json.dumps({'grupo': 'B', 'local': 'observação', 'internacao': False})
        },
        {
            'categoria': 'conduta',
            'subcategoria': 'grupo_c',
            'pergunta': 'Qual a conduta para paciente Grupo C (dengue com sinais de alarme)?',
            'resposta': 'GRUPO C - DENGUE COM SINAIS DE ALARME: URGÊNCIA - Atendimento em até 30 minutos. Internação em leito de observação ou enfermaria. Hidratação IV: 10ml/kg/hora nas primeiras 2h, depois reavaliar. Hematócrito a cada 2-4h. Monitorização contínua. Preparar para transferência se necessário.',
            'fonte': 'Protocolo MS 2024',
            'dados': json.dumps({'grupo': 'C', 'local': 'internação', 'internacao': True})
        },
        {
            'categoria': 'conduta',
            'subcategoria': 'grupo_d',
            'pergunta': 'Qual a conduta para paciente Grupo D (dengue grave)?',
            'resposta': 'GRUPO D - DENGUE GRAVE: EMERGÊNCIA - Atendimento IMEDIATO. UTI ou sala de emergência. Acesso venoso calibroso. Reposição volêmica: 20ml/kg em 20 min, repetir até 3x se necessário. Hemograma, função renal/hepática, coagulograma. Avaliar hemoderivados. Monitorização contínua. Suporte avançado de vida.',
            'fonte': 'Protocolo MS 2024',
            'dados': json.dumps({'grupo': 'D', 'local': 'UTI/emergência', 'internacao': True})
        },
    ]
    
    knowledge_entries.extend(condutas)
    
    # ----- CATEGORIA: PERÍODO CRÍTICO -----
    
    knowledge_entries.append({
        'categoria': 'periodo_critico',
        'subcategoria': 'evolucao_temporal',
        'pergunta': 'Qual o período crítico da dengue?',
        'resposta': 'O PERÍODO CRÍTICO da dengue ocorre entre o 3º e 7º dia de doença, geralmente quando a febre começa a ceder. Neste período há maior risco de evolução para formas graves. Pacientes devem ser orientados a procurar atendimento IMEDIATAMENTE se apresentarem: vômitos persistentes, dor abdominal intensa, sangramento, tontura, sonolência excessiva.',
        'fonte': 'Protocolo MS 2024',
        'dados': json.dumps({'periodo_inicio': 3, 'periodo_fim': 7, 'momento': 'defervescência'})
    })
    
    # ----- CATEGORIA: HIDRATAÇÃO -----
    
    hidratacao_entries = [
        {
            'categoria': 'hidratacao',
            'subcategoria': 'oral_adulto',
            'pergunta': 'Como calcular hidratação oral para adulto com dengue?',
            'resposta': 'HIDRATAÇÃO ORAL ADULTO: 60-80ml/kg/dia. Para adulto de 70kg: 4.200 a 5.600ml/dia. Distribuir: 1/3 soro de reidratação oral (SRO) + 2/3 líquidos (água, sucos, água de coco). Oferecer líquidos frequentemente, mesmo sem sede. Evitar refrigerantes e bebidas muito açucaradas.',
            'fonte': 'Protocolo MS 2024',
            'dados': json.dumps({'tipo': 'oral', 'volume_kg': '60-80ml/kg/dia'})
        },
        {
            'categoria': 'hidratacao',
            'subcategoria': 'venosa_alarme',
            'pergunta': 'Como fazer hidratação venosa em dengue com sinais de alarme?',
            'resposta': 'HIDRATAÇÃO VENOSA - SINAIS DE ALARME: Iniciar com 10ml/kg/hora de SF 0.9% ou Ringer Lactato nas primeiras 2 horas. Reavaliar hematócrito e sinais vitais. Se melhora: reduzir para 5-7ml/kg/h por 2-4h. Se piora ou sem melhora: aumentar para 15-20ml/kg/h e reavaliar.',
            'fonte': 'Protocolo MS 2024',
            'dados': json.dumps({'tipo': 'venosa', 'fase_inicial': '10ml/kg/h'})
        },
        {
            'categoria': 'hidratacao',
            'subcategoria': 'venosa_grave',
            'pergunta': 'Como fazer hidratação venosa em dengue grave?',
            'resposta': 'HIDRATAÇÃO VENOSA - DENGUE GRAVE: Expansão volêmica rápida: 20ml/kg em 20 minutos com SF 0.9% ou Ringer. Repetir até 3 vezes se necessário. Após estabilização: manter 10ml/kg/h. Monitorar: diurese (mínimo 0.5ml/kg/h), sinais vitais, hematócrito seriado. Considerar coloides se sem resposta.',
            'fonte': 'Protocolo MS 2024',
            'dados': json.dumps({'tipo': 'venosa_emergencia', 'expansao': '20ml/kg em 20min'})
        },
    ]
    
    knowledge_entries.extend(hidratacao_entries)
    
    # ----- CATEGORIA: MEDICAMENTOS -----
    
    medicamentos_entries = [
        {
            'categoria': 'medicamentos',
            'subcategoria': 'contraindicados',
            'pergunta': 'Quais medicamentos são contraindicados na dengue?',
            'resposta': 'MEDICAMENTOS CONTRAINDICADOS NA DENGUE: AAS (Aspirina), Ibuprofeno, Diclofenaco, Nimesulida e outros AINEs. Estes medicamentos aumentam o risco de sangramento por inibirem a função plaquetária. Também contraindicados: corticoides (exceto em casos específicos) e anticoagulantes (avaliar risco-benefício).',
            'fonte': 'Protocolo MS 2024',
            'dados': json.dumps({'contraindicados': ['AAS', 'Ibuprofeno', 'Diclofenaco', 'Nimesulida', 'AINEs']})
        },
        {
            'categoria': 'medicamentos',
            'subcategoria': 'permitidos',
            'pergunta': 'Quais medicamentos podem ser usados na dengue?',
            'resposta': 'MEDICAMENTOS PERMITIDOS NA DENGUE: Para febre e dor: Paracetamol (500-750mg a cada 6h) ou Dipirona (500-1000mg a cada 6h). Para náuseas: Metoclopramida ou Bromoprida. Para prurido: Anti-histamínicos. Manter hidratação como principal tratamento.',
            'fonte': 'Protocolo MS 2024',
            'dados': json.dumps({'permitidos': ['Paracetamol', 'Dipirona', 'Metoclopramida', 'Anti-histamínicos']})
        },
    ]
    
    knowledge_entries.extend(medicamentos_entries)
    
    # ----- CATEGORIA: EXAMES -----
    
    exames_entries = [
        {
            'categoria': 'exames',
            'subcategoria': 'hemograma',
            'pergunta': 'Como interpretar hemograma na dengue?',
            'resposta': 'HEMOGRAMA NA DENGUE: Plaquetas <100.000/mm³ indica trombocitopenia importante. Hematócrito elevado (>20% do basal ou >45% em homens/>40% em mulheres) indica hemoconcentração. Leucopenia é comum. Monitorar hematócrito seriado para detectar hemoconcentração precoce.',
            'fonte': 'Protocolo MS 2024',
            'dados': json.dumps({'plaquetas_alarme': 100000, 'hematocrito_alarme_h': 45, 'hematocrito_alarme_m': 40})
        },
        {
            'categoria': 'exames',
            'subcategoria': 'quando_solicitar',
            'pergunta': 'Quando solicitar exames na dengue?',
            'resposta': 'EXAMES NA DENGUE: Grupo A: hemograma a critério clínico. Grupo B: hemograma obrigatório. Grupo C: hemograma + hematócrito seriado (2-4h). Grupo D: hemograma, hematócrito seriado, função renal, função hepática, coagulograma, gasometria.',
            'fonte': 'Protocolo MS 2024',
            'dados': json.dumps({'grupo_a': 'opcional', 'grupo_b': 'obrigatório', 'grupo_c': 'seriado', 'grupo_d': 'completo'})
        },
    ]
    
    knowledge_entries.extend(exames_entries)
    
    # ===== SALVAR BASE DE CONHECIMENTO =====
    print(f"\n[6/7] Salvando base de conhecimento ({len(knowledge_entries)} entradas)...")
    
    Path("data").mkdir(exist_ok=True)
    
    # Salvar em CSV (formato similar ao iFood)
    csv_path = "data/base_conhecimento_dengue.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['categoria', 'subcategoria', 'pergunta', 'resposta', 'fonte', 'dados'])
        writer.writeheader()
        writer.writerows(knowledge_entries)
    
    print(f"      CSV salvo em: {csv_path}")
    
    # Salvar em JSON (formato mais rico)
    json_path = "data/knowledge_base_completo.json"
    
    # Organizar por categoria
    anos_fonte = sorted(df['_ANO_ARQUIVO'].unique()) if '_ANO_ARQUIVO' in df.columns else ['N/A']
    kb_organizado = {
        'metadata': {
            'data_geracao': datetime.now().isoformat(),
            'total_casos_analisados': len(df),
            'total_obitos': len(obitos),
            'total_graves': len(casos_graves_all),
            'total_entradas_conhecimento': len(knowledge_entries),
            'arquivos_processados': len(arquivos),
            'anos_cobertos': list(map(str, anos_fonte)),
            'fonte': f'SINAN/DATASUS - {len(arquivos)} arquivos ({", ".join(map(str, anos_fonte))})'
        },
        'entradas': knowledge_entries,
        'estatisticas_resumo': {
            'por_faixa_etaria': {},
            'taxa_obito_geral': round(len(obitos) / len(df) * 100, 4),
            'taxa_hospitalizacao_geral': round((df['HOSPITALIZ'] == 1).sum() / len(df) * 100, 2)
        }
    }
    
    # Adicionar estatísticas por faixa
    for faixa in df['FAIXA_ETARIA'].unique():
        if faixa != 'Desconhecida':
            df_faixa = df[df['FAIXA_ETARIA'] == faixa]
            kb_organizado['estatisticas_resumo']['por_faixa_etaria'][faixa] = {
                'n_casos': len(df_faixa),
                'taxa_obito': round((df_faixa['EVOLUCAO'] == 2).sum() / len(df_faixa) * 100, 4) if len(df_faixa) > 0 else 0,
                'taxa_hospitalizacao': round((df_faixa['HOSPITALIZ'] == 1).sum() / len(df_faixa) * 100, 2) if len(df_faixa) > 0 else 0
            }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(kb_organizado, f, ensure_ascii=False, indent=2)
    
    print(f"      JSON salvo em: {json_path}")
    
    # Atualizar knowledge_base.json original
    kb_simples = {
        'metadata': kb_organizado['metadata'],
        'estatisticas_faixa_etaria': [
            {
                'faixa_etaria': faixa,
                **dados
            }
            for faixa, dados in kb_organizado['estatisticas_resumo']['por_faixa_etaria'].items()
        ],
        'total_entradas_rag': len(knowledge_entries)
    }
    
    with open("data/knowledge_base.json", 'w', encoding='utf-8') as f:
        json.dump(kb_simples, f, ensure_ascii=False, indent=2)
    
    print("      knowledge_base.json atualizado")
    
    # ===== RELATÓRIO FINAL =====
    print("\n[7/7] Gerando relatório...")
    
    print("\n" + "=" * 70)
    print("RELATÓRIO DE GERAÇÃO DA BASE DE CONHECIMENTO")
    print("=" * 70)
    
    # Informar arquivos processados
    anos_processados = sorted(df['_ANO_ARQUIVO'].unique()) if '_ANO_ARQUIVO' in df.columns else ['N/A']
    print(f"\nArquivos processados: {len(arquivos)}")
    print(f"Anos cobertos: {', '.join(map(str, anos_processados))}")
    print(f"\nTotal de casos analisados: {len(df):,}")
    print(f"Total de óbitos: {len(obitos):,}")
    print(f"Total de casos graves: {len(casos_graves_all):,}")
    print(f"\nEntradas de conhecimento geradas: {len(knowledge_entries)}")
    
    # Contagem por categoria
    categorias = {}
    for entry in knowledge_entries:
        cat = entry['categoria']
        categorias[cat] = categorias.get(cat, 0) + 1
    
    print("\nEntradas por categoria:")
    for cat, count in sorted(categorias.items()):
        print(f"  - {cat}: {count}")
    
    print("\n" + "=" * 70)
    print("BASE DE CONHECIMENTO GERADA COM SUCESSO!")
    print("=" * 70)
    print(f"\nArquivos criados:")
    print(f"  - data/base_conhecimento_dengue.csv")
    print(f"  - data/knowledge_base_completo.json")
    print(f"  - data/knowledge_base.json (atualizado)")
    
    return kb_organizado


if __name__ == "__main__":
    processar_dados_sinan()
