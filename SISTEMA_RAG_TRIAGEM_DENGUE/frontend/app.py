"""
Frontend Streamlit para Sistema de Triagem de Dengue com IA
Interface interativa para enfermeiros realizarem triagem de pacientes
"""

import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Adicionar path do backend
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from questionario import QuestionarioTriagemDengue, TipoPergunta

# Importar analisador local (sempre disponível)
IA_AVAILABLE = False
try:
    from local_analyzer import initialize_local_analyzer
    IA_AVAILABLE = True
except ImportError:
    initialize_local_analyzer = None

# Configuração da página
st.set_page_config(
    page_title="Sistema de Triagem de Dengue",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .stAlert > div {
        padding: 1rem;
        border-radius: 0.5rem;
    }
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
    .section-header {
        background-color: #262730;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
        margin: 1rem 0;
        color: #fafafa;
    }
    .section-header h3 {
        color: #fafafa !important;
    }
</style>
""", unsafe_allow_html=True)


# Inicialização do session state
if 'questionario' not in st.session_state:
    st.session_state.questionario = QuestionarioTriagemDengue()

if 'ia_system' not in st.session_state:
    st.session_state.ia_system = None
    st.session_state.ia_loaded = False

if 'analise_completa' not in st.session_state:
    st.session_state.analise_completa = None

if 'historico' not in st.session_state:
    st.session_state.historico = []

if 'show_save_dialog' not in st.session_state:
    st.session_state.show_save_dialog = False

if 'nav_to_resultado' not in st.session_state:
    st.session_state.nav_to_resultado = False

# Carregar IA automaticamente no início
if IA_AVAILABLE and not st.session_state.ia_loaded:
    try:
        data_path = Path(__file__).parent.parent / 'data'
        st.session_state.ia_system = initialize_local_analyzer(
            knowledge_base_path=str(data_path)
        )
        st.session_state.ia_loaded = True
    except Exception as e:
        st.session_state.ia_loaded = False


def carregar_ia_system():
    """Carrega sistema de IA (lazy loading)"""
    if not IA_AVAILABLE:
        st.warning("Sistema de IA não disponível.")
        return False
    
    if not st.session_state.ia_loaded:
        data_path = Path(__file__).parent.parent / 'data'
        with st.spinner('Inicializando sistema de inteligência artificial...'):
            try:
                st.session_state.ia_system = initialize_local_analyzer(
                    knowledge_base_path=str(data_path)
                )
                st.session_state.ia_loaded = True
                return True
            except Exception as e:
                st.error(f"Erro ao carregar sistema de IA: {e}")
                return False
    return True


def renderizar_pergunta(pergunta):
    """Renderiza uma pergunta do questionário"""
    
    # Verificar condição
    if pergunta.condicao:
        # Simplificado: apenas verificar se variável referenciada é True
        var_name = pergunta.condicao.split('==')[0].strip()
        resposta_previa = st.session_state.questionario.respostas.get(var_name)
        
        if not resposta_previa:
            return None
    
    # Label com ajuda se disponível
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
    
    elif pergunta.tipo == TipoPergunta.SELECAO_MULTIPLA:
        resposta = st.multiselect(
            label,
            options=pergunta.opcoes,
            key=pergunta.id,
            help=pergunta.ajuda
        )
        return resposta if resposta else None
    
    elif pergunta.tipo == TipoPergunta.TEXTO:
        resposta = st.text_input(
            label,
            key=pergunta.id,
            help=pergunta.ajuda
        )
        return resposta if resposta != '' else None
    
    return None


def exibir_classificacao_risco(risco_info):
    """Exibe classificação de risco com cores"""
    nivel = risco_info['nivel']
    
    if nivel == 'CRÍTICO':
        st.markdown(f'<div class="risk-critical">🚨 RISCO {nivel} 🚨<br>Score: {risco_info["score"]}</div>', 
                   unsafe_allow_html=True)
    elif nivel == 'ALTO':
        st.markdown(f'<div class="risk-high">⚠️ RISCO {nivel} ⚠️<br>Score: {risco_info["score"]}</div>', 
                   unsafe_allow_html=True)
    elif nivel == 'MÉDIO':
        st.markdown(f'<div class="risk-medium">⚡ RISCO {nivel}<br>Score: {risco_info["score"]}</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="risk-low">✅ RISCO {nivel}<br>Score: {risco_info["score"]}</div>', 
                   unsafe_allow_html=True)
    
    st.info(f"**Conduta Recomendada:** {risco_info['acao']}")


def criar_grafico_risco(score):
    """Cria gráfico gauge do score de risco"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Score de Risco"},
        gauge={
            'axis': {'range': [None, 20]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 3], 'color': "#00cc66"},
                {'range': [3, 6], 'color': "#ffbb00"},
                {'range': [6, 10], 'color': "#ff8800"},
                {'range': [10, 20], 'color': "#ff4444"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig


def criar_grafico_sintomas(dados_paciente):
    """Cria gráfico de sintomas presentes"""
    categorias = []
    contagens = []
    
    if dados_paciente['sintomas']:
        categorias.append('Sintomas')
        contagens.append(len(dados_paciente['sintomas']))
    
    if dados_paciente['sinais_alarme']:
        categorias.append('Sinais de Alarme')
        contagens.append(len(dados_paciente['sinais_alarme']))
    
    if dados_paciente['sinais_gravidade']:
        categorias.append('Sinais de Gravidade')
        contagens.append(len(dados_paciente['sinais_gravidade']))
    
    if dados_paciente['comorbidades']:
        categorias.append('Comorbidades')
        contagens.append(len(dados_paciente['comorbidades']))
    
    fig = px.bar(
        x=categorias,
        y=contagens,
        title="Resumo Clínico do Paciente",
        labels={'x': 'Categoria', 'y': 'Quantidade'},
        color=contagens,
        color_continuous_scale=['green', 'yellow', 'orange', 'red']
    )
    
    fig.update_layout(showlegend=False, height=300)
    return fig


def main():
    """Função principal do app"""
    
    # Header
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.title("🦟 Sistema de Triagem de Dengue")
        st.markdown("### Sistema Inteligente com IA para Avaliação de Risco")
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/mosquito.png", width=80)
        st.title("Menu")
        
        pagina = st.radio(
            "Navegação",
            ["📝 Nova Triagem", "📊 Resultado", "📚 Histórico", "ℹ️ Sobre"]
        )
        
        st.divider()
        
        # Informações do sistema
        st.subheader("Status do Sistema")
        if st.session_state.ia_loaded:
            st.success("✅ IA Ativa")
        else:
            st.warning("⏳ IA Desativada")
        
        st.info(f"Triagens hoje: {len(st.session_state.historico)}")
        
        st.divider()
        
        # Botão para limpar
        if st.button("🔄 Nova Triagem", use_container_width=True):
            st.session_state.questionario = QuestionarioTriagemDengue()
            st.session_state.analise_completa = None
            st.session_state.show_save_dialog = False
            st.session_state.nav_to_resultado = False
            st.rerun()
    
    # Verificar navegação automática para resultado
    if st.session_state.nav_to_resultado:
        st.session_state.nav_to_resultado = False
        pagina_resultado()
        return
    
    # Páginas
    if pagina == "📝 Nova Triagem":
        pagina_triagem()
    elif pagina == "📊 Resultado":
        pagina_resultado()
    elif pagina == "📚 Histórico":
        pagina_historico()
    elif pagina == "ℹ️ Sobre":
        pagina_sobre()


def pagina_triagem():
    """Página de triagem do paciente"""
    
    # Diálogo de confirmação para salvar antes de sair
    if st.session_state.show_save_dialog:
        st.warning("⚠️ Você tem uma triagem não salva!")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Salvar e Ver Resultados", use_container_width=True, type="primary"):
                registrar_triagem()
                st.session_state.show_save_dialog = False
                st.session_state.nav_to_resultado = True
                st.rerun()
        with col2:
            if st.button("🚫 Não Salvar", use_container_width=True):
                st.session_state.show_save_dialog = False
                st.session_state.nav_to_resultado = True
                st.rerun()
        with col3:
            if st.button("↩️ Cancelar", use_container_width=True):
                st.session_state.show_save_dialog = False
                st.rerun()
        return
    
    st.header("Questionário de Triagem")
    
    questionario = st.session_state.questionario
    secoes = questionario.obter_secoes()
    
    # Tabs para cada seção
    tabs = st.tabs([nome.replace('_', ' ').title() for nome in secoes])
    
    for idx, secao in enumerate(secoes):
        with tabs[idx]:
            st.markdown(f'<div class="section-header"><h3>{secao.replace("_", " ").title()}</h3></div>', 
                       unsafe_allow_html=True)
            
            perguntas = questionario.obter_perguntas_secao(secao)
            
            for pergunta in perguntas:
                resposta = renderizar_pergunta(pergunta)
                
                if resposta is not None:
                    try:
                        questionario.registrar_resposta(pergunta.id, resposta)
                    except Exception as e:
                        st.error(f"Erro: {e}")
            
            st.divider()
    
    # Botões de ação
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("💾 Registrar Triagem", use_container_width=True, type="primary"):
            registrar_triagem()
    
    with col2:
        if st.button("📊 Visualizar Resultados", use_container_width=True):
            visualizar_resultados()
    
    with col3:
        if st.button("🔄 Limpar Formulário", use_container_width=True):
            st.session_state.questionario = QuestionarioTriagemDengue()
            st.session_state.analise_completa = None
            st.rerun()


def registrar_triagem():
    """Registra a triagem e realiza análise com IA"""
    
    questionario = st.session_state.questionario
    
    # Verificar perguntas obrigatórias
    perguntas_faltando = []
    for pergunta in questionario.perguntas:
        if pergunta.obrigatoria and pergunta.id not in questionario.respostas:
            perguntas_faltando.append(pergunta.texto)
    
    if perguntas_faltando:
        st.error(f"Por favor, responda todas as perguntas obrigatórias:")
        for p in perguntas_faltando[:5]:
            st.write(f"- {p}")
        return
    
    with st.spinner('Registrando triagem e analisando com IA...'):
        # Classificação por score
        risco_score = questionario.classificar_risco()
        
        # Preparar dados para análise
        dados_paciente = questionario.gerar_dados_paciente()
        
        # Análise com IA
        analise_ia = None
        if carregar_ia_system() and st.session_state.ia_system:
            try:
                analise_ia = st.session_state.ia_system.analyze_patient(dados_paciente)
            except Exception as e:
                st.warning(f"Erro na análise de IA: {e}")
        
        # Consolidar análise
        st.session_state.analise_completa = {
            'timestamp': datetime.now().isoformat(),
            'risco_score': risco_score,
            'dados_paciente': dados_paciente,
            'analise_ia': analise_ia,
            'respostas_completas': questionario.respostas.copy(),
            'registrada': True
        }
        
        # Adicionar ao histórico
        st.session_state.historico.append(st.session_state.analise_completa)
        
        st.success("✅ Triagem registrada com sucesso!")
        st.balloons()


def visualizar_resultados():
    """Visualiza resultados - pergunta se deseja salvar antes se não foi registrada"""
    
    questionario = st.session_state.questionario
    
    # Verificar se há respostas não salvas
    tem_respostas = len(questionario.respostas) > 0
    ja_registrada = st.session_state.analise_completa is not None and st.session_state.analise_completa.get('registrada', False)
    
    if tem_respostas and not ja_registrada:
        # Mostrar diálogo de confirmação
        st.session_state.show_save_dialog = True
        st.rerun()
    else:
        # Ir direto para resultados
        st.session_state.nav_to_resultado = True
        st.rerun()


def realizar_analise():
    """Realiza análise completa do paciente (mantida para compatibilidade)"""
    registrar_triagem()


def pagina_resultado():
    """Página de resultado da análise"""
    
    if st.session_state.analise_completa is None:
        st.warning("⚠️ Nenhuma análise disponível. Por favor, realize uma triagem primeiro.")
        return
    
    analise = st.session_state.analise_completa
    risco = analise['risco_score']
    dados = analise['dados_paciente']
    
    st.header("📊 Resultado da Triagem")
    
    # Linha 1: Classificação de risco e gauge
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Classificação de Risco")
        exibir_classificacao_risco(risco)
    
    with col2:
        st.plotly_chart(criar_grafico_risco(risco['score']), use_container_width=True)
    
    st.divider()
    
    # Linha 2: Resumo do paciente
    st.subheader("📋 Resumo do Paciente")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Idade", f"{dados.get('idade', '?')} anos")
    
    with col2:
        st.metric("Sexo", dados.get('sexo', '?'))
    
    with col3:
        st.metric("Dias de Sintomas", dados.get('dias_sintomas', '?'))
    
    with col4:
        gestante = "Sim" if dados.get('gestante') else "Não"
        st.metric("Gestante", gestante)
    
    st.divider()
    
    # Linha 3: Detalhes clínicos
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
            cor = "red" if plaq < 100000 else "orange" if plaq < 150000 else "green"
            st.write(f"**Plaquetas:** :{cor}[{plaq:,}/mm³]")
        
        if 'hematocrito' in dados:
            st.write(f"**Hematócrito:** {dados['hematocrito']}%")
    
    st.plotly_chart(criar_grafico_sintomas(dados), use_container_width=True)
    
    st.divider()
    
    # Linha 4: Análise da IA
    if analise.get('analise_ia'):
        st.subheader("🤖 Análise da Inteligência Artificial")
        
        ia = analise['analise_ia']
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Exibir análise formatada
            st.markdown(ia.get('analise', 'Análise não disponível'))
        
        with col2:
            st.metric("Classificação", ia.get('classificacao', 'N/A'))
            st.metric("Nível de Risco", ia.get('nivel_risco', 'N/A'))
            confianca = ia.get('confianca', (0, 'N/A'))
            if isinstance(confianca, tuple):
                st.metric("Confiança", f"{confianca[0]:.0%} ({confianca[1]})")
            else:
                st.metric("Confiança", str(confianca))
        
        # Conduta recomendada
        if ia.get('conduta'):
            with st.expander("📝 Conduta Recomendada", expanded=True):
                conduta = ia['conduta']
                st.write(f"**Local:** {conduta.get('local', 'N/A')}")
                st.write(f"**Prioridade:** {conduta.get('prioridade', 'N/A')}")
                st.write(f"**Hidratação:** {conduta.get('hidratacao', 'N/A')}")
                st.write(f"**Exames:** {conduta.get('exames', 'N/A')}")
                st.write(f"**Reavaliação:** {conduta.get('reavaliacao', 'N/A')}")
                if conduta.get('orientacoes'):
                    st.write("**Orientações:**")
                    for o in conduta['orientacoes']:
                        st.write(f"- {o}")
        
        # Fatores de risco identificados
        if ia.get('fatores_risco'):
            with st.expander("⚠️ Fatores de Risco Identificados"):
                for fator in ia['fatores_risco']:
                    st.write(f"**{fator.get('fator', 'N/A')}** - Impacto: {fator.get('impacto', 'N/A')}")
                    st.write(f"_{fator.get('descricao', '')}_")
                    st.divider()
        
        # Citações/Referências
        if ia.get('citacoes'):
            with st.expander("📚 Referências"):
                for cit in ia['citacoes']:
                    st.write(f"- **{cit.get('fonte', 'N/A')}**: {cit.get('documento', '')} ({cit.get('ano', '')})")
    
    else:
        st.info("💡 Registre a triagem para obter análise completa com IA.")
    
    st.divider()
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Gerar Relatório PDF", use_container_width=True):
            st.info("Funcionalidade em desenvolvimento")
    
    with col2:
        if st.button("📧 Enviar por Email", use_container_width=True):
            st.info("Funcionalidade em desenvolvimento")
    
    with col3:
        if st.button("💾 Salvar no Sistema", use_container_width=True):
            salvar_triagem()


def salvar_triagem():
    """Salva triagem em arquivo"""
    if st.session_state.analise_completa:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"triagem_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.analise_completa, f, ensure_ascii=False, indent=2)
        
        st.success(f"✅ Triagem salva: {filename}")


def pagina_historico():
    """Página de histórico de triagens"""
    
    st.header("📚 Histórico de Triagens")
    
    if not st.session_state.historico:
        st.info("Nenhuma triagem realizada ainda.")
        return
    
    st.write(f"Total de triagens: {len(st.session_state.historico)}")
    
    # Estatísticas
    col1, col2, col3, col4 = st.columns(4)
    
    niveis = [h['risco_score']['nivel'] for h in st.session_state.historico]
    
    with col1:
        st.metric("Risco Baixo", niveis.count('BAIXO'))
    with col2:
        st.metric("Risco Médio", niveis.count('MÉDIO'))
    with col3:
        st.metric("Risco Alto", niveis.count('ALTO'))
    with col4:
        st.metric("Risco Crítico", niveis.count('CRÍTICO'))
    
    st.divider()
    
    # Lista de triagens
    for idx, triagem in enumerate(reversed(st.session_state.historico), 1):
        with st.expander(f"Triagem {len(st.session_state.historico) - idx + 1} - {triagem['timestamp'][:19]}"):
            risco = triagem['risco_score']
            dados = triagem['dados_paciente']
            
            st.write(f"**Risco:** {risco['nivel']} (Score: {risco['score']})")
            st.write(f"**Paciente:** {dados.get('idade')} anos, {dados.get('sexo')}")
            st.write(f"**Sintomas:** {len(dados['sintomas'])}")
            st.write(f"**Sinais de alarme:** {len(dados['sinais_alarme'])}")
            st.write(f"**Sinais de gravidade:** {len(dados['sinais_gravidade'])}")


def pagina_sobre():
    """Página sobre o sistema"""
    
    st.header("ℹ️ Sobre o Sistema")
    
    st.markdown("""
    ## Sistema RAG de Triagem de Dengue
    
    ### 🎯 Objetivo
    Este sistema utiliza **Inteligência Artificial** e **RAG (Retrieval-Augmented Generation)** 
    para auxiliar enfermeiros na triagem e avaliação de risco de pacientes com suspeita de dengue.
    
    ### 🧠 Tecnologia
    - **Base de Conhecimento**: Treinado com dados reais do SINAN/DATASUS
    - **RAG**: Recuperação de casos similares para contextualizar análise
    - **Embeddings**: Sentence Transformers para busca semântica
    - **Vector Store**: ChromaDB para armazenamento eficiente
    
    ### 📊 Funcionalidades
    - ✅ Questionário estruturado baseado em protocolos do Ministério da Saúde
    - ✅ Cálculo automático de score de risco
    - ✅ Análise por IA com casos similares da base de dados
    - ✅ Classificação em 4 níveis: Baixo, Médio, Alto, Crítico
    - ✅ Recomendações de conduta
    - ✅ Histórico de triagens
    
    ### ⚕️ Classificação de Risco
    
    **🟢 BAIXO (Score < 3)**
    - Dengue sem sinais de alarme
    - Tratamento ambulatorial
    - Orientações e retorno se piora
    
    **🟡 MÉDIO (Score 3-6)**
    - Dengue com fatores de risco
    - Monitoramento intensivo
    - Reavaliação em 24h
    
    **🟠 ALTO (Score 6-10)**
    - Dengue com sinais de alarme
    - Avaliação médica urgente
    - Considerar internação
    
    **🔴 CRÍTICO (Score > 10)**
    - Dengue grave
    - ATENDIMENTO IMEDIATO
    - Encaminhar para emergência

    
    ### ⚠️ Importante
    Este sistema é uma ideia de **ferramenta de apoio** à decisão clínica. A avaliação médica 
    presencial permanece essencial para o diagnóstico e tratamento adequados.
    
    ---
    
    **Versão**: 1.0.0  
    **Data**: Janeiro 2026
    """)
    
    st.divider()
    
    st.subheader("📖 Referências")
    st.markdown("""
    - Ministério da Saúde - Diretrizes Nacionais para Prevenção e Controle de Epidemias de Dengue
    - DATASUS - Sistema de Informação de Agravos de Notificação (SINAN)
    - OMS - Dengue: Guidelines for Diagnosis, Treatment, Prevention and Control
    """)


if __name__ == "__main__":
    main()
