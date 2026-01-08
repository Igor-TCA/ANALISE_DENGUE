"""
Sistema RAG (Retrieval-Augmented Generation) para Triagem de Dengue
Utiliza embeddings e LLM para análise de casos clínicos
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
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
        
        Args:
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
        
        # Template de prompt especializado para triagem médica
        prompt_template = """Você é um sistema especialista em triagem de dengue, treinado com milhares de casos reais do SINAN/DATASUS.

Sua função é analisar informações clínicas de pacientes e determinar o risco de evolução para formas graves de dengue, baseando-se em:
- Padrões epidemiológicos identificados em casos reais
- Fatores de risco conhecidos (idade, comorbidades, sinais de alarme)
- Progressão temporal típica da doença

Contexto de casos similares da base de dados:
{context}

Informações do paciente atual:
{question}

IMPORTANTE:
- Seja preciso e baseie-se nos dados epidemiológicos fornecidos
- Identifique sinais de alarme e fatores de risco
- Classifique o risco como: BAIXO, MÉDIO, ALTO ou CRÍTICO
- Forneça recomendações claras de conduta
- Use linguagem técnica mas acessível para enfermeiros
- Destaque urgência quando necessário

Análise e recomendação:"""

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
        
        Args:
            patient_data: Dicionário com dados do paciente
            
        Returns:
            Dicionário com análise, classificação de risco e recomendações
        """
        
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
        
        # Montar resposta estruturada
        response = {
            'analysis': analysis,
            'risk_level': risk_level,
            'risk_color': self._get_risk_color(risk_level),
            'similar_cases': self._format_similar_cases(source_docs),
            'confidence': self._calculate_confidence(source_docs),
            'patient_summary': self._create_patient_summary(patient_data)
        }
        
        logger.info(f"Análise concluída - Risco: {risk_level}")
        
        return response
    
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
            query_parts.append(f"⚠️ SINAIS DE ALARME: {', '.join(alarmes)}")
        
        # Sinais de gravidade
        gravidade = patient_data.get('sinais_gravidade', [])
        if gravidade:
            query_parts.append(f"🚨 SINAIS DE GRAVIDADE: {', '.join(gravidade)}")
        
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
        """Formata casos similares encontrados"""
        similar = []
        
        for doc in source_docs[:3]:  # Top 3 casos mais similares
            similar.append({
                'content': doc.page_content[:200] + "...",
                'metadata': doc.metadata
            })
        
        return similar
    
    def _calculate_confidence(self, source_docs: List[Document]) -> float:
        """Calcula confiança baseada em documentos recuperados"""
        # Simplificado: baseado no número de documentos relevantes encontrados
        if len(source_docs) >= 5:
            return 0.9
        elif len(source_docs) >= 3:
            return 0.75
        elif len(source_docs) >= 1:
            return 0.6
        else:
            return 0.4
    
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
    Função helper para inicializar sistema RAG completo
    
    Args:
        knowledge_base_path: Caminho para base de conhecimento
        force_reindex: Se True, recria vector store
        
    Returns:
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
