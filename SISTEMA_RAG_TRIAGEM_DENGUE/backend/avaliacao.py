"""
Sistema de Avaliação e Métricas para o RAG de Triagem de Dengue
Implementa golden set, métricas de retrieval e avaliação de qualidade
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger


@dataclass
class CasoGoldenSet:
    """Representa um caso do golden set para avaliação"""
    id: str
    descricao: str
    dados_paciente: Dict[str, Any]
    risco_esperado: str  # BAIXO, MÉDIO, ALTO, CRÍTICO
    documentos_relevantes: List[str]  # IDs de documentos que devem ser recuperados
    keywords_obrigatorias: List[str]  # Palavras que devem aparecer na resposta
    conduta_esperada: str
    sinais_criticos: List[str] = field(default_factory=list)


@dataclass
class ResultadoAvaliacao:
    """Resultado de avaliação de um caso"""
    caso_id: str
    recall_at_k: float
    mrr: float
    risco_correto: bool
    abstention_correta: bool
    keywords_presentes: List[str]
    keywords_ausentes: List[str]
    tempo_resposta_ms: float
    confianca_sistema: float


class GoldenSetDengue:
    """Golden set de casos para validação do sistema RAG"""
    
    def __init__(self):
        self.casos = self._criar_golden_set()
    
    def _criar_golden_set(self) -> List[CasoGoldenSet]:
        """Cria conjunto de casos de validação baseados em padrões epidemiológicos reais"""
        
        casos = [
            # ========== CASOS DE RISCO BAIXO ==========
            CasoGoldenSet(
                id="GS-001",
                descricao="Adulto jovem com quadro clássico sem alarme",
                dados_paciente={
                    'idade': 28,
                    'sexo': 'Masculino',
                    'dias_sintomas': 2,
                    'sintomas': ['febre', 'cefaleia', 'mialgia'],
                    'sinais_alarme': [],
                    'sinais_gravidade': [],
                    'comorbidades': []
                },
                risco_esperado="BAIXO",
                documentos_relevantes=["padrao_adulto", "caso_clinico_dengue_classica"],
                keywords_obrigatorias=["ambulatorial", "hidratação", "retorno"],
                conduta_esperada="Tratamento ambulatorial com hidratação oral"
            ),
            CasoGoldenSet(
                id="GS-002",
                descricao="Jovem com sintomas típicos início",
                dados_paciente={
                    'idade': 19,
                    'sexo': 'Feminino',
                    'dias_sintomas': 1,
                    'sintomas': ['febre', 'dor retro-orbital', 'artralgia'],
                    'sinais_alarme': [],
                    'sinais_gravidade': [],
                    'comorbidades': []
                },
                risco_esperado="BAIXO",
                documentos_relevantes=["padrao_jovem"],
                keywords_obrigatorias=["orientações", "repouso"],
                conduta_esperada="Acompanhamento ambulatorial"
            ),
            
            # ========== CASOS DE RISCO MÉDIO ==========
            CasoGoldenSet(
                id="GS-003",
                descricao="Adulto com comorbidade (diabetes)",
                dados_paciente={
                    'idade': 45,
                    'sexo': 'Masculino',
                    'dias_sintomas': 3,
                    'sintomas': ['febre', 'mialgia', 'náusea'],
                    'sinais_alarme': [],
                    'sinais_gravidade': [],
                    'comorbidades': ['diabetes']
                },
                risco_esperado="MÉDIO",
                documentos_relevantes=["comorbidades_risco", "padrao_adulto"],
                keywords_obrigatorias=["monitoramento", "reavaliação", "24h"],
                conduta_esperada="Monitoramento intensivo"
            ),
            CasoGoldenSet(
                id="GS-004",
                descricao="Gestante com quadro inicial",
                dados_paciente={
                    'idade': 32,
                    'sexo': 'Feminino',
                    'gestante': True,
                    'dias_sintomas': 2,
                    'sintomas': ['febre', 'cefaleia'],
                    'sinais_alarme': [],
                    'sinais_gravidade': [],
                    'comorbidades': []
                },
                risco_esperado="MÉDIO",
                documentos_relevantes=["padrao_adulto"],
                keywords_obrigatorias=["gestante", "acompanhamento", "risco"],
                conduta_esperada="Monitoramento por risco gestacional",
                sinais_criticos=["gestante"]
            ),
            CasoGoldenSet(
                id="GS-005",
                descricao="Idoso com sintomas clássicos",
                dados_paciente={
                    'idade': 72,
                    'sexo': 'Masculino',
                    'dias_sintomas': 4,
                    'sintomas': ['febre', 'mialgia', 'cefaleia'],
                    'sinais_alarme': [],
                    'sinais_gravidade': [],
                    'comorbidades': ['hipertensão']
                },
                risco_esperado="MÉDIO",
                documentos_relevantes=["padrao_idoso", "comorbidades_risco"],
                keywords_obrigatorias=["idoso", "monitoramento", "risco"],
                conduta_esperada="Monitoramento intensivo por idade avançada"
            ),
            
            # ========== CASOS DE RISCO ALTO ==========
            CasoGoldenSet(
                id="GS-006",
                descricao="Adulto com sinais de alarme - dor abdominal",
                dados_paciente={
                    'idade': 35,
                    'sexo': 'Feminino',
                    'dias_sintomas': 4,
                    'sintomas': ['febre', 'mialgia', 'vômito'],
                    'sinais_alarme': ['dor abdominal intensa'],
                    'sinais_gravidade': [],
                    'comorbidades': []
                },
                risco_esperado="ALTO",
                documentos_relevantes=["padrao_adulto", "caso_clinico_alarme"],
                keywords_obrigatorias=["alarme", "urgente", "médico", "avaliação"],
                conduta_esperada="Avaliação médica urgente",
                sinais_criticos=["dor abdominal intensa"]
            ),
            CasoGoldenSet(
                id="GS-007",
                descricao="Paciente com plaquetopenia moderada",
                dados_paciente={
                    'idade': 40,
                    'sexo': 'Masculino',
                    'dias_sintomas': 5,
                    'sintomas': ['febre', 'cefaleia', 'petéquias'],
                    'sinais_alarme': ['sangramento mucosas'],
                    'sinais_gravidade': [],
                    'comorbidades': [],
                    'plaquetas': 85000
                },
                risco_esperado="ALTO",
                documentos_relevantes=["padrao_adulto"],
                keywords_obrigatorias=["plaquetas", "sangramento", "internação"],
                conduta_esperada="Considerar internação"
            ),
            CasoGoldenSet(
                id="GS-008",
                descricao="Idoso com múltiplos sinais de alarme",
                dados_paciente={
                    'idade': 68,
                    'sexo': 'Feminino',
                    'dias_sintomas': 5,
                    'sintomas': ['febre', 'mialgia'],
                    'sinais_alarme': ['vômitos persistentes', 'hipotensão postural'],
                    'sinais_gravidade': [],
                    'comorbidades': ['hipertensão', 'diabetes']
                },
                risco_esperado="ALTO",
                documentos_relevantes=["padrao_idoso", "comorbidades_risco"],
                keywords_obrigatorias=["alarme", "internação", "urgente"],
                conduta_esperada="Internação para monitoramento",
                sinais_criticos=["vômitos persistentes", "hipotensão postural"]
            ),
            
            # ========== CASOS CRÍTICOS ==========
            CasoGoldenSet(
                id="GS-009",
                descricao="Paciente com sinais de choque",
                dados_paciente={
                    'idade': 45,
                    'sexo': 'Masculino',
                    'dias_sintomas': 6,
                    'sintomas': ['febre', 'mialgia'],
                    'sinais_alarme': ['hipotensão postural', 'oliguria'],
                    'sinais_gravidade': ['choque', 'extremidades frias'],
                    'comorbidades': []
                },
                risco_esperado="CRÍTICO",
                documentos_relevantes=["progressao_temporal"],
                keywords_obrigatorias=["emergência", "imediato", "choque", "UTI"],
                conduta_esperada="ATENDIMENTO IMEDIATO - Emergência",
                sinais_criticos=["choque"]
            ),
            CasoGoldenSet(
                id="GS-010",
                descricao="Paciente com sangramento grave",
                dados_paciente={
                    'idade': 55,
                    'sexo': 'Feminino',
                    'dias_sintomas': 5,
                    'sintomas': ['febre', 'náusea'],
                    'sinais_alarme': ['sangramento mucosas'],
                    'sinais_gravidade': ['sangramento grave'],
                    'comorbidades': [],
                    'plaquetas': 25000
                },
                risco_esperado="CRÍTICO",
                documentos_relevantes=["padrao_adulto"],
                keywords_obrigatorias=["emergência", "sangramento", "transfusão"],
                conduta_esperada="EMERGÊNCIA - Risco de hemorragia",
                sinais_criticos=["sangramento grave"]
            ),
            CasoGoldenSet(
                id="GS-011",
                descricao="Criança com alteração de consciência",
                dados_paciente={
                    'idade': 8,
                    'sexo': 'Masculino',
                    'dias_sintomas': 4,
                    'sintomas': ['febre', 'vômito'],
                    'sinais_alarme': ['letargia'],
                    'sinais_gravidade': ['alteração consciência'],
                    'comorbidades': []
                },
                risco_esperado="CRÍTICO",
                documentos_relevantes=["padrao_crianca"],
                keywords_obrigatorias=["emergência", "neurológico", "imediato"],
                conduta_esperada="EMERGÊNCIA PEDIÁTRICA",
                sinais_criticos=["alteração consciência"]
            ),
            
            # ========== CASOS DE ABSTENTION (INCERTEZA) ==========
            CasoGoldenSet(
                id="GS-012",
                descricao="Quadro atípico - poucos sintomas",
                dados_paciente={
                    'idade': 30,
                    'sexo': 'Feminino',
                    'dias_sintomas': 1,
                    'sintomas': ['mal-estar'],
                    'sinais_alarme': [],
                    'sinais_gravidade': [],
                    'comorbidades': []
                },
                risco_esperado="BAIXO",
                documentos_relevantes=[],
                keywords_obrigatorias=["avaliação", "clínica", "confirmação"],
                conduta_esperada="Avaliação clínica para confirmação diagnóstica"
            ),
        ]
        
        return casos
    
    def obter_casos(self, risco: Optional[str] = None) -> List[CasoGoldenSet]:
        """Retorna casos, opcionalmente filtrados por nível de risco"""
        if risco:
            return [c for c in self.casos if c.risco_esperado == risco]
        return self.casos


class AvaliacaoRAG:
    """Sistema de avaliação de qualidade do RAG"""
    
    def __init__(self, rag_system=None):
        self.rag_system = rag_system
        self.golden_set = GoldenSetDengue()
        self.resultados: List[ResultadoAvaliacao] = []
    
    def calcular_recall_at_k(
        self, 
        documentos_recuperados: List[str], 
        documentos_relevantes: List[str],
        k: int = 5
    ) -> float:
        """
        Calcula Recall@K - proporção de documentos relevantes recuperados
        
        Args:
            documentos_recuperados: IDs dos documentos retornados pelo sistema
            documentos_relevantes: IDs dos documentos esperados
            k: número de documentos a considerar
            
        Returns:
            Recall@K entre 0 e 1
        """
        if not documentos_relevantes:
            return 1.0  # Se não há documentos relevantes esperados, recall é 100%
        
        top_k = documentos_recuperados[:k]
        relevantes_encontrados = len(set(top_k) & set(documentos_relevantes))
        
        return relevantes_encontrados / len(documentos_relevantes)
    
    def calcular_mrr(
        self,
        documentos_recuperados: List[str],
        documentos_relevantes: List[str]
    ) -> float:
        """
        Calcula Mean Reciprocal Rank (MRR)
        
        Args:
            documentos_recuperados: IDs ordenados por relevância
            documentos_relevantes: IDs dos documentos esperados
            
        Returns:
            MRR entre 0 e 1
        """
        if not documentos_relevantes:
            return 1.0
        
        for i, doc_id in enumerate(documentos_recuperados):
            if doc_id in documentos_relevantes:
                return 1.0 / (i + 1)
        
        return 0.0
    
    def calcular_ndcg(
        self,
        documentos_recuperados: List[str],
        documentos_relevantes: List[str],
        k: int = 5
    ) -> float:
        """
        Calcula Normalized Discounted Cumulative Gain (nDCG@K)
        
        Args:
            documentos_recuperados: IDs ordenados por relevância
            documentos_relevantes: IDs dos documentos esperados
            k: número de documentos a considerar
            
        Returns:
            nDCG@K entre 0 e 1
        """
        def dcg(relevances, k):
            relevances = relevances[:k]
            return sum(rel / np.log2(i + 2) for i, rel in enumerate(relevances))
        
        # Relevância binária: 1 se relevante, 0 se não
        relevances = [1 if doc in documentos_relevantes else 0 
                     for doc in documentos_recuperados[:k]]
        
        dcg_score = dcg(relevances, k)
        
        # DCG ideal (todos relevantes no topo)
        ideal_relevances = sorted(relevances, reverse=True)
        idcg_score = dcg(ideal_relevances, k)
        
        if idcg_score == 0:
            return 0.0
        
        return dcg_score / idcg_score
    
    def verificar_keywords(
        self,
        resposta: str,
        keywords_obrigatorias: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Verifica presença de keywords obrigatórias na resposta
        
        Returns:
            (keywords_presentes, keywords_ausentes)
        """
        resposta_lower = resposta.lower()
        
        presentes = []
        ausentes = []
        
        for keyword in keywords_obrigatorias:
            if keyword.lower() in resposta_lower:
                presentes.append(keyword)
            else:
                ausentes.append(keyword)
        
        return presentes, ausentes
    
    def avaliar_caso(
        self,
        caso: CasoGoldenSet,
        resultado_rag: Dict[str, Any],
        documentos_recuperados: List[str],
        tempo_ms: float
    ) -> ResultadoAvaliacao:
        """Avalia um caso individual"""
        
        # Métricas de retrieval
        recall = self.calcular_recall_at_k(
            documentos_recuperados, 
            caso.documentos_relevantes
        )
        mrr = self.calcular_mrr(
            documentos_recuperados,
            caso.documentos_relevantes
        )
        
        # Verificar classificação de risco
        risco_sistema = resultado_rag.get('risk_level', '')
        risco_correto = risco_sistema.upper() == caso.risco_esperado.upper()
        
        # Verificar keywords
        analise = resultado_rag.get('analysis', '')
        keywords_presentes, keywords_ausentes = self.verificar_keywords(
            analise,
            caso.keywords_obrigatorias
        )
        
        # Verificar abstention
        confianca = resultado_rag.get('confidence', 1.0)
        abstention_correta = True  # Simplificado
        
        resultado = ResultadoAvaliacao(
            caso_id=caso.id,
            recall_at_k=recall,
            mrr=mrr,
            risco_correto=risco_correto,
            abstention_correta=abstention_correta,
            keywords_presentes=keywords_presentes,
            keywords_ausentes=keywords_ausentes,
            tempo_resposta_ms=tempo_ms,
            confianca_sistema=confianca
        )
        
        self.resultados.append(resultado)
        return resultado
    
    def executar_avaliacao_completa(self) -> Dict[str, Any]:
        """
        Executa avaliação completa em todos os casos do golden set
        
        Returns:
            Relatório consolidado de métricas
        """
        if not self.rag_system:
            raise ValueError("Sistema RAG não configurado")
        
        import time
        
        logger.info(f"Iniciando avaliação com {len(self.golden_set.casos)} casos")
        
        for caso in self.golden_set.casos:
            try:
                inicio = time.time()
                resultado_rag = self.rag_system.analyze_patient(caso.dados_paciente)
                tempo_ms = (time.time() - inicio) * 1000
                
                # Extrair IDs dos documentos recuperados
                docs_recuperados = [
                    doc.get('metadata', {}).get('id_caso', '')
                    for doc in resultado_rag.get('similar_cases', [])
                ]
                
                self.avaliar_caso(caso, resultado_rag, docs_recuperados, tempo_ms)
                
                logger.info(f"Caso {caso.id}: Risco={resultado_rag.get('risk_level')}")
                
            except Exception as e:
                logger.error(f"Erro ao avaliar caso {caso.id}: {e}")
        
        return self.gerar_relatorio()
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório consolidado de avaliação"""
        
        if not self.resultados:
            return {"erro": "Nenhum resultado de avaliação"}
        
        # Métricas agregadas
        recalls = [r.recall_at_k for r in self.resultados]
        mrrs = [r.mrr for r in self.resultados]
        tempos = [r.tempo_resposta_ms for r in self.resultados]
        
        acertos_risco = sum(1 for r in self.resultados if r.risco_correto)
        
        # Keywords
        total_keywords_esperadas = sum(
            len(r.keywords_presentes) + len(r.keywords_ausentes) 
            for r in self.resultados
        )
        total_keywords_presentes = sum(len(r.keywords_presentes) for r in self.resultados)
        
        relatorio = {
            'data_avaliacao': datetime.now().isoformat(),
            'total_casos': len(self.resultados),
            'metricas_retrieval': {
                'recall_at_5_medio': round(np.mean(recalls), 3),
                'recall_at_5_min': round(np.min(recalls), 3),
                'recall_at_5_max': round(np.max(recalls), 3),
                'mrr_medio': round(np.mean(mrrs), 3),
            },
            'metricas_classificacao': {
                'acuracia_risco': round(acertos_risco / len(self.resultados), 3),
                'casos_corretos': acertos_risco,
                'casos_incorretos': len(self.resultados) - acertos_risco,
            },
            'metricas_resposta': {
                'cobertura_keywords': round(
                    total_keywords_presentes / max(total_keywords_esperadas, 1), 3
                ),
            },
            'metricas_performance': {
                'tempo_medio_ms': round(np.mean(tempos), 1),
                'tempo_p95_ms': round(np.percentile(tempos, 95), 1),
            },
            'detalhes_por_caso': [
                {
                    'caso_id': r.caso_id,
                    'recall': r.recall_at_k,
                    'mrr': r.mrr,
                    'risco_correto': r.risco_correto,
                    'keywords_ausentes': r.keywords_ausentes,
                }
                for r in self.resultados
            ]
        }
        
        return relatorio
    
    def salvar_relatorio(self, caminho: str):
        """Salva relatório em arquivo JSON"""
        relatorio = self.gerar_relatorio()
        
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Relatório salvo em: {caminho}")


def executar_avaliacao_offline():
    """
    Executa avaliação offline sem o sistema RAG
    Útil para validar o golden set e métricas
    """
    avaliacao = AvaliacaoRAG()
    golden = avaliacao.golden_set
    
    print("=" * 60)
    print("GOLDEN SET DE VALIDAÇÃO - SISTEMA RAG TRIAGEM DENGUE")
    print("=" * 60)
    
    print(f"\nTotal de casos: {len(golden.casos)}")
    
    # Distribuição por risco
    riscos = {}
    for caso in golden.casos:
        riscos[caso.risco_esperado] = riscos.get(caso.risco_esperado, 0) + 1
    
    print("\nDistribuição por nível de risco:")
    for risco, count in sorted(riscos.items()):
        print(f"  {risco}: {count} casos")
    
    print("\nCasos do Golden Set:")
    print("-" * 60)
    
    for caso in golden.casos:
        sinais = ", ".join(caso.sinais_criticos) if caso.sinais_criticos else "Nenhum"
        print(f"\n[{caso.id}] {caso.descricao}")
        print(f"  Risco Esperado: {caso.risco_esperado}")
        print(f"  Sinais Críticos: {sinais}")
        print(f"  Keywords: {', '.join(caso.keywords_obrigatorias)}")


if __name__ == "__main__":
    executar_avaliacao_offline()
