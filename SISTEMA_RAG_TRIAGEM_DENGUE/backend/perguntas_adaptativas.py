"""
Sistema de Perguntas Adaptativas para Triagem de Dengue
Implementa minimização de perguntas via Information Gain e Expected Utility
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger


class PrioridadePergunta(Enum):
    """Prioridade de perguntas no fluxo adaptativo"""
    OBRIGATORIA_SEGURANCA = 1  # NUNCA pode ser pulada
    ALTA_DISCRIMINACAO = 2     # Alto information gain
    MEDIA_DISCRIMINACAO = 3    # Médio information gain
    BAIXA_DISCRIMINACAO = 4    # Pode ser pulada se confiança alta
    OPCIONAL = 5               # Apenas para refinamento


@dataclass
class PerguntaAdaptativa:
    """Pergunta com metadados para sistema adaptativo"""
    id: str
    texto: str
    prioridade: PrioridadePergunta
    information_gain: float  # Bits de informação esperados
    prob_positivo_base: float  # P(resposta positiva) na população geral
    impacto_risco: Dict[str, float]  # Impacto no score por nível de risco
    dependencias: List[str] = field(default_factory=list)
    condicao_ativacao: Optional[str] = None
    grupo: str = "geral"


@dataclass 
class EstadoTriagem:
    """Estado atual da triagem adaptativa"""
    respostas: Dict[str, Any] = field(default_factory=dict)
    score_atual: float = 0.0
    risco_estimado: str = "INDETERMINADO"
    confianca: float = 0.0
    perguntas_respondidas: List[str] = field(default_factory=list)
    perguntas_puladas: List[str] = field(default_factory=list)
    sinais_criticos_detectados: List[str] = field(default_factory=list)
    modo_emergencia: bool = False


class SistemaAdaptativo:
    """
    Sistema de perguntas adaptativas que minimiza perguntas
    mantendo segurança clínica
    """
    
    # Thresholds de confiança
    CONFIANCA_MINIMA_PARADA = 0.85
    CONFIANCA_ABSTENTION = 0.60
    
    # Thresholds de risco para parada antecipada
    SCORE_CRITICO = 10.0
    SCORE_ALTO = 6.0
    SCORE_MEDIO = 3.0
    
    def __init__(self):
        self.perguntas = self._criar_banco_perguntas()
        self.estado = EstadoTriagem()
        self._historico_triagens: List[Dict] = []
    
    def _criar_banco_perguntas(self) -> Dict[str, PerguntaAdaptativa]:
        """Cria banco de perguntas com metadados adaptativos"""
        
        perguntas = {}
        
        # ========== PERGUNTAS OBRIGATÓRIAS DE SEGURANÇA ==========
        # Estas NUNCA podem ser puladas - são essenciais para segurança
        
        perguntas['idade'] = PerguntaAdaptativa(
            id='idade',
            texto='Qual a idade do paciente (anos)?',
            prioridade=PrioridadePergunta.OBRIGATORIA_SEGURANCA,
            information_gain=0.8,
            prob_positivo_base=1.0,  # Sempre respondida
            impacto_risco={
                '<1': 1.5, '1-14': 0.3, '15-59': 0.0, '>=60': 1.5
            },
            grupo='identificacao'
        )
        
        perguntas['febre_presente'] = PerguntaAdaptativa(
            id='febre_presente',
            texto='Paciente apresenta ou apresentou febre?',
            prioridade=PrioridadePergunta.OBRIGATORIA_SEGURANCA,
            information_gain=0.9,
            prob_positivo_base=0.85,  # 85% dos casos têm febre
            impacto_risco={'sim': 0.3, 'nao': -0.5},
            grupo='sintomas'
        )
        
        perguntas['dias_sintomas'] = PerguntaAdaptativa(
            id='dias_sintomas',
            texto='Há quantos dias iniciaram os sintomas?',
            prioridade=PrioridadePergunta.OBRIGATORIA_SEGURANCA,
            information_gain=0.85,
            prob_positivo_base=1.0,
            impacto_risco={
                '0-2': 0.0, '3-7': 1.0, '>7': 0.5
            },
            grupo='historia'
        )
        
        # SINAIS DE GRAVIDADE - Obrigatórios
        perguntas['choque'] = PerguntaAdaptativa(
            id='choque',
            texto='[GRAVIDADE] Apresenta sinais de CHOQUE (PA baixa, extremidades frias, pulso fraco)?',
            prioridade=PrioridadePergunta.OBRIGATORIA_SEGURANCA,
            information_gain=0.95,
            prob_positivo_base=0.02,  # Raro, mas crítico
            impacto_risco={'sim': 5.0, 'nao': 0.0},
            grupo='gravidade'
        )
        
        perguntas['sangramento_grave'] = PerguntaAdaptativa(
            id='sangramento_grave',
            texto='[GRAVIDADE] Apresenta SANGRAMENTO GRAVE (hematemese, melena, sangramento abundante)?',
            prioridade=PrioridadePergunta.OBRIGATORIA_SEGURANCA,
            information_gain=0.95,
            prob_positivo_base=0.01,
            impacto_risco={'sim': 5.0, 'nao': 0.0},
            grupo='gravidade'
        )
        
        perguntas['alteracao_consciencia'] = PerguntaAdaptativa(
            id='alteracao_consciencia',
            texto='[GRAVIDADE] Apresenta alteracao do nivel de consciencia (confusao, letargia intensa)?',
            prioridade=PrioridadePergunta.OBRIGATORIA_SEGURANCA,
            information_gain=0.95,
            prob_positivo_base=0.02,
            impacto_risco={'sim': 5.0, 'nao': 0.0},
            grupo='gravidade'
        )
        
        perguntas['insuficiencia_respiratoria'] = PerguntaAdaptativa(
            id='insuficiencia_respiratoria',
            texto='[GRAVIDADE] Apresenta dificuldade respiratoria intensa?',
            prioridade=PrioridadePergunta.OBRIGATORIA_SEGURANCA,
            information_gain=0.95,
            prob_positivo_base=0.01,
            impacto_risco={'sim': 5.0, 'nao': 0.0},
            grupo='gravidade'
        )
        
        # ========== SINAIS DE ALARME - Alta Discriminação ==========
        
        perguntas['dor_abdominal_intensa'] = PerguntaAdaptativa(
            id='dor_abdominal_intensa',
            texto='[ALARME] Apresenta dor abdominal INTENSA e CONTINUA?',
            prioridade=PrioridadePergunta.ALTA_DISCRIMINACAO,
            information_gain=0.75,
            prob_positivo_base=0.08,
            impacto_risco={'sim': 3.0, 'nao': 0.0},
            grupo='alarme'
        )
        
        perguntas['vomitos_persistentes'] = PerguntaAdaptativa(
            id='vomitos_persistentes',
            texto='[ALARME] Apresenta vomitos PERSISTENTES (nao consegue se hidratar)?',
            prioridade=PrioridadePergunta.ALTA_DISCRIMINACAO,
            information_gain=0.72,
            prob_positivo_base=0.10,
            impacto_risco={'sim': 3.0, 'nao': 0.0},
            grupo='alarme'
        )
        
        perguntas['sangramento_mucosas'] = PerguntaAdaptativa(
            id='sangramento_mucosas',
            texto='[ALARME] Apresenta sangramento de mucosas (gengivas, nariz)?',
            prioridade=PrioridadePergunta.ALTA_DISCRIMINACAO,
            information_gain=0.70,
            prob_positivo_base=0.05,
            impacto_risco={'sim': 3.5, 'nao': 0.0},
            grupo='alarme'
        )
        
        perguntas['hipotensao_postural'] = PerguntaAdaptativa(
            id='hipotensao_postural',
            texto='[ALARME] Apresenta tontura intensa ao levantar (hipotensao postural)?',
            prioridade=PrioridadePergunta.ALTA_DISCRIMINACAO,
            information_gain=0.68,
            prob_positivo_base=0.07,
            impacto_risco={'sim': 3.5, 'nao': 0.0},
            grupo='alarme'
        )
        
        perguntas['oliguria'] = PerguntaAdaptativa(
            id='oliguria',
            texto='[ALARME] Percebeu diminuicao significativa da urina?',
            prioridade=PrioridadePergunta.ALTA_DISCRIMINACAO,
            information_gain=0.65,
            prob_positivo_base=0.06,
            impacto_risco={'sim': 3.0, 'nao': 0.0},
            grupo='alarme'
        )
        
        # ========== COMORBIDADES - Média Discriminação ==========
        
        perguntas['gestante'] = PerguntaAdaptativa(
            id='gestante',
            texto='A paciente está gestante?',
            prioridade=PrioridadePergunta.ALTA_DISCRIMINACAO,
            information_gain=0.60,
            prob_positivo_base=0.05,
            impacto_risco={'sim': 2.0, 'nao': 0.0},
            condicao_ativacao='sexo == "Feminino"',
            grupo='comorbidades'
        )
        
        perguntas['diabetes'] = PerguntaAdaptativa(
            id='diabetes',
            texto='Paciente tem diabetes?',
            prioridade=PrioridadePergunta.MEDIA_DISCRIMINACAO,
            information_gain=0.45,
            prob_positivo_base=0.12,
            impacto_risco={'sim': 1.3, 'nao': 0.0},
            grupo='comorbidades'
        )
        
        perguntas['hipertensao'] = PerguntaAdaptativa(
            id='hipertensao',
            texto='Paciente tem hipertensão arterial?',
            prioridade=PrioridadePergunta.MEDIA_DISCRIMINACAO,
            information_gain=0.40,
            prob_positivo_base=0.25,
            impacto_risco={'sim': 1.2, 'nao': 0.0},
            grupo='comorbidades'
        )
        
        perguntas['doenca_renal'] = PerguntaAdaptativa(
            id='doenca_renal',
            texto='Paciente tem doença renal crônica?',
            prioridade=PrioridadePergunta.MEDIA_DISCRIMINACAO,
            information_gain=0.50,
            prob_positivo_base=0.04,
            impacto_risco={'sim': 1.8, 'nao': 0.0},
            grupo='comorbidades'
        )
        
        perguntas['imunossupressao'] = PerguntaAdaptativa(
            id='imunossupressao',
            texto='Paciente tem imunossupressão (HIV, quimioterapia, corticoides)?',
            prioridade=PrioridadePergunta.MEDIA_DISCRIMINACAO,
            information_gain=0.55,
            prob_positivo_base=0.03,
            impacto_risco={'sim': 2.0, 'nao': 0.0},
            grupo='comorbidades'
        )
        
        # ========== SINTOMAS CLÁSSICOS - Baixa/Média Discriminação ==========
        
        perguntas['cefaleia'] = PerguntaAdaptativa(
            id='cefaleia',
            texto='Apresenta dor de cabeça?',
            prioridade=PrioridadePergunta.BAIXA_DISCRIMINACAO,
            information_gain=0.25,
            prob_positivo_base=0.80,
            impacto_risco={'sim': 0.3, 'nao': 0.0},
            grupo='sintomas'
        )
        
        perguntas['mialgia'] = PerguntaAdaptativa(
            id='mialgia',
            texto='Apresenta dor muscular?',
            prioridade=PrioridadePergunta.BAIXA_DISCRIMINACAO,
            information_gain=0.22,
            prob_positivo_base=0.75,
            impacto_risco={'sim': 0.3, 'nao': 0.0},
            grupo='sintomas'
        )
        
        perguntas['dor_retro_orbital'] = PerguntaAdaptativa(
            id='dor_retro_orbital',
            texto='Apresenta dor atrás dos olhos?',
            prioridade=PrioridadePergunta.BAIXA_DISCRIMINACAO,
            information_gain=0.35,
            prob_positivo_base=0.35,
            impacto_risco={'sim': 0.4, 'nao': 0.0},
            grupo='sintomas'
        )
        
        perguntas['nausea'] = PerguntaAdaptativa(
            id='nausea',
            texto='Apresenta náusea?',
            prioridade=PrioridadePergunta.BAIXA_DISCRIMINACAO,
            information_gain=0.30,
            prob_positivo_base=0.45,
            impacto_risco={'sim': 0.4, 'nao': 0.0},
            grupo='sintomas'
        )
        
        perguntas['vomito'] = PerguntaAdaptativa(
            id='vomito',
            texto='Apresenta vômitos (não persistentes)?',
            prioridade=PrioridadePergunta.BAIXA_DISCRIMINACAO,
            information_gain=0.35,
            prob_positivo_base=0.30,
            impacto_risco={'sim': 0.5, 'nao': 0.0},
            grupo='sintomas'
        )
        
        # ========== LABORATORIAIS - Opcional mas importante ==========
        
        perguntas['tem_hemograma'] = PerguntaAdaptativa(
            id='tem_hemograma',
            texto='Possui hemograma recente (últimas 24h)?',
            prioridade=PrioridadePergunta.OPCIONAL,
            information_gain=0.50,
            prob_positivo_base=0.30,
            impacto_risco={'sim': 0.0, 'nao': 0.0},
            grupo='laboratorio'
        )
        
        perguntas['plaquetas'] = PerguntaAdaptativa(
            id='plaquetas',
            texto='Contagem de plaquetas (valor)?',
            prioridade=PrioridadePergunta.ALTA_DISCRIMINACAO,
            information_gain=0.80,
            prob_positivo_base=0.15,  # 15% têm plaquetas baixas
            impacto_risco={
                '<50000': 3.0, '50000-100000': 2.0, 
                '100000-150000': 1.0, '>150000': 0.0
            },
            condicao_ativacao='tem_hemograma == True',
            grupo='laboratorio'
        )
        
        return perguntas
    
    def calcular_entropia(self, probabilidade: float) -> float:
        """
        Calcula entropia de Shannon para uma variável binária
        
        H(X) = -p*log2(p) - (1-p)*log2(1-p)
        """
        if probabilidade <= 0 or probabilidade >= 1:
            return 0.0
        
        return -probabilidade * math.log2(probabilidade) - \
               (1 - probabilidade) * math.log2(1 - probabilidade)
    
    def calcular_information_gain_esperado(
        self,
        pergunta: PerguntaAdaptativa
    ) -> float:
        """
        Calcula information gain esperado de uma pergunta
        baseado no estado atual
        """
        # Entropia atual do sistema
        entropia_atual = self._calcular_entropia_estado()
        
        # Probabilidade ajustada pela resposta anterior
        prob_positivo = self._ajustar_probabilidade(
            pergunta.prob_positivo_base,
            pergunta.id
        )
        
        # Entropia esperada após a pergunta
        entropia_pos_positivo = self._estimar_entropia_pos_resposta(
            pergunta, True
        )
        entropia_pos_negativo = self._estimar_entropia_pos_resposta(
            pergunta, False
        )
        
        entropia_esperada = (
            prob_positivo * entropia_pos_positivo +
            (1 - prob_positivo) * entropia_pos_negativo
        )
        
        return max(0, entropia_atual - entropia_esperada)
    
    def _calcular_entropia_estado(self) -> float:
        """Calcula entropia atual baseada na confiança"""
        # Simplificação: usar confiança como proxy
        confianca = self.estado.confianca
        if confianca >= 0.95:
            return 0.1
        elif confianca >= 0.85:
            return 0.3
        elif confianca >= 0.70:
            return 0.6
        else:
            return 1.0
    
    def _ajustar_probabilidade(
        self, 
        prob_base: float, 
        pergunta_id: str
    ) -> float:
        """
        Ajusta probabilidade base considerando respostas anteriores
        (correlações entre sintomas)
        """
        # Ajustes baseados em padrões epidemiológicos conhecidos
        ajuste = 0.0
        
        # Se já tem febre, sintomas clássicos são mais prováveis
        if self.estado.respostas.get('febre_presente', False):
            if pergunta_id in ['cefaleia', 'mialgia', 'artralgia']:
                ajuste += 0.15
        
        # Se já tem sinais de alarme, outros alarmes são mais prováveis
        if any(self.estado.respostas.get(a, False) for a in [
            'dor_abdominal_intensa', 'vomitos_persistentes', 'sangramento_mucosas'
        ]):
            if pergunta_id in ['hipotensao_postural', 'oliguria']:
                ajuste += 0.10
        
        # Se idoso, comorbidades são mais prováveis
        idade = self.estado.respostas.get('idade', 30)
        if idade and idade >= 60:
            if pergunta_id in ['diabetes', 'hipertensao', 'doenca_renal']:
                ajuste += 0.20
        
        return min(0.95, max(0.05, prob_base + ajuste))
    
    def _estimar_entropia_pos_resposta(
        self,
        pergunta: PerguntaAdaptativa,
        resposta_positiva: bool
    ) -> float:
        """Estima entropia após uma resposta hipotética"""
        impacto = pergunta.impacto_risco.get(
            'sim' if resposta_positiva else 'nao', 0.0
        )
        
        # Maior impacto = maior redução de entropia
        if impacto >= 3.0:
            return 0.2
        elif impacto >= 1.0:
            return 0.5
        else:
            return 0.8
    
    def obter_proxima_pergunta(self) -> Optional[PerguntaAdaptativa]:
        """
        Seleciona próxima pergunta usando critério de utilidade esperada
        
        Prioriza:
        1. Perguntas obrigatórias de segurança não respondidas
        2. Perguntas com maior information gain ajustado
        3. Respeita condições de ativação
        """
        # Verificar modo emergência
        if self.estado.modo_emergencia:
            return None
        
        # 1. PRIMEIRO: Perguntas obrigatórias de segurança
        for pergunta in self.perguntas.values():
            if (pergunta.prioridade == PrioridadePergunta.OBRIGATORIA_SEGURANCA and
                pergunta.id not in self.estado.perguntas_respondidas and
                self._condicao_satisfeita(pergunta)):
                return pergunta
        
        # Verificar se já podemos parar (confiança suficiente)
        if self._pode_parar_antecipadamente():
            return None
        
        # 2. Calcular utility para perguntas restantes
        candidatas = []
        
        for pergunta in self.perguntas.values():
            if (pergunta.id not in self.estado.perguntas_respondidas and
                pergunta.prioridade != PrioridadePergunta.OBRIGATORIA_SEGURANCA and
                self._condicao_satisfeita(pergunta)):
                
                # Calcular utilidade esperada
                ig = self.calcular_information_gain_esperado(pergunta)
                
                # Boost para alta discriminação
                if pergunta.prioridade == PrioridadePergunta.ALTA_DISCRIMINACAO:
                    ig *= 1.5
                elif pergunta.prioridade == PrioridadePergunta.OPCIONAL:
                    ig *= 0.5
                
                candidatas.append((pergunta, ig))
        
        if not candidatas:
            return None
        
        # Ordenar por utilidade esperada
        candidatas.sort(key=lambda x: x[1], reverse=True)
        
        return candidatas[0][0]
    
    def _condicao_satisfeita(self, pergunta: PerguntaAdaptativa) -> bool:
        """Verifica se condição de ativação está satisfeita"""
        if not pergunta.condicao_ativacao:
            return True
        
        # Parser simples de condições
        try:
            # Formato: "variavel == valor" ou "variavel == True"
            partes = pergunta.condicao_ativacao.split('==')
            if len(partes) != 2:
                return True
            
            var_name = partes[0].strip()
            valor_esperado = partes[1].strip().strip('"').strip("'")
            
            valor_atual = self.estado.respostas.get(var_name)
            
            if valor_esperado == 'True':
                return valor_atual == True
            elif valor_esperado == 'False':
                return valor_atual == False
            else:
                return str(valor_atual) == valor_esperado
                
        except:
            return True
    
    def _pode_parar_antecipadamente(self) -> bool:
        """
        Verifica se podemos parar antecipadamente
        
        Condições:
        1. Todas perguntas obrigatórias respondidas
        2. Confiança >= threshold
        3. Risco não é INDETERMINADO
        """
        # Verificar obrigatórias
        obrigatorias_pendentes = [
            p for p in self.perguntas.values()
            if (p.prioridade == PrioridadePergunta.OBRIGATORIA_SEGURANCA and
                p.id not in self.estado.perguntas_respondidas and
                self._condicao_satisfeita(p))
        ]
        
        if obrigatorias_pendentes:
            return False
        
        # Se risco é CRÍTICO ou ALTO, não parar - continuar para confirmar
        if self.estado.risco_estimado in ['CRÍTICO']:
            return True  # Emergência - encaminhar imediatamente
        
        # Verificar confiança
        return self.estado.confianca >= self.CONFIANCA_MINIMA_PARADA
    
    def registrar_resposta(
        self, 
        pergunta_id: str, 
        resposta: Any
    ) -> Dict[str, Any]:
        """
        Registra resposta e atualiza estado
        
        Returns:
            Status atualizado com:
            - score_atualizado
            - risco_estimado
            - confianca
            - modo_emergencia
            - proxima_pergunta (ou None se finalizado)
        """
        pergunta = self.perguntas.get(pergunta_id)
        if not pergunta:
            raise ValueError(f"Pergunta não encontrada: {pergunta_id}")
        
        # Registrar resposta
        self.estado.respostas[pergunta_id] = resposta
        self.estado.perguntas_respondidas.append(pergunta_id)
        
        # Atualizar score
        self._atualizar_score(pergunta, resposta)
        
        # Verificar sinais críticos
        self._verificar_sinais_criticos(pergunta, resposta)
        
        # Atualizar risco e confiança
        self._atualizar_classificacao()
        
        # Obter próxima pergunta
        proxima = self.obter_proxima_pergunta()
        
        return {
            'score': self.estado.score_atual,
            'risco': self.estado.risco_estimado,
            'confianca': self.estado.confianca,
            'modo_emergencia': self.estado.modo_emergencia,
            'sinais_criticos': self.estado.sinais_criticos_detectados,
            'proxima_pergunta': proxima,
            'perguntas_restantes': self._contar_perguntas_restantes(),
            'pode_finalizar': proxima is None
        }
    
    def _atualizar_score(
        self, 
        pergunta: PerguntaAdaptativa, 
        resposta: Any
    ):
        """Atualiza score baseado na resposta"""
        
        # Para perguntas numéricas (idade, plaquetas)
        if pergunta.id == 'idade':
            idade = resposta
            if idade < 1 or idade > 65:
                self.estado.score_atual += 1.5
            if idade < 5:
                self.estado.score_atual += 1.0
                
        elif pergunta.id == 'plaquetas':
            plaq = resposta
            if plaq < 50000:
                self.estado.score_atual += 3.0
            elif plaq < 100000:
                self.estado.score_atual += 2.0
            elif plaq < 150000:
                self.estado.score_atual += 1.0
                
        elif pergunta.id == 'dias_sintomas':
            dias = resposta
            if 3 <= dias <= 7:
                self.estado.score_atual += 1.0
        
        # Para perguntas booleanas
        elif isinstance(resposta, bool) and resposta:
            impacto = pergunta.impacto_risco.get('sim', 0.0)
            self.estado.score_atual += impacto
    
    def _verificar_sinais_criticos(
        self,
        pergunta: PerguntaAdaptativa,
        resposta: Any
    ):
        """Verifica e registra sinais críticos que requerem ação imediata"""
        
        sinais_gravidade = [
            'choque', 'sangramento_grave', 'alteracao_consciencia',
            'insuficiencia_respiratoria'
        ]
        
        if pergunta.id in sinais_gravidade and resposta == True:
            self.estado.sinais_criticos_detectados.append(pergunta.id)
            self.estado.modo_emergencia = True
            logger.warning(f"SINAL CRITICO DETECTADO: {pergunta.id}")
    
    def _atualizar_classificacao(self):
        """Atualiza classificação de risco e confiança"""
        score = self.estado.score_atual
        
        # Classificar risco
        if self.estado.modo_emergencia or score >= self.SCORE_CRITICO:
            self.estado.risco_estimado = "CRÍTICO"
            self.estado.confianca = 0.95
        elif score >= self.SCORE_ALTO:
            self.estado.risco_estimado = "ALTO"
            self.estado.confianca = 0.85
        elif score >= self.SCORE_MEDIO:
            self.estado.risco_estimado = "MÉDIO"
            self.estado.confianca = 0.80
        else:
            self.estado.risco_estimado = "BAIXO"
            # Confiança aumenta com mais perguntas respondidas
            n_respondidas = len(self.estado.perguntas_respondidas)
            self.estado.confianca = min(0.90, 0.50 + (n_respondidas * 0.05))
    
    def _contar_perguntas_restantes(self) -> int:
        """Conta perguntas que ainda podem ser feitas"""
        return len([
            p for p in self.perguntas.values()
            if (p.id not in self.estado.perguntas_respondidas and
                self._condicao_satisfeita(p))
        ])
    
    def iniciar_nova_triagem(self):
        """Reinicia estado para nova triagem"""
        self.estado = EstadoTriagem()
    
    def gerar_resumo_triagem(self) -> Dict[str, Any]:
        """Gera resumo da triagem para logging e análise"""
        return {
            'timestamp': logger._core.handlers[0]._sink._file.name if hasattr(logger, '_core') else None,
            'total_perguntas': len(self.estado.perguntas_respondidas),
            'perguntas_respondidas': self.estado.perguntas_respondidas,
            'score_final': self.estado.score_atual,
            'risco_final': self.estado.risco_estimado,
            'confianca_final': self.estado.confianca,
            'sinais_criticos': self.estado.sinais_criticos_detectados,
            'modo_emergencia': self.estado.modo_emergencia
        }
    
    def deve_abstenir(self) -> Tuple[bool, str]:
        """
        Verifica se o sistema deve se abster de dar resposta
        
        Returns:
            (deve_abstenir, motivo)
        """
        # Caso 1: Poucas perguntas respondidas
        if len(self.estado.perguntas_respondidas) < 4:
            return True, "Informações insuficientes para avaliação"
        
        # Caso 2: Confiança muito baixa
        if self.estado.confianca < self.CONFIANCA_ABSTENTION:
            return True, "Confiança insuficiente - recomenda-se avaliação médica presencial"
        
        # Caso 3: Dados inconsistentes
        # (ex: sem febre mas com sinais de alarme típicos de dengue grave)
        if not self.estado.respostas.get('febre_presente', True):
            sinais_alarme = any(
                self.estado.respostas.get(a, False) 
                for a in ['dor_abdominal_intensa', 'vomitos_persistentes']
            )
            if sinais_alarme:
                return True, "Quadro atípico - avaliação médica necessária"
        
        return False, ""


def demonstrar_sistema_adaptativo():
    """Demonstração do sistema de perguntas adaptativas"""
    
    sistema = SistemaAdaptativo()
    
    print("=" * 60)
    print("SISTEMA ADAPTATIVO DE TRIAGEM - DEMONSTRAÇÃO")
    print("=" * 60)
    
    # Simular respostas de um paciente de risco médio
    respostas_simuladas = [
        ('idade', 65),
        ('febre_presente', True),
        ('dias_sintomas', 4),
        ('choque', False),
        ('sangramento_grave', False),
        ('alteracao_consciencia', False),
        ('insuficiencia_respiratoria', False),
        ('dor_abdominal_intensa', False),
        ('vomitos_persistentes', True),  # Sinal de alarme
        ('diabetes', True),  # Comorbidade
    ]
    
    print("\nSimulando triagem de paciente...\n")
    
    for pergunta_id, resposta in respostas_simuladas:
        pergunta = sistema.perguntas.get(pergunta_id)
        if pergunta:
            resultado = sistema.registrar_resposta(pergunta_id, resposta)
            
            print(f"P: {pergunta.texto}")
            print(f"R: {resposta}")
            print(f"   → Score: {resultado['score']:.1f} | "
                  f"Risco: {resultado['risco']} | "
                  f"Confiança: {resultado['confianca']:.0%}")
            
            if resultado['modo_emergencia']:
                print("   MODO EMERGENCIA ATIVADO")
                break
            
            if resultado['pode_finalizar']:
                print("\n   Triagem pode ser finalizada (confianca suficiente)")
                break
            
            print()
    
    # Resumo final
    resumo = sistema.gerar_resumo_triagem()
    print("\n" + "=" * 60)
    print("RESUMO DA TRIAGEM")
    print("=" * 60)
    print(f"Perguntas realizadas: {resumo['total_perguntas']}")
    print(f"Score final: {resumo['score_final']:.1f}")
    print(f"Classificação: {resumo['risco_final']}")
    print(f"Confiança: {resumo['confianca_final']:.0%}")
    
    # Verificar abstention
    deve_abstenir, motivo = sistema.deve_abstenir()
    if deve_abstenir:
        print(f"\nABSTENTION: {motivo}")


if __name__ == "__main__":
    demonstrar_sistema_adaptativo()
