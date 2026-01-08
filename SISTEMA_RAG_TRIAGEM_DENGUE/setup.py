"""
Script de Inicialização do Sistema
Processa dados e cria base de conhecimento para o sistema RAG
"""

import sys
from pathlib import Path
from loguru import logger

# Configurar logging
logger.add("logs/setup.log", rotation="10 MB", level="INFO")

def main():
    """Script principal de setup"""
    
    logger.info("=" * 60)
    logger.info("INICIANDO SETUP DO SISTEMA DE TRIAGEM DE DENGUE")
    logger.info("=" * 60)
    
    # 1. Verificar arquivos necessários
    logger.info("\n[1/4] Verificando arquivos necessários...")
    
    data_file = Path("../DENGBR25.csv")
    if not data_file.exists():
        logger.error(f"Arquivo de dados não encontrado: {data_file}")
        logger.error("Por favor, certifique-se de que DENGBR25.csv está no diretório pai")
        return False
    
    logger.success("✓ Arquivo de dados encontrado")
    
    # 2. Processar dados
    logger.info("\n[2/4] Processando dados do SINAN...")
    
    try:
        from backend.data_processor import DengueDataProcessor
        
        processor = DengueDataProcessor(str(data_file))
        processor.load_data() \
                 .clean_data() \
                 .extract_severe_cases() \
                 .create_knowledge_documents() \
                 .save_knowledge_base("data/knowledge_base.json")
        
        # Relatório
        report = processor.generate_statistics_report()
        logger.info("\n--- Estatísticas de Processamento ---")
        for key, value in report.items():
            logger.info(f"{key}: {value}")
        
        logger.success("✓ Dados processados com sucesso")
    
    except Exception as e:
        logger.error(f"✗ Erro ao processar dados: {e}")
        return False
    
    # 3. Criar vector store
    logger.info("\n[3/4] Criando vector store (embeddings)...")
    
    try:
        from backend.rag_system import initialize_system
        
        rag_system = initialize_system(
            knowledge_base_path="data/knowledge_base.json",
            force_reindex=True
        )
        
        stats = rag_system.get_statistics()
        logger.info("\n--- Estatísticas do Vector Store ---")
        for key, value in stats.items():
            logger.info(f"{key}: {value}")
        
        logger.success("✓ Vector store criado com sucesso")
    
    except Exception as e:
        logger.error(f"✗ Erro ao criar vector store: {e}")
        logger.warning("Sistema pode funcionar sem IA, mas com funcionalidade limitada")
    
    # 4. Verificar dependências
    logger.info("\n[4/4] Verificando dependências...")
    
    try:
        import pandas
        import streamlit
        import langchain
        import chromadb
        
        logger.success("✓ Todas as dependências instaladas")
    
    except ImportError as e:
        logger.error(f"✗ Dependência faltando: {e}")
        logger.error("Execute: pip install -r requirements.txt")
        return False
    
    # Finalização
    logger.info("\n" + "=" * 60)
    logger.success("SETUP CONCLUÍDO COM SUCESSO!")
    logger.info("=" * 60)
    logger.info("\nPróximos passos:")
    logger.info("1. Configure as chaves de API no arquivo .env")
    logger.info("2. Execute o sistema: streamlit run frontend/app.py")
    logger.info("\nPara mais informações, consulte README.md")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
