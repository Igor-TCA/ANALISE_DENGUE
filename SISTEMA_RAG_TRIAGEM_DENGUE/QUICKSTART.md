# Guia Rápido - Sistema de Triagem de Dengue

## ⚡ Início Rápido (5 minutos)

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Inicializar sistema
```bash
python setup.py
```

### 3. Configurar API (opcional)
```bash
# Copiar exemplo
cp .env.example .env

# Editar .env e adicionar:
OPENAI_API_KEY=sua_chave_aqui
```

### 4. Executar
```bash
python run.py
```

## 📋 Checklist de Triagem

### Informações Obrigatórias
- [ ] Idade do paciente
- [ ] Sexo
- [ ] Dias desde início dos sintomas
- [ ] Febre presente?

### Sintomas (marcar presentes)
- [ ] Cefaleia
- [ ] Dor retro-orbital
- [ ] Mialgia
- [ ] Artralgia
- [ ] Náusea
- [ ] Vômito

### ⚠️ Sinais de Alarme (ATENÇÃO!)
- [ ] Dor abdominal intensa
- [ ] Vômitos persistentes
- [ ] Sangramento de mucosas
- [ ] Letargia/irritabilidade
- [ ] Hepatomegalia dolorosa
- [ ] Hipotensão postural
- [ ] Oligúria
- [ ] Queda temperatura com sudorese
- [ ] Acúmulo de líquidos

### 🚨 Sinais de Gravidade (EMERGÊNCIA!)
- [ ] Choque
- [ ] Sangramento grave
- [ ] Insuficiência respiratória
- [ ] Alteração de consciência
- [ ] Comprometimento de órgãos

### Comorbidades
- [ ] Diabetes
- [ ] Hipertensão
- [ ] Doença hematológica
- [ ] Hepatopatia
- [ ] Doença renal
- [ ] Doença cardiovascular
- [ ] Imunossupressão

### Laboratorial (se disponível)
- [ ] Plaquetas: _______ /mm³
- [ ] Hematócrito: _______ %

## 🎯 Interpretação de Resultados

### Score < 3 - 🟢 BAIXO
**Conduta**: Ambulatorial
- Hidratação oral abundante
- Paracetamol para sintomas
- Repouso
- Retorno se piora

### Score 3-6 - 🟡 MÉDIO
**Conduta**: Monitoramento
- Reavaliação em 24h
- Hemograma de controle
- Atenção a sinais de alarme
- Considerar hidratação venosa

### Score 6-10 - 🟠 ALTO
**Conduta**: Urgente
- Avaliação médica imediata
- Hemograma urgente
- Hidratação venosa
- Considerar internação

### Score > 10 - 🔴 CRÍTICO
**Conduta**: EMERGÊNCIA
- Atendimento imediato
- Acesso venoso
- Monitorização contínua
- UTI se necessário

## 💡 Dicas

### Período Crítico
- Dias 3-7 após início: maior risco
- Atenção especial neste período

### Grupos de Risco
- Gestantes
- Lactentes (<1 ano)
- Idosos (>65 anos)
- Comorbidades

### Plaquetopenia
- < 50.000: Grave
- < 100.000: Moderada
- < 150.000: Leve

### Hemoconcentração
- Aumento >20% do hematócrito
- Sugere extravasamento plasmático

## ❓ FAQ

**Q: Posso usar sem internet?**
A: Sim, mas sem análise de IA.

**Q: Preciso de chave de API?**
A: Não é obrigatório, mas recomendado.

**Q: Os dados são salvos?**
A: Apenas localmente, não enviamos dados.

**Q: Posso personalizar os critérios?**
A: Sim, edite config/config.yaml

## 🆘 Problemas Comuns

### Erro ao instalar dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro "knowledge_base.json not found"
```bash
python setup.py
```

### Streamlit não abre
```bash
streamlit run frontend/app.py --server.port 8502
```

## 📞 Suporte

- GitHub Issues
- Email: suporte@exemplo.com
- Documentação: README.md
