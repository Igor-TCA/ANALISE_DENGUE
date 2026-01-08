"""
Exemplo de Uso do Sistema RAG de Triagem
Demonstra como usar o sistema programaticamente
"""

import sys
from pathlib import Path

# Adicionar backend ao path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from backend.questionario import QuestionarioTriagemDengue
from backend.rag_system import initialize_system


def exemplo_triagem_simples():
    """Exemplo de triagem sem IA"""
    
    print("=" * 60)
    print("EXEMPLO 1: Triagem Simples (sem IA)")
    print("=" * 60)
    
    # Criar questionário
    questionario = QuestionarioTriagemDengue()
    
    # Simular preenchimento de um paciente
    respostas = {
        # Identificação
        'idade': 35,
        'sexo': 'Feminino',
        'gestante': False,
        
        # História
        'dias_sintomas': 4,
        'febre_presente': True,
        'temperatura_maxima': 39.5,
        'quedafebre_piora': False,
        
        # Sintomas
        'cefaleia': True,
        'intensidade_cefaleia': 'Intensa',
        'dor_retro_orbital': True,
        'mialgia': True,
        'artralgia': True,
        'exantema': False,
        'nausea': True,
        'vomito': True,
        
        # Sinais de alarme
        'dor_abdominal_intensa': False,
        'vomitos_persistentes': False,
        'sangramento_mucosas': False,
        'letargia_irritabilidade': False,
        'hepatomegalia_dolorosa': False,
        'hipotensao_postural': False,
        'oliguria': False,
        'queda_temperatura_sudorese': False,
        'acumulo_liquidos': False,
        
        # Sinais de gravidade
        'choque': False,
        'sangramento_grave': False,
        'insuficiencia_respiratoria': False,
        'alteracao_consciencia': False,
        'comprometimento_orgao': False,
        
        # Comorbidades
        'diabetes': False,
        'hipertensao': False,
        'doenca_hematologica': False,
        'hepatopatia': False,
        'doenca_renal': False,
        'doenca_cardiovascular': False,
        'imunossupressao': False,
        
        # Laboratório
        'tem_hemograma': True,
        'plaquetas': 145000,
        'hematocrito': 42,
        'leucocitos': 3500,
        
        # Exame físico
        'prova_laco': False,
        'pressao_sistolica': 120,
        'pressao_diastolica': 80,
        'frequencia_cardiaca': 88,
    }
    
    # Registrar respostas
    for pergunta_id, resposta in respostas.items():
        try:
            questionario.registrar_resposta(pergunta_id, resposta)
        except Exception as e:
            print(f"Erro ao registrar {pergunta_id}: {e}")
    
    # Calcular risco
    risco = questionario.classificar_risco()
    
    print("\n--- RESULTADO ---")
    print(f"Score de Risco: {risco['score']}")
    print(f"Classificação: {risco['nivel']} ({risco['cor']})")
    print(f"Conduta: {risco['acao']}")
    
    # Gerar dados para análise
    dados = questionario.gerar_dados_paciente()
    
    print("\n--- RESUMO CLÍNICO ---")
    print(f"Paciente: {dados['idade']} anos, {dados['sexo']}")
    print(f"Dias de sintomas: {dados['dias_sintomas']}")
    print(f"Sintomas ({len(dados['sintomas'])}): {', '.join(dados['sintomas'][:5])}")
    print(f"Sinais de alarme: {len(dados['sinais_alarme'])}")
    print(f"Sinais de gravidade: {len(dados['sinais_gravidade'])}")
    print(f"Comorbidades: {len(dados['comorbidades'])}")
    
    if 'plaquetas' in dados:
        print(f"Plaquetas: {dados['plaquetas']:,}/mm³")


def exemplo_triagem_com_ia():
    """Exemplo de triagem com análise de IA"""
    
    print("\n\n" + "=" * 60)
    print("EXEMPLO 2: Triagem com Análise de IA")
    print("=" * 60)
    
    try:
        # Inicializar sistema RAG
        print("\nInicializando sistema de IA...")
        rag_system = initialize_system(
            knowledge_base_path="data/knowledge_base.json",
            force_reindex=False
        )
        
        # Dados do paciente
        paciente = {
            'idade': 65,
            'sexo': 'M',
            'gestante': False,
            'dias_sintomas': 5,
            'sintomas': ['febre', 'cefaleia', 'mialgia', 'náusea', 'vomito'],
            'sinais_alarme': ['dor_abdominal_intensa', 'vomitos_persistentes'],
            'sinais_gravidade': [],
            'comorbidades': ['hipertensao', 'diabetes'],
            'plaquetas': 78000,
            'hematocrito': 48
        }
        
        print("\nAnalisando paciente...")
        resultado = rag_system.analyze_patient(paciente)
        
        print("\n--- ANÁLISE DA IA ---")
        print(f"Risco detectado: {resultado['risk_level']} ({resultado['risk_color']})")
        print(f"Confiança: {resultado['confidence']:.0%}")
        print(f"\nResumo: {resultado['patient_summary']}")
        
        print("\n--- AVALIAÇÃO DETALHADA ---")
        print(resultado['analysis'])
        
        if resultado.get('similar_cases'):
            print("\n--- CASOS SIMILARES ---")
            for i, caso in enumerate(resultado['similar_cases'][:2], 1):
                print(f"\nCaso Similar {i}:")
                print(caso['content'][:200] + "...")
                print(f"Tipo: {caso['metadata'].get('tipo')}")
    
    except FileNotFoundError:
        print("\n⚠️  Base de conhecimento não encontrada!")
        print("Execute 'python setup.py' primeiro para processar os dados.")
    
    except Exception as e:
        print(f"\n❌ Erro ao executar análise de IA: {e}")
        print("Verifique se as chaves de API estão configuradas no arquivo .env")


def exemplo_caso_grave():
    """Exemplo de caso grave/crítico"""
    
    print("\n\n" + "=" * 60)
    print("EXEMPLO 3: Caso Grave (Sinais de Alarme)")
    print("=" * 60)
    
    questionario = QuestionarioTriagemDengue()
    
    # Paciente com múltiplos sinais de alarme
    respostas_graves = {
        'idade': 72,
        'sexo': 'Feminino',
        'gestante': False,
        'dias_sintomas': 5,
        'febre_presente': True,
        'quedafebre_piora': True,  # IMPORTANTE
        'cefaleia': True,
        'mialgia': True,
        'nausea': True,
        'vomito': True,
        
        # SINAIS DE ALARME
        'dor_abdominal_intensa': True,
        'vomitos_persistentes': True,
        'sangramento_mucosas': True,
        'letargia_irritabilidade': True,
        'hepatomegalia_dolorosa': True,
        
        # Comorbidades
        'diabetes': True,
        'hipertensao': True,
        
        # Lab
        'tem_hemograma': True,
        'plaquetas': 42000,  # Plaquetopenia grave
        'hematocrito': 52,    # Hemoconcentração
    }
    
    for pid, resp in respostas_graves.items():
        try:
            questionario.registrar_resposta(pid, resp)
        except:
            pass
    
    risco = questionario.classificar_risco()
    dados = questionario.gerar_dados_paciente()
    
    print("\n🚨 ALERTA DE RISCO ELEVADO 🚨")
    print(f"\nClassificação: {risco['nivel']} (Score: {risco['score']})")
    print(f"Conduta: {risco['acao']}")
    
    print("\n--- FATORES DE RISCO IDENTIFICADOS ---")
    print(f"✓ Idade: {dados['idade']} anos (fator de risco)")
    print(f"✓ Período crítico: Dia {dados['dias_sintomas']} de doença")
    print(f"✓ Piora após queda da febre")
    print(f"✓ Plaquetas: {dados['plaquetas']:,}/mm³ (GRAVE)")
    print(f"✓ Comorbidades: {', '.join(dados['comorbidades'])}")
    
    print("\n--- SINAIS DE ALARME PRESENTES ---")
    for sinal in dados['sinais_alarme']:
        print(f"⚠️  {sinal}")
    
    print("\n" + "=" * 60)
    print("⚡ AÇÃO IMEDIATA NECESSÁRIA ⚡")
    print("- Avaliação médica URGENTE")
    print("- Acesso venoso calibroso")
    print("- Hidratação venosa imediata")
    print("- Internação para monitoramento")
    print("- Hemograma a cada 2-4 horas")
    print("=" * 60)


def exemplo_estatisticas():
    """Exemplo de estatísticas do sistema"""
    
    print("\n\n" + "=" * 60)
    print("EXEMPLO 4: Estatísticas do Sistema")
    print("=" * 60)
    
    try:
        rag_system = initialize_system(
            knowledge_base_path="data/knowledge_base.json",
            force_reindex=False
        )
        
        stats = rag_system.get_statistics()
        
        print("\n--- INFORMAÇÕES DO SISTEMA ---")
        print(f"Total de documentos indexados: {stats['total_documents']}")
        print(f"Modelo de embeddings: {stats['embedding_model']}")
        print(f"Provedor LLM: {stats['llm_provider']}")
        print(f"Local do vector store: {stats['vectorstore_path']}")
        
        # Buscar casos similares
        print("\n--- EXEMPLO DE BUSCA ---")
        query = "paciente idoso com plaquetas baixas e sangramento"
        casos = rag_system.search_similar_cases(query, k=3)
        
        print(f"\nBuscando: '{query}'")
        print(f"Encontrados: {len(casos)} casos similares\n")
        
        for i, caso in enumerate(casos, 1):
            print(f"Caso {i}:")
            print(f"  Tipo: {caso['metadata'].get('tipo', 'N/A')}")
            print(f"  Conteúdo: {caso['content'][:150]}...")
            print()
    
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def main():
    """Executa todos os exemplos"""
    
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "EXEMPLOS DE USO - SISTEMA DE TRIAGEM" + " " * 11 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Exemplo 1: Triagem básica
    exemplo_triagem_simples()
    
    # Exemplo 2: Com IA
    exemplo_triagem_com_ia()
    
    # Exemplo 3: Caso grave
    exemplo_caso_grave()
    
    # Exemplo 4: Estatísticas
    exemplo_estatisticas()
    
    print("\n\n" + "=" * 60)
    print("✅ Exemplos concluídos!")
    print("=" * 60)
    print("\nPara usar o sistema completo, execute:")
    print("  python run.py")
    print("\nOu acesse a interface web:")
    print("  streamlit run frontend/app.py")
    print()


if __name__ == "__main__":
    main()
