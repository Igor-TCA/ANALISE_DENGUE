"""
Script para executar o sistema de triagem
"""

import subprocess
import sys
import os
from pathlib import Path

def check_setup():
    """Verifica se o setup foi executado"""
    kb_path = Path("data/knowledge_base.json")
    
    if not kb_path.exists():
        print("❌ Sistema não inicializado!")
        print("\nPor favor, execute primeiro:")
        print("  python setup.py")
        return False
    
    return True

def check_env():
    """Verifica se .env existe"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("⚠️  Arquivo .env não encontrado!")
        print("\nPara habilitar IA:")
        print("  1. Copie .env.example para .env")
        print("  2. Adicione suas chaves de API")
        print("\nO sistema funcionará com funcionalidade limitada.")
        
        resposta = input("\nContinuar mesmo assim? (s/n): ")
        return resposta.lower() == 's'
    
    return True

def main():
    print("=" * 60)
    print("🦟 SISTEMA DE TRIAGEM DE DENGUE")
    print("=" * 60)
    print()
    
    # Verificar setup
    if not check_setup():
        sys.exit(1)
    
    # Verificar .env
    if not check_env():
        sys.exit(1)
    
    # Executar Streamlit
    print("\n🚀 Iniciando aplicação...")
    print("📱 A aplicação abrirá no navegador automaticamente")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Para encerrar: Pressione Ctrl+C\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "frontend/app.py",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n\n✅ Aplicação encerrada com sucesso!")

if __name__ == "__main__":
    main()
