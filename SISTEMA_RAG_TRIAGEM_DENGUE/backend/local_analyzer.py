"""
Sistema RAG de Triagem de Dengue - Versão Local
Utiliza base de conhecimento gerada a partir de 1.6M+ casos reais do SINAN
Implementa busca por similaridade sem dependência de APIs externas
"""

import json
import csv
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict
from loguru import logger


class LocalRAGSystem:
    """
    Sistema RAG (Retrieval Augmented Generation) Local para Triagem de Dengue
    Baseado em dados reais de 1.6M+ casos do SINAN/DATASUS
    """
    
    def __init__(self, data_path: str = "./data"):
        """Inicializa o sistema RAG com base de conhecimento"""
        self.data_path = Path(data_path)
        self.knowledge_entries: List[Dict] = []
        self.metadata: Dict = {}
        self._load_knowledge_base()
        logger.info(f"Sistema RAG Local inicializado - {len(self.knowledge_entries)} entradas de conhecimento")
    
    def _load_knowledge_base(self):
        """Carrega todas as bases de conhecimento disponíveis"""
        csv_path = self.data_path / "base_conhecimento_dengue.csv"
        json_completo_path = self.data_path / "knowledge_base_completo.json"
        json_simples_path = self.data_path / "knowledge_base.json"
        
        if csv_path.exists():
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.knowledge_entries = list(reader)
                logger.info(f"Base CSV carregada: {len(self.knowledge_entries)} entradas")
            except Exception as e:
                logger.error(f"Erro ao carregar CSV: {e}")
        
        if json_completo_path.exists():
            try:
                with open(json_completo_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metadata = data.get('metadata', {})
                    self.estatisticas = data.get('estatisticas_resumo', {})
                    if not self.knowledge_entries:
                        self.knowledge_entries = data.get('entradas', [])
                logger.info(f"Metadados carregados: {self.metadata.get('total_casos_analisados', 'N/A')} casos")
            except Exception as e:
                logger.error(f"Erro ao carregar JSON completo: {e}")
        
        if not self.knowledge_entries and json_simples_path.exists():
            try:
                with open(json_simples_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metadata = data.get('metadata', data)
                logger.info("Base JSON simples carregada (fallback)")
            except Exception as e:
                logger.error(f"Erro ao carregar JSON simples: {e}")
        
        if not self.knowledge_entries:
            logger.warning("Nenhuma base encontrada, usando conhecimento padrão")
            self._create_default_knowledge()
    
    def _create_default_knowledge(self):
        """Cria conhecimento padrão baseado em protocolos do MS"""
        self.knowledge_entries = [
            {'categoria': 'conduta', 'subcategoria': 'grupo_a', 'pergunta': 'Qual a conduta para Grupo A?',
             'resposta': 'GRUPO A - Dengue sem sinais de alarme: Tratamento ambulatorial, hidratação oral 60-80ml/kg/dia.',
             'fonte': 'Protocolo MS 2024', 'dados': '{}'},
            {'categoria': 'conduta', 'subcategoria': 'grupo_d', 'pergunta': 'Qual a conduta para Grupo D?',
             'resposta': 'GRUPO D - Dengue grave: EMERGÊNCIA, UTI, expansão volêmica imediata 20ml/kg em 20min.',
             'fonte': 'Protocolo MS 2024', 'dados': '{}'}
        ]
        self.metadata = {'total_casos_analisados': 0, 'fonte': 'Conhecimento padrão'}
    
    def _calculate_similarity(self, query: str, text: str) -> float:
        """Calcula similaridade entre consulta e texto usando TF-IDF simplificado"""
        def normalize(s):
            s = s.lower()
            s = re.sub(r'[^\w\s]', ' ', s)
            return set(s.split())
        
        query_words = normalize(query)
        text_words = normalize(text)
        
        if not query_words or not text_words:
            return 0.0
        
        intersection = query_words & text_words
        union = query_words | text_words
        
        if not union:
            return 0.0
        
        important_words = {'alarme', 'gravidade', 'grave', 'urgência', 'emergência',
                         'sangramento', 'vômito', 'dor', 'abdominal', 'letargia',
                         'choque', 'hipotensão', 'hemorragia', 'óbito', 'morte'}
        
        important_matches = intersection & important_words
        bonus = len(important_matches) * 0.1
        
        similarity = (len(intersection) / len(union)) + bonus
        return min(similarity, 1.0)
    
    def search_knowledge(self, query: str, categoria: Optional[str] = None, top_k: int = 5) -> List[Dict]:
        """Busca conhecimento relevante na base de dados"""
        results = []
        
        for entry in self.knowledge_entries:
            if categoria and entry.get('categoria') != categoria:
                continue
            
            text_to_compare = f"{entry.get('pergunta', '')} {entry.get('resposta', '')}"
            similarity = self._calculate_similarity(query, text_to_compare)
            
            if similarity > 0.05:
                results.append({**entry, 'similarity': round(similarity, 3)})
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def get_risk_by_age(self, idade: int) -> Dict:
        """Obtém dados de risco por faixa etária"""
        if idade < 2:
            faixa = "Lactente (0-2)"
        elif idade < 15:
            faixa = "Criança (2-14)"
        elif idade < 23:
            faixa = "Jovem (15-22)"
        elif idade < 60:
            faixa = "Adulto (23-59)"
        else:
            faixa = "Idoso (60+)"
        
        for entry in self.knowledge_entries:
            if entry.get('categoria') == 'classificacao_risco':
                if faixa in entry.get('resposta', ''):
                    try:
                        dados = json.loads(entry.get('dados', '{}'))
                        return {'faixa_etaria': faixa, 'dados': dados, 'fonte': entry.get('fonte', 'SINAN'),
                                'resposta_completa': entry.get('resposta', '')}
                    except:
                        pass
        
        return {'faixa_etaria': faixa, 'dados': {'taxa_hospitalizacao': 4.5, 'taxa_obito': 0.1, 'nivel_risco': 'MÉDIO'},
                'fonte': 'Estimativa padrão'}
    
    def get_alarm_sign_info(self, sinal: str) -> Optional[Dict]:
        """Obtém informações sobre um sinal de alarme específico"""
        results = self.search_knowledge(f"sinal alarme {sinal}", categoria='sinais_alarme', top_k=1)
        return results[0] if results else None
    
    def get_severity_sign_info(self, sinal: str) -> Optional[Dict]:
        """Obtém informações sobre um sinal de gravidade específico"""
        results = self.search_knowledge(f"sinal gravidade {sinal}", categoria='sinais_gravidade', top_k=1)
        return results[0] if results else None
    
    def get_comorbidity_info(self, comorbidade: str) -> Optional[Dict]:
        """Obtém informações sobre impacto de comorbidade"""
        results = self.search_knowledge(f"comorbidade {comorbidade} risco", categoria='comorbidades', top_k=1)
        return results[0] if results else None
    
    def get_conduct_info(self, grupo: str) -> Optional[Dict]:
        """Obtém conduta recomendada por grupo"""
        results = self.search_knowledge(f"conduta grupo {grupo}", categoria='conduta', top_k=1)
        return results[0] if results else None


class LocalDengueAnalyzer:
    """Analisador de Dengue com Sistema RAG Local - Baseado em 1.6M+ casos reais"""
    
    def __init__(self, knowledge_base_path: str = "./data"):
        """Inicializa o analisador com sistema RAG"""
        self.rag = LocalRAGSystem(knowledge_base_path)
        logger.info("Analisador Local de Dengue com RAG inicializado")
    
    def analyze_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa dados do paciente utilizando RAG e regras clínicas"""
        logger.info(f"Analisando paciente: idade={patient_data.get('idade')}")
        
        idade = patient_data.get('idade', 30)
        sexo = patient_data.get('sexo', 'Não informado')
        dias_sintomas = patient_data.get('dias_sintomas', 0)
        sintomas = patient_data.get('sintomas', [])
        sinais_alarme = patient_data.get('sinais_alarme', [])
        sinais_gravidade = patient_data.get('sinais_gravidade', [])
        comorbidades = patient_data.get('comorbidades', [])
        
        classificacao, nivel_risco = self._classificar_paciente(
            idade, dias_sintomas, sintomas, sinais_alarme, sinais_gravidade, comorbidades
        )
        
        conhecimento_rag = self._buscar_conhecimento_relevante(
            idade, sintomas, sinais_alarme, sinais_gravidade, comorbidades, classificacao
        )
        
        conduta = self._gerar_conduta_rag(classificacao, conhecimento_rag)
        fatores_risco = self._identificar_fatores_risco_rag(
            idade, comorbidades, sinais_alarme, sinais_gravidade, conhecimento_rag
        )
        stats_faixa = self.rag.get_risk_by_age(idade)
        
        analise_texto = self._gerar_analise_rag(
            idade, sexo, dias_sintomas, sintomas, sinais_alarme,
            sinais_gravidade, comorbidades, classificacao, conduta,
            stats_faixa, conhecimento_rag
        )
        
        casos_similares = self._buscar_casos_similares(sintomas, sinais_alarme, sinais_gravidade)
        
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'classificacao': classificacao,
            'nivel_risco': nivel_risco,
            'conduta': conduta,
            'fatores_risco': fatores_risco,
            'analise': analise_texto,
            'estatisticas_faixa': stats_faixa.get('dados', {}),
            'faixa_etaria': stats_faixa.get('faixa_etaria', 'Desconhecida'),
            'confianca': self._calcular_confianca(patient_data, conhecimento_rag),
            'citacoes': self._gerar_citacoes_rag(conhecimento_rag),
            'conhecimento_rag': conhecimento_rag,
            'similar_cases': casos_similares,
            'abstencao': False,
            'motivo_abstencao': None,
            'metadata_rag': {
                'total_casos_base': self.rag.metadata.get('total_casos_analisados', 0),
                'entradas_conhecimento': len(self.rag.knowledge_entries),
                'fonte': self.rag.metadata.get('fonte', 'SINAN/DATASUS')
            }
        }
        
        logger.info(f"Análise RAG concluída: {classificacao} - Risco {nivel_risco}")
        return resultado
    
    def _classificar_paciente(
        self, idade: int, dias_sintomas: int, sintomas: List[str],
        sinais_alarme: List[str], sinais_gravidade: List[str], comorbidades: List[str]
    ) -> Tuple[str, str]:
        """Classifica paciente segundo protocolo do Ministério da Saúde"""
        if sinais_gravidade:
            return "GRUPO D - DENGUE GRAVE", "CRÍTICO"
        if sinais_alarme:
            return "GRUPO C - DENGUE COM SINAIS DE ALARME", "ALTO"
        condicoes_especiais = (idade < 2 or idade > 65 or len(comorbidades) > 0 or
                              'gestante' in [c.lower() for c in comorbidades])
        if condicoes_especiais:
            return "GRUPO B - CONDIÇÕES ESPECIAIS", "MÉDIO"
        return "GRUPO A - DENGUE SEM SINAIS DE ALARME", "BAIXO"
    
    def _buscar_conhecimento_relevante(
        self, idade: int, sintomas: List[str], sinais_alarme: List[str],
        sinais_gravidade: List[str], comorbidades: List[str], classificacao: str
    ) -> Dict[str, Any]:
        """Busca conhecimento relevante no RAG para o caso"""
        conhecimento = {
            'faixa_etaria': self.rag.get_risk_by_age(idade),
            'sinais_alarme_info': [], 'sinais_gravidade_info': [],
            'comorbidades_info': [], 'conduta_info': None, 'referencias_encontradas': 0
        }
        
        for sinal in sinais_alarme:
            info = self.rag.get_alarm_sign_info(sinal)
            if info:
                conhecimento['sinais_alarme_info'].append(info)
                conhecimento['referencias_encontradas'] += 1
        
        for sinal in sinais_gravidade:
            info = self.rag.get_severity_sign_info(sinal)
            if info:
                conhecimento['sinais_gravidade_info'].append(info)
                conhecimento['referencias_encontradas'] += 1
        
        for comorbidade in comorbidades:
            info = self.rag.get_comorbidity_info(comorbidade)
            if info:
                conhecimento['comorbidades_info'].append(info)
                conhecimento['referencias_encontradas'] += 1
        
        grupo = classificacao.split(' - ')[0].replace('GRUPO ', '')
        conhecimento['conduta_info'] = self.rag.get_conduct_info(grupo)
        
        return conhecimento
    
    def _gerar_conduta_rag(self, classificacao: str, conhecimento_rag: Dict) -> Dict[str, Any]:
        """Gera conduta baseada em RAG e protocolos"""
        condutas_base = {
            "GRUPO D - DENGUE GRAVE": {
                "local": "UTI / Unidade de Emergência",
                "hidratacao": "Reposição volêmica imediata - 20ml/kg em 20 min, repetir até 3x",
                "exames": "Hemograma, Hematócrito seriado, Função renal/hepática, Coagulograma",
                "reavaliacao": "Contínua", "internacao": True,
                "prioridade": "🔴 EMERGÊNCIA - Atendimento IMEDIATO",
                "orientacoes": ["Acesso venoso calibroso IMEDIATO", "Expansão volêmica agressiva",
                               "Monitorização contínua de sinais vitais", "Avaliar hemoderivados",
                               "Suporte avançado de vida", "Transferir para UTI"]
            },
            "GRUPO C - DENGUE COM SINAIS DE ALARME": {
                "local": "Leito de observação / Internação",
                "hidratacao": "10ml/kg/hora nas primeiras 2 horas, depois 5-7ml/kg/h",
                "exames": "Hemograma com plaquetas, Hematócrito a cada 2-4h",
                "reavaliacao": "A cada 2-4 horas", "internacao": True,
                "prioridade": "🟠 URGÊNCIA - Atendimento em até 30 minutos",
                "orientacoes": ["Hidratação venosa IMEDIATA", "Monitorar sinais vitais/hora",
                               "Hematócrito seriado", "Observar sinais de alarme", "Preparar transferência"]
            },
            "GRUPO B - CONDIÇÕES ESPECIAIS": {
                "local": "Unidade de Saúde com leito de observação",
                "hidratacao": "80ml/kg/dia VO supervisionada",
                "exames": "Hemograma com plaquetas OBRIGATÓRIO",
                "reavaliacao": "Diária até 48h após febre", "internacao": False,
                "prioridade": "🟡 PRIORIDADE - Atendimento em até 2 horas",
                "orientacoes": ["Hidratação oral supervisionada", "Retorno diário",
                               "Orientar sinais de alarme", "Repouso", "Não usar AINEs"]
            },
            "GRUPO A - DENGUE SEM SINAIS DE ALARME": {
                "local": "Atendimento ambulatorial",
                "hidratacao": "60-80ml/kg/dia VO",
                "exames": "Hemograma a critério clínico",
                "reavaliacao": "Retorno em 24-48h", "internacao": False,
                "prioridade": "🟢 Atendimento conforme demanda",
                "orientacoes": ["Hidratação oral abundante", "Repouso", "Paracetamol ou Dipirona",
                               "NÃO usar AAS/AINEs", "Retorno se sinais de alarme"]
            }
        }
        
        conduta = condutas_base.get(classificacao, condutas_base["GRUPO A - DENGUE SEM SINAIS DE ALARME"])
        conduta_rag = conhecimento_rag.get('conduta_info', {})
        if conduta_rag and conduta_rag.get('resposta'):
            conduta['detalhamento_rag'] = conduta_rag.get('resposta', '')
        return conduta
    
    def _identificar_fatores_risco_rag(
        self, idade: int, comorbidades: List[str], sinais_alarme: List[str],
        sinais_gravidade: List[str], conhecimento_rag: Dict
    ) -> List[Dict[str, str]]:
        """Identifica fatores de risco enriquecidos com dados RAG"""
        fatores = []
        faixa_info = conhecimento_rag.get('faixa_etaria', {})
        dados_faixa = faixa_info.get('dados', {})
        
        if idade < 2:
            fatores.append({"fator": "Lactente/Criança pequena", "impacto": "ALTO",
                          "descricao": "Maior risco de desidratação", "dados_rag": f"Taxa óbito: {dados_faixa.get('taxa_obito', 'N/A')}%"})
        elif idade > 65:
            taxa_obito = dados_faixa.get('taxa_obito', 0.45)
            fatores.append({"fator": "Idoso (>65 anos)", "impacto": "ALTO",
                          "descricao": f"Taxa de óbito elevada: {taxa_obito}%",
                          "dados_rag": f"Base: {self.rag.metadata.get('total_casos_analisados', 'N/A')} casos"})
        
        for i, comorbidade in enumerate(comorbidades):
            info_rag = conhecimento_rag.get('comorbidades_info', [])
            descricao, dados = "Fator de risco", ""
            if i < len(info_rag):
                try:
                    dados_json = json.loads(info_rag[i].get('dados', '{}'))
                    risco = dados_json.get('risco_relativo', 'N/A')
                    descricao = info_rag[i].get('resposta', descricao)[:200] if len(info_rag[i].get('resposta', '')) > 200 else info_rag[i].get('resposta', descricao)
                    dados = f"Risco relativo: {risco}x"
                except: pass
            fatores.append({"fator": comorbidade, "impacto": "MÉDIO-ALTO", "descricao": descricao, "dados_rag": dados})
        
        for i, sinal in enumerate(sinais_alarme):
            info_alarmes = conhecimento_rag.get('sinais_alarme_info', [])
            freq = "N/A"
            if i < len(info_alarmes):
                try:
                    dados = json.loads(info_alarmes[i].get('dados', '{}'))
                    freq = dados.get('frequencia_casos_graves', 'N/A')
                except: pass
            fatores.append({"fator": f"Sinal de alarme: {sinal}", "impacto": "ALTO",
                          "descricao": "Evolução para dengue grave", "dados_rag": f"Presente em {freq}% dos casos graves"})
        
        for i, sinal in enumerate(sinais_gravidade):
            info_grav = conhecimento_rag.get('sinais_gravidade_info', [])
            freq = "N/A"
            if i < len(info_grav):
                try:
                    dados = json.loads(info_grav[i].get('dados', '{}'))
                    freq = dados.get('frequencia_obitos', 'N/A')
                except: pass
            fatores.append({"fator": f"Sinal de gravidade: {sinal}", "impacto": "CRÍTICO",
                          "descricao": "DENGUE GRAVE - risco iminente", "dados_rag": f"Presente em {freq}% dos óbitos"})
        
        return fatores
    
    def _gerar_analise_rag(
        self, idade: int, sexo: str, dias_sintomas: int, sintomas: List[str],
        sinais_alarme: List[str], sinais_gravidade: List[str], comorbidades: List[str],
        classificacao: str, conduta: Dict, stats_faixa: Dict, conhecimento_rag: Dict
    ) -> str:
        """Gera análise textual enriquecida com RAG"""
        dados_faixa = stats_faixa.get('dados', {})
        faixa = stats_faixa.get('faixa_etaria', 'Desconhecida')
        
        analise = f"""
## 📋 ANÁLISE CLÍNICA COM INTELIGÊNCIA ARTIFICIAL

### 🔬 Base de Dados
- **Total de casos analisados:** {self.rag.metadata.get('total_casos_analisados', 'N/A'):,}
- **Fonte:** SINAN/DATASUS 2025
- **Referências encontradas:** {conhecimento_rag.get('referencias_encontradas', 0)}

---

### 👤 Dados do Paciente
| Campo | Valor |
|-------|-------|
| **Idade** | {idade} anos |
| **Sexo** | {sexo} |
| **Faixa etária** | {faixa} |
| **Dias de sintomas** | {dias_sintomas} |

### 📊 Quadro Clínico
- **Sintomas:** {', '.join(sintomas) if sintomas else 'Não informados'}
- **Sinais de alarme:** {', '.join(sinais_alarme) if sinais_alarme else '✅ Nenhum identificado'}
- **Sinais de gravidade:** {', '.join(sinais_gravidade) if sinais_gravidade else '✅ Nenhum identificado'}
- **Comorbidades:** {', '.join(comorbidades) if comorbidades else 'Nenhuma relatada'}

---

## 🎯 CLASSIFICAÇÃO: {classificacao}

### 📈 Dados Epidemiológicos Reais (SINAN 2025)
| Indicador | Valor |
|-----------|-------|
| Taxa de hospitalização na faixa | **{dados_faixa.get('taxa_hospitalizacao', 'N/A')}%** |
| Taxa de óbito na faixa | **{dados_faixa.get('taxa_obito', 'N/A')}%** |
| Nível de risco da faixa | **{dados_faixa.get('nivel_risco', 'N/A')}** |

---

## ⚠️ {conduta.get('prioridade', 'A definir')}

### 💊 Conduta Recomendada
| Aspecto | Recomendação |
|---------|--------------|
| **Local** | {conduta.get('local', 'A definir')} |
| **Hidratação** | {conduta.get('hidratacao', 'Conforme protocolo')} |
| **Exames** | {conduta.get('exames', 'A critério clínico')} |
| **Reavaliação** | {conduta.get('reavaliacao', 'Conforme evolução')} |
| **Internação** | {'✅ SIM - INDICADA' if conduta.get('internacao') else '❌ Não indicada'} |

### 📝 Orientações
"""
        for i, orientacao in enumerate(conduta.get('orientacoes', []), 1):
            analise += f"{i}. {orientacao}\n"
        
        if conhecimento_rag.get('sinais_alarme_info'):
            analise += "\n---\n\n### 📚 Sinais de Alarme (Base RAG)\n"
            for info in conhecimento_rag['sinais_alarme_info'][:3]:
                analise += f"\n**{info.get('subcategoria', 'Sinal')}:** {info.get('resposta', '')}\n"
        
        if dias_sintomas >= 3 and dias_sintomas <= 7:
            analise += f"""
---

### ⚠️ ATENÇÃO - PERÍODO CRÍTICO
Paciente no **{dias_sintomas}º dia de doença**, dentro do **período crítico (3º-7º dia)**.
**MONITORAMENTO INTENSIVO RECOMENDADO.**
"""
        return analise
    
    def _buscar_casos_similares(self, sintomas: List[str], sinais_alarme: List[str], sinais_gravidade: List[str]) -> List[Dict]:
        """Busca padrões similares na base"""
        query_parts = sintomas[:3] + (['alarme'] + sinais_alarme[:2] if sinais_alarme else []) + \
                      (['gravidade'] + sinais_gravidade[:2] if sinais_gravidade else [])
        if not query_parts:
            return []
        
        resultados = self.rag.search_knowledge(" ".join(query_parts), top_k=3)
        return [{'categoria': r.get('categoria', ''), 'relevancia': f"{r.get('similarity', 0) * 100:.0f}%",
                'resumo': r.get('resposta', '')[:150] + '...', 'fonte': r.get('fonte', 'SINAN')} for r in resultados]
    
    def _calcular_confianca(self, patient_data: Dict, conhecimento_rag: Dict) -> Tuple[float, str]:
        """Calcula confiança da análise"""
        score = 0.5
        campos = ['idade', 'sexo', 'dias_sintomas', 'sintomas']
        preenchidos = sum(1 for c in campos if patient_data.get(c))
        score += (preenchidos / len(campos)) * 0.2
        score += min(conhecimento_rag.get('referencias_encontradas', 0) * 0.05, 0.2)
        if self.rag.metadata.get('total_casos_analisados', 0) > 1000000:
            score += 0.1
        score = min(score, 0.95)
        nivel = "ALTA" if score >= 0.85 else "MÉDIA-ALTA" if score >= 0.7 else "MÉDIA" if score >= 0.5 else "BAIXA"
        return (round(score, 2), nivel)
    
    def _gerar_citacoes_rag(self, conhecimento_rag: Dict) -> List[Dict]:
        """Gera citações"""
        citacoes = [
            {"fonte": "Ministério da Saúde", "documento": "Dengue: diagnóstico e manejo clínico",
             "ano": 2024, "relevancia": "Protocolo oficial"},
            {"fonte": "SINAN/DATASUS", "documento": f"Base: {self.rag.metadata.get('total_casos_analisados', 'N/A')} casos",
             "ano": 2025, "relevancia": "Estatísticas epidemiológicas"}
        ]
        for info in conhecimento_rag.get('sinais_alarme_info', [])[:2]:
            citacoes.append({"fonte": info.get('fonte', 'SINAN'), "documento": f"Análise: {info.get('subcategoria', '')}",
                           "ano": 2025, "relevancia": "Dados de casos reais"})
        return citacoes[:5]


def initialize_local_analyzer(knowledge_base_path: str = "./data") -> LocalDengueAnalyzer:
    """Inicializa o analisador local com RAG"""
    logger.info("Inicializando Sistema RAG Local de Triagem de Dengue...")
    analyzer = LocalDengueAnalyzer(knowledge_base_path)
    logger.info("Sistema RAG inicializado com sucesso!")
    return analyzer

