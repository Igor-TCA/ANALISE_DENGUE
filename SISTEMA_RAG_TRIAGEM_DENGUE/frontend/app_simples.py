"""
Frontend Streamlit SIMPLIFICADO para Sistema de Triagem de Dengue
FUNCIONA SEM IA - Usa apenas cálculo de score
"""

import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime

# Adicionar path do backend
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from questionario import QuestionarioTriagemDengue, TipoPergunta

# Configuração da página
st.set_page_config(
    page_title="Sistema de Triagem de Dengue",
    page_icon="🦟",
    layout="wide",
)

# CSS customizado
st.markdown("""
<style>
    .risk-critical {
        background-color: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        text-align: center;
        font-size: 1.2rem;
    }
    .risk-high {
        background-color: #ff8800;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        text-align: center;
        font-size: 1.2rem;
    }
    .risk-medium {
        background-color: #ffbb00;
        color: black;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        text-align: center;
        font-size: 1.2rem;
    }
    .risk-low {
        background-color: #00cc66;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        text-align: center;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)


# Inicialização
if 'questionario' not in st.session_state:
    st.session_state.questionario = QuestionarioTriagemDengue()

if 'resultado' not in st.session_state:
    st.session_state.resultado = None


def renderizar_pergunta(pergunta):
    """Renderiza uma pergunta do questionário"""
    
    # Verificar condição
    if pergunta.condicao:
        var_name = pergunta.condicao.split('==')[0].strip()
        resposta_previa = st.session_state.questionario.respostas.get(var_name)
        if not resposta_previa:
            return None
    
    label = pergunta.texto
    if not pergunta.obrigatoria:
        label += " (opcional)"
    
    # Renderizar por tipo
    if pergunta.tipo == TipoPergunta.SIM_NAO:
        resposta = st.radio(
            label,
            options=['Não', 'Sim'],
            key=pergunta.id,
            help=pergunta.ajuda,
            horizontal=True
        )
        return resposta == 'Sim'
    
    elif pergunta.tipo == TipoPergunta.NUMERO:
        resposta = st.number_input(
            label,
            min_value=pergunta.valor_min,
            max_value=pergunta.valor_max,
            key=pergunta.id,
            help=pergunta.ajuda
        )
        return resposta
    
    elif pergunta.tipo == TipoPergunta.SELECAO_UNICA:
        resposta = st.selectbox(
            label,
            options=[''] + pergunta.opcoes,
            key=pergunta.id,
            help=pergunta.ajuda
        )
        return resposta if resposta != '' else None
    
    return None


def main():
    """Função principal"""
    
    # Header
    st.title("🦟 Sistema de Triagem de Dengue")
    st.markdown("### Sistema de Avaliação de Risco")
    
    # Sidebar
    with st.sidebar:
        st.title("Menu")
        
        if st.button("🔄 Nova Triagem", use_container_width=True):
            st.session_state.questionario = QuestionarioTriagemDengue()
            st.session_state.resultado = None
            st.rerun()
        
        st.divider()
        st.info("💡 Sistema funcionando em modo básico (sem IA)")
    
    # Se já tem resultado, mostrar
    if st.session_state.resultado:
        mostrar_resultado()
        return
    
    # Questionário
    st.header("Questionário de Triagem")
    
    questionario = st.session_state.questionario
    secoes = questionario.obter_secoes()
    
    # Tabs para cada seção
    tabs = st.tabs([nome.replace('_', ' ').title() for nome in secoes])
    
    for idx, secao in enumerate(secoes):
        with tabs[idx]:
            st.subheader(secao.replace("_", " ").title())
            
            perguntas = questionario.obter_perguntas_secao(secao)
            
            for pergunta in perguntas:
                resposta = renderizar_pergunta(pergunta)
                
                if resposta is not None:
                    try:
                        questionario.registrar_resposta(pergunta.id, resposta)
                    except Exception as e:
                        st.error(f"Erro: {e}")
    
    # Botão de análise
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔍 Analisar Paciente", use_container_width=True, type="primary"):
            realizar_analise()


def realizar_analise():
    """Realiza análise do paciente"""
    
    questionario = st.session_state.questionario
    
    # Calcular risco
    risco = questionario.classificar_risco()
    dados = questionario.gerar_dados_paciente()
    
    st.session_state.resultado = {
        'risco': risco,
        'dados': dados,
        'timestamp': datetime.now().isoformat()
    }
    
    st.success("✅ Análise concluída!")
    st.rerun()


def mostrar_resultado():
    """Mostra resultado da análise"""
    
    st.header("📊 Resultado da Triagem")
    
    resultado = st.session_state.resultado
    risco = resultado['risco']
    dados = resultado['dados']
    
    # Classificação de risco
    nivel = risco['nivel']
    
    if nivel == 'CRÍTICO':
        st.markdown(f'<div class="risk-critical">🚨 RISCO {nivel} 🚨<br>Score: {risco["score"]}</div>', 
                   unsafe_allow_html=True)
    elif nivel == 'ALTO':
        st.markdown(f'<div class="risk-high">⚠️ RISCO {nivel} ⚠️<br>Score: {risco["score"]}</div>', 
                   unsafe_allow_html=True)
    elif nivel == 'MÉDIO':
        st.markdown(f'<div class="risk-medium">⚡ RISCO {nivel}<br>Score: {risco["score"]}</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="risk-low">✅ RISCO {nivel}<br>Score: {risco["score"]}</div>', 
                   unsafe_allow_html=True)
    
    st.info(f"**Conduta Recomendada:** {risco['acao']}")
    
    st.divider()
    
    # Resumo do paciente
    st.subheader("📋 Resumo do Paciente")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Idade", f"{dados.get('idade', '?')} anos")
    
    with col2:
        st.metric("Sexo", dados.get('sexo', '?'))
    
    with col3:
        st.metric("Dias de Sintomas", dados.get('dias_sintomas', '?'))
    
    st.divider()
    
    # Detalhes clínicos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🩺 Apresentação Clínica")
        
        if dados['sintomas']:
            st.write("**Sintomas:**")
            for sintoma in dados['sintomas']:
                st.write(f"✓ {sintoma.title()}")
        
        if dados['sinais_alarme']:
            st.write("**⚠️ Sinais de Alarme:**")
            for sinal in dados['sinais_alarme']:
                st.warning(f"⚠️ {sinal.title()}")
        
        if dados['sinais_gravidade']:
            st.write("**🚨 Sinais de Gravidade:**")
            for sinal in dados['sinais_gravidade']:
                st.error(f"🚨 {sinal.title()}")
    
    with col2:
        st.subheader("🏥 Informações Adicionais")
        
        if dados['comorbidades']:
            st.write("**Comorbidades:**")
            for comorb in dados['comorbidades']:
                st.write(f"• {comorb.title()}")
        
        if 'plaquetas' in dados:
            plaq = dados['plaquetas']
            if plaq < 100000:
                st.error(f"**Plaquetas:** {plaq:,}/mm³ (BAIXO)")
            elif plaq < 150000:
                st.warning(f"**Plaquetas:** {plaq:,}/mm³ (Limítrofe)")
            else:
                st.success(f"**Plaquetas:** {plaq:,}/mm³ (Normal)")
        
        if 'hematocrito' in dados:
            st.write(f"**Hematócrito:** {dados['hematocrito']}%")
    
    st.divider()
    
    # Informação sobre IA
    st.info("💡 **Modo Básico**: Este resultado foi calculado usando algoritmo de score. Para análise com IA, configure as chaves de API no arquivo .env")


if __name__ == "__main__":
    main()
