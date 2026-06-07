# virtual_machine.py - Máquina Virtual para Patito
#
# Mapa de Memoria de Ejecución
# ┌─────────────────────────────────────────────────────────┐
# │  Segmento    │  Tipo     │  Rango de direcciones        │
# ├─────────────────────────────────────────────────────────┤
# │  Global      │  entero   │  1000 – 1999                 │
# │              │  flotante │  2000 – 2999                 │
# │              │  bool     │  3000 – 3999                 │
# ├─────────────────────────────────────────────────────────┤
# │  Local       │  entero   │  4000 – 4999  (por frame)    │
# │              │  flotante │  5000 – 5999  (por frame)    │
# │              │  bool     │  6000 – 6999  (por frame)    │
# ├─────────────────────────────────────────────────────────┤
# │  Temporal    │  entero   │  7000 – 7999  (por frame)    │
# │              │  flotante │  8000 – 8999  (por frame)    │
# │              │  bool     │  9000 – 9999  (por frame)    │
# ├─────────────────────────────────────────────────────────┤
# │  Constante   │  entero   │ 10000 – 10999                │
# │              │  flotante │ 11000 – 11999                │
# │              │  bool     │ 12000 – 12999                │
# │              │  string   │ 13000 – 13999                │
# └─────────────────────────────────────────────────────────┘
#
# Los segmentos Local y Temporal son por frame: cada llamada a función
# apila un nuevo dict vacío; al regresar se desapila. Así, dos llamadas
# al mismo procedimiento no comparten direcciones aunque usen el mismo rango.


class MemoriaEjecucion:
    """
    Memoria de ejecución en tiempo de corrida.

    Estructura:
      _global   : dict[addr -> valor]   — variables globales (1000-3999)
      _local    : list[dict]            — pila de frames locales (4000-6999)
      _temporal : list[dict]            — pila de frames temporales (7000-9999)
      _constante: dict[addr -> valor]   — constantes de compilación (10000-13999)

    Indexación por dirección virtual:
      addr < 4000          → _global
      4000 <= addr < 7000  → _local[-1]   (frame activo)
      7000 <= addr < 10000 → _temporal[-1] (frame activo)
      addr >= 10000        → _constante
    """

    def __init__(self, tabla_constantes: dict):
        """
        tabla_constantes: {addr: valor} generado por MemoryManager en compilación.
        """
        self._global    = {}
        self._local     = [{}]   # frame global inicial (para main)
        self._temporal  = [{}]
        self._constante = dict(tabla_constantes)

    # ── Selección de segmento ──────────────────────────────────────────────

    def _frame(self, addr: int) -> dict:
        if addr < 4000:
            return self._global
        if addr < 7000:
            return self._local[-1]
        if addr < 10000:
            return self._temporal[-1]
        return self._constante

    # ── Lectura / escritura ───────────────────────────────────────────────

    def leer(self, addr: int):
        val = self._frame(addr).get(addr)
        if val is None:
            raise RuntimeError(f"Dirección {addr} sin inicializar")
        return val

    def escribir(self, addr: int, valor):
        if addr >= 10000:
            raise RuntimeError("No se puede escribir en el segmento de constantes")
        self._frame(addr)[addr] = valor

    # ── Gestión de frames (llamadas a función) ─────────────────────────────

    def push_frame(self):
        """Crea un nuevo frame local y temporal para una llamada a función."""
        self._local.append({})
        self._temporal.append({})

    def pop_frame(self):
        """Destruye el frame activo al regresar de una función."""
        if len(self._local) <= 1:
            raise RuntimeError("pop_frame: pila de frames vacía")
        self._local.pop()
        self._temporal.pop()

    # ── Paso de parámetros ─────────────────────────────────────────────────

    def copiar_a_staging(self, src_addr: int, dst_addr: int, staging: dict):
        """
        Copia el valor de src_addr al dict de staging antes de push_frame.
        Se usa para pasar argumentos: el valor se lee del frame actual
        y se almacena en staging para luego escribirlo en el frame nuevo.
        """
        staging[dst_addr] = self.leer(src_addr)

    def cargar_staging(self, staging: dict):
        """
        Escribe el staging en el frame recién creado (el tope de la pila).
        Debe llamarse DESPUÉS de push_frame.
        """
        for addr, val in staging.items():
            self._local[-1][addr] = val

    def __repr__(self):
        return (
            f"Global={self._global}\n"
            f"Local(top)={self._local[-1]}\n"
            f"Temporal(top)={self._temporal[-1]}"
        )


# ─── Máquina Virtual ─────────────────────────────────────────────────────────

class VirtualMachine:
    """
    Interpreta la lista de cuádruplos generada por el compilador de Patito.

    Opcodes soportados:
      Aritméticos : + - * /
      Relacionales: < > == !=
      Asignación  : =
      Saltos      : GOTO  GOTOF  GOTOT
      I/O         : PRINT
      Funciones   : ERA  PARAM  GOSUB  ENDFUNC
      Fin         : END
    """

    def __init__(self, func_dir, cuadruplos, mem_mgr):
        self._func_dir   = func_dir
        self._quads      = cuadruplos._fila     # lista de Cuadruplo
        self._ip         = 0                    # instruction pointer

        # Construir tabla de constantes a partir del MemoryManager compilado
        tabla_cte = {}
        for (valor, _tipo), addr in mem_mgr._constantes.items():
            tabla_cte[addr] = valor
        self._mem = MemoriaEjecucion(tabla_cte)

        # Pila de retorno: (ip_de_regreso, nombre_funcion)
        self._call_stack: list[tuple[int, str]] = []

        # Staging buffer para paso de parámetros (antes del push_frame)
        self._staging: dict = {}

    # ── Bucle de interpretación ───────────────────────────────────────────

    def ejecutar(self):
        inicio = self._func_dir.functions["global"].inicio
        if inicio is None:
            raise RuntimeError("No se encontró el bloque principal")
        self._ip = inicio

        while self._ip < len(self._quads):
            q = self._quads[self._ip]
            op = q.operador

            if op == 'END':
                break
            elif op == '=':
                self._op_asignar(q)
            elif op in ('+', '-', '*', '/'):
                self._op_aritmetico(q)
            elif op in ('<', '>', '==', '!='):
                self._op_relacional(q)
            elif op == 'GOTO':
                self._ip = q.resultado
                continue
            elif op == 'GOTOF':
                self._op_gotof(q)
                continue
            elif op == 'GOTOT':
                self._op_gotot(q)
                continue
            elif op == 'PRINT':
                self._op_print(q)
            elif op == 'ERA':
                self._staging = {}
            elif op == 'PARAM':
                self._op_param(q)
            elif op == 'GOSUB':
                self._op_gosub(q)
                continue
            elif op == 'ENDFUNC':
                self._op_endfunc()
                continue
            else:
                raise RuntimeError(f"Opcode desconocido: '{op}'")

            self._ip += 1

    # ── Operaciones individuales ──────────────────────────────────────────

    def _op_asignar(self, q):
        valor = self._mem.leer(q.izquierdo)
        self._mem.escribir(q.resultado, valor)

    def _op_aritmetico(self, q):
        a = self._mem.leer(q.izquierdo)
        b = self._mem.leer(q.derecho)
        op = q.operador
        if op == '+':
            res = a + b
        elif op == '-':
            res = a - b
        elif op == '*':
            res = a * b
        elif op == '/':
            if b == 0:
                raise RuntimeError("División entre cero")
            res = a / b
        self._mem.escribir(q.resultado, res)

    def _op_relacional(self, q):
        a = self._mem.leer(q.izquierdo)
        b = self._mem.leer(q.derecho)
        op = q.operador
        if op == '<':
            res = a < b
        elif op == '>':
            res = a > b
        elif op == '==':
            res = a == b
        elif op == '!=':
            res = a != b
        self._mem.escribir(q.resultado, res)

    def _op_gotof(self, q):
        cond = self._mem.leer(q.izquierdo)
        if not cond:
            self._ip = q.resultado
        else:
            self._ip += 1

    def _op_gotot(self, q):
        cond = self._mem.leer(q.izquierdo)
        if cond:
            self._ip = q.resultado
        else:
            self._ip += 1

    def _op_print(self, q):
        valor = self._mem.leer(q.izquierdo)
        print(valor)

    def _op_param(self, q):
        # q.izquierdo = dirección del argumento (frame actual)
        # q.resultado = dirección del parámetro (frame destino)
        valor = self._mem.leer(q.izquierdo)
        self._staging[q.resultado] = valor

    def _op_gosub(self, q):
        # Guardar ip de retorno y nombre de función activa
        self._call_stack.append((self._ip + 1, q.izquierdo))
        # Crear frame y cargar parámetros
        self._mem.push_frame()
        self._mem.cargar_staging(self._staging)
        self._staging = {}
        # Saltar al inicio de la función
        self._ip = q.resultado

    def _op_endfunc(self):
        if not self._call_stack:
            raise RuntimeError("ENDFUNC sin llamada activa")
        ret_ip, _ = self._call_stack.pop()
        self._mem.pop_frame()
        self._ip = ret_ip
