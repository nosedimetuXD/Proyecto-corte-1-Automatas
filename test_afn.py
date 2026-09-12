"""
test_afn.py
Pruebas automáticas para la construcción de AFN-λ y sus representaciones:
- Grafo
- Matriz de transiciones
- Función Δ(Q, Σ)
- Aceptación y rechazo de cadenas
"""

import unittest
from afn_lambda import GeneradorAFN, LAMBDA


class TestAFNLambda(unittest.TestCase):

    def setUp(self):
        self.generador = GeneradorAFN()

    def test_simbolo_simple(self):
        afn = self.generador.construir_afn("a")
        self.assertEqual(afn.Sigma, ["a"])
        # Con la regla de λ >= 1, tiene al menos 1 transición λ
        num_lambdas = sum(1 for t in afn.transiciones if t[1] == LAMBDA)
        self.assertGreaterEqual(num_lambdas, 1)
        self.assertEqual(afn.q0, "q0")
        self.assertTrue(afn.acepta_cadena("a"))
        self.assertFalse(afn.acepta_cadena(""))
        self.assertFalse(afn.acepta_cadena("b"))
        self.assertFalse(afn.acepta_cadena("aa"))

    def test_concatenacion(self):
        afn = self.generador.construir_afn("ab")
        self.assertEqual(sorted(afn.Sigma), ["a", "b"])
        self.assertTrue(afn.acepta_cadena("ab"))
        self.assertFalse(afn.acepta_cadena("a"))
        self.assertFalse(afn.acepta_cadena("b"))
        self.assertFalse(afn.acepta_cadena("aba"))

    def test_union(self):
        afn = self.generador.construir_afn("a|b")
        self.assertTrue(afn.acepta_cadena("a"))
        self.assertTrue(afn.acepta_cadena("b"))
        self.assertFalse(afn.acepta_cadena("ab"))
        self.assertFalse(afn.acepta_cadena(""))

    def test_union_con_letra_U(self):
        # En el libro se usa U para unión: aUb
        afn = self.generador.construir_afn("aUb")
        self.assertTrue(afn.acepta_cadena("a"))
        self.assertTrue(afn.acepta_cadena("b"))
        self.assertFalse(afn.acepta_cadena("ab"))

    def test_estrella_kleene(self):
        afn = self.generador.construir_afn("a*")
        self.assertTrue(afn.acepta_cadena(""))
        self.assertTrue(afn.acepta_cadena("a"))
        self.assertTrue(afn.acepta_cadena("aaaaa"))
        self.assertFalse(afn.acepta_cadena("b"))
        self.assertFalse(afn.acepta_cadena("ab"))

    def test_cadenas_que_terminan_en_b(self):
        # Ejemplo del libro (Sección 2.3/2.4): (a|b)*b
        afn = self.generador.construir_afn("(a|b)*b")
        self.assertTrue(afn.acepta_cadena("b"))
        self.assertTrue(afn.acepta_cadena("ab"))
        self.assertTrue(afn.acepta_cadena("aab"))
        self.assertTrue(afn.acepta_cadena("babab"))
        self.assertFalse(afn.acepta_cadena(""))
        self.assertFalse(afn.acepta_cadena("a"))
        self.assertFalse(afn.acepta_cadena("ba"))
        self.assertFalse(afn.acepta_cadena("abba"))

    def test_ejemplo_de_castro_seccion_2_9(self):
        # Ejemplo de Sección 2.9: a*(ab|ba)*
        afn = self.generador.construir_afn("a*(ab|ba)*")
        self.assertTrue(afn.acepta_cadena(""))
        self.assertTrue(afn.acepta_cadena("a"))
        self.assertTrue(afn.acepta_cadena("aaa"))
        self.assertTrue(afn.acepta_cadena("ab"))
        self.assertTrue(afn.acepta_cadena("ba"))
        self.assertTrue(afn.acepta_cadena("aabba"))
        self.assertTrue(afn.acepta_cadena("aaabba"))
        self.assertTrue(afn.acepta_cadena("aab"))  # a ∈ a*, ab ∈ (ab|ba)*
        self.assertFalse(afn.acepta_cadena("b"))
        self.assertFalse(afn.acepta_cadena("abb"))
        self.assertFalse(afn.acepta_cadena("bba"))

    def test_salidas_grafo_matriz_delta(self):
        afn = self.generador.construir_afn("a(b|c)*")
        
        # 1. Grafo
        mermaid = afn.generar_grafo_mermaid()
        self.assertIn("graph LR", mermaid)
        self.assertIn("-->|inicio| q0", mermaid)
        dot = afn.generar_grafo_dot()
        self.assertIn("digraph AFN_Lambda", dot)

        # 2. Matriz
        encabezados, filas = afn.obtener_matriz_transiciones()
        self.assertEqual(encabezados, ["Estado", "a", "b", "c", LAMBDA])
        self.assertEqual(len(filas), len(afn.Q))
        matriz_str = afn.formato_matriz_ascii()
        self.assertIn("->q0", matriz_str)

        # 3. Función Delta
        delta_str = afn.formato_funcion_delta()
        self.assertIn("Δ : Q × (Σ ∪ {λ}) ──> ℘(Q)", delta_str)
        self.assertIn("Δ(q", delta_str)


if __name__ == "__main__":
    unittest.main()
