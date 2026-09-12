"""
afn_lambda.py
Construcción de Autómata Finito No Determinista con Transiciones Lambda (AFN-λ)
a partir de una Expresión Regular.
Basado en: 'Teoría de la Computación: lenguajes, autómatas, gramáticas'
por Rodrigo De Castro Korgi (Capítulo 2, Secciones 2.4, 2.6 y 2.8).
"""

from collections import deque
from typing import Dict, List, Set, Tuple


LAMBDA = "λ"


class AFNLambda:
    """
    Representa un Autómata Finito No Determinista con Transiciones Lambda (AFN-λ).
    Definido formalmente como la 5-tupla: M = (Σ, Q, q0, F, Δ)
    """

    def __init__(
        self,
        estados: List[str],
        alfabeto: List[str],
        estado_inicial: str,
        estados_finales: Set[str],
        transiciones: List[Tuple[str, str, str]],
        expresion_original: str = "",
    ):
        self.Q = estados  # Lista ordenada de estados: ['q0', 'q1', ...]
        self.Sigma = sorted(alfabeto)  # Alfabeto de entrada (sin λ)
        self.q0 = estado_inicial  # Estado inicial
        self.F = estados_finales  # Conjunto de estados de aceptación
        self.transiciones = transiciones  # Lista de tuplas (origen, simbolo, destino)
        self.expresion_original = expresion_original

        # Construir la estructura para la función de transición Δ
        # delta_dict[estado][simbolo] = set(destinos)
        self.delta: Dict[str, Dict[str, Set[str]]] = {
            q: {s: set() for s in self.Sigma + [LAMBDA]} for q in self.Q
        }
        for orig, symb, dest in self.transiciones:
            if orig in self.delta and symb in self.delta[orig]:
                self.delta[orig][symb].add(dest)

    # -------------------------------------------------------------
    # Salida 1: Grafo (formatos Mermaid y DOT de Graphviz)
    # -------------------------------------------------------------
    def generar_grafo_mermaid(self) -> str:
        """Genera la representación del grafo en formato Mermaid."""
        lineas = ["graph LR"]
        # Estado inicial virtual
        lineas.append(f'    start_node(( )) -->|inicio| {self.q0}')
        lineas.append("    style start_node fill:#fff,stroke:#fff,stroke-width:0px")

        # Declarar estados finales con doble borde/estilo distintivo
        for q in self.Q:
            if q in self.F:
                lineas.append(f'    {q}((( "{q} [Final]" )))')
            else:
                lineas.append(f'    {q}(( "{q}" ))')

        # Agrupar transiciones entre los mismos pares (u, v)
        arcos: Dict[Tuple[str, str], List[str]] = {}
        for orig, symb, dest in self.transiciones:
            arcos.setdefault((orig, dest), []).append(symb)

        for (orig, dest), symbs in arcos.items():
            etiqueta = ", ".join(sorted(symbs))
            lineas.append(f'    {orig} -->|"{etiqueta}"| {dest}')

        return "\n".join(lineas)

    def generar_grafo_dot(self) -> str:
        """Genera la representación del grafo en formato DOT de Graphviz."""
        lineas = [
            "digraph AFN_Lambda {",
            '    rankdir=LR;',
            '    node [shape = circle, fontname="Helvetica"];',
            '    edge [fontname="Helvetica"];',
            "",
            "    // Estado inicial ficticio",
            '    __start [shape=none, label="", width=0, height=0];',
            f'    __start -> "{self.q0}" [label="inicio"];',
            "",
            "    // Estados de aceptación (doble círculo)",
        ]
        for f in sorted(self.F):
            lineas.append(f'    "{f}" [shape=doublecircle];')

        lineas.append("\n    // Transiciones")
        arcos: Dict[Tuple[str, str], List[str]] = {}
        for orig, symb, dest in self.transiciones:
            arcos.setdefault((orig, dest), []).append(symb)

        for (orig, dest), symbs in arcos.items():
            etiqueta = ", ".join(sorted(symbs))
            lineas.append(f'    "{orig}" -> "{dest}" [label="{etiqueta}"];')

        lineas.append("}")
        return "\n".join(lineas)

    # -------------------------------------------------------------
    # Salida 2: Matriz de Transiciones (Tabla de estados x símbolos)
    # -------------------------------------------------------------
    def obtener_matriz_transiciones(self) -> Tuple[List[str], List[List[str]]]:
        """
        Retorna:
          encabezados: ['Estado', s1, s2, ..., 'λ']
          filas: lista de filas con los estados destino formateados como {q_i, ...} o ∅
        """
        columnas = self.Sigma + [LAMBDA]
        encabezados = ["Estado"] + columnas
        filas = []

        for q in self.Q:
            prefijo = ""
            if q == self.q0:
                prefijo += "->"
            if q in self.F:
                prefijo += "*"
            nombre_estado = f"{prefijo}{q}" if prefijo else q

            fila = [nombre_estado]
            for s in columnas:
                destinos = self.delta[q].get(s, set())
                if destinos:
                    dest_str = "{" + ", ".join(sorted(destinos)) + "}"
                else:
                    dest_str = "∅"
                fila.append(dest_str)
            filas.append(fila)

        return encabezados, filas

    def formato_matriz_ascii(self) -> str:
        """Formatea la matriz de transiciones como una tabla ASCII elegante."""
        encabezados, filas = self.obtener_matriz_transiciones()
        anchos = [len(h) for h in encabezados]
        for fila in filas:
            for col_idx, celda in enumerate(fila):
                anchos[col_idx] = max(anchos[col_idx], len(celda))

        sep_line = "+-" + "-+-".join("-" * w for w in anchos) + "-+"
        header_line = "| " + " | ".join(h.center(anchos[i]) for i, h in enumerate(encabezados)) + " |"

        resultado = [sep_line, header_line, sep_line]
        for fila in filas:
            linea_fila = "| " + " | ".join(celda.center(anchos[i]) for i, celda in enumerate(fila)) + " |"
            resultado.append(linea_fila)
        resultado.append(sep_line)
        resultado.append("Convenciones: '->' = estado inicial, '*' = estado de aceptación, '∅' = sin transición.")
        return "\n".join(resultado)

    # -------------------------------------------------------------
    # Salida 3: Función Formal Δ(Q, Σ U {λ})
    # -------------------------------------------------------------
    def formato_funcion_delta(self) -> str:
        """
        Genera la especificación formal matemática de la función de transición
        Δ: Q x (Σ ∪ {λ}) -> P(Q), detallando cada transición no vacía.
        """
        lineas = []
        lineas.append("================================================================================")
        lineas.append("ESPECIFICACIÓN FORMAL DEL AFN-λ (Quíntupla M = (Σ, Q, q0, F, Δ))")
        lineas.append("================================================================================")
        lineas.append(f"• Expresión regular de origen : {self.expresion_original}")
        lineas.append(f"• Alfabeto de entrada (Σ)     : {{ {', '.join(self.Sigma)} }}")
        lineas.append(f"• Conjunto de estados (Q)     : {{ {', '.join(self.Q)} }} (Total: {len(self.Q)})")
        lineas.append(f"• Estado inicial (q0)         : {self.q0}")
        lineas.append(f"• Estados de aceptación (F)   : {{ {', '.join(sorted(self.F))} }}")
        lineas.append("")
        lineas.append("Definición de la Función de Transición:")
        lineas.append("  Δ : Q × (Σ ∪ {λ}) ──> ℘(Q)")
        lineas.append("--------------------------------------------------------------------------------")

        columnas = self.Sigma + [LAMBDA]
        trans_activas = []
        for q in self.Q:
            for s in columnas:
                destinos = self.delta[q].get(s, set())
                if destinos:
                    dest_formateado = "{" + ", ".join(sorted(destinos)) + "}"
                    trans_activas.append(f"  Δ({q}, {s}) = {dest_formateado}")

        if trans_activas:
            lineas.extend(trans_activas)
        else:
            lineas.append("  (No hay transiciones definidas)")

        lineas.append("")
        lineas.append("Para cualquier otra combinación (q, s) no listada:")
        lineas.append("  Δ(q, s) = ∅ (cómputo abortado en esa rama)")
        lineas.append("================================================================================")
        return "\n".join(lineas)

    # -------------------------------------------------------------
    # Simulador de Cadenas (Evaluar si una cadena es aceptada)
    # -------------------------------------------------------------
    def lambda_clausura(self, estados: Set[str]) -> Set[str]:
        """Calcula la λ-clausura λ[S] de un conjunto de estados."""
        clausura = set(estados)
        pila = list(estados)
        while pila:
            actual = pila.pop()
            destinos_lambda = self.delta[actual].get(LAMBDA, set())
            for d in destinos_lambda:
                if d not in clausura:
                    clausura.add(d)
                    pila.append(d)
        return clausura

    def acepta_cadena(self, cadena: str) -> bool:
        """Evalúa si la cadena dada pertenece al lenguaje reconocido por el AFN-λ."""
        # Conjunto inicial: λ-clausura del estado inicial
        estados_actuales = self.lambda_clausura({self.q0})

        # Procesar símbolo a símbolo
        for simbolo in cadena:
            if simbolo not in self.Sigma:
                return False  # Símbolo no reconocido en el alfabeto
            siguientes = set()
            for q in estados_actuales:
                siguientes.update(self.delta[q].get(simbolo, set()))
            estados_actuales = self.lambda_clausura(siguientes)
            if not estados_actuales:
                return False

        # Se acepta si algún estado alcanzado es final
        return bool(estados_actuales.intersection(self.F))


# =====================================================================
# Motor de Thompson / Teorema de Kleene I (Rodrigo De Castro)
# =====================================================================

class _FragmentoAFN:
    """Estructura auxiliar intermedia para la construcción recursiva."""
    def __init__(self, start: int, accept: int, transitions: List[Tuple[int, str, int]]):
        self.start = start
        self.accept = accept
        self.transitions = transitions


class GeneradorAFN:
    """
    Parsea una expresión regular y construye el AFN-λ siguiendo
    el Teorema de Kleene I (Construcción inductiva de Thompson).
    """

    def __init__(self):
        self._state_counter = 0

    def _nuevo_estado(self) -> int:
        s = self._state_counter
        self._state_counter += 1
        return s

    def _normalizar_regex(self, er: str) -> str:
        r"""
        Limpia y estandariza símbolos de la expresión regular:
        - Soporta 'U', 'u', o '|' como operador de unión.
        - Soporta '\L', '\lambda', 'lambda', 'eps' como λ.
        """
        er = er.strip()
        reemplazos = [
            ("\\lambda", LAMBDA),
            ("\\L", LAMBDA),
            ("lambda", LAMBDA),
            ("eps", LAMBDA),
        ]
        for viejo, nuevo in reemplazos:
            er = er.replace(viejo, nuevo)

        res = []
        i = 0
        while i < len(er):
            c = er[i]
            if c in ("U", "u", "|"):
                res.append("|")
            else:
                res.append(c)
            i += 1
        return "".join(res)

    def _insertar_concatenacion_explicita(self, er: str) -> str:
        """
        Inserta el operador de concatenación explícita '·' donde corresponda:
        Ejemplo: 'ab' -> 'a·b', 'a(b)' -> 'a·(b)', '(a)b' -> '(a)·b', 'a*b' -> 'a*·b'
        """
        res = []
        longitud = len(er)
        for i in range(longitud):
            c1 = er[i]
            res.append(c1)
            if i + 1 < longitud:
                c2 = er[i + 1]

                es_c1_fin = c1 not in ("|", "(", "·")
                es_c2_ini = c2 not in ("|", ")", "*", "+", "·")

                if es_c1_fin and es_c2_ini:
                    res.append("·")

        return "".join(res)

    def _infijo_a_postfijo(self, er: str) -> List[str]:
        """
        Algoritmo Shunting-Yard para convertir la expresión regular infija
        a notación postfija (Reverse Polish Notation).
        Precedencia:
          3: '*', '+' (clausuras, mayor)
          2: '·' (concatenación)
          1: '|' (unión, menor)
        """
        precedencia = {"*": 3, "+": 3, "·": 2, "|": 1}
        salida: List[str] = []
        operadores: List[str] = []

        i = 0
        while i < len(er):
            c = er[i]

            if c.isalnum() or c == LAMBDA or c in ("#", "@", "_"):
                salida.append(c)
            elif c == "(":
                operadores.append(c)
            elif c == ")":
                while operadores and operadores[-1] != "(":
                    salida.append(operadores.pop())
                if operadores and operadores[-1] == "(":
                    operadores.pop()
                else:
                    raise ValueError("Paréntesis desbalanceados en la expresión regular.")
            elif c in precedencia:
                while (
                    operadores
                    and operadores[-1] != "("
                    and precedencia.get(operadores[-1], 0) >= precedencia[c]
                ):
                    salida.append(operadores.pop())
                operadores.append(c)
            elif c.isspace():
                pass
            else:
                salida.append(c)
            i += 1

        while operadores:
            op = operadores.pop()
            if op == "(":
                raise ValueError("Paréntesis desbalanceados en la expresión regular.")
            salida.append(op)

        return salida

    def construir_afn(self, er_texto: str) -> AFNLambda:
        """
        Construye el AFN-λ a partir del texto de la expresión regular.
        """
        if not er_texto or er_texto.strip() == "":
            raise ValueError("La expresión regular no puede estar vacía.")

        er_norm = self._normalizar_regex(er_texto)
        er_con_cat = self._insertar_concatenacion_explicita(er_norm)
        postfijo = self._infijo_a_postfijo(er_con_cat)

        self._state_counter = 0
        pila: List[_FragmentoAFN] = []
        alfabeto_detectado: Set[str] = set()

        for token in postfijo:
            if token == "|":
                # Unión: R U S (paralelo)
                if len(pila) < 2:
                    raise ValueError("Error de sintaxis: faltan operandos para la unión '|'.")
                b = pila.pop()
                a = pila.pop()

                nuevo_inicio = self._nuevo_estado()
                nuevo_fin = self._nuevo_estado()

                trans = a.transitions + b.transitions
                trans.append((nuevo_inicio, LAMBDA, a.start))
                trans.append((nuevo_inicio, LAMBDA, b.start))
                trans.append((a.accept, LAMBDA, nuevo_fin))
                trans.append((b.accept, LAMBDA, nuevo_fin))

                pila.append(_FragmentoAFN(nuevo_inicio, nuevo_fin, trans))

            elif token == "·":
                # Concatenación: R · S (serie)
                if len(pila) < 2:
                    raise ValueError("Error de sintaxis: faltan operandos para la concatenación.")
                b = pila.pop()
                a = pila.pop()

                trans = a.transitions + b.transitions
                trans.append((a.accept, LAMBDA, b.start))

                pila.append(_FragmentoAFN(a.start, b.accept, trans))

            elif token == "*":
                # Estrella de Kleene: R*
                if len(pila) < 1:
                    raise ValueError("Error de sintaxis: falta operando para la estrella '*'.")
                a = pila.pop()

                nuevo_inicio = self._nuevo_estado()
                nuevo_fin = self._nuevo_estado()

                trans = list(a.transitions)
                trans.append((nuevo_inicio, LAMBDA, nuevo_fin))
                trans.append((nuevo_inicio, LAMBDA, a.start))
                trans.append((a.accept, LAMBDA, a.start))
                trans.append((a.accept, LAMBDA, nuevo_fin))

                pila.append(_FragmentoAFN(nuevo_inicio, nuevo_fin, trans))

            elif token == "+":
                # Clausura positiva: R+
                if len(pila) < 1:
                    raise ValueError("Error de sintaxis: falta operando para el '+'.")
                a = pila.pop()

                nuevo_inicio = self._nuevo_estado()
                nuevo_fin = self._nuevo_estado()

                trans = list(a.transitions)
                trans.append((nuevo_inicio, LAMBDA, a.start))
                trans.append((a.accept, LAMBDA, a.start))
                trans.append((a.accept, LAMBDA, nuevo_fin))

                pila.append(_FragmentoAFN(nuevo_inicio, nuevo_fin, trans))

            else:
                # Símbolo básico: a ∈ Σ o λ
                s_ini = self._nuevo_estado()
                s_fin = self._nuevo_estado()
                simbolo = token
                if simbolo != LAMBDA:
                    alfabeto_detectado.add(simbolo)
                trans = [(s_ini, simbolo, s_fin)]
                pila.append(_FragmentoAFN(s_ini, s_fin, trans))

        if len(pila) != 1:
            raise ValueError("Expresión regular mal formada.")

        fragmento_final = pila.pop()

        return self._renombrar_canonicamente(
            fragmento_final, sorted(alfabeto_detectado), er_texto
        )

    def _renombrar_canonicamente(
        self,
        frag: _FragmentoAFN,
        alfabeto: List[str],
        er_texto: str,
    ) -> AFNLambda:
        """
        Renumera los estados numéricos dispersos a q0, q1, ..., qn
        asegurando que q0 sea siempre el estado inicial.
        """
        mapa_nombres: Dict[int, str] = {}
        cola = deque([frag.start])
        mapa_nombres[frag.start] = "q0"
        contador = 1

        ady: Dict[int, List[int]] = {}
        for u, _, v in frag.transitions:
            ady.setdefault(u, []).append(v)

        while cola:
            u = cola.popleft()
            for v in ady.get(u, []):
                if v not in mapa_nombres:
                    mapa_nombres[v] = f"q{contador}"
                    contador += 1
                    cola.append(v)

        todos_los_estados_raw = {frag.start, frag.accept}
        for u, _, v in frag.transitions:
            todos_los_estados_raw.add(u)
            todos_los_estados_raw.add(v)

        for s in sorted(todos_los_estados_raw):
            if s not in mapa_nombres:
                mapa_nombres[s] = f"q{contador}"
                contador += 1

        lista_estados = sorted(mapa_nombres.values(), key=lambda x: int(x[1:]))

        nuevas_transiciones = [
            (mapa_nombres[u], symb, mapa_nombres[v])
            for u, symb, v in frag.transitions
        ]

        nuevas_transiciones.sort(
            key=lambda t: (int(t[0][1:]), t[1], int(t[2][1:]))
        )

        return AFNLambda(
            estados=lista_estados,
            alfabeto=alfabeto,
            estado_inicial="q0",
            estados_finales={mapa_nombres[frag.accept]},
            transiciones=nuevas_transiciones,
            expresion_original=er_texto,
        )
