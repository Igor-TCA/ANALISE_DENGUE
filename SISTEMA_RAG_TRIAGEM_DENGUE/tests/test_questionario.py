"""
Testes Unitários para o Sistema de Triagem
"""

import unittest
import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from questionario import QuestionarioTriagemDengue, TipoPergunta


class TestQuestionario(unittest.TestCase):
    """Testes para o questionário de triagem"""
    
    def setUp(self):
        """Setup antes de cada teste"""
        self.questionario = QuestionarioTriagemDengue()
    
    def test_criacao_questionario(self):
        """Testa se questionário é criado corretamente"""
        self.assertIsNotNone(self.questionario)
        self.assertGreater(len(self.questionario.perguntas), 0)
        self.assertGreater(len(self.questionario.secoes), 0)
    
    def test_registro_resposta_valida(self):
        """Testa registro de resposta válida"""
        self.questionario.registrar_resposta('idade', 35)
        self.assertEqual(self.questionario.respostas['idade'], 35)
    
    def test_registro_resposta_invalida(self):
        """Testa rejeição de resposta inválida"""
        with self.assertRaises(ValueError):
            self.questionario.registrar_resposta('idade', -5)
    
    def test_calculo_score_sem_respostas(self):
        """Testa cálculo de score sem respostas"""
        score = self.questionario.calcular_score_risco()
        self.assertEqual(score, 0.0)
    
    def test_calculo_score_com_alarmes(self):
        """Testa que sinais de alarme aumentam score"""
        self.questionario.registrar_resposta('dor_abdominal_intensa', True)
        score = self.questionario.calcular_score_risco()
        self.assertGreater(score, 0)
    
    def test_classificacao_risco_baixo(self):
        """Testa classificação de risco baixo"""
        self.questionario.registrar_resposta('idade', 30)
        self.questionario.registrar_resposta('febre_presente', True)
        
        risco = self.questionario.classificar_risco()
        self.assertEqual(risco['nivel'], 'BAIXO')
    
    def test_classificacao_risco_critico(self):
        """Testa classificação de risco crítico"""
        self.questionario.registrar_resposta('idade', 70)
        self.questionario.registrar_resposta('choque', True)
        self.questionario.registrar_resposta('sangramento_grave', True)
        self.questionario.registrar_resposta('alteracao_consciencia', True)
        
        risco = self.questionario.classificar_risco()
        self.assertEqual(risco['nivel'], 'CRÍTICO')
    
    def test_geracao_dados_paciente(self):
        """Testa geração de dados estruturados do paciente"""
        self.questionario.registrar_resposta('idade', 45)
        self.questionario.registrar_resposta('sexo', 'Feminino')
        self.questionario.registrar_resposta('febre_presente', True)
        self.questionario.registrar_resposta('cefaleia', True)
        
        dados = self.questionario.gerar_dados_paciente()
        
        self.assertEqual(dados['idade'], 45)
        self.assertEqual(dados['sexo'], 'Feminino')
        self.assertIn('febre', dados['sintomas'])
        self.assertIn('cefaleia', dados['sintomas'])
    
    def test_idade_extrema_aumenta_risco(self):
        """Testa que idades extremas aumentam risco"""
        # Idoso
        self.questionario.registrar_resposta('idade', 70)
        score_idoso = self.questionario.calcular_score_risco()
        
        # Adulto
        questionario2 = QuestionarioTriagemDengue()
        questionario2.registrar_resposta('idade', 35)
        score_adulto = questionario2.calcular_score_risco()
        
        self.assertGreater(score_idoso, score_adulto)
    
    def test_plaquetopenia_aumenta_risco(self):
        """Testa que plaquetas baixas aumentam risco"""
        self.questionario.registrar_resposta('tem_hemograma', True)
        self.questionario.registrar_resposta('plaquetas', 45000)
        
        score = self.questionario.calcular_score_risco()
        self.assertGreater(score, 2.0)


class TestValidacoes(unittest.TestCase):
    """Testes de validação de respostas"""
    
    def setUp(self):
        self.questionario = QuestionarioTriagemDengue()
    
    def test_validacao_numero_fora_range(self):
        """Testa validação de número fora do range"""
        valida, erro = self.questionario.validar_resposta('idade', 150)
        self.assertFalse(valida)
        self.assertIsNotNone(erro)
    
    def test_validacao_opcao_invalida(self):
        """Testa validação de opção inválida"""
        valida, erro = self.questionario.validar_resposta('sexo', 'Outro')
        self.assertFalse(valida)
    
    def test_validacao_campo_obrigatorio(self):
        """Testa validação de campo obrigatório"""
        valida, erro = self.questionario.validar_resposta('idade', None)
        self.assertFalse(valida)


def run_tests():
    """Executa todos os testes"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestQuestionario))
    suite.addTests(loader.loadTestsFromTestCase(TestValidacoes))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
