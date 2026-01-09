"""
Sistema RAG (Retrieval-Augmented Generation) para Triagem de Dengue
Utiliza embeddings e LLM para análise de casos clínicos

Versão 2.0 - Melhorias de segurança, abstention e citações
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

# Importações opcionais para LLM
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
except ImportError:
    ChatOpenAI = None
    OpenAIEmbeddings = None
from loguru import logger


class DengueRAGSystem:
    """Sistema RAG para análise e triagem de dengue"""
    
    def __init__(
        self, 
        knowledge_base_path: str,
        vector_store_path: str = "./vectorstore",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_provider: str = "openai"
    ):
        """
        Inicializa o sistema RAG
        
        Argumentos:
            knowledge_base_path: Caminho para base de conhecimento (JSON)
            vector_store_path: Caminho para salvar/carregar vector store
            embedding_model: Modelo de embeddings
            llm_provider: Provedor LLM (openai ou anthropic)
        """
        load_dotenv()
        
        self.knowledge_base_path = Path(knowledge_base_path)
        self.vector_store_path = Path(vector_store_path)
        self.embedding_model_name = embedding_model
        self.llm_provider = llm_provider
        
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        
        logger.info("Sistema RAG inicializado")
    
    def setup_embeddings(self):
        """Configura modelo de embeddings"""
        logger.info(f"Configurando embeddings: {self.embedding_model_name}")
        
        # Usar embeddings locais (Hugging Face) para economizar API calls
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        logger.info("Embeddings configurados")
        return self
    
    def setup_llm(self, model_name: Optional[str] = None, temperature: float = 0.3):
        """Configura modelo LLM"""
        
        if self.llm_provider == "openai":
            model = model_name or os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
            logger.info(f"Configurando LLM: OpenAI {model}")
            
            self.llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        
        elif self.llm_provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            model = model_name or "claude-3-opus-20240229"
            logger.info(f"Configurando LLM: Anthropic {model}")
            
            self.llm = ChatAnthropic(
                model=model,
                temperature=temperature,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        
        else:
            raise ValueError(f"LLM provider não suportado: {self.llm_provider}")
        
        logger.info("LLM configurado")
        return self
    
    def load_and_index_knowledge(self, force_reindex: bool = False):
        """Carrega base de conhecimento e cria/carrega vector store"""
        
        if self.vector_store_path.exists() and not force_reindex:
            logger.info("Carregando vector store existente...")
            self.vectorstore = Chroma(
                persist_directory=str(self.vector_store_path),
                embedding_function=self.embeddings
            )
            logger.info(f"Vector store carregado: {self.vectorstore._collection.count()} documentos")
        
        else:
            logger.info("Criando novo vector store...")
            
            # Carregar base de conhecimento
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                knowledge_data = json.load(f)
            
            logger.info(f"Base de conhecimento carregada: {len(knowledge_data)} documentos")
            
            # Converter para documentos LangChain
            documents = self._convert_to_langchain_docs(knowledge_data)
            
            # Criar chunks menores se necessário
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            split_docs = text_splitter.split_documents(documents)
            logger.info(f"Documentos divididos em {len(split_docs)} chunks")
            
            # Criar vector store
            self.vectorstore = Chroma.from_documents(
                documents=split_docs,
                embedding=self.embeddings,
                persist_directory=str(self.vector_store_path)
            )
            
            self.vectorstore.persist()
            logger.info("Vector store criado e persistido")
        
        return self
    
    def _convert_to_langchain_docs(self, knowledge_data: List[Dict]) -> List[Document]:
        """Converte dados da base de conhecimento para documentos LangChain"""
        documents = []
        
        for item in knowledge_data:
            # Usar narrativa como conteúdo principal
            content = item.get('texto_narrativo', '')
            
            # Metadados estruturados
            metadata = {
                'tipo': item.get('tipo', 'desconhecido'),
                'id_caso': item.get('id_caso', ''),
            }
            
            # Adicionar metadados específicos por tipo
            if item.get('tipo') == 'caso_clinico':
                metadata['faixa_etaria'] = item.get('perfil', {}).get('faixa_etaria', '')
                metadata['classificacao'] = item.get('evolucao', {}).get('classificacao_final', '')
                metadata['desfecho'] = item.get('evolucao', {}).get('desfecho', '')
            
            elif item.get('tipo') == 'padrao_epidemiologico':
                metadata['faixa_etaria'] = item.get('faixa_etaria', '')
                metadata['n_casos'] = item.get('n_casos', 0)
            
            # Enriquecer conteúdo com informação estruturada
            if item.get('tipo') == 'caso_clinico':
                sintomas = item.get('apresentacao_clinica', {}).get('sintomas', [])
                alarmes = item.get('apresentacao_clinica', {}).get('sinais_alarme', [])
                
                if sintomas:
                    content += f"\nSintomas: {', '.join(sintomas)}"
                if alarmes:
                    content += f"\nSinais de alarme: {', '.join(alarmes)}"
            
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)
        
        return documents
    
    def create_qa_chain(self):
        """Cria chain de Question-Answering com contexto médico"""
        
        # Template de prompt especializado para triagem médica com GUARDRAILS DE SEGURANÇA
        prompt_template = """Você é um sistema de APOIO À DECISÃO em triagem de dengue, treinado com dados reais do SINAN/DATASUS.

AVISO DE SEGURANCA - LEIA ANTES DE PROSSEGUIR:
Este sistema é APENAS auxiliar e NÃO substitui avaliação médica presencial.
NUNCA forneça diagnóstico definitivo ou garanta prognóstico.
Sempre recomende avaliação profissional para casos com qualquer sinal de alarme.

Sua função é:
1. Analisar informações clínicas e identificar padrões de risco
2. Classificar o risco baseando-se em evidências epidemiológicas
3. Recomendar condutas seguindo protocolos do Ministério da Saúde
4. CITAR os casos similares que fundamentam sua análise

Contexto de casos similares da base de dados:
{context}

Informações do paciente atual:
{question}

REGRAS OBRIGATÓRIAS:
1. Se houver QUALQUER sinal de gravidade (choque, sangramento grave, alteração consciência) → Classificar como CRÍTICO
2. Se houver QUALQUER sinal de alarme → Classificar como ALTO ou superior
3. Se paciente for idoso (>60), gestante ou tiver comorbidades → Aumentar um nível de risco
4. Se as informações forem insuficientes → Indicar "CONFIANÇA BAIXA" e recomendar avaliação presencial
5. SEMPRE incluir seção "Fundamentação" com referência aos casos similares encontrados
6. NUNCA afirmar certeza diagnóstica - use termos como "sugere", "indica", "padrão consistente com"

FORMATO DA RESPOSTA:

**CLASSIFICAÇÃO DE RISCO:** [BAIXO/MÉDIO/ALTO/CRÍTICO]
**CONFIANÇA DA ANÁLISE:** [ALTA/MÉDIA/BAIXA]

**ANÁLISE CLÍNICA:**
[Análise dos sintomas e fatores de risco identificados]

**FUNDAMENTAÇÃO (Casos Similares):**
[Cite padrões encontrados nos casos da base que fundamentam a análise]

**SINAIS DE ALERTA IDENTIFICADOS:**
[Liste sinais de alarme ou gravidade presentes, ou "Nenhum identificado"]

**CONDUTA RECOMENDADA:**
[Recomendação clara de próximos passos]

**OBSERVAÇÕES DE SEGURANÇA:**
[Orientações específicas para monitoramento e quando buscar atendimento urgente]

Análise:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Criar retriever com busca por similaridade
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # Retornar top 5 documentos mais similares
        )
        
        # Criar chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        logger.info("QA Chain criada")
        return self
    
    def analyze_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa dados de um paciente e retorna avaliação de risco
        
        Argumentos:
            patient_data: Dicionário com dados do paciente
            
        Retorna:
            Dicionário com análise, classificação de risco, recomendações e citações
        """
        inicio = datetime.now()
        
        # Formatar dados do paciente como query
        query = self._format_patient_query(patient_data)
        
        logger.info(f"Analisando paciente...")
        
        # Executar chain
        result = self.qa_chain({"query": query})
        
        # Extrair informações
        analysis = result['result']
        source_docs = result.get('source_documents', [])
        
        # Classificar risco baseado na resposta
        risk_level = self._extract_risk_level(analysis)
        
        # Calcular confiança melhorada
        confidence_score, confidence_level = self._calculate_confidence(
            source_docs, patient_data, analysis
        )
        
        # Verificar se deve abster-se
        should_abstain, abstain_reason = self._should_abstain(confidence_score, patient_data)
        
        # Formatar casos similares com citações
        similar_cases = self._format_similar_cases(source_docs)
        
        # Tempo de processamento
        tempo_ms = (datetime.now() - inicio).total_seconds() * 1000
        
        # Montar resposta estruturada
        response = {
            'analysis': analysis,
            'risk_level': risk_level,
            'risk_color': self._get_risk_color(risk_level),
            'similar_cases': similar_cases,
            'citations': self._format_citations(similar_cases),
            'confidence': confidence_score,
            'confidence_level': confidence_level,
            'should_abstain': should_abstain,
            'abstain_reason': abstain_reason,
            'patient_summary': self._create_patient_summary(patient_data),
            'processing_time_ms': round(tempo_ms, 1),
            'disclaimer': self._get_safety_disclaimer(risk_level)
        }
        
        # Log estruturado para análise posterior
        self._log_analysis(patient_data, response)
        
        logger.info(f"Análise concluída - Risco: {risk_level} | Confiança: {confidence_level}")
        
        return response
    
    def _format_citations(self, similar_cases: List[Dict]) -> str:
        """Formata citações dos casos recuperados"""
        if not similar_cases:
            return "Nenhuma referência encontrada na base de dados."
        
        citations = []
        for i, caso in enumerate(similar_cases[:3], 1):
            tipo = caso.get('tipo', 'caso')
            faixa = caso.get('faixa_etaria', '')
            preview = caso.get('content_preview', '')[:150]
            
            citation = f"[{caso['id']}] {tipo.upper()}"
            if faixa:
                citation += f" ({faixa})"
            citation += f": {preview}..."
            citations.append(citation)
        
        return "\n".join(citations)
    
    def _get_safety_disclaimer(self, risk_level: str) -> str:
        """Retorna disclaimer de segurança apropriado ao nível de risco"""
        base_disclaimer = (
            "AVISO: Este e um sistema de APOIO A DECISAO. "
            "NÃO substitui avaliação médica profissional. "
        )
        
        if risk_level == 'CRÍTICO':
            return base_disclaimer + (
                "ATENCAO: Caso com sinais de gravidade identificados. "
                "ENCAMINHAR IMEDIATAMENTE para atendimento de emergência. "
                "Não aguardar - cada minuto conta."
            )
        elif risk_level == 'ALTO':
            return base_disclaimer + (
                "ALERTA: Paciente com sinais de alarme. "
                "Avaliação médica urgente é NECESSÁRIA. "
                "Se piora do quadro, buscar emergência imediatamente."
            )
        elif risk_level == 'MÉDIO':
            return base_disclaimer + (
                "Monitoramento recomendado. "
                "Reavaliação em 24 horas. "
                "Orientar sinais de alarme para busca de atendimento."
            )
        else:
            return base_disclaimer + (
                "Acompanhamento ambulatorial. "
                "Retorno se piora ou não melhora em 48h. "
                "Manter hidratação adequada."
            )
    
    def _log_analysis(self, patient_data: Dict, response: Dict):
        """Log estruturado para análise e melhoria do sistema"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'patient_age': patient_data.get('idade'),
            'patient_sex': patient_data.get('sexo'),
            'days_symptoms': patient_data.get('dias_sintomas'),
            'n_symptoms': len(patient_data.get('sintomas', [])),
            'n_alarm_signs': len(patient_data.get('sinais_alarme', [])),
            'n_severity_signs': len(patient_data.get('sinais_gravidade', [])),
            'risk_level': response['risk_level'],
            'confidence': response['confidence'],
            'should_abstain': response['should_abstain'],
            'processing_time_ms': response['processing_time_ms']
        }
        
        logger.info(f"TRIAGEM_LOG: {json.dumps(log_entry)}")
    
    def _format_patient_query(self, patient_data: Dict) -> str:
        """Formata dados do paciente como query para o sistema"""
        
        query_parts = []
        
        # Informações demográficas
        idade = patient_data.get('idade', 'não informada')
        sexo = patient_data.get('sexo', 'não informado')
        gestante = patient_data.get('gestante', False)
        
        query_parts.append(f"Paciente: {idade} anos, sexo {sexo}")
        if gestante:
            query_parts.append("GESTANTE")
        
        # Dias de sintomas
        dias_sintomas = patient_data.get('dias_sintomas', 0)
        query_parts.append(f"Dias desde início dos sintomas: {dias_sintomas}")
        
        # Sintomas
        sintomas = patient_data.get('sintomas', [])
        if sintomas:
            query_parts.append(f"Sintomas presentes: {', '.join(sintomas)}")
        
        # Sinais de alarme
        alarmes = patient_data.get('sinais_alarme', [])
        if alarmes:
            query_parts.append(f"SINAIS DE ALARME: {', '.join(alarmes)}")
        
        # Sinais de gravidade
        gravidade = patient_data.get('sinais_gravidade', [])
        if gravidade:
            query_parts.append(f"SINAIS DE GRAVIDADE: {', '.join(gravidade)}")
        
        # Comorbidades
        comorbidades = patient_data.get('comorbidades', [])
        if comorbidades:
            query_parts.append(f"Comorbidades: {', '.join(comorbidades)}")
        
        # Dados laboratoriais
        if 'plaquetas' in patient_data:
            query_parts.append(f"Plaquetas: {patient_data['plaquetas']}/mm³")
        
        if 'hematocrito' in patient_data:
            query_parts.append(f"Hematócrito: {patient_data['hematocrito']}%")
        
        return "\n".join(query_parts)
    
    def _extract_risk_level(self, analysis: str) -> str:
        """Extrai nível de risco da análise"""
        analysis_upper = analysis.upper()
        
        if 'CRÍTICO' in analysis_upper or 'EMERGÊNCIA' in analysis_upper:
            return 'CRÍTICO'
        elif 'ALTO' in analysis_upper and 'RISCO' in analysis_upper:
            return 'ALTO'
        elif 'MÉDIO' in analysis_upper or 'MODERADO' in analysis_upper:
            return 'MÉDIO'
        else:
            return 'BAIXO'
    
    def _get_risk_color(self, risk_level: str) -> str:
        """Retorna cor associada ao nível de risco"""
        colors = {
            'BAIXO': 'verde',
            'MÉDIO': 'amarelo',
            'ALTO': 'laranja',
            'CRÍTICO': 'vermelho'
        }
        return colors.get(risk_level, 'cinza')
    
    def _format_similar_cases(self, source_docs: List[Document]) -> List[Dict]:
        """Formata casos similares encontrados com citações completas"""
        similar = []
        
        for i, doc in enumerate(source_docs[:5]):  # Top 5 casos mais similares
            caso = {
                'id': f"REF-{i+1}",
                'content': doc.page_content,  # Conteúdo completo para citação
                'content_preview': doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                'metadata': doc.metadata,
                'tipo': doc.metadata.get('tipo', 'desconhecido'),
                'faixa_etaria': doc.metadata.get('faixa_etaria', ''),
                'desfecho': doc.metadata.get('desfecho', '')
            }
            similar.append(caso)
        
        return similar
    
    def _calculate_confidence(
        self, 
        source_docs: List[Document],
        patient_data: Dict[str, Any],
        analysis: str
    ) -> Tuple[float, str]:
        """
        Calcula confiança baseada em múltiplos fatores
        
        Retorna:
            (score_confianca, nivel_confianca)
        """
        score = 0.0
        
        # Fator 1: Número de documentos relevantes encontrados (0-0.3)
        if len(source_docs) >= 5:
            score += 0.30
        elif len(source_docs) >= 3:
            score += 0.20
        elif len(source_docs) >= 1:
            score += 0.10
        
        # Fator 2: Completude dos dados do paciente (0-0.3)
        campos_essenciais = ['idade', 'sexo', 'dias_sintomas', 'sintomas']
        campos_preenchidos = sum(1 for c in campos_essenciais if patient_data.get(c))
        score += (campos_preenchidos / len(campos_essenciais)) * 0.30
        
        # Fator 3: Consistência da análise (0-0.2)
        # Verificar se a análise contém elementos estruturados
        elementos_esperados = [
            'CLASSIFICAÇÃO', 'CONDUTA', 'RISCO', 'ANÁLISE'
        ]
        elementos_encontrados = sum(1 for e in elementos_esperados if e in analysis.upper())
        score += (elementos_encontrados / len(elementos_esperados)) * 0.20
        
        # Fator 4: Presença de sinais claros (0-0.2)
        # Sinais de alarme/gravidade aumentam confiança na classificação
        tem_alarmes = len(patient_data.get('sinais_alarme', [])) > 0
        tem_gravidade = len(patient_data.get('sinais_gravidade', [])) > 0
        if tem_alarmes or tem_gravidade:
            score += 0.20  # Quadro mais definido = maior confiança
        else:
            score += 0.10  # Quadro inicial pode ser menos claro
        
        # Converter score em nível
        if score >= 0.80:
            nivel = "ALTA"
        elif score >= 0.60:
            nivel = "MÉDIA"
        else:
            nivel = "BAIXA"
        
        return round(score, 2), nivel
    
    def _should_abstain(
        self, 
        confidence: float,
        patient_data: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Verifica se o sistema deve se abster de dar resposta definitiva
        
        Retorna:
            (deve_abstenir, motivo)
        """
        ABSTENTION_THRESHOLD = 0.50
        
        # Caso 1: Confiança muito baixa
        if confidence < ABSTENTION_THRESHOLD:
            return True, "Informações insuficientes para avaliação confiável"
        
        # Caso 2: Dados essenciais faltando
        if not patient_data.get('idade'):
            return True, "Idade do paciente não informada - essencial para avaliação"
        
        if not patient_data.get('dias_sintomas') and patient_data.get('dias_sintomas') != 0:
            return True, "Tempo de evolução não informado"
        
        # Caso 3: Quadro atípico
        tem_febre = 'febre' in [s.lower() for s in patient_data.get('sintomas', [])]
        tem_alarmes = len(patient_data.get('sinais_alarme', [])) > 0
        
        if not tem_febre and tem_alarmes:
            return True, "Quadro atípico (sinais de alarme sem febre) - avaliação médica necessária"
        
        return False, ""
    
    def _create_patient_summary(self, patient_data: Dict) -> str:
        """Cria resumo do paciente"""
        idade = patient_data.get('idade', '?')
        sexo = patient_data.get('sexo', '?')
        dias = patient_data.get('dias_sintomas', '?')
        
        n_sintomas = len(patient_data.get('sintomas', []))
        n_alarmes = len(patient_data.get('sinais_alarme', []))
        n_gravidade = len(patient_data.get('sinais_gravidade', []))
        
        summary = f"{idade} anos, {sexo}, {dias} dias de sintomas. "
        summary += f"{n_sintomas} sintomas"
        
        if n_alarmes > 0:
            summary += f", {n_alarmes} sinais de alarme"
        
        if n_gravidade > 0:
            summary += f", {n_gravidade} sinais de gravidade"
        
        return summary
    
    def search_similar_cases(self, query: str, k: int = 5) -> List[Dict]:
        """Busca casos similares na base de conhecimento"""
        
        docs = self.vectorstore.similarity_search(query, k=k)
        
        results = []
        for doc in docs:
            results.append({
                'content': doc.page_content,
                'metadata': doc.metadata
            })
        
        return results
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do sistema"""
        
        stats = {
            'total_documents': self.vectorstore._collection.count() if self.vectorstore else 0,
            'embedding_model': self.embedding_model_name,
            'llm_provider': self.llm_provider,
            'vectorstore_path': str(self.vector_store_path)
        }
        
        return stats


def initialize_system(
    knowledge_base_path: str = "./data/knowledge_base.json",
    force_reindex: bool = False
) -> DengueRAGSystem:
    """
    Função auxiliar para inicializar sistema RAG completo
    
    Argumentos:
        knowledge_base_path: Caminho para base de conhecimento
        force_reindex: Se True, recria vector store
        
    Retorna:
        Sistema RAG configurado e pronto para uso
    """
    
    logger.info("Inicializando sistema RAG de triagem de dengue...")
    
    # Criar sistema
    rag_system = DengueRAGSystem(
        knowledge_base_path=knowledge_base_path,
        vector_store_path="./vectorstore",
        embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        llm_provider=os.getenv("LLM_PROVIDER", "openai")
    )
    
    # Configurar componentes
    rag_system.setup_embeddings() \
              .setup_llm() \
              .load_and_index_knowledge(force_reindex=force_reindex) \
              .create_qa_chain()
    
    logger.info("Sistema RAG inicializado com sucesso!")
    
    return rag_system


if __name__ == "__main__":
    # Teste do sistema
    logger.add("logs/rag_system.log", rotation="10 MB")
    
    # Inicializar
    rag = initialize_system(force_reindex=False)
    
    # Testar com caso exemplo
    test_patient = {
        'idade': 35,
        'sexo': 'F',
        'dias_sintomas': 4,
        'sintomas': ['febre', 'cefaleia', 'mialgia', 'náusea'],
        'sinais_alarme': ['vomitos_persistentes', 'dor_abdominal_intensa'],
        'comorbidades': ['hipertensao'],
        'plaquetas': 85000
    }
    
    result = rag.analyze_patient(test_patient)
    
    print("\n=== RESULTADO DA ANÁLISE ===")
    print(f"Risco: {result['risk_level']} ({result['risk_color']})")
    print(f"Confiança: {result['confidence']:.0%}")
    print(f"\nResumo: {result['patient_summary']}")
    print(f"\nAnálise:\n{result['analysis']}")
