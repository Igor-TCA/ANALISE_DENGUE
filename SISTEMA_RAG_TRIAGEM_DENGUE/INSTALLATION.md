# 📦 Guia de Instalação Completo

## Sistema Operacional

Este guia cobre instalação em:
- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Debian, etc)
- ✅ macOS

## Pré-requisitos

### Python 3.9+

**Verificar instalação:**
```bash
python --version
# ou
python3 --version
```

**Instalar se necessário:**

**Windows:**
- Baixar de https://www.python.org/downloads/
- Durante instalação, marcar "Add Python to PATH"

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
brew install python3
```

### Git (opcional, para clonar repositório)

```bash
# Verificar
git --version

# Instalar no Ubuntu
sudo apt install git

# Instalar no macOS
brew install git
```

## Passo a Passo

### 1. Obter o código

**Opção A: Já tem a pasta**
```bash
cd ANALISE_DENGUE/SISTEMA_RAG_TRIAGEM_DENGUE
```

**Opção B: Clonar do Git**
```bash
git clone <seu-repositorio>
cd SISTEMA_RAG_TRIAGEM_DENGUE
```

### 2. Criar ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Se houver erro de permissão:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Você verá `(venv)` no início da linha de comando quando ativado.

### 3. Atualizar pip

```bash
python -m pip install --upgrade pip
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

**Tempo estimado:** 5-10 minutos (depende da conexão)

#### Problemas comuns:

**Erro com torch/tensorflow:**
```bash
# Pular dependências pesadas (não essenciais)
pip install -r requirements.txt --no-deps
pip install streamlit pandas numpy
```

**Erro de compilação no Windows:**
- Instalar Microsoft C++ Build Tools
- https://visualstudio.microsoft.com/visual-cpp-build-tools/

**Erro no Linux:**
```bash
sudo apt install python3-dev build-essential
pip install -r requirements.txt
```

### 5. Configurar dados

Certifique-se de que o arquivo `DENGBR25.csv` está no diretório pai:

```
ANALISE_DENGUE/
├── DENGBR25.csv          ← Arquivo de dados aqui
└── SISTEMA_RAG_TRIAGEM_DENGUE/
    ├── backend/
    ├── frontend/
    └── ...
```

### 6. Configurar APIs (opcional, mas recomendado)

**a) Criar conta OpenAI ou Anthropic:**

- OpenAI: https://platform.openai.com/
- Anthropic: https://console.anthropic.com/

**b) Obter chave de API**

**c) Configurar no sistema:**

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env (usar bloco de notas ou editor de texto)
# Windows:
notepad .env

# Linux/Mac:
nano .env
```

Adicionar sua chave:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
# ou
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
```

**Importante:** Mantenha sua chave em segredo!

### 7. Inicializar sistema

```bash
python setup.py
```

Este script irá:
1. ✅ Verificar arquivos necessários
2. ✅ Processar 1,5M+ registros de dengue
3. ✅ Extrair casos graves
4. ✅ Criar base de conhecimento
5. ✅ Gerar embeddings
6. ✅ Criar vector store

**Tempo estimado:** 10-30 minutos (primeira execução)

#### Saída esperada:
```
============================================================
INICIANDO SETUP DO SISTEMA DE TRIAGEM DE DENGUE
============================================================

[1/4] Verificando arquivos necessários...
✓ Arquivo de dados encontrado

[2/4] Processando dados do SINAN...
Dados carregados: 1502259 registros
Casos graves identificados: 45231
Documentos criados: 12845
✓ Dados processados com sucesso

[3/4] Criando vector store (embeddings)...
✓ Vector store criado com sucesso

[4/4] Verificando dependências...
✓ Todas as dependências instaladas

============================================================
SETUP CONCLUÍDO COM SUCESSO!
============================================================
```

### 8. Executar sistema

```bash
python run.py
```

Ou diretamente com Streamlit:
```bash
streamlit run frontend/app.py
```

O navegador abrirá automaticamente em: `http://localhost:8501`

## Verificação da Instalação

### Teste rápido

```bash
python -c "from backend import QuestionarioTriagemDengue; print('✅ Backend OK')"
```

### Executar testes

```bash
python tests/test_questionario.py
```

### Executar exemplos

```bash
python exemplo_uso.py
```

## Estrutura de Diretórios Após Instalação

```
SISTEMA_RAG_TRIAGEM_DENGUE/
│
├── backend/
│   ├── __init__.py
│   ├── data_processor.py
│   ├── rag_system.py
│   └── questionario.py
│
├── frontend/
│   └── app.py
│
├── config/
│   └── config.yaml
│
├── data/
│   └── knowledge_base.json      ← Criado pelo setup
│
├── vectorstore/                 ← Criado pelo setup
│   └── chroma.sqlite3
│
├── logs/                        ← Criado automaticamente
│   ├── setup.log
│   └── rag_system.log
│
├── venv/                        ← Ambiente virtual
│
├── .env                         ← Suas configurações
├── requirements.txt
├── setup.py
├── run.py
└── README.md
```

## Desinstalação

### Remover ambiente virtual

```bash
# Desativar
deactivate

# Remover pasta
# Windows
rmdir /s venv

# Linux/Mac
rm -rf venv
```

### Limpar dados processados

```bash
# Windows
rmdir /s data vectorstore logs

# Linux/Mac
rm -rf data vectorstore logs
```

## Atualização

```bash
# Ativar ambiente
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Atualizar dependências
pip install --upgrade -r requirements.txt

# Re-processar dados (se necessário)
python setup.py
```

## Solução de Problemas

### Sistema não abre no navegador

1. Verificar se porta 8501 está disponível
2. Tentar porta diferente:
```bash
streamlit run frontend/app.py --server.port 8502
```

### Erro "ModuleNotFoundError"

```bash
# Verificar ambiente virtual ativado
which python  # Linux/Mac
where python  # Windows

# Reinstalar
pip install -r requirements.txt
```

### Erro "knowledge_base.json not found"

```bash
python setup.py
```

### Sistema lento

1. Usar modelo de embedding menor
2. Reduzir número de documentos recuperados
3. Usar modo sem IA (apenas score)

### Erro de memória

1. Processar dados em batches menores
2. Usar máquina com mais RAM
3. Fechar outros programas

## Requisitos de Hardware

### Mínimo
- CPU: 2 cores
- RAM: 4 GB
- Disco: 5 GB livres
- Internet: Para APIs (se usar IA)

### Recomendado
- CPU: 4+ cores
- RAM: 8+ GB
- Disco: 10 GB livres
- SSD: Para melhor performance

### Para processamento inicial
- RAM: 8+ GB recomendado
- Tempo: ~15-30 minutos

## Próximos Passos

1. ✅ Ler README.md completo
2. ✅ Executar exemplo_uso.py
3. ✅ Abrir interface web
4. ✅ Fazer triagem de teste
5. ✅ Configurar para produção

## Suporte

- 📖 Documentação: README.md
- 🚀 Início rápido: QUICKSTART.md
- 💻 Exemplos: exemplo_uso.py
- 🐛 Issues: GitHub Issues
- 📧 Email: suporte@exemplo.com

## Checklist de Instalação

```
[ ] Python 3.9+ instalado
[ ] Ambiente virtual criado
[ ] Dependências instaladas
[ ] Arquivo DENGBR25.csv presente
[ ] API configurada (opcional)
[ ] Setup executado com sucesso
[ ] Sistema abre no navegador
[ ] Triagem de teste funciona
```

**Pronto! Sistema instalado e funcionando! 🎉**
