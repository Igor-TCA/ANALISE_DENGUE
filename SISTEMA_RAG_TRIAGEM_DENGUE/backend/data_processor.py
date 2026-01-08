"""
Processador de Dados de Dengue
Prepara os dados do SINAN para criação de embeddings e conhecimento do sistema RAG
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from loguru import logger


class DengueDataProcessor:
    """Processa dados de dengue do SINAN para criar base de conhecimento"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.df = None
        self.knowledge_base = []
        
    def load_data(self):
        """Carrega dados de dengue"""
        logger.info(f"Carregando dados de: {self.data_path}")
        self.df = pd.read_csv(self.data_path, low_memory=False)
        logger.info(f"Dados carregados: {len(self.df)} registros")
        return self
    
    def clean_data(self):
        """Limpa e prepara os dados"""
        logger.info("Limpando dados...")
        
        # Remover duplicatas
        self.df = self.df.drop_duplicates()
        
        # Criar idade em anos
        self.df['IDADE_ANOS'] = self.df['NU_IDADE_N'].apply(self._calcular_idade)
        
        # Criar faixa etária
        self.df['FAIXA_ETARIA'] = self.df['IDADE_ANOS'].apply(self._classificar_faixa_etaria)
        
        logger.info(f"Dados limpos: {len(self.df)} registros")
        return self
    
    def extract_severe_cases(self):
        """Extrai casos que evoluíram para formas graves"""
        logger.info("Extraindo casos graves...")
        
        # Casos com sinais de alarme
        alarme_cols = [col for col in self.df.columns if col.startswith('ALRM_')]
        
        # Casos com sinais de gravidade
        grav_cols = [col for col in self.df.columns if col.startswith('GRAV_')]
        
        # Casos que foram a óbito
        obitos = self.df[self.df['EVOLUCAO'] == 2].copy()
        
        # Casos graves (classificação final grave)
        graves = self.df[self.df['CLASSI_FIN'].isin([2, 3])].copy()  # Dengue com alarme ou grave
        
        # Casos hospitalizados
        hospitalizados = self.df[self.df['HOSPITALIZ'] == 1].copy()
        
        self.casos_graves = pd.concat([obitos, graves, hospitalizados]).drop_duplicates()
        
        logger.info(f"Casos graves identificados: {len(self.casos_graves)}")
        return self
    
    def create_knowledge_documents(self):
        """Cria documentos estruturados para a base de conhecimento"""
        logger.info("Criando documentos de conhecimento...")
        
        # Processar casos graves para criar padrões
        for idx, caso in self.casos_graves.iterrows():
            doc = self._criar_documento_caso(caso)
            if doc:
                self.knowledge_base.append(doc)
        
        # Criar documentos de padrões agregados
        self._criar_documentos_padroes()
        
        logger.info(f"Documentos criados: {len(self.knowledge_base)}")
        return self
    
    def _criar_documento_caso(self, caso) -> dict:
        """Cria documento estruturado de um caso individual"""
        
        # Extrair sintomas presentes
        sintomas = self._extrair_sintomas(caso)
        
        # Extrair sinais de alarme
        sinais_alarme = self._extrair_sinais_alarme(caso)
        
        # Extrair sinais de gravidade
        sinais_gravidade = self._extrair_sinais_gravidade(caso)
        
        # Extrair comorbidades
        comorbidades = self._extrair_comorbidades(caso)
        
        # Classificação e evolução
        evolucao = self._interpretar_evolucao(caso.get('EVOLUCAO'))
        classificacao = self._interpretar_classificacao(caso.get('CLASSI_FIN'))
        
        # Calcular dias até evolução grave (se aplicável)
        dias_evolucao = self._calcular_dias_evolucao(caso)
        
        documento = {
            'tipo': 'caso_clinico',
            'id_caso': f"caso_{idx}",
            'perfil': {
                'idade': int(caso.get('IDADE_ANOS', 0)),
                'faixa_etaria': caso.get('FAIXA_ETARIA', 'Desconhecida'),
                'sexo': 'Feminino' if caso.get('CS_SEXO') == 'F' else 'Masculino',
                'gestante': caso.get('CS_GESTANT') == 1,
            },
            'apresentacao_clinica': {
                'sintomas': sintomas,
                'sinais_alarme': sinais_alarme,
                'sinais_gravidade': sinais_gravidade,
                'comorbidades': comorbidades,
            },
            'evolucao': {
                'classificacao_final': classificacao,
                'desfecho': evolucao,
                'hospitalizado': caso.get('HOSPITALIZ') == 1,
                'dias_ate_gravidade': dias_evolucao,
            },
            'texto_narrativo': self._gerar_narrativa_caso(
                sintomas, sinais_alarme, sinais_gravidade, 
                comorbidades, classificacao, evolucao
            )
        }
        
        return documento
    
    def _criar_documentos_padroes(self):
        """Cria documentos sobre padrões agregados identificados nos dados"""
        
        # Padrão 1: Sintomas que precedem casos graves por faixa etária
        for faixa in ['Criança', 'Jovem', 'Adulto', 'Idoso']:
            casos_faixa = self.casos_graves[self.casos_graves['FAIXA_ETARIA'] == faixa]
            
            if len(casos_faixa) > 10:  # Apenas se houver dados suficientes
                sintomas_freq = self._calcular_frequencia_sintomas(casos_faixa)
                alarmes_freq = self._calcular_frequencia_alarmes(casos_faixa)
                
                doc_padrao = {
                    'tipo': 'padrao_epidemiologico',
                    'id_caso': f'padrao_{faixa.lower()}',
                    'faixa_etaria': faixa,
                    'n_casos': len(casos_faixa),
                    'sintomas_mais_comuns': sintomas_freq,
                    'sinais_alarme_mais_comuns': alarmes_freq,
                    'taxa_hospitalizacao': (casos_faixa['HOSPITALIZ'] == 1).mean(),
                    'taxa_obito': (casos_faixa['EVOLUCAO'] == 2).mean(),
                    'texto_narrativo': self._gerar_narrativa_padrao(
                        faixa, len(casos_faixa), sintomas_freq, alarmes_freq
                    )
                }
                
                self.knowledge_base.append(doc_padrao)
        
        # Padrão 2: Comorbidades e risco
        self._criar_documento_comorbidades()
        
        # Padrão 3: Progressão temporal
        self._criar_documento_progressao_temporal()
    
    def _extrair_sintomas(self, caso) -> list:
        """Extrai sintomas presentes no caso"""
        sintomas_map = {
            'FEBRE': 'febre',
            'MIALGIA': 'dor muscular',
            'CEFALEIA': 'cefaleia',
            'EXANTEMA': 'exantema',
            'VOMITO': 'vômito',
            'NAUSEA': 'náusea',
            'DOR_COSTAS': 'dor nas costas',
            'CONJUNTVIT': 'conjuntivite',
            'ARTRITE': 'artrite',
            'ARTRALGIA': 'artralgia',
            'DOR_RETRO': 'dor retro-orbital',
        }
        
        sintomas = []
        for col, nome in sintomas_map.items():
            if caso.get(col) == 1:
                sintomas.append(nome)
        
        return sintomas
    
    def _extrair_sinais_alarme(self, caso) -> list:
        """Extrai sinais de alarme presentes"""
        alarme_map = {
            'ALRM_HIPOT': 'hipotensão postural',
            'ALRM_PLAQ': 'queda de plaquetas',
            'ALRM_VOM': 'vômitos persistentes',
            'ALRM_SANG': 'sangramento de mucosas',
            'ALRM_HEMAT': 'aumento do hematócrito',
            'ALRM_ABDOM': 'dor abdominal intensa',
            'ALRM_LETAR': 'letargia ou irritabilidade',
            'ALRM_HEPAT': 'hepatomegalia dolorosa',
            'ALRM_LIQ': 'acúmulo de líquidos',
        }
        
        sinais = []
        for col, nome in alarme_map.items():
            if caso.get(col) == 1:
                sinais.append(nome)
        
        return sinais
    
    def _extrair_sinais_gravidade(self, caso) -> list:
        """Extrai sinais de gravidade presentes"""
        grav_map = {
            'GRAV_PULSO': 'pulso fraco ou ausente',
            'GRAV_CONV': 'convulsões',
            'GRAV_ENCH': 'enchimento capilar lento',
            'GRAV_INSUF': 'insuficiência respiratória',
            'GRAV_TAQUI': 'taquicardia',
            'GRAV_EXTRE': 'extremidades frias',
            'GRAV_HIPOT': 'hipotensão arterial',
            'GRAV_HEMAT': 'hematócrito muito elevado',
            'GRAV_MELEN': 'melena',
            'GRAV_METRO': 'metrorragia',
            'GRAV_SANG': 'sangramento grave',
            'GRAV_MIOC': 'miocardite',
            'GRAV_CONSC': 'alteração de consciência',
            'GRAV_ORGAO': 'comprometimento de órgãos',
        }
        
        sinais = []
        for col, nome in grav_map.items():
            if caso.get(col) == 1:
                sinais.append(nome)
        
        return sinais
    
    def _extrair_comorbidades(self, caso) -> list:
        """Extrai comorbidades presentes"""
        comorb_map = {
            'DIABETES': 'diabetes',
            'HEMATOLOG': 'doença hematológica',
            'HEPATOPAT': 'hepatopatia',
            'RENAL': 'doença renal',
            'HIPERTENSA': 'hipertensão',
            'ACIDO_PEPT': 'doença ácido-péptica',
            'AUTO_IMUNE': 'doença autoimune',
        }
        
        comorbidades = []
        for col, nome in comorb_map.items():
            if caso.get(col) == 1:
                comorbidades.append(nome)
        
        return comorbidades
    
    def _interpretar_evolucao(self, codigo) -> str:
        """Interpreta código de evolução"""
        evolucao_map = {
            1: 'Cura',
            2: 'Óbito por dengue',
            3: 'Óbito por outras causas',
            9: 'Ignorado'
        }
        return evolucao_map.get(codigo, 'Desconhecido')
    
    def _interpretar_classificacao(self, codigo) -> str:
        """Interpreta classificação final"""
        class_map = {
            1: 'Dengue',
            2: 'Dengue com sinais de alarme',
            3: 'Dengue grave',
            4: 'Descartado',
            5: 'Chikungunya',
            10: 'Dengue clássico',
            11: 'Dengue com complicações',
            12: 'Síndrome de choque da dengue',
        }
        return class_map.get(codigo, 'Não classificado')
    
    def _calcular_dias_evolucao(self, caso) -> int:
        """Calcula dias entre início dos sintomas e sinais de gravidade"""
        try:
            if pd.notna(caso.get('DT_SIN_PRI')) and pd.notna(caso.get('DT_GRAV')):
                dt_inicio = pd.to_datetime(caso['DT_SIN_PRI'], errors='coerce')
                dt_grav = pd.to_datetime(caso['DT_GRAV'], errors='coerce')
                
                if pd.notna(dt_inicio) and pd.notna(dt_grav):
                    dias = (dt_grav - dt_inicio).days
                    return max(0, dias)
        except:
            pass
        
        return None
    
    def _gerar_narrativa_caso(self, sintomas, alarmes, gravidade, 
                              comorbidades, classificacao, evolucao) -> str:
        """Gera narrativa textual do caso para embedding"""
        
        narrativa = f"Caso clínico de {classificacao}. "
        
        if sintomas:
            narrativa += f"Sintomas apresentados: {', '.join(sintomas)}. "
        
        if comorbidades:
            narrativa += f"Comorbidades: {', '.join(comorbidades)}. "
        
        if alarmes:
            narrativa += f"Sinais de alarme identificados: {', '.join(alarmes)}. "
        
        if gravidade:
            narrativa += f"Sinais de gravidade presentes: {', '.join(gravidade)}. "
        
        narrativa += f"Evolução: {evolucao}."
        
        return narrativa
    
    def _gerar_narrativa_padrao(self, faixa, n_casos, sintomas_freq, alarmes_freq) -> str:
        """Gera narrativa de padrão epidemiológico"""
        
        narrativa = f"Padrão epidemiológico em {faixa}s baseado em {n_casos} casos graves. "
        
        if sintomas_freq:
            top_sintomas = list(sintomas_freq.keys())[:5]
            narrativa += f"Sintomas mais frequentes: {', '.join(top_sintomas)}. "
        
        if alarmes_freq:
            top_alarmes = list(alarmes_freq.keys())[:3]
            narrativa += f"Sinais de alarme mais comuns: {', '.join(top_alarmes)}. "
        
        return narrativa
    
    def _calcular_frequencia_sintomas(self, df_subset) -> dict:
        """Calcula frequência de sintomas em subset de dados"""
        sintomas_cols = ['FEBRE', 'MIALGIA', 'CEFALEIA', 'VOMITO', 'NAUSEA', 
                        'DOR_COSTAS', 'ARTRALGIA', 'DOR_RETRO']
        
        freq = {}
        for col in sintomas_cols:
            if col in df_subset.columns:
                prop = (df_subset[col] == 1).mean()
                if prop > 0:
                    nome = col.lower().replace('_', ' ')
                    freq[nome] = round(prop * 100, 1)
        
        return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
    
    def _calcular_frequencia_alarmes(self, df_subset) -> dict:
        """Calcula frequência de sinais de alarme"""
        alarme_cols = [col for col in df_subset.columns if col.startswith('ALRM_')]
        
        freq = {}
        for col in alarme_cols:
            prop = (df_subset[col] == 1).mean()
            if prop > 0:
                nome = col.replace('ALRM_', '').lower().replace('_', ' ')
                freq[nome] = round(prop * 100, 1)
        
        return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
    
    def _criar_documento_comorbidades(self):
        """Cria documento sobre impacto de comorbidades"""
        comorb_cols = ['DIABETES', 'HIPERTENSA', 'HEMATOLOG', 'HEPATOPAT', 'RENAL']
        
        doc = {
            'tipo': 'analise_comorbidades',
            'id_caso': 'comorbidades_risco',
            'analise': {}
        }
        
        for col in comorb_cols:
            if col in self.casos_graves.columns:
                casos_com = self.casos_graves[self.casos_graves[col] == 1]
                if len(casos_com) > 5:
                    taxa_obito = (casos_com['EVOLUCAO'] == 2).mean()
                    doc['analise'][col.lower()] = {
                        'n_casos': len(casos_com),
                        'taxa_obito': round(taxa_obito * 100, 2)
                    }
        
        doc['texto_narrativo'] = self._gerar_narrativa_comorbidades(doc['analise'])
        self.knowledge_base.append(doc)
    
    def _gerar_narrativa_comorbidades(self, analise) -> str:
        """Gera narrativa sobre comorbidades"""
        narrativa = "Análise de comorbidades e risco em casos graves: "
        
        for comorb, dados in analise.items():
            narrativa += f"{comorb} presente em {dados['n_casos']} casos graves " \
                        f"com taxa de óbito de {dados['taxa_obito']}%. "
        
        return narrativa
    
    def _criar_documento_progressao_temporal(self):
        """Cria documento sobre progressão temporal da doença"""
        
        # Casos com informação de dias até gravidade
        casos_com_tempo = self.casos_graves[
            self.casos_graves.apply(lambda x: self._calcular_dias_evolucao(x) is not None, axis=1)
        ].copy()
        
        if len(casos_com_tempo) > 10:
            casos_com_tempo['dias_gravidade'] = casos_com_tempo.apply(
                lambda x: self._calcular_dias_evolucao(x), axis=1
            )
            
            doc = {
                'tipo': 'progressao_temporal',
                'id_caso': 'progressao_temporal',
                'estatisticas': {
                    'media_dias': round(casos_com_tempo['dias_gravidade'].mean(), 1),
                    'mediana_dias': round(casos_com_tempo['dias_gravidade'].median(), 1),
                    'percentil_25': round(casos_com_tempo['dias_gravidade'].quantile(0.25), 1),
                    'percentil_75': round(casos_com_tempo['dias_gravidade'].quantile(0.75), 1),
                },
                'texto_narrativo': f"Análise de progressão temporal: casos graves desenvolvem "
                                  f"sinais de gravidade em média {round(casos_com_tempo['dias_gravidade'].mean(), 1)} "
                                  f"dias após início dos sintomas. 50% dos casos graves manifestam sinais "
                                  f"críticos em até {round(casos_com_tempo['dias_gravidade'].median(), 1)} dias."
            }
            
            self.knowledge_base.append(doc)
    
    def _calcular_idade(self, nu_idade_n):
        """Converte código de idade para anos"""
        if pd.isna(nu_idade_n):
            return None
        
        codigo = str(int(nu_idade_n))
        
        if len(codigo) != 4:
            return None
        
        tipo = int(codigo[0])
        valor = int(codigo[1:])
        
        if tipo == 4:  # Anos
            return valor
        elif tipo == 3:  # Meses
            return valor / 12
        elif tipo == 2:  # Dias
            return valor / 365
        elif tipo == 1:  # Horas
            return valor / (365 * 24)
        
        return None
    
    def _classificar_faixa_etaria(self, idade):
        """Classifica idade em faixas etárias"""
        if pd.isna(idade):
            return 'Desconhecida'
        
        if idade < 15:
            return 'Criança'
        elif idade < 23:
            return 'Jovem'
        elif idade < 60:
            return 'Adulto'
        else:
            return 'Idoso'
    
    def save_knowledge_base(self, output_path: str):
        """Salva base de conhecimento em JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Base de conhecimento salva em: {output_file}")
        logger.info(f"Total de documentos: {len(self.knowledge_base)}")
        
    def generate_statistics_report(self) -> dict:
        """Gera relatório estatístico dos dados processados"""
        report = {
            'total_casos': len(self.df),
            'casos_graves': len(self.casos_graves),
            'documentos_gerados': len(self.knowledge_base),
            'distribuicao_faixa_etaria': self.casos_graves['FAIXA_ETARIA'].value_counts().to_dict(),
            'taxa_hospitalizacao': (self.casos_graves['HOSPITALIZ'] == 1).mean(),
            'taxa_obito': (self.casos_graves['EVOLUCAO'] == 2).mean(),
        }
        
        return report


if __name__ == "__main__":
    # Configurar logging
    logger.add("logs/data_processing.log", rotation="10 MB")
    
    # Caminhos
    data_path = "../DENGBR25.csv"
    output_path = "../data/knowledge_base.json"
    
    # Processar dados
    processor = DengueDataProcessor(data_path)
    processor.load_data() \
             .clean_data() \
             .extract_severe_cases() \
             .create_knowledge_documents() \
             .save_knowledge_base(output_path)
    
    # Gerar relatório
    report = processor.generate_statistics_report()
    print("\n=== Relatório de Processamento ===")
    for key, value in report.items():
        print(f"{key}: {value}")
