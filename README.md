# Generador de AFN-λ a partir de Expresiones Regulares

Proyecto desarrollado con base en la teoría y metodología del libro **«Teoría de la Computación: lenguajes, autómatas, gramáticas»** de **Rodrigo De Castro Korgi** (Universidad Nacional de Colombia, Bogotá), específicamente:
* **Capítulo 2, Sección 2.4:** Autómatas Finitos No Deterministas (AFN).
* **Capítulo 2, Sección 2.6:** Autómatas con Transiciones Nulas (AFN-$\lambda$).
* **Capítulo 2, Sección 2.8:** Teorema de Kleene (Parte I: Construcción inductiva de Thompson).

El programa recibe una **expresión regular** y genera su **Autómata Finito No Determinista con Transiciones Lambda (AFN-$\lambda$)** en sus 3 representaciones formales:
1. **Grafo** (Diagrama de transiciones visual e interactivo, además de formatos estándar Mermaid y Graphviz DOT).
2. **Matriz de Transiciones** (Tabla de estados $\times$ símbolos de entrada y $\lambda$, indicando $\to$ estado inicial, $*$ estados de aceptación y $\emptyset$ para cómputos abortados).
3. **Función de Transición Formal $\Delta(Q, \Sigma)$** (Especificación formal de la 5-tupla $M = (\Sigma, Q, q_0, F, \Delta)$ y desglose de las imágenes $\Delta(q, s)$).

---

## Estructura de Archivos

* **`index.html`**: Aplicación web visual e interactiva. **No requiere instalar nada**. Ábrela con doble clic en cualquier navegador (Chrome, Edge, Firefox). Permite:
  * Escribir cualquier expresión regular o elegir ejemplos del libro.
  * Ver y mover interactivamente los nodos del grafo (círculos normales, doble círculo para estados finales, flecha para inicio).
  * Consultar la Matriz de Transiciones en una tabla limpia y responsiva.
  * Ver la especificación matemática de la función $\Delta$.
  * Probar cadenas en un **simulador integrado** para comprobar si son aceptadas o rechazadas.
* **`afn_lambda.py`**: Módulo central en Python que implementa:
  * Normalización y preprocesamiento de la expresión regular.
  * Inserción de concatenación explícita.
  * Algoritmo Shunting-Yard (conversión infijo a postfijo).
  * Construcción de Thompson / Kleene I.
  * Renombrado canónico en orden BFS ($q_0, q_1, \dots, q_n$).
  * Formateadores de Grafo, Matriz y Función $\Delta$.
  * Simulador de cadenas mediante cálculo de $\lambda$-clausuras.
* **`main.py`**: Interfaz de línea de comandos (CLI) para ejecutar en terminal.
* **`test_afn.py`**: Batería de pruebas unitarias automatizadas con ejemplos clásicos del libro.

---

## Sintaxis de Expresiones Regulares Soportada

| Operación | Sintaxis en el programa | Ejemplo |
| :--- | :--- | :--- |
| **Símbolos básicos** | Caracteres alfanuméricos | `a`, `b`, `0`, `1` |
| **Cadena vacía ($\lambda$)** | `λ`, `\L`, `\lambda`, `eps` | `λ` |
| **Unión ($R \cup S$)** | `\|` o `U` o `u` | `a\|b` o `aUb` |
| **Concatenación ($RS$)** | Implícita o con punto `.` | `ab` o `a.b` |
| **Estrella de Kleene ($R^*$)** | `*` | `a*`, `(a\|b)*` |
| **Clausura positiva ($R^+$)** | `+` | `a+` |
| **Agrupación** | `(` y `)` | `(a\|b)*b` |

---

## Cómo Ejecutar

### Opción 1: Interfaz Web Visual (Recomendada)
Haz doble clic en el archivo `index.html` o ábrelo en tu navegador favorito:
```bash
start index.html
```

### Opción 2: Línea de Comandos en Python
Puedes pasar la expresión directamente como argumento:
```bash
python main.py "a*(ab|ba)*"
```
O ejecutar sin argumentos para ver el menú interactivo con ejemplos del libro:
```bash
python main.py
```

### Opción 3: Ejecutar las pruebas unitarias
```bash
python test_afn.py
```
