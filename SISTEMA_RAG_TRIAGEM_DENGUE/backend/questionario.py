"""
Questionário Estruturado de Triagem de Dengue
Sistema de perguntas e coleta de dados para avaliação de pacientes
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json
from pathlib import Path


class TipoPergunta(Enum):
    """Tipos de perguntas do questionário"""
    TEXTO = "texto"
    NUMERO = "numero"
    SELECAO_UNICA = "selecao_unica"
    SELECAO_MULTIPLA = "selecao_multipla"
    SIM_NAO = "sim_nao"
    DATA = "data"


@dataclass
class Pergunta:
    """Representa uma pergunta do questionário"""
    id: str
    texto: str
    tipo: TipoPergunta
    obrigatoria: bool = True
    opcoes: List[str] = field(default_factory=list)
    valor_min: Optional[float] = None
    valor_max: Optional[float] = None
    unidade: Optional[str] = None
    ajuda: Optional[str] = None
    condicao: Optional[str] = None  # Mostra pergunta apenas se condição for satisfeita
    peso_risco: float = 0.0  # Peso para cálculo de score de risco


class QuestionarioTriagemDengue:
    """Sistema de questionário estruturado para triagem de dengue"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa questionário
        
        Args:
            config_path: Caminho para arquivo de configuração YAML
        """
        self.config_path = config_path
        self.perguntas: List[Pergunta] = []
        self.secoes: Dict[str, List[Pergunta]] = {}
        self.respostas: Dict[str, Any] = {}
        
        self._criar_questionario()
    
    def _criar_questionario(self):
        """Cria estrutura completa do questionário"""
        
        # SEÇÃO 1: IDENTIFICAÇÃO E DADOS DEMOGRÁFICOS
        self.secoes['identificacao'] = [
            Pergunta(
                id='idade',
                texto='Qual a idade do paciente?',
                tipo=TipoPergunta.NUMERO,
                valor_min=0,
                valor_max=120,
                unidade='anos',
                ajuda='Idade em anos completos',
                peso_risco=0.0  # Peso será calculado dinamicamente
            ),
            Pergunta(
                id='sexo',
                texto='Sexo do paciente',
                tipo=TipoPergunta.SELECAO_UNICA,
                opcoes=['Masculino', 'Feminino'],
                obrigatoria=True
            ),
            Pergunta(
                id='gestante',
                texto='Paciente está gestante?',
                tipo=TipoPergunta.SIM_NAO,
                condicao='sexo == "Feminino"',
                peso_risco=2.0  # Gestantes têm risco aumentado
            ),
            Pergunta(
                id='semanas_gestacao',
                texto='Idade gestacional (semanas)',
                tipo=TipoPergunta.NUMERO,
                valor_min=1,
                valor_max=42,
                unidade='semanas',
                condicao='gestante == True',
                obrigatoria=False
            ),
        ]
        
        # SEÇÃO 2: HISTÓRIA DA DOENÇA ATUAL
        self.secoes['historia_atual'] = [
            Pergunta(
                id='dias_sintomas',
                texto='Há quantos dias iniciaram os sintomas?',
                tipo=TipoPergunta.NUMERO,
                valor_min=0,
                valor_max=30,
                unidade='dias',
                ajuda='Dias desde o primeiro sintoma',
                peso_risco=0.5  # Mais dias = potencial progressão
            ),
            Pergunta(
                id='febre_presente',
                texto='Paciente apresenta ou apresentou febre?',
                tipo=TipoPergunta.SIM_NAO,
                obrigatoria=True,
                peso_risco=0.3
            ),
            Pergunta(
                id='temperatura_maxima',
                texto='Temperatura máxima registrada',
                tipo=TipoPergunta.NUMERO,
                valor_min=36.0,
                valor_max=42.0,
                unidade='°C',
                condicao='febre_presente == True',
                obrigatoria=False
            ),
            Pergunta(
                id='quedafebre_piora',
                texto='Houve piora dos sintomas após queda da febre?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='Piora após defervescência é sinal de alarme importante',
                peso_risco=2.5
            ),
        ]
        
        # SEÇÃO 3: SINTOMAS CLÁSSICOS
        self.secoes['sintomas_classicos'] = [
            Pergunta(
                id='cefaleia',
                texto='Apresenta dor de cabeça (cefaleia)?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=0.3
            ),
            Pergunta(
                id='intensidade_cefaleia',
                texto='Intensidade da dor de cabeça',
                tipo=TipoPergunta.SELECAO_UNICA,
                opcoes=['Leve', 'Moderada', 'Intensa'],
                condicao='cefaleia == True',
                obrigatoria=False
            ),
            Pergunta(
                id='dor_retro_orbital',
                texto='Apresenta dor atrás dos olhos (retro-orbital)?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=0.4
            ),
            Pergunta(
                id='mialgia',
                texto='Apresenta dor muscular (mialgia)?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=0.3
            ),
            Pergunta(
                id='artralgia',
                texto='Apresenta dor nas articulações (artralgia)?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=0.3
            ),
            Pergunta(
                id='exantema',
                texto='Apresenta erupções na pele (exantema)?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=0.2
            ),
            Pergunta(
                id='nausea',
                texto='Apresenta náusea?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=0.4
            ),
            Pergunta(
                id='vomito',
                texto='Apresenta vômitos?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=0.5
            ),
        ]
        
        # SEÇÃO 4: SINAIS DE ALARME (CRÍTICO!)
        self.secoes['sinais_alarme'] = [
            Pergunta(
                id='dor_abdominal_intensa',
                texto='⚠️ Dor abdominal intensa e contínua?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='Sinal de alarme - extravasamento plasmático',
                peso_risco=3.0
            ),
            Pergunta(
                id='vomitos_persistentes',
                texto='⚠️ Vômitos persistentes (não consegue hidratar)?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='Sinal de alarme - risco de desidratação',
                peso_risco=3.0
            ),
            Pergunta(
                id='sangramento_mucosas',
                texto='⚠️ Sangramento de mucosas (gengivas, nariz, etc)?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='Sinal de alarme - plaquetopenia grave',
                peso_risco=3.5
            ),
            Pergunta(
                id='letargia_irritabilidade',
                texto='⚠️ Letargia ou irritabilidade?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='Sinal de alarme - comprometimento do SNC',
                peso_risco=3.5
            ),
            Pergunta(
                id='hepatomegalia_dolorosa',
                texto='⚠️ Fígado aumentado e doloroso?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='Sinal de alarme - hepatomegalia',
                peso_risco=3.0
            ),
            Pergunta(
                id='hipotensao_postural',
                texto='⚠️ Tontura ao levantar ou hipotensão?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='Sinal de alarme - hipovolemia',
                peso_risco=3.5
            ),
            Pergunta(
                id='oliguria',
                texto='⚠️ Diminuição da quantidade de urina?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='Sinal de alarme - hipoperfusão renal',
                peso_risco=3.0
            ),
            Pergunta(
                id='queda_temperatura_sudorese',
                texto='⚠️ Queda da temperatura com sudorese fria?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='Sinal de alarme - possível choque',
                peso_risco=4.0
            ),
            Pergunta(
                id='acumulo_liquidos',
                texto='⚠️ Acúmulo de líquidos (ascite, derrame)?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='Sinal de alarme - extravasamento plasmático',
                peso_risco=3.5
            ),
        ]
        
        # SEÇÃO 5: SINAIS DE GRAVIDADE (EMERGÊNCIA!)
        self.secoes['sinais_gravidade'] = [
            Pergunta(
                id='choque',
                texto='🚨 Sinais de choque (PA baixa, extremidades frias)?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='EMERGÊNCIA - choque',
                peso_risco=5.0
            ),
            Pergunta(
                id='sangramento_grave',
                texto='🚨 Sangramento grave (hematêmese, melena)?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='EMERGÊNCIA - hemorragia grave',
                peso_risco=5.0
            ),
            Pergunta(
                id='insuficiencia_respiratoria',
                texto='🚨 Desconforto respiratório ou insuficiência respiratória?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='EMERGÊNCIA - comprometimento respiratório',
                peso_risco=5.0
            ),
            Pergunta(
                id='alteracao_consciencia',
                texto='🚨 Alteração do nível de consciência?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='EMERGÊNCIA - comprometimento neurológico',
                peso_risco=5.0
            ),
            Pergunta(
                id='comprometimento_orgao',
                texto='🚨 Sinais de comprometimento de órgãos?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='EMERGÊNCIA - falência de órgãos',
                peso_risco=5.0
            ),
        ]
        
        # SEÇÃO 6: COMORBIDADES
        self.secoes['comorbidades'] = [
            Pergunta(
                id='diabetes',
                texto='Paciente tem diabetes?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=1.3
            ),
            Pergunta(
                id='hipertensao',
                texto='Paciente tem hipertensão arterial?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=1.2
            ),
            Pergunta(
                id='doenca_hematologica',
                texto='Paciente tem doença hematológica?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='Ex: anemia falciforme, leucemia, etc',
                peso_risco=2.0
            ),
            Pergunta(
                id='hepatopatia',
                texto='Paciente tem doença hepática?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=2.0
            ),
            Pergunta(
                id='doenca_renal',
                texto='Paciente tem doença renal?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=1.8
            ),
            Pergunta(
                id='doenca_cardiovascular',
                texto='Paciente tem doença cardiovascular?',
                tipo=TipoPergunta.SIM_NAO,
                peso_risco=1.5
            ),
            Pergunta(
                id='imunossupressao',
                texto='Paciente tem imunossupressão?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='HIV, uso de corticoides, quimioterapia, etc',
                peso_risco=2.0
            ),
        ]
        
        # SEÇÃO 7: DADOS LABORATORIAIS (se disponíveis)
        self.secoes['laboratorio'] = [
            Pergunta(
                id='tem_hemograma',
                texto='Possui hemograma recente?',
                tipo=TipoPergunta.SIM_NAO,
                obrigatoria=False
            ),
            Pergunta(
                id='plaquetas',
                texto='Contagem de plaquetas',
                tipo=TipoPergunta.NUMERO,
                valor_min=0,
                valor_max=500000,
                unidade='/mm³',
                condicao='tem_hemograma == True',
                obrigatoria=False,
                ajuda='Valor normal: 150.000-450.000/mm³',
                peso_risco=0.0  # Calculado dinamicamente
            ),
            Pergunta(
                id='hematocrito',
                texto='Hematócrito',
                tipo=TipoPergunta.NUMERO,
                valor_min=0,
                valor_max=70,
                unidade='%',
                condicao='tem_hemograma == True',
                obrigatoria=False,
                ajuda='Aumento >20% sugere hemoconcentração',
                peso_risco=0.0  # Calculado dinamicamente
            ),
            Pergunta(
                id='leucocitos',
                texto='Leucócitos',
                tipo=TipoPergunta.NUMERO,
                valor_min=0,
                valor_max=50000,
                unidade='/mm³',
                condicao='tem_hemograma == True',
                obrigatoria=False,
                ajuda='Leucopenia é comum na dengue'
            ),
        ]
        
        # SEÇÃO 8: EXAME FÍSICO
        self.secoes['exame_fisico'] = [
            Pergunta(
                id='prova_laco',
                texto='Prova do laço positiva?',
                tipo=TipoPergunta.SIM_NAO,
                ajuda='20 ou mais petéquias em área de 2,5cm²',
                peso_risco=2.0,
                obrigatoria=False
            ),
            Pergunta(
                id='pressao_sistolica',
                texto='Pressão arterial sistólica',
                tipo=TipoPergunta.NUMERO,
                valor_min=50,
                valor_max=250,
                unidade='mmHg',
                obrigatoria=False
            ),
            Pergunta(
                id='pressao_diastolica',
                texto='Pressão arterial diastólica',
                tipo=TipoPergunta.NUMERO,
                valor_min=30,
                valor_max=150,
                unidade='mmHg',
                obrigatoria=False
            ),
            Pergunta(
                id='frequencia_cardiaca',
                texto='Frequência cardíaca',
                tipo=TipoPergunta.NUMERO,
                valor_min=30,
                valor_max=220,
                unidade='bpm',
                obrigatoria=False
            ),
        ]
        
        # Consolidar todas as perguntas
        for secao_perguntas in self.secoes.values():
            self.perguntas.extend(secao_perguntas)
    
    def obter_secoes(self) -> List[str]:
        """Retorna lista de seções do questionário"""
        return list(self.secoes.keys())
    
    def obter_perguntas_secao(self, secao: str) -> List[Pergunta]:
        """Retorna perguntas de uma seção específica"""
        return self.secoes.get(secao, [])
    
    def validar_resposta(self, pergunta_id: str, resposta: Any) -> tuple[bool, Optional[str]]:
        """
        Valida uma resposta
        
        Returns:
            (valida, mensagem_erro)
        """
        pergunta = next((p for p in self.perguntas if p.id == pergunta_id), None)
        
        if not pergunta:
            return False, "Pergunta não encontrada"
        
        # Verificar obrigatoriedade
        if pergunta.obrigatoria and (resposta is None or resposta == ''):
            return False, "Esta pergunta é obrigatória"
        
        # Validar por tipo
        if pergunta.tipo == TipoPergunta.NUMERO:
            try:
                valor = float(resposta)
                if pergunta.valor_min is not None and valor < pergunta.valor_min:
                    return False, f"Valor mínimo: {pergunta.valor_min}"
                if pergunta.valor_max is not None and valor > pergunta.valor_max:
                    return False, f"Valor máximo: {pergunta.valor_max}"
            except (ValueError, TypeError):
                return False, "Valor numérico inválido"
        
        elif pergunta.tipo == TipoPergunta.SELECAO_UNICA:
            if resposta not in pergunta.opcoes:
                return False, f"Opção deve ser uma de: {', '.join(pergunta.opcoes)}"
        
        elif pergunta.tipo == TipoPergunta.SELECAO_MULTIPLA:
            if not isinstance(resposta, list):
                return False, "Resposta deve ser uma lista"
            for item in resposta:
                if item not in pergunta.opcoes:
                    return False, f"Opção inválida: {item}"
        
        return True, None
    
    def registrar_resposta(self, pergunta_id: str, resposta: Any):
        """Registra resposta de uma pergunta"""
        valida, erro = self.validar_resposta(pergunta_id, resposta)
        
        if not valida:
            raise ValueError(f"Resposta inválida para '{pergunta_id}': {erro}")
        
        self.respostas[pergunta_id] = resposta
    
    def calcular_score_risco(self) -> float:
        """
        Calcula score de risco baseado nas respostas
        
        Returns:
            Score de risco (0-100)
        """
        score = 0.0
        
        for pergunta in self.perguntas:
            resposta = self.respostas.get(pergunta.id)
            
            if resposta is None:
                continue
            
            # Para perguntas SIM/NAO
            if pergunta.tipo == TipoPergunta.SIM_NAO and resposta:
                score += pergunta.peso_risco
            
            # Para idade (faixas de risco)
            if pergunta.id == 'idade' and isinstance(resposta, (int, float)):
                if resposta < 1 or resposta > 65:
                    score += 1.5  # Extremos de idade
                if resposta < 5:
                    score += 1.0  # Crianças pequenas
            
            # Para plaquetas
            if pergunta.id == 'plaquetas' and isinstance(resposta, (int, float)):
                if resposta < 50000:
                    score += 3.0  # Plaquetopenia grave
                elif resposta < 100000:
                    score += 2.0  # Plaquetopenia moderada
                elif resposta < 150000:
                    score += 1.0  # Plaquetopenia leve
            
            # Para hematócrito (hemoconcentração)
            if pergunta.id == 'hematocrito' and isinstance(resposta, (int, float)):
                sexo = self.respostas.get('sexo', '')
                if sexo == 'Masculino' and resposta > 50:
                    score += 2.5
                elif sexo == 'Feminino' and resposta > 44:
                    score += 2.5
            
            # Para dias de sintomas (janela crítica)
            if pergunta.id == 'dias_sintomas' and isinstance(resposta, (int, float)):
                if 3 <= resposta <= 7:
                    score += 1.0  # Período crítico
        
        return min(score, 100.0)  # Cap no máximo de 100
    
    def classificar_risco(self) -> Dict[str, Any]:
        """
        Classifica risco baseado no score
        
        Returns:
            Dicionário com classificação de risco
        """
        score = self.calcular_score_risco()
        
        if score >= 10.0:
            nivel = 'CRÍTICO'
            cor = 'vermelho'
            acao = 'ATENDIMENTO IMEDIATO - Encaminhar para emergência'
        elif score >= 6.0:
            nivel = 'ALTO'
            cor = 'laranja'
            acao = 'PRIORIDADE ALTA - Avaliação médica urgente'
        elif score >= 3.0:
            nivel = 'MÉDIO'
            cor = 'amarelo'
            acao = 'Monitoramento intensivo - Reavaliação em 24h'
        else:
            nivel = 'BAIXO'
            cor = 'verde'
            acao = 'Tratamento ambulatorial - Orientações e retorno se piora'
        
        return {
            'score': round(score, 2),
            'nivel': nivel,
            'cor': cor,
            'acao': acao
        }
    
    def gerar_dados_paciente(self) -> Dict[str, Any]:
        """Gera dicionário estruturado com dados do paciente para análise RAG"""
        
        dados = {
            'idade': self.respostas.get('idade'),
            'sexo': self.respostas.get('sexo'),
            'gestante': self.respostas.get('gestante', False),
            'dias_sintomas': self.respostas.get('dias_sintomas', 0),
            'sintomas': [],
            'sinais_alarme': [],
            'sinais_gravidade': [],
            'comorbidades': [],
        }
        
        # Coletar sintomas
        sintomas_ids = ['febre_presente', 'cefaleia', 'dor_retro_orbital', 'mialgia', 
                       'artralgia', 'exantema', 'nausea', 'vomito']
        
        for sintoma_id in sintomas_ids:
            if self.respostas.get(sintoma_id):
                nome = sintoma_id.replace('_presente', '').replace('_', ' ')
                dados['sintomas'].append(nome)
        
        # Coletar sinais de alarme
        alarme_ids = ['dor_abdominal_intensa', 'vomitos_persistentes', 'sangramento_mucosas',
                     'letargia_irritabilidade', 'hepatomegalia_dolorosa', 'hipotensao_postural',
                     'oliguria', 'queda_temperatura_sudorese', 'acumulo_liquidos']
        
        for alarme_id in alarme_ids:
            if self.respostas.get(alarme_id):
                nome = alarme_id.replace('_', ' ')
                dados['sinais_alarme'].append(nome)
        
        # Coletar sinais de gravidade
        gravidade_ids = ['choque', 'sangramento_grave', 'insuficiencia_respiratoria',
                        'alteracao_consciencia', 'comprometimento_orgao']
        
        for grav_id in gravidade_ids:
            if self.respostas.get(grav_id):
                nome = grav_id.replace('_', ' ')
                dados['sinais_gravidade'].append(nome)
        
        # Coletar comorbidades
        comorb_ids = ['diabetes', 'hipertensao', 'doenca_hematologica', 'hepatopatia',
                     'doenca_renal', 'doenca_cardiovascular', 'imunossupressao']
        
        for comorb_id in comorb_ids:
            if self.respostas.get(comorb_id):
                nome = comorb_id.replace('_', ' ')
                dados['comorbidades'].append(nome)
        
        # Adicionar dados laboratoriais
        if self.respostas.get('plaquetas'):
            dados['plaquetas'] = self.respostas['plaquetas']
        
        if self.respostas.get('hematocrito'):
            dados['hematocrito'] = self.respostas['hematocrito']
        
        return dados
    
    def gerar_relatorio_texto(self) -> str:
        """Gera relatório em texto das respostas"""
        linhas = ["=== TRIAGEM DE DENGUE ===\n"]
        
        for secao_nome, perguntas in self.secoes.items():
            linhas.append(f"\n{secao_nome.upper().replace('_', ' ')}")
            linhas.append("-" * 50)
            
            for pergunta in perguntas:
                resposta = self.respostas.get(pergunta.id)
                
                if resposta is not None:
                    texto_resposta = str(resposta)
                    
                    if pergunta.tipo == TipoPergunta.SIM_NAO:
                        texto_resposta = "SIM" if resposta else "NÃO"
                    
                    if pergunta.unidade:
                        texto_resposta += f" {pergunta.unidade}"
                    
                    linhas.append(f"  {pergunta.texto}: {texto_resposta}")
        
        # Adicionar classificação de risco
        risco = self.classificar_risco()
        linhas.append("\n" + "=" * 50)
        linhas.append(f"RISCO: {risco['nivel']} (Score: {risco['score']})")
        linhas.append(f"CONDUTA: {risco['acao']}")
        linhas.append("=" * 50)
        
        return "\n".join(linhas)


if __name__ == "__main__":
    # Teste do questionário
    questionario = QuestionarioTriagemDengue()
    
    print(f"Total de perguntas: {len(questionario.perguntas)}")
    print(f"Seções: {', '.join(questionario.obter_secoes())}")
    
    # Simular preenchimento
    questionario.registrar_resposta('idade', 45)
    questionario.registrar_resposta('sexo', 'Feminino')
    questionario.registrar_resposta('dias_sintomas', 4)
    questionario.registrar_resposta('febre_presente', True)
    questionario.registrar_resposta('cefaleia', True)
    questionario.registrar_resposta('mialgia', True)
    questionario.registrar_resposta('dor_abdominal_intensa', True)
    questionario.registrar_resposta('vomitos_persistentes', True)
    questionario.registrar_resposta('hipertensao', True)
    questionario.registrar_resposta('plaquetas', 85000)
    
    # Gerar classificação
    risco = questionario.classificar_risco()
    print(f"\nClassificação: {risco['nivel']} ({risco['cor']})")
    print(f"Score: {risco['score']}")
    print(f"Ação: {risco['acao']}")
    
    # Gerar dados para RAG
    dados = questionario.gerar_dados_paciente()
    print(f"\nDados do paciente:")
    print(json.dumps(dados, indent=2, ensure_ascii=False))
