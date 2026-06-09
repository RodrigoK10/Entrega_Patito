# Documentación — Compilador Patito

## Índice

1. [Descripción del lenguaje](#1-descripción-del-lenguaje)
2. [Gramática BNF](#2-gramática-bnf)
3. [Cubo Semántico](#3-cubo-semántico)
4. [Mapa de Direcciones Virtuales](#4-mapa-de-direcciones-virtuales)
5. [Puntos Neurálgicos del Compilador](#5-puntos-neurálgicos-del-compilador)
6. [Generación de Cuádruplos para Funciones](#6-generación-de-cuádruplos-para-funciones)
7. [Memoria de Ejecución — Estructura y Acceso](#7-memoria-de-ejecución--estructura-y-acceso)
8. [Máquina Virtual — Ciclo de Interpretación](#8-máquina-virtual--ciclo-de-interpretación)
9. [Test Cases](#9-test-cases)
10. [Estructura de Archivos](#10-estructura-de-archivos)

---

## 1. Descripción del lenguaje

**Patito** es un lenguaje imperativo con tipado estático diseñado para ilustrar los conceptos fundamentales de compiladores: análisis léxico/sintáctico, semántica de tipos, generación de código intermedio y ejecución por máquina virtual.

| Característica | Detalle |
|---|---|
| Tipos de dato | `entero`, `flotante` (+ `bool` interno para condiciones) |
| Ámbito de variables | Global y local por función |
| Flujo de control | `si/sino/fin_si`, `mientras/haz/fin_mientras` |
| Funciones | Declaradas con parámetros tipados; pueden ser `nula` o retornar `entero`/`flotante` con `regresa` |
| Salida | `imprime(expr)` — imprime expresiones y cadenas literales |
| Comentarios | `# texto` — hasta fin de línea |

---

## 2. Gramática BNF

Gramática completa en su versión final. Las acciones semánticas se describen en §5.

```
<programa>        → programa ID ; <prog_goto> <vars> <funcion_list> <principal>

<prog_goto>       → ε                               (* emite GOTO inicial *)

<vars>            → vars { <var_decl_list> }
                  | ε

<var_decl_list>   → <var_decl_list> <var_decl>
                  | <var_decl>

<var_decl>        → <tipo> <id_list> ;

<id_list>         → <id_list> , ID
                  | ID

<tipo>            → entero
                  | flotante

<funcion_list>    → <funcion_list> <funcion>
                  | ε

<funcion>         → funcion <funcion_decl> ( <param_list> ) <vars_local> <cuerpo_func>

<funcion_decl>    → ID           (* función nula - sin valor de retorno *)
                  | ID : <tipo>  (* función tipada - retorna entero o flotante *)

<param_list>      → <param_list> , <param_decl>
                  | <param_decl>
                  | ε

<param_decl>      → ID : <tipo>

<vars_local>      → vars { <var_decl_list> }
                  | ε

<cuerpo_func>     → { <estatuto_list> }   (* emite ENDFUNC; resetea memoria local *)

<principal>       → <marca_principal> ( ) <cuerpo> <end_principal>

<marca_principal> → principal             (* rellena GOTO inicial; fija inicio global *)

<end_principal>   → fin                  (* emite END *)

<cuerpo>          → { <estatuto_list> }

<estatuto_list>   → <estatuto_list> <estatuto>
                  | ε

<estatuto>        → <asignacion>
                  | <condicion>
                  | <ciclo>
                  | <imprime>
                  | <llamada_funcion>
                  | <regresa_stmt>

<asignacion>      → ID = <expresion> ;
                  | ID = <asig_llamada> ;     (* asignación desde función tipada *)

<asig_llamada>    → <asig_era> ( <arg_list> )

<asig_era>        → ID                        (* solo funciones con valor de retorno *)

<regresa_stmt>    → regresa <expresion> ;     (* solo en funciones tipadas *)

<condicion>       → <si_cond> <cuerpo> fin_si
                  | <si_cond> <cuerpo> <si_sino> <cuerpo> fin_si

<si_cond>         → si ( <expresion> ) entonces   (* emite GOTOF *)

<si_sino>         → sino                          (* emite GOTO; rellena GOTOF *)

<ciclo>           → <mientras_cond> <cuerpo> fin_mientras

<mientras_inicio> → mientras                      (* guarda IP de retorno *)

<mientras_cond>   → <mientras_inicio> ( <expresion> ) haz   (* emite GOTOF *)

<imprime>         → imprime ( <print_list> ) ;

<print_list>      → <print_list> , <print_item>
                  | <print_item>

<print_item>      → <expresion>
                  | CTE_STRING

<llamada_funcion> → <llamada_era> ( <arg_list> ) ;

<llamada_era>     → ID          (* emite ERA; registra llamada en pila *)

<arg_list>        → <arg_list> , <arg>
                  | <arg>
                  | ε

<arg>             → <expresion>  (* valida tipo; emite PARAM *)

<expresion>       → <exp>
                  | <exp> < <exp>
                  | <exp> > <exp>
                  | <exp> == <exp>
                  | <exp> != <exp>

<exp>             → <exp> + <termino>
                  | <exp> - <termino>
                  | <termino>

<termino>         → <termino> * <factor>
                  | <termino> / <factor>
                  | <factor>

<factor>          → ( <expresion> )
                  | ID
                  | CTE_ENTERO
                  | CTE_FLOTANTE
                  | - <factor>
```

---

## 3. Cubo Semántico

El cubo semántico (`semantic_cube.py`) valida en tiempo de compilación si una operación entre dos tipos es legal y determina el tipo resultado. Se implementa como un diccionario `(tipo_izq, operador, tipo_der) → tipo_resultado`; si la clave no existe el resultado es `None` y se lanza error.

### Operaciones aritméticas

| Izq | Op | Der | Resultado |
|---|---|---|---|
| entero | + − × | entero | entero |
| entero | / | entero | **flotante** |
| flotante | + − × / | flotante | flotante |
| entero | + − × / | flotante | flotante |
| flotante | + − × / | entero | flotante |

### Operaciones relacionales

| Izq | Op | Der | Resultado |
|---|---|---|---|
| entero | < > == != | entero | bool |
| flotante | < > == != | flotante | bool |
| entero | < > == != | flotante | bool |
| flotante | < > == != | entero | bool |

### Asignaciones

| Destino | Op | Fuente | Resultado |
|---|---|---|---|
| entero | = | entero | entero |
| flotante | = | flotante | flotante |
| flotante | = | entero | flotante |
| entero | = | flotante | **inválido** |

---

## 4. Mapa de Direcciones Virtuales

El `MemoryManager` asigna una **dirección virtual** (entero) a cada variable, temporal y constante durante la compilación. Esa dirección es el único identificador que aparece en los cuádruplos y es el índice directo en la memoria de ejecución de la VM.

```
┌─────────────────────────────────────────────────────────────┐
│  Segmento    │  Tipo      │  Rango de direcciones virtuales  │
├─────────────────────────────────────────────────────────────┤
│  Retorno     │  cualquiera│    999  (registro de retorno)    │
├─────────────────────────────────────────────────────────────┤
│  Global      │  entero    │   1000 –  1999                   │
│              │  flotante  │   2000 –  2999                   │
│              │  bool      │   3000 –  3999                   │
├─────────────────────────────────────────────────────────────┤
│  Local       │  entero    │   4000 –  4999  (por frame)      │
│  (función)   │  flotante  │   5000 –  5999  (por frame)      │
│              │  bool      │   6000 –  6999  (por frame)      │
├─────────────────────────────────────────────────────────────┤
│  Temporal    │  entero    │   7000 –  7999  (por frame)      │
│  (función)   │  flotante  │   8000 –  8999  (por frame)      │
│              │  bool      │   9000 –  9999  (por frame)      │
├─────────────────────────────────────────────────────────────┤
│  Constante   │  entero    │  10000 – 10999                   │
│              │  flotante  │  11000 – 11999                   │
│              │  bool      │  12000 – 12999                   │
│              │  string    │  13000 – 13999                   │
└─────────────────────────────────────────────────────────────┘
```

**Asignación de constantes:** `asignar_constante(valor, tipo)` usa un diccionario `{(valor, tipo) → addr}` para garantizar que la misma constante literal comparta dirección en todo el programa.

**Reset local:** al terminar de compilar una función, `reset_local()` reinicia los contadores local y temporal a sus valores de inicio. Esto permite que la siguiente función reutilice el mismo rango numérico, lo cual es correcto porque en ejecución cada llamada tiene su propio frame independiente.

---

## 5. Puntos Neurálgicos del Compilador

Los puntos neurálgicos son las acciones semánticas incrustadas en las reglas del parser que producen cuádruplos y mantienen las estructuras de compilación.

### PN-1 — Salto inicial del programa (`p_prog_goto`)

Se emite el cuádruplo `GOTO _ _ ?` (índice 0) cuyo destino queda pendiente. El índice se apila en `_saltos`. Garantiza que la ejecución salte sobre todos los cuerpos de funciones declaradas antes de `principal`.

### PN-2 — Declaración de función (`p_funcion_decl`)

1. Emite `GOTO _ _ ?` para saltar el cuerpo de esta función; apila el índice.
2. Registra la función en `FunctionDirectory` (lanza excepción si ya existe).
3. Cambia `_scope_actual` al nombre de la función.
4. Registra `inicio = cuadruplos.siguiente()` en `FunctionInfo`.

### PN-3 — Fin de función (`p_funcion`)

Al completarse `cuerpo_func` (que ya emitió `ENDFUNC` y llamó `mem_mgr.reset_local()`), se desapila el índice del GOTO de PN-2 y se rellena con `cuadruplos.siguiente()`.

### PN-4 — Inicio de `principal` (`p_marca_principal`)

1. Desapila el índice del GOTO de PN-1 y lo rellena con `cuadruplos.siguiente()`.
2. Fija `FunctionInfo["global"].inicio = cuadruplos.siguiente()` — la VM usará este valor como IP inicial.

### PN-5 — Asignación (`p_asignacion`)

1. Busca dirección virtual y tipo del identificador (scope local → global).
2. Desapila dirección y tipo de la expresión evaluada.
3. Consulta cubo semántico con `(tipo_var, '=', tipo_expr)`; si es `None`, lanza error.
4. Emite `= val_addr _ var_addr`.

### PN-6 — Condicional `si/sino`

- **`si_cond`**: desapila condición bool; emite `GOTOF cond _ ?`; apila índice.
- **Sin `sino`**: al llegar a `fin_si`, desapila y rellena GOTOF con `siguiente()`.
- **Con `sino`**: al llegar a `sino`, emite `GOTO _ _ ?` (índice A); rellena el GOTOF previo; apila A. Al llegar a `fin_si`, desapila A y lo rellena.

### PN-7 — Ciclo `mientras`

- **`mientras_inicio`**: apila `siguiente()` (IP de retorno al inicio de la condición).
- **`mientras_cond`**: desapila condición bool; emite `GOTOF cond _ ?`; apila el índice del GOTOF.
- **`ciclo`**: desapila el GOTOF y el IP de retorno; emite `GOTO _ _ inicio_ciclo`; rellena GOTOF con `siguiente()`.

### PN-8 — Preparación de llamada — ERA (`p_llamada_era`)

1. Verifica que la función exista en `FunctionDirectory`.
2. Emite `ERA nombre _ _`.
3. Empuja `(nombre, 0)` en `_func_call_stack`.

### PN-9 — Paso de argumento — PARAM (`p_arg`)

1. Consulta `_func_call_stack[-1]` para nombre y contador actual.
2. Verifica que no se excedan los parámetros declarados.
3. Obtiene la dirección virtual del parámetro desde `FunctionDirectory`.
4. Desapila dirección y tipo del argumento.
5. Valida compatibilidad de tipos vía cubo semántico.
6. Emite `PARAM arg_addr _ param_addr`.
7. Incrementa el contador.

### PN-10 — Invocación — GOSUB (`p_llamada_funcion`)

1. Desapila `(nombre, n_args)` de `_func_call_stack`.
2. Verifica `n_args == len(fi.parameters)`.
3. Emite `GOSUB nombre _ fi.inicio`.

### PN-11 — Fin de cuerpo de función (`p_cuerpo_func`)

1. Emite `ENDFUNC _ _ _`.
2. Llama `mem_mgr.reset_local()`.
3. Restaura `_scope_actual = "global"`.

---

## 6. Generación de Cuádruplos para Funciones

### Tabla de códigos de operación

| Opcode | Izquierdo | Derecho | Resultado | Descripción |
|---|---|---|---|---|
| `ERA` | nombre_func | — | — | Prepara el Activation Record |
| `PARAM` | addr_argumento | — | addr_parámetro | Copia argumento al staging buffer |
| `GOSUB` | nombre_func | — | ip_inicio | Salta al inicio de la función |
| `ENDFUNC` | — | — | — | Regresa al llamador |
| `=` | addr_src | — | addr_dst | Asignación |
| `+` `−` `*` `/` | addr_izq | addr_der | addr_tmp | Aritmética |
| `<` `>` `==` `!=` | addr_izq | addr_der | addr_tmp | Relacional → bool |
| `GOTOF` | addr_bool | — | ip_destino | Salta si falso |
| `GOTOT` | addr_bool | — | ip_destino | Salta si verdadero |
| `GOTO` | — | — | ip_destino | Salto incondicional |
| `PRINT` | addr | — | — | Imprime el valor |
| `END` | — | — | — | Fin del programa |

### Secuencia para `sumar(3, 4)` donde `a`→4000, `b`→4001

```
ERA    sumar      _      _
PARAM  10000      _      4000    # constante 3 → parámetro a
PARAM  10001      _      4001    # constante 4 → parámetro b
GOSUB  sumar      _      <ip_inicio_sumar>
```

---

## 7. Memoria de Ejecución — Estructura y Acceso

### Descripción de `MemoriaEjecucion` (`virtual_machine.py`)

`MemoriaEjecucion` es la estructura central de la VM en tiempo de ejecución. Divide la memoria en cuatro segmentos; cada uno se implementa con un `dict` de Python que mapea `dirección_virtual → valor`.

```python
class MemoriaEjecucion:
    _global    : dict[int, Any]        # Variables globales (únicas)
    _local     : list[dict[int, Any]]  # Pila de frames locales
    _temporal  : list[dict[int, Any]]  # Pila de frames temporales
    _constante : dict[int, Any]        # Constantes (sólo lectura)
```

### Representación gráfica

```
╔══════════════════════════════════════════════════════════════════╗
║              MEMORIA DE EJECUCIÓN — Patito VM                   ║
╠══════════════════════════════════════════════════════════════════╣
║  _constante  (dict único, inmutable en ejecución)               ║
║  ┌──────────────────────────────────────────────────────────┐   ║
║  │ 10000:3  10001:4  10002:5  13000:"Hola"  13001:"Suma:"  │   ║
║  └──────────────────────────────────────────────────────────┘   ║
╠══════════════════════════════════════════════════════════════════╣
║  _global  (dict único)                                          ║
║  ┌──────────────────────────────────────────────────────────┐   ║
║  │ 1000:10  1001:20  1002:30  2000:15.0                     │   ║
║  └──────────────────────────────────────────────────────────┘   ║
╠══════════════════════════════════════════════════════════════════╣
║  _local  (pila de frames)          _temporal  (pila de frames)  ║
║  ┌────────────────────────┐        ┌────────────────────────┐   ║
║  │ frame[-1]  ← ACTIVO    │        │ frame[-1]  ← ACTIVO    │   ║
║  │  4000:3   4001:4       │        │  7000:7                │   ║
║  ├────────────────────────┤        ├────────────────────────┤   ║
║  │ frame[-2]  (llamador)  │        │ frame[-2]              │   ║
║  │  {}  (frame global)    │        │  {}                    │   ║
║  └────────────────────────┘        └────────────────────────┘   ║
║         ▲ push_frame() / pop_frame() gestiona la pila ▲         ║
╚══════════════════════════════════════════════════════════════════╝
```

### Cómo las Direcciones Virtuales indexan la memoria

El método `_frame(addr)` traduce cualquier dirección virtual al diccionario correcto en tiempo O(1), sin tabla de símbolos ni nombres de variables:

```python
def _frame(self, addr: int) -> dict:
    if addr < 4000:      return self._global       # 1000–3999
    if addr < 7000:      return self._local[-1]    # 4000–6999 → frame activo
    if addr < 10000:     return self._temporal[-1] # 7000–9999 → frame activo
    return self._constante                          # 10000+
```

Dado que los rangos son disjuntos y fijos en compilación, el cuádruplo `+ 1000 1001 7000` ejecuta directamente `_global[7000] = _global[1000] + _global[1001]` sin búsquedas adicionales.

Los segmentos **Local** y **Temporal** son *por frame*: cada llamada a función apila dicts vacíos nuevos. Al regresar, se desapilan. Dos llamadas al mismo procedimiento no interfieren aunque usen las mismas direcciones numéricas.

### Métodos de acceso principales

| Método | Descripción |
|---|---|
| `leer(addr)` | Lee el valor; lanza `RuntimeError` si la dirección no fue inicializada |
| `escribir(addr, valor)` | Escribe el valor; lanza error si se intenta escribir en constantes |
| `push_frame()` | Apila dicts vacíos en `_local` y `_temporal` para una nueva llamada |
| `pop_frame()` | Desapila los frames del tope al retornar de una función |
| `cargar_staging(staging)` | Copia el staging buffer al frame recién creado (paso de parámetros) |

### Protocolo de llamada a función

```
Cuádruplos ERA / PARAM acumulan staging buffer:

  ERA   sumar  →  _staging = {}
  PARAM 10000 _ 4000  →  _staging[4000] = mem.leer(10000)  # = 3
  PARAM 10001 _ 4001  →  _staging[4001] = mem.leer(10001)  # = 4

GOSUB:
  1. _call_stack.push((ip+1, nombre_func))
  2. push_frame()        →  _local.append({}),  _temporal.append({})
  3. cargar_staging()    →  _local[-1] = {4000:3, 4001:4}
  4. _staging = {}
  5. _ip = ip_inicio_función

ENDFUNC:
  1. ret_ip, _ = _call_stack.pop()
  2. pop_frame()         →  _local.pop(),  _temporal.pop()
  3. _ip = ret_ip
```

El **staging buffer** (`_staging: dict`) es necesario porque los argumentos se leen del frame actual *antes* de crear el frame nuevo. Sin él, `push_frame()` cambiaría el frame activo y `leer()` leería desde el frame vacío recién creado.

---

## 8. Máquina Virtual — Ciclo de Interpretación

`VirtualMachine` recibe `(func_dir, cuadruplos, mem_mgr)` del compilador. Su constructor:

1. Reconstruye la tabla de constantes desde `mem_mgr._constantes` y la carga en `MemoriaEjecucion`.
2. Obtiene el IP inicial de `func_dir.functions["global"].inicio`.

### Algoritmo

```
ip ← func_dir["global"].inicio

mientras ip < len(cuádruplos):
    q ← cuádruplos[ip]
    según q.operador:
        END      → terminar
        =        → escribir(q.resultado, leer(q.izquierdo))
        +−×/     → escribir(q.resultado, leer(q.izq) op leer(q.der))
        <>=!     → escribir(q.resultado, leer(q.izq) cmp leer(q.der))
        GOTO     → ip = q.resultado ; continuar
        GOTOF    → si ¬leer(q.izq): ip = q.resultado ; continuar
        GOTOT    → si  leer(q.izq): ip = q.resultado ; continuar
        PRINT    → print(leer(q.izquierdo))
        ERA      → _staging = {}
        PARAM    → _staging[q.resultado] = leer(q.izquierdo)
        GOSUB    → call_stack.push(ip+1) ; push_frame()
                   cargar_staging() ; ip = q.resultado ; continuar
        ENDFUNC  → ip = call_stack.pop()[0] ; pop_frame() ; continuar
    ip += 1
```

---

## 9. Test Cases

Los test cases se ejecutan con `python3 main.py`. Se muestran los cuádruplos generados y la salida de la VM.

---

### TC-1: Hola mundo

**Propósito:** verificar salida de strings y expresiones aritméticas simples.

```patito
programa tc1;
principal ()
{
    imprime("Hola Patito");
    imprime(3 + 4);
}
fin
```

**Cuádruplos:**
```
[  0] GOTO     None       None       1
[  1] PRINT    13000      None       None    # "Hola Patito" → dir constante string
[  2] +        10000      10001      7000    # 3 + 4 → temporal entero
[  3] PRINT    7000       None       None
[  4] END      None       None       None
```

**Salida:**
```
Hola Patito
7
```

---

### TC-2: Variables globales y aritmética mixta

**Propósito:** declaración global, asignación, aritmética entero/flotante, cubo semántico.

```patito
programa tc2;
vars { entero x, y, suma;  flotante promedio; }
principal ()
{
    x = 10;  y = 20;
    suma = x + y;
    promedio = suma / 2;
    imprime("Suma:");    imprime(suma);
    imprime("Promedio:"); imprime(promedio);
}
fin
```

**Salida:**
```
Suma:
30
Promedio:
15.0
```

*Nota:* `entero / entero → flotante` según el cubo semántico; por eso el temporal de `suma/2` cae en el rango 8000–8999 (temporal flotante) y `promedio` en 2000–2999 (global flotante).

---

### TC-3: Condicional si/sino

**Propósito:** control de flujo con decisión y ambas ramas.

```patito
programa tc3;
vars { entero n; }
principal ()
{
    n = 7;
    si (n > 5) entonces { imprime("Mayor que 5"); }
    sino                { imprime("Menor o igual a 5"); }
    fin_si
}
fin
```

**Cuádruplos clave:**
```
[  2] >        1000       10001      9000    # n > 5 → bool temporal
[  3] GOTOF    9000       None       6       # si falso → rama sino
[  4] PRINT    13000      ...                # "Mayor que 5"
[  5] GOTO     None       None       7       # saltar sino
[  6] PRINT    13001      ...                # "Menor o igual a 5"
```

**Salida:**
```
Mayor que 5
```

---

### TC-4: Ciclo mientras (suma 1…5)

**Propósito:** ciclo con condición, acumulación.

```patito
programa tc4;
vars { entero i, acum; }
principal ()
{
    i = 1;  acum = 0;
    mientras (i < 6) haz { acum = acum + i;  i = i + 1; }
    fin_mientras
    imprime("Suma 1..5:");  imprime(acum);
}
fin
```

**Salida:**
```
Suma 1..5:
15
```

---

### TC-5: Declaración e invocación de función

**Propósito:** ERA / PARAM / GOSUB / ENDFUNC, paso de parámetros, múltiples llamadas.

```patito
programa tc5;
vars { entero resultado; }
funcion sumar (a : entero, b : entero) { imprime(a + b); }
principal ()
{
    sumar(3, 4);
    resultado = 10;
    sumar(resultado, 5);
}
fin
```

**Salida:**
```
7
15
```

---

### TC-6: Función con variable local y ciclo interno

**Propósito:** variables locales en función, ciclo dentro de función.

```patito
programa tc6;
funcion tabla (n : entero)
vars { entero i; }
{
    i = 1;
    mientras (i < 11) haz { imprime(n * i);  i = i + 1; }
    fin_mientras
}
principal () { imprime("Tabla del 3:");  tabla(3); }
fin
```

**Salida:**
```
Tabla del 3:
3  6  9  12  15  18  21  24  27  30
```

---

### TC-7: Dos funciones — máximo y mínimo

**Propósito:** múltiples funciones, condicional dentro de función, reutilización de direcciones locales.

```patito
programa tc7;
vars { entero a, b; }
funcion maximo (x : entero, y : entero)
{
    si (x > y) entonces { imprime(x); } sino { imprime(y); } fin_si
}
funcion minimo (x : entero, y : entero)
{
    si (x < y) entonces { imprime(x); } sino { imprime(y); } fin_si
}
principal ()
{
    a = 8;  b = 13;
    imprime("Max:");  maximo(a, b);
    imprime("Min:");  minimo(a, b);
}
fin
```

**Salida:**
```
Max:
13
Min:
8
```

*Nota:* `maximo` y `minimo` usan las mismas direcciones 4000 y 4001 para sus parámetros `x` e `y`. Esto es correcto porque cada llamada crea un frame independiente y `reset_local()` reinicia los contadores entre funciones en compilación.

---

### TC-8: Error semántico — asignación de tipo incompatible

**Propósito:** verificar que el cubo semántico rechaza asignar `flotante` a `entero`.

```patito
programa tc8;
vars { entero x;  flotante y; }
principal () { x = y; }
fin
```

**Error capturado en compilación:**
```
Asignación inválida: no se puede asignar flotante a entero
```

---

### TC-9: Error semántico — variable no declarada

**Propósito:** verificar búsqueda en tablas de símbolos local y global.

```patito
programa tc9;
principal () { imprime(z); }
fin
```

**Error capturado en compilación:**
```
Variable no declarada: 'z'
```

---

### TC-10: Factorial en principal (iterativo, n = 6)

**Propósito:** prueba obligatoria — factorial calculado directamente en `principal` con ciclo `mientras`.

```patito
programa tc10;
vars { entero n, resultado, i; }
principal ()
{
    n = 6;
    resultado = 1;
    i = 1;
    mientras (i < n + 1) haz
    {
        resultado = resultado * i;
        i = i + 1;
    }
    fin_mientras
    imprime("Factorial de 6 (en principal):");
    imprime(resultado);
}
fin
```

**Cuádruplos clave:**
```
[  4] +        1000       10001      7000    # n + 1 → temporal
[  5] <        1002       7000       9000    # i < (n+1) → bool
[  6] GOTOF    9000       None       12      # salir si i >= n+1
[  7] *        1001       1002       7001    # resultado * i
[  8] =        7001       None       1001    # resultado = tmp
[  9] +        1002       10001      7002    # i + 1
[ 10] =        7002       None       1002    # i = tmp
[ 11] GOTO     None       None       4       # volver a condición
```

**Salida:**
```
Factorial de 6 (en principal):
720
```

---

### TC-11: Factorial en función (cíclico), múltiples llamadas

**Propósito:** prueba obligatoria — factorial encapsulado en función, llamada tres veces con distintos argumentos.

```patito
programa tc11;
funcion factorial (n : entero)
vars { entero resultado, i; }
{
    resultado = 1;
    i = 1;
    mientras (i < n + 1) haz
    {
        resultado = resultado * i;
        i = i + 1;
    }
    fin_mientras
    imprime(resultado);
}
principal ()
{
    imprime("Factorial de 5:");  factorial(5);
    imprime("Factorial de 6:");  factorial(6);
    imprime("Factorial de 7:");  factorial(7);
}
fin
```

**Cuádruplos del cuerpo de `factorial`** (dirs: `n`→4000, `resultado`→4001, `i`→4002):
```
[  2] =        10000      None       4001    # resultado = 1
[  3] =        10000      None       4002    # i = 1
[  4] +        4000       10000      7000    # n + 1
[  5] <        4002       7000       9000    # i < (n+1)
[  6] GOTOF    9000       None       12
[  7] *        4001       4002       7001    # resultado * i
[  8] =        7001       None       4001
[  9] +        4002       10000      7002    # i + 1
[ 10] =        7002       None       4002
[ 11] GOTO     None       None       4
[ 12] PRINT    4001       None       None    # imprime resultado
[ 13] ENDFUNC  None       None       None
```

**Salida:**
```
Factorial de 5:
120
Factorial de 6:
720
Factorial de 7:
5040
```

*Demostración del manejo de contexto:* cada llamada crea un frame nuevo con `push_frame()`. Los valores de `resultado` e `i` en la segunda llamada son completamente independientes de la primera; al regresar, `pop_frame()` destruye esos valores. El frame del llamador queda intacto.

---

### TC-12: Serie de Fibonacci en principal (iterativo, 8 términos)

**Propósito:** prueba obligatoria — Fibonacci calculado en `principal` con variables globales y ciclo.

```patito
programa tc12;
vars { entero n, a, b, temp, i; }
principal ()
{
    n = 8;
    a = 0;  b = 1;
    imprime("Fibonacci (8 terminos, en principal):");
    imprime(a);
    imprime(b);
    i = 2;
    mientras (i < n) haz
    {
        temp = a + b;
        a = b;
        b = temp;
        imprime(b);
        i = i + 1;
    }
    fin_mientras
}
fin
```

**Salida:**
```
Fibonacci (8 terminos, en principal):
0
1
1
2
3
5
8
13
```

---

### TC-13: Serie de Fibonacci en función (cíclica), llamada con distintos n

**Propósito:** prueba obligatoria — Fibonacci encapsulado en función, combinando ciclo y condicional dentro de la función.

```patito
programa tc13;
funcion fibonacci (n : entero)
vars { entero a, b, temp, i; }
{
    a = 0;  b = 1;
    imprime(a);
    si (n > 1) entonces
    {
        imprime(b);
        i = 2;
        mientras (i < n) haz
        {
            temp = a + b;
            a = b;
            b = temp;
            imprime(b);
            i = i + 1;
        }
        fin_mientras
    }
    fin_si
}
principal ()
{
    imprime("Fibonacci (5 terminos):");  fibonacci(5);
    imprime("Fibonacci (8 terminos):");  fibonacci(8);
}
fin
```

**Dirs locales:** `n`→4000, `a`→4001, `b`→4002, `temp`→4003, `i`→4004

**Salida:**
```
Fibonacci (5 terminos):
0
1
1
2
3
Fibonacci (8 terminos):
0
1
1
2
3
5
8
13
```

*Demostración:* entre la primera y segunda llamada, `pop_frame()` destruye el frame con los valores de Fibonacci(5); `push_frame()` crea un frame limpio para Fibonacci(8). Los temporales booleanos de la condición `n > 1` y de `i < n` también están en el frame local y se destruyen al regresar.

---

---

### TC-14: Factorial RECURSIVO — función tipada con `regresa`

**Propósito:** prueba obligatoria — función con parámetro que retorna valor, recursividad, `regresa`, registro de retorno (dir. 999).

```patito
programa tc14;
vars { entero res; }

funcion factorial : entero (n : entero)
vars { entero parcial; }
{
    si (n == 0) entonces
    {
        regresa 1;
    }
    fin_si
    parcial = factorial(n - 1);   # llamada recursiva, resultado en dir 999
    regresa n * parcial;
}

principal ()
{
    imprime("Factorial recursivo de 0:");
    res = factorial(0);   imprime(res);
    imprime("Factorial recursivo de 5:");
    res = factorial(5);   imprime(res);
    imprime("Factorial recursivo de 7:");
    res = factorial(7);   imprime(res);
}
fin
```

**Cuádruplos del cuerpo de `factorial`** (`n`→4000, `parcial`→4001):
```
[  2] ==       4000       10000      9000    # n == 0
[  3] GOTOF    9000       None       5       # si n != 0, saltar
[  4] RETURN   10001      None       None    # regresa 1 → escribe 1 en dir 999
[  5] ERA      factorial  None       None    # preparar llamada recursiva
[  6] -        4000       10001      7000    # n - 1
[  7] PARAM    7000       None       4000    # pasa n-1 como argumento
[  8] GOSUB    factorial  None       2       # llamada recursiva
[  9] =        999        None       4001    # parcial = valor de retorno (dir 999)
[ 10] *        4000       4001       7001    # n * parcial
[ 11] RETURN   7001       None       None    # regresa resultado
[ 12] ENDFUNC  None       None       None    # inalcanzable
```

**Cómo funciona el registro de retorno (dir. 999):**
- `RETURN addr` escribe `mem.leer(addr)` en `_global[999]` y luego hace `pop_frame + salto`
- El caller lee 999 con `= 999 _ var_addr` inmediatamente después de que `GOSUB` regresa
- Durante la recursión, cada nivel escribe en 999 justo antes de regresar, y el nivel superior lo lee de inmediato — sin colisión

**Salida:**
```
Factorial recursivo de 0:
1
Factorial recursivo de 5:
120
Factorial recursivo de 7:
5040
```

---

## 10. Estructura de Archivos

```
Entrega_Patito/
├── lexer.py             — Scanner: tokeniza el código fuente
├── symbol_table.py      — VariableInfo, VariableTable
├── function_directory.py — FunctionInfo, FunctionDirectory
├── semantic_cube.py     — Cubo semántico (validación de tipos)
├── memory_manager.py    — Asignador de direcciones virtuales
├── quadruple.py         — Cuadruplo, FilaCuadruplos
├── parser.py            — Parser + puntos neurálgicos + generación de cuádruplos
├── virtual_machine.py   — MemoriaEjecucion, VirtualMachine
├── semantic_analyzer.py — SemanticAnalyzer (auxiliar de entregas previas)
├── main.py              — Test cases TC-1 a TC-14
├── requirements.txt     — Dependencia: ply
└── DOCUMENTACION.md     — Este archivo

## Cómo ejecutar

```bash
pip install ply          # solo la primera vez
python3 main.py          # corre todos los test cases
```
```
