"""
main.py
Programa principal de consola para generar AFN-λ a partir de una Expresión Regular.
Genera:
 1. Grafo (Mermaid y Graphviz DOT)
 2. Matriz de Transiciones
 3. Función formal Δ(Q, Σ ∪ {λ})
"""

import sys
import os
import io

# Asegurar compatibilidad con UTF-8 en terminales de Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from afn_lambda import GeneradorAFN, LAMBDA


def mostrar_menu_ejemplos():
    print("\n--- Ejemplos típicos del libro de Rodrigo De Castro ---")
    print(" 1. a*(ab|ba)*           (Sección 2.9)")
    print(" 2. (a|b)*b              (Cadenas que terminan en 'b')")
    print(" 3. (0|1)*00(0|1)*       (Cadenas que contienen dos ceros)")
    print(" 4. (a|b)*ab(a|b)*       (Cadenas que contienen la subcadena 'ab')")
    print(" 5. a(b|a)*              (Cadenas que inician con 'a')")
    print(" 6. Ingresar mi propia expresión regular")


def procesar_expresion(er: str):
    generador = GeneradorAFN()
    try:
        afn = generador.construir_afn(er)
    except Exception as e:
        print(f"\n[ERROR] No se pudo procesar la expresión regular: {e}")
        return

    print("\n" + "=" * 80)
    print(f" AUTÓMATA FINITO NO DETERMINISTA CON TRANSICIONES LAMBDA (AFN-{LAMBDA})")
    print("=" * 80)
    print(f"Expresión regular: {afn.expresion_original}")
    print(f"Alfabeto Σ:        {afn.Sigma}")
    print(f"Total de estados:  {len(afn.Q)}")

    # -------------------------------------------------------------
    # 1. FUNCIÓN FORMAL Δ(Q, Σ ∪ {λ})
    # -------------------------------------------------------------
    print("\n" + "#" * 80)
    print(" [1] FUNCIÓN DE TRANSICIÓN FORMAL Δ(Q, Σ ∪ {λ})")
    print("#" * 80)
    print(afn.formato_funcion_delta())

    # -------------------------------------------------------------
    # 2. MATRIZ DE TRANSICIONES
    # -------------------------------------------------------------
    print("\n" + "#" * 80)
    print(" [2] MATRIZ (TABLA) DE TRANSICIONES")
    print("#" * 80)
    print(afn.formato_matriz_ascii())

    # -------------------------------------------------------------
    # 3. GRAFO (DIAGRAMA DE TRANSICIONES)
    # -------------------------------------------------------------
    print("\n" + "#" * 80)
    print(" [3] GRAFO DEL AUTÓMATA (DIAGRAMA DE TRANSICIONES)")
    print("#" * 80)
    print("\n--- Código de Grafo en formato Mermaid (renderizable en GitHub / Markdown / Live Editor) ---")
    print("```mermaid")
    print(afn.generar_grafo_mermaid())
    print("```")

    print("\n--- Código de Grafo en formato Graphviz DOT ---")
    print(afn.generar_grafo_dot())

    # -------------------------------------------------------------
    # Opción interactiva para probar cadenas
    # -------------------------------------------------------------
    print("\n" + "-" * 80)
    try:
        probar = input("¿Deseas probar cadenas en este autómata? (s/n): ").strip().lower()
    except EOFError:
        probar = "n"

    if probar == "s":
        print("Ingresa una cadena para evaluar (o presiona ENTER vacío para evaluar λ, 'salir' para terminar):")
        while True:
            try:
                cad = input("Cadena a probar > ")
            except EOFError:
                break
            if cad.lower() == "salir":
                break
            es_valida = afn.acepta_cadena(cad)
            etiqueta = "CADENA VACÍA (λ)" if cad == "" else f"'{cad}'"
            if es_valida:
                print(f"  --> La cadena {etiqueta} es: [ACEPTADA] ✓")
            else:
                print(f"  --> La cadena {etiqueta} es: [RECHAZADA] ✗")


def main():
    if len(sys.argv) > 1:
        # Se pasó la expresión por línea de comandos
        er = " ".join(sys.argv[1:])
        procesar_expresion(er)
    else:
        print("================================================================================")
        print(" GENERADOR DE AFN-λ A PARTIR DE EXPRESIONES REGULARES")
        print(" Teoría de la Computación - Rodrigo De Castro Korgi")
        print("================================================================================")
        mostrar_menu_ejemplos()
        opcion = input("\nSelecciona una opción (1-6): ").strip()

        ejemplos = {
            "1": "a*(ab|ba)*",
            "2": "(a|b)*b",
            "3": "(0|1)*00(0|1)*",
            "4": "(a|b)*ab(a|b)*",
            "5": "a(b|a)*",
        }

        if opcion in ejemplos:
            er = ejemplos[opcion]
            print(f"\nSeleccionado: {er}")
            procesar_expresion(er)
        elif opcion == "6":
            er = input("\nIngresa la expresión regular: ").strip()
            if er:
                procesar_expresion(er)
            else:
                print("No se ingresó ninguna expresión.")
        else:
            # Si el usuario directamente ingresó una expresión en vez del número
            if opcion:
                procesar_expresion(opcion)


if __name__ == "__main__":
    main()
