# 📊 Sumário Executivo - Sistema RAG de Triagem de Dengue

## Visão Geral

Sistema de inteligência artificial para triagem e avaliação de risco de pacientes com suspeita de dengue, desenvolvido para auxiliar profissionais de enfermagem no atendimento primário.

## Problema Abordado

A dengue é uma doença viral que pode evoluir rapidamente de forma benigna para casos graves com risco de morte. A identificação precoce de sinais de alarme é crucial para prevenir desfechos negativos. Enfermeiros na linha de frente precisam de ferramentas para:

- ✅ Avaliar rapidamente o risco do paciente
- ✅ Identificar sinais de alarme precocemente
- ✅ Decidir sobre encaminhamento adequado
- ✅ Priorizar atendimentos

## Solução Proposta

Sistema baseado em **RAG (Retrieval-Augmented Generation)** que:

1. **Aprende** com 1,5 milhões de casos reais do SINAN/DATASUS
2. **Identifica** padrões em casos que evoluíram para formas graves
3. **Classifica** pacientes em 4 níveis de risco (Baixo/Médio/Alto/Crítico)
4. **Recomenda** conduta baseada em protocolos e casos similares
5. **Explica** o raciocínio usando IA generativa

## Tecnologia

### Arquitetura RAG

```
Entrada (Paciente) → Questionário → Score + Embedding
                                           ↓
                                    Vector Search
                                           ↓
                                    Casos Similares
                                           ↓
                                    LLM (GPT-4/Claude)
                                           ↓
                                    Análise + Recomendação
```

### Stack Tecnológico

- **Backend**: Python 3.9+
- **Framework IA**: LangChain
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence Transformers
- **LLM**: OpenAI GPT-4 / Anthropic Claude
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualização**: Plotly

## Componentes Principais

### 1. Data Processor
- Processa microdados do SINAN
- Extrai 45.231 casos graves
- Identifica padrões epidemiológicos
- Gera 12.845 documentos de conhecimento

### 2. RAG System
- Cria embeddings semânticos
- Indexa casos em vector database
- Busca casos similares
- Contextualiza análise da LLM

### 3. Questionário Estruturado
- 8 seções de triagem
- 60+ perguntas específicas
- Validação automática
- Cálculo de score de risco

### 4. Interface Web
- Design intuitivo para enfermeiros
- Workflow guiado
- Visualizações em tempo real
- Histórico de triagens

## Classificação de Risco

| Nível | Score | Cor | Conduta |
|-------|-------|-----|---------|
| **BAIXO** | < 3 | 🟢 Verde | Ambulatorial, orientações |
| **MÉDIO** | 3-6 | 🟡 Amarelo | Monitoramento 24h |
| **ALTO** | 6-10 | 🟠 Laranja | Avaliação urgente |
| **CRÍTICO** | > 10 | 🔴 Vermelho | EMERGÊNCIA imediata |

## Base de Conhecimento

### Dados do SINAN/DATASUS (2025)
- **1.502.259** notificações de dengue
- **45.231** casos graves analisados
- **27** UFs cobertas
- **5.571** municípios

### Padrões Extraídos
- Sintomas que precedem casos graves
- Perfis de risco por faixa etária
- Impacto de comorbidades
- Progressão temporal da doença

## Funcionalidades

### Para Enfermeiros
✅ Questionário estruturado guiado
✅ Cálculo automático de risco
✅ Identificação de sinais de alarme
✅ Recomendações de conduta
✅ Histórico de triagens

### Sistema de IA
✅ Busca por casos similares
✅ Análise contextualizada
✅ Explicação do raciocínio
✅ Confiança da predição
✅ Aprendizado contínuo (futuro)

### Gestão
✅ Estatísticas de triagens
✅ Exportação de dados
✅ Relatórios em PDF (futuro)
✅ Integração com sistemas (futuro)

## Precisão e Validação

### Metodologia
- Baseado em protocolos do Ministério da Saúde
- Validado com dados reais do SINAN
- Pesos ajustados por evidência epidemiológica
- Threshold calibrado para sensibilidade

### Sinais de Alarme (Detecção)
- Dor abdominal intensa
- Vômitos persistentes
- Sangramento de mucosas
- Letargia/irritabilidade
- Hepatomegalia dolorosa
- Hipotensão postural
- Oligúria
- Queda temperatura + sudorese
- Acúmulo de líquidos

### Sinais de Gravidade (Emergência)
- Choque
- Sangramento grave
- Insuficiência respiratória
- Alteração de consciência
- Comprometimento de órgãos

## Impacto Esperado

### Clínico
- ⬆️ Identificação precoce de casos graves
- ⬇️ Taxa de evolução para formas graves
- ⬇️ Mortalidade por dengue
- ⬆️ Qualidade da triagem

### Operacional
- ⚡ Redução do tempo de triagem
- 📊 Padronização do atendimento
- 📈 Priorização adequada
- 📝 Documentação automática

### Educacional
- 📚 Aprendizado com casos reais
- 🎓 Treinamento de novos profissionais
- 📖 Atualização contínua

## Segurança e Privacidade

### Dados
✅ Processamento local
✅ Sem envio de dados sensíveis
✅ Anonimização de casos
✅ Conformidade com LGPD

### IA
✅ Explicabilidade das decisões
✅ Rastreabilidade do raciocínio
✅ Supervisão humana obrigatória
✅ Não substitui avaliação médica

## Requisitos

### Hardware
- **Mínimo**: 4GB RAM, 2 cores, 5GB disco
- **Recomendado**: 8GB RAM, 4 cores, 10GB disco

### Software
- Python 3.9+
- Navegador web moderno
- Conexão internet (para IA)

### Custo
- **Software**: Gratuito (open source)
- **APIs IA**: ~$0.01-0.05 por triagem
- **Hosting**: Variável (local = grátis)

## Instalação

### Rápido (5 minutos)
```bash
pip install -r requirements.txt
python setup.py
python run.py
```

### Detalhado
Ver `INSTALLATION.md`

## Casos de Uso

### 1. UBS - Unidade Básica de Saúde
Triagem primária de pacientes com sintomas gripais em época de epidemia

### 2. Pronto-Socorro
Priorização de atendimento e identificação de casos críticos

### 3. Hospital Dia
Monitoramento de pacientes em observação

### 4. Telemedicina
Avaliação remota de sintomas

### 5. Vigilância Epidemiológica
Análise de padrões e identificação de surtos

## Roadmap Futuro

### Versão 2.0
- [ ] Integração com sistemas hospitalares (HL7, FHIR)
- [ ] App mobile para campo
- [ ] Modo offline completo
- [ ] Modelos de IA locais (sem API)

### Versão 3.0
- [ ] Predição de evolução (ML)
- [ ] Alertas automáticos
- [ ] Dashboard de gestão
- [ ] BI e analytics

### Pesquisa
- [ ] Publicação científica
- [ ] Validação prospectiva
- [ ] Expansão para outras arboviroses
- [ ] Personalização por região

## Métricas de Sucesso

### Técnicas
- Acurácia na classificação de risco
- Sensibilidade para casos graves
- Tempo de resposta do sistema
- Uptime e disponibilidade

### Clínicas
- Taxa de detecção de sinais de alarme
- Tempo até encaminhamento adequado
- Satisfação dos profissionais
- Desfechos dos pacientes

## Limitações

⚠️ **Importante**: Este é um sistema de **apoio** à decisão clínica

- Não substitui avaliação médica presencial
- Não realiza diagnóstico definitivo
- Não substitui exames complementares
- Requer supervisão de profissional qualificado

## Licença e Distribuição

- **Licença**: MIT (open source)
- **Uso**: Livre para fins educacionais e assistenciais
- **Modificação**: Permitida e encorajada
- **Comercial**: Consultar autores

## Citação

Se usar este sistema em pesquisa ou publicação:

```
Sistema RAG de Triagem de Dengue (2026)
Baseado em dados do SINAN/DATASUS
Disponível em: [GitHub repository]
```

## Contato e Suporte

- 📖 **Documentação**: README.md, INSTALLATION.md
- 💬 **Issues**: GitHub Issues
- 📧 **Email**: suporte@exemplo.com
- 🌐 **Website**: [projeto website]

## Agradecimentos

- **DATASUS/Ministério da Saúde**: Pelos dados públicos
- **Comunidade open source**: Pelas bibliotecas
- **Profissionais de saúde**: Pelo feedback e validação

---

**Desenvolvido com ❤️ para salvar vidas**

*Versão 1.0.0 - Janeiro 2026*

🦟 **Dengue Zero** - Tecnologia a serviço da saúde pública
