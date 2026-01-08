"""
Script Rápido para Executar Sistema de Triagem
Execute este arquivo para iniciar o sistema imediatamente
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("=" * 60)
    print("🦟 SISTEMA DE TRIAGEM DE DENGUE")
    print("=" * 60)
    print()
    
    # Verificar se está na pasta correta
    if not Path("frontend/app.py").exists():
        print("❌ Erro: Execute este script da pasta SISTEMA_RAG_TRIAGEM_DENGUE")
        sys.exit(1)
    
    print("✅ Sistema encontrado!")
    print()
    print("📱 Abrindo interface web...")
    print("🔗 URL: http://localhost:8501")
    print()
    print("💡 IMPORTANTE:")
    print("   - Este sistema funciona SEM chaves de API")
    print("   - Para análise com IA, configure .env com sua chave")
    print("   - Funcionalidade básica disponível sem IA")
    print()
    print("🔧 Para encerrar: Pressione Ctrl+C")
    print("=" * 60)
    print()
    
    try:
        # Executar Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "frontend/app.py",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n✅ Sistema encerrado!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\nTente executar manualmente:")
        print(f"  {sys.executable} -m streamlit run frontend/app.py")

if __name__ == "__main__":
    main()
