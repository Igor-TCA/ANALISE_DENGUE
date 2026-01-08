"""
Demo do Sistema de Triagem - Versao Simplificada
Processa dados e executa triagem sem dependencias complexas
"""

import sys
import os
from pathlib import Path

# Configurar paths
sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

import pandas as pd
import json
from datetime import datetime


def processar_dados_sinan():
    """Processa os dados do SINAN para criar base de conhecimento"""
    
    print("=" * 70)
    print("PROCESSAMENTO DE DADOS DO SINAN")
    print("=" * 70)
    
    data_path = Path("../DENGBR25.csv")
    
    if not data_path.exists():
        print(f"[ERRO] Arquivo nao encontrado: {data_path}")
        return None
    
    print(f"\n[1/4] Carregando dados de: {data_path}")
    df = pd.read_csv(data_path, low_memory=False, encoding='latin-1')
    print(f"      Registros carregados: {len(df):,}")
    
    print("\n[2/4] Processando variaveis...")
    
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
    
    # Faixa etaria
    def classificar_faixa(idade):
        if pd.isna(idade):
            return 'Desconhecida'
        if idade < 15:
            return 'Crianca (0-14)'
        elif idade < 23:
            return 'Jovem (15-22)'
        elif idade < 60:
            return 'Adulto (23-59)'
        else:
            return 'Idoso (60+)'
    
    df['FAIXA_ETARIA'] = df['IDADE_ANOS'].apply(classificar_faixa)
    
    print("\n[3/4] Identificando casos graves...")
    
    # Casos graves (obitos, classificacao grave, hospitalizados)
    obitos = df[df['EVOLUCAO'] == 2]
    graves = df[df['CLASSI_FIN'].isin([2, 3])]
    hospitalizados = df[df['HOSPITALIZ'] == 1]
    
    casos_graves = pd.concat([obitos, graves, hospitalizados]).drop_duplicates()
    
    print(f"      Obitos: {len(obitos):,}")
    print(f"      Casos graves (classificacao): {len(graves):,}")
    print(f"      Hospitalizados: {len(hospitalizados):,}")
    print(f"      Total casos graves (unicos): {len(casos_graves):,}")
    
    print("\n[4/4] Gerando estatisticas para base de conhecimento...")
    
    # Estatisticas por faixa etaria
    stats_faixa = []
    for faixa in ['Crianca (0-14)', 'Jovem (15-22)', 'Adulto (23-59)', 'Idoso (60+)']:
        df_faixa = df[df['FAIXA_ETARIA'] == faixa]
        n_total = len(df_faixa)
        
        if n_total > 0:
            n_hosp = (df_faixa['HOSPITALIZ'] == 1).sum()
            n_obito = (df_faixa['EVOLUCAO'] == 2).sum()
            n_grave = df_faixa['CLASSI_FIN'].isin([2, 3]).sum()
            
            stats_faixa.append({
                'faixa_etaria': faixa,
                'n_casos': n_total,
                'n_hospitalizacoes': int(n_hosp),
                'taxa_hospitalizacao': round(n_hosp / n_total * 100, 2),
                'n_obitos': int(n_obito),
                'taxa_obito': round(n_obito / n_total * 100, 3),
                'n_graves': int(n_grave),
                'taxa_gravidade': round(n_grave / n_total * 100, 2)
            })
    
    # Sintomas mais frequentes em casos graves
    sintomas = ['FEBRE', 'MIALGIA', 'CEFALEIA', 'VOMITO', 'NAUSEA', 'DOR_RETRO', 'ARTRALGIA']
    freq_sintomas = {}
    for sint in sintomas:
        if sint in casos_graves.columns:
            freq_sintomas[sint] = round((casos_graves[sint] == 1).sum() / len(casos_graves) * 100, 1)
    
    # Base de conhecimento
    knowledge_base = {
        'metadata': {
            'data_geracao': datetime.now().isoformat(),
            'total_casos': len(df),
            'total_graves': len(casos_graves),
            'fonte': 'SINAN/DATASUS - DENGBR25.csv'
        },
        'estatisticas_faixa_etaria': stats_faixa,
        'frequencia_sintomas_graves': freq_sintomas,
        'alertas_triagem': [
            {
                'regra': 'idade_risco',
                'condicao': 'Idoso (60+)',
                'risco': 'ALTO',
                'taxa_obito_observada': stats_faixa[-1]['taxa_obito'] if stats_faixa else 0,
                'acao': 'Monitoramento intensivo recomendado'
            },
            {
                'regra': 'periodo_critico',
                'condicao': 'Dias 3-7 de sintomas',
                'risco': 'MEDIO-ALTO',
                'acao': 'Reavaliar diariamente, orientar sinais de alarme'
            }
        ]
    }
    
    # Salvar base de conhecimento
    Path("data").mkdir(exist_ok=True)
    with open("data/knowledge_base.json", "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    
    print("\n[OK] Base de conhecimento salva em data/knowledge_base.json")
    
    return knowledge_base


def executar_triagem_demo(kb):
    """Executa demonstracao de triagem"""
    
    print("\n" + "=" * 70)
    print("DEMONSTRACAO DE TRIAGEM")
    print("=" * 70)
    
    # Caso exemplo 1: Adulto com sintomas leves
    caso1 = {
        'idade': 35,
        'sexo': 'Feminino',
        'dias_sintomas': 2,
        'febre': True,
        'cefaleia': True,
        'mialgia': True,
        'vomito': False,
        'dor_abdominal': False,
        'sangramento': False,
        'comorbidades': []
    }
    
    # Caso exemplo 2: Idoso com sinais de alarme
    caso2 = {
        'idade': 72,
        'sexo': 'Masculino',
        'dias_sintomas': 5,
        'febre': True,
        'cefaleia': True,
        'mialgia': True,
        'vomito': True,
        'dor_abdominal': True,
        'sangramento': False,
        'comorbidades': ['DIABETES', 'HIPERTENSA']
    }
    
    # Caso exemplo 3: Crianca com vomitos
    caso3 = {
        'idade': 8,
        'sexo': 'Masculino',
        'dias_sintomas': 4,
        'febre': True,
        'cefaleia': True,
        'mialgia': False,
        'vomito': True,
        'dor_abdominal': True,
        'sangramento': False,
        'comorbidades': []
    }
    
    casos = [
        ("Caso 1: Adulta 35 anos, sintomas leves, dia 2", caso1),
        ("Caso 2: Idoso 72 anos, sinais de alarme, dia 5", caso2),
        ("Caso 3: Crianca 8 anos, vomitos, dia 4", caso3)
    ]
    
    for nome, caso in casos:
        print(f"\n{'-' * 60}")
        print(f"{nome}")
        print(f"{'-' * 60}")
        
        resultado = avaliar_caso(caso, kb)
        
        print(f"\n  Classificacao de Risco: {resultado['classificacao']}")
        print(f"  Score de Risco: {resultado['score']}/100")
        print(f"\n  Fatores identificados:")
        for fator in resultado['fatores']:
            print(f"    - {fator}")
        print(f"\n  Recomendacao:")
        print(f"    {resultado['recomendacao']}")


def avaliar_caso(caso, kb):
    """Avalia um caso usando regras baseadas nos dados"""
    
    score = 0
    fatores = []
    
    # Fator 1: Idade
    idade = caso['idade']
    if idade >= 60:
        score += 25
        fatores.append("Idoso (60+) - grupo de maior risco")
    elif idade < 15:
        score += 15
        fatores.append("Crianca - requer atencao especial")
    
    # Fator 2: Dias de sintomas (periodo critico)
    dias = caso['dias_sintomas']
    if 3 <= dias <= 7:
        score += 20
        fatores.append(f"Dia {dias} de sintomas - periodo critico de evolucao")
    elif dias > 7:
        score += 10
        fatores.append(f"Dia {dias} de sintomas - fase tardia")
    
    # Fator 3: Sinais de alarme
    sinais_alarme = 0
    if caso.get('vomito'):
        sinais_alarme += 1
        fatores.append("Vomitos presentes")
    if caso.get('dor_abdominal'):
        sinais_alarme += 1
        fatores.append("Dor abdominal presente")
    if caso.get('sangramento'):
        sinais_alarme += 2
        fatores.append("Sangramento presente - sinal de gravidade")
    
    score += sinais_alarme * 15
    
    # Fator 4: Comorbidades
    comorb = caso.get('comorbidades', [])
    if 'DIABETES' in comorb:
        score += 15
        fatores.append("Diabetes - acelera evolucao")
    if 'HIPERTENSA' in comorb:
        score += 10
        fatores.append("Hipertensao - fator de risco")
    
    # Classificacao
    if score >= 60:
        classificacao = "ALTO RISCO"
        recomendacao = "Encaminhar para avaliacao medica URGENTE. Considerar internacao para observacao."
    elif score >= 35:
        classificacao = "RISCO MODERADO"
        recomendacao = "Avaliacao medica recomendada em ate 24h. Retorno imediato se piora dos sintomas."
    else:
        classificacao = "BAIXO RISCO"
        recomendacao = "Hidratacao oral vigorosa. Retorno se: vomitos, dor abdominal, sangramento ou prostacao."
    
    return {
        'score': min(score, 100),
        'classificacao': classificacao,
        'fatores': fatores if fatores else ["Sem fatores de risco identificados"],
        'recomendacao': recomendacao
    }


def main():
    """Funcao principal"""
    
    print("\n" + "=" * 70)
    print("SISTEMA RAG DE TRIAGEM DE DENGUE - DEMONSTRACAO")
    print("=" * 70)
    print("\nEste script processa os dados reais do SINAN e demonstra")
    print("o sistema de triagem baseado em regras derivadas dos dados.")
    
    # Processar dados
    kb = processar_dados_sinan()
    
    if kb:
        # Mostrar estatisticas
        print("\n" + "=" * 70)
        print("ESTATISTICAS DA BASE DE CONHECIMENTO")
        print("=" * 70)
        
        print(f"\nTotal de casos analisados: {kb['metadata']['total_casos']:,}")
        print(f"Total de casos graves: {kb['metadata']['total_graves']:,}")
        
        print("\nEstatisticas por Faixa Etaria:")
        print("-" * 70)
        print(f"{'Faixa':<20} {'Casos':>10} {'Hosp':>8} {'Taxa%':>8} {'Obitos':>8} {'Taxa%':>8}")
        print("-" * 70)
        
        for stat in kb['estatisticas_faixa_etaria']:
            print(f"{stat['faixa_etaria']:<20} {stat['n_casos']:>10,} {stat['n_hospitalizacoes']:>8,} "
                  f"{stat['taxa_hospitalizacao']:>7.1f}% {stat['n_obitos']:>8,} {stat['taxa_obito']:>7.3f}%")
        
        print("\nSintomas mais frequentes em casos graves:")
        for sint, freq in sorted(kb['frequencia_sintomas_graves'].items(), key=lambda x: -x[1]):
            print(f"  {sint}: {freq}%")
        
        # Executar demo de triagem
        executar_triagem_demo(kb)
        
        print("\n" + "=" * 70)
        print("DEMONSTRACAO CONCLUIDA")
        print("=" * 70)
        print("\nBase de conhecimento salva em: data/knowledge_base.json")
        print("Esta base pode ser usada pelo sistema RAG completo.")


if __name__ == "__main__":
    main()
