# parser.py - Analizador sintáctico y generador de cuádruplos para Patito
import ply.yacc as yacc
from lexer import tokens, lexer
from function_directory import FunctionDirectory
from memory_manager import MemoryManager
from quadruple import FilaCuadruplos
from semantic_cube import SemanticCube

# ─── Estado global del compilador ────────────────────────────────────────────

func_dir        = None
mem_mgr         = None
cuadruplos      = None
sem_cube        = None
_operandos      = []   # (dirección_virtual, tipo)
_saltos         = []   # índices de cuádruplos pendientes de rellenar
_func_call_stack = []  # (nombre_func, índice_arg_actual)
_scope_actual   = "global"
_tipo_actual    = None


def _reset():
    global func_dir, mem_mgr, cuadruplos, sem_cube
    global _operandos, _saltos, _func_call_stack, _scope_actual, _tipo_actual
    func_dir         = FunctionDirectory()
    mem_mgr          = MemoryManager()
    cuadruplos       = FilaCuadruplos()
    sem_cube         = SemanticCube()
    _operandos       = []
    _saltos          = []
    _func_call_stack = []
    _scope_actual    = "global"
    _tipo_actual     = None


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _buscar_var(name):
    if _scope_actual != "global":
        lt = func_dir.functions[_scope_actual].variable_table
        if lt.variable_exists(name):
            v = lt.get_variable(name)
            return v.address, v.var_type
    gt = func_dir.functions["global"].variable_table
    if gt.variable_exists(name):
        v = gt.get_variable(name)
        return v.address, v.var_type
    raise Exception(f"Variable no declarada: '{name}'")


def _declarar_variable(name, tipo):
    if _scope_actual == "global":
        addr = mem_mgr.asignar_global(tipo)
        func_dir.functions["global"].variable_table.add_variable(name, tipo, addr)
    else:
        addr = mem_mgr.asignar_local(tipo)
        fi = func_dir.functions[_scope_actual]
        fi.variable_table.add_variable(name, tipo, addr)
        if tipo == 'entero':
            fi.tam_local_entero += 1
        elif tipo == 'flotante':
            fi.tam_local_flotante += 1


def _declarar_parametro(name, tipo):
    addr = mem_mgr.asignar_local(tipo)
    fi = func_dir.functions[_scope_actual]
    fi.variable_table.add_variable(name, tipo, addr)
    fi.parameters.append({"name": name, "type": tipo, "address": addr})
    if tipo == 'entero':
        fi.tam_local_entero += 1
    elif tipo == 'flotante':
        fi.tam_local_flotante += 1


def _bin_op(op):
    d2, t2 = _operandos.pop()
    d1, t1 = _operandos.pop()
    res_t = sem_cube.get_result_type(t1, op, t2)
    if res_t is None:
        raise Exception(f"Operación inválida: {t1} {op} {t2}")
    tmp = mem_mgr.asignar_temporal(res_t)
    cuadruplos.agregar(op, d1, d2, tmp)
    _operandos.append((tmp, res_t))


# ─── Gramática ───────────────────────────────────────────────────────────────

def p_programa(p):
    'programa : PROGRAMA ID SEMICOLON prog_goto vars funcion_list principal'


def p_prog_goto(p):
    'prog_goto : empty'
    # Cuádruplo 0: GOTO al inicio de principal (se rellena más adelante)
    idx = cuadruplos.agregar('GOTO', None, None, None)
    _saltos.append(idx)


# ─── vars ─────────────────────────────────────────────────────────────────────

def p_vars(p):
    '''vars : VARS LBRACE var_decl_list RBRACE
            | empty'''


def p_var_decl_list_multi(p):
    'var_decl_list : var_decl_list var_decl'


def p_var_decl_list_single(p):
    'var_decl_list : var_decl'


def p_var_decl(p):
    'var_decl : tipo id_list SEMICOLON'


def p_id_list_multi(p):
    'id_list : id_list COMMA ID'
    _declarar_variable(p[3], _tipo_actual)


def p_id_list_single(p):
    'id_list : ID'
    _declarar_variable(p[1], _tipo_actual)


def p_tipo_entero(p):
    'tipo : ENTERO'
    global _tipo_actual
    _tipo_actual = 'entero'


def p_tipo_flotante(p):
    'tipo : FLOTANTE'
    global _tipo_actual
    _tipo_actual = 'flotante'


# ─── funciones ───────────────────────────────────────────────────────────────

def p_funcion_list_multi(p):
    'funcion_list : funcion_list funcion'


def p_funcion_list_empty(p):
    'funcion_list : empty'


def p_funcion(p):
    'funcion : FUNCION funcion_decl LPAREN param_list RPAREN vars_local cuerpo_func'
    # Rellenar el GOTO que salta el cuerpo de esta función
    idx = _saltos.pop()
    cuadruplos.rellena_salto(idx, cuadruplos.siguiente())


def p_funcion_decl(p):
    'funcion_decl : ID'
    global _scope_actual
    nombre = p[1]
    if func_dir.function_exists(nombre):
        raise Exception(f"Función ya declarada: '{nombre}'")
    # GOTO para saltar el cuerpo; se rellena al terminar la función
    idx = cuadruplos.agregar('GOTO', None, None, None)
    _saltos.append(idx)
    func_dir.add_function(nombre, 'nula')
    _scope_actual = nombre
    # inicio = primer cuádruplo real del cuerpo (después del GOTO)
    func_dir.set_inicio(nombre, cuadruplos.siguiente())


def p_param_list_multi(p):
    'param_list : param_list COMMA param_decl'


def p_param_list_single(p):
    'param_list : param_decl'


def p_param_list_empty(p):
    'param_list : empty'


def p_param_decl(p):
    'param_decl : ID COLON tipo'
    _declarar_parametro(p[1], _tipo_actual)


def p_vars_local(p):
    '''vars_local : VARS LBRACE var_decl_list RBRACE
                  | empty'''


def p_cuerpo_func(p):
    'cuerpo_func : LBRACE estatuto_list RBRACE'
    global _scope_actual
    cuadruplos.agregar('ENDFUNC', None, None, None)
    mem_mgr.reset_local()
    _scope_actual = "global"


# ─── principal ───────────────────────────────────────────────────────────────

def p_principal(p):
    'principal : marca_principal LPAREN RPAREN cuerpo END_PRINCIPAL'


def p_marca_principal(p):
    'marca_principal : PRINCIPAL'
    # Rellenar el GOTO inicial del programa
    idx = _saltos.pop()
    cuadruplos.rellena_salto(idx, cuadruplos.siguiente())
    func_dir.functions["global"].inicio = cuadruplos.siguiente()


def p_end_principal(p):
    'END_PRINCIPAL : FIN'
    cuadruplos.agregar('END', None, None, None)


# ─── cuerpo ──────────────────────────────────────────────────────────────────

def p_cuerpo(p):
    'cuerpo : LBRACE estatuto_list RBRACE'


def p_estatuto_list_multi(p):
    'estatuto_list : estatuto_list estatuto'


def p_estatuto_list_empty(p):
    'estatuto_list : empty'


def p_estatuto(p):
    '''estatuto : asignacion
                | condicion
                | ciclo
                | imprime
                | llamada_funcion'''


# ─── asignación ──────────────────────────────────────────────────────────────

def p_asignacion(p):
    'asignacion : ID IGUAL expresion SEMICOLON'
    addr, tipo = _buscar_var(p[1])
    val_addr, val_tipo = _operandos.pop()
    res_t = sem_cube.get_result_type(tipo, '=', val_tipo)
    if res_t is None:
        raise Exception(f"Asignación inválida: no se puede asignar {val_tipo} a {tipo}")
    cuadruplos.agregar('=', val_addr, None, addr)


# ─── condición (si / sino / fin_si) ──────────────────────────────────────────

def p_si_cond(p):
    'si_cond : SI LPAREN expresion RPAREN ENTONCES'
    cond_addr, cond_tipo = _operandos.pop()
    if cond_tipo != 'bool':
        raise Exception("Condición del 'si' debe ser bool")
    idx = cuadruplos.agregar('GOTOF', cond_addr, None, None)
    _saltos.append(idx)


def p_condicion_sin_sino(p):
    'condicion : si_cond cuerpo FIN_SI'
    idx = _saltos.pop()
    cuadruplos.rellena_salto(idx, cuadruplos.siguiente())


def p_si_sino(p):
    'si_sino : SINO'
    # Generar GOTO para saltar el bloque SINO y rellenar el GOTOF del SI
    idx_goto = cuadruplos.agregar('GOTO', None, None, None)
    idx_gotof = _saltos.pop()
    cuadruplos.rellena_salto(idx_gotof, cuadruplos.siguiente())
    _saltos.append(idx_goto)


def p_condicion_con_sino(p):
    'condicion : si_cond cuerpo si_sino cuerpo FIN_SI'
    idx_goto = _saltos.pop()
    cuadruplos.rellena_salto(idx_goto, cuadruplos.siguiente())


# ─── ciclo (mientras / haz / fin_mientras) ───────────────────────────────────

def p_mientras_inicio(p):
    'mientras_inicio : MIENTRAS'
    # Guardar posición del primer cuádruplo de la condición (retorno del GOTO)
    _saltos.append(cuadruplos.siguiente())


def p_mientras_cond(p):
    'mientras_cond : mientras_inicio LPAREN expresion RPAREN HAZ'
    # La condición ya fue evaluada; emitir GOTOF ANTES del cuerpo
    cond_addr, cond_tipo = _operandos.pop()
    if cond_tipo != 'bool':
        raise Exception("Condición del 'mientras' debe ser bool")
    idx_gotof = cuadruplos.agregar('GOTOF', cond_addr, None, None)
    _saltos.append(idx_gotof)


def p_ciclo(p):
    'ciclo : mientras_cond cuerpo FIN_MIENTRAS'
    idx_gotof    = _saltos.pop()
    inicio_ciclo = _saltos.pop()
    cuadruplos.agregar('GOTO', None, None, inicio_ciclo)
    cuadruplos.rellena_salto(idx_gotof, cuadruplos.siguiente())


# ─── imprime ─────────────────────────────────────────────────────────────────

def p_imprime(p):
    'imprime : IMPRIME LPAREN print_list RPAREN SEMICOLON'


def p_print_list_multi(p):
    'print_list : print_list COMMA print_item'


def p_print_list_single(p):
    'print_list : print_item'


def p_print_item_expr(p):
    'print_item : expresion'
    addr, _ = _operandos.pop()
    cuadruplos.agregar('PRINT', addr, None, None)


def p_print_item_str(p):
    'print_item : CTE_STRING'
    addr = mem_mgr.asignar_constante(p[1], 'string')
    cuadruplos.agregar('PRINT', addr, None, None)


# ─── llamada a función ───────────────────────────────────────────────────────

def p_llamada_era(p):
    'llamada_era : ID'
    nombre = p[1]
    if not func_dir.function_exists(nombre):
        raise Exception(f"Función no declarada: '{nombre}'")
    cuadruplos.agregar('ERA', nombre, None, None)
    _func_call_stack.append((nombre, 0))


def p_llamada_funcion(p):
    'llamada_funcion : llamada_era LPAREN arg_list RPAREN SEMICOLON'
    nombre, n_args = _func_call_stack.pop()
    fi = func_dir.get_function(nombre)
    if n_args != len(fi.parameters):
        raise Exception(
            f"'{nombre}' espera {len(fi.parameters)} argumento(s), recibió {n_args}")
    cuadruplos.agregar('GOSUB', nombre, None, fi.inicio)


def p_arg_list_multi(p):
    'arg_list : arg_list COMMA arg'


def p_arg_list_single(p):
    'arg_list : arg'


def p_arg_list_empty(p):
    'arg_list : empty'


def p_arg(p):
    'arg : expresion'
    nombre, idx = _func_call_stack[-1]
    fi = func_dir.get_function(nombre)
    if idx >= len(fi.parameters):
        raise Exception(f"Demasiados argumentos para '{nombre}'")
    param_info = fi.parameters[idx]
    arg_addr, arg_tipo = _operandos.pop()
    res_t = sem_cube.get_result_type(param_info['type'], '=', arg_tipo)
    if res_t is None:
        raise Exception(
            f"Tipo de argumento inválido en '{nombre}' (param {idx + 1}): "
            f"esperado {param_info['type']}, recibido {arg_tipo}")
    cuadruplos.agregar('PARAM', arg_addr, None, param_info['address'])
    _func_call_stack[-1] = (nombre, idx + 1)


# ─── expresiones ─────────────────────────────────────────────────────────────

def p_expresion_simple(p):
    'expresion : exp'


def p_expresion_relacional(p):
    '''expresion : exp MENOR exp
                 | exp MAYOR exp
                 | exp IGUAL_IGUAL exp
                 | exp DIFERENTE exp'''
    d2, t2 = _operandos.pop()
    d1, t1 = _operandos.pop()
    op = p[2]
    res_t = sem_cube.get_result_type(t1, op, t2)
    if res_t is None:
        raise Exception(f"Operación relacional inválida: {t1} {op} {t2}")
    tmp = mem_mgr.asignar_temporal(res_t)
    cuadruplos.agregar(op, d1, d2, tmp)
    _operandos.append((tmp, res_t))


def p_exp_mas(p):
    'exp : exp MAS termino'
    _bin_op('+')


def p_exp_menos(p):
    'exp : exp MENOS termino'
    _bin_op('-')


def p_exp_termino(p):
    'exp : termino'


def p_termino_mult(p):
    'termino : termino MULT factor'
    _bin_op('*')


def p_termino_div(p):
    'termino : termino DIV factor'
    _bin_op('/')


def p_termino_factor(p):
    'termino : factor'


def p_factor_paren(p):
    'factor : LPAREN expresion RPAREN'


def p_factor_id(p):
    'factor : ID'
    addr, tipo = _buscar_var(p[1])
    _operandos.append((addr, tipo))


def p_factor_cte_entero(p):
    'factor : CTE_ENTERO'
    addr = mem_mgr.asignar_constante(p[1], 'entero')
    _operandos.append((addr, 'entero'))


def p_factor_cte_flotante(p):
    'factor : CTE_FLOTANTE'
    addr = mem_mgr.asignar_constante(p[1], 'flotante')
    _operandos.append((addr, 'flotante'))


def p_factor_negativo(p):
    'factor : MENOS factor'
    addr, tipo = _operandos.pop()
    cero = mem_mgr.asignar_constante(0, tipo)
    tmp = mem_mgr.asignar_temporal(tipo)
    cuadruplos.agregar('-', cero, addr, tmp)
    _operandos.append((tmp, tipo))


# ─── epsilon ─────────────────────────────────────────────────────────────────

def p_empty(p):
    'empty :'


def p_error(p):
    if p:
        raise SyntaxError(f"Error sintáctico en token '{p.value}' (línea {p.lineno})")
    raise SyntaxError("Error sintáctico: fin de archivo inesperado")


parser = yacc.yacc(debug=False, write_tables=False)


# ─── API pública ─────────────────────────────────────────────────────────────

def compilar(codigo_fuente):
    """
    Compila código Patito.
    Devuelve (func_dir, cuadruplos, mem_mgr) para pasarlos a la VM.
    """
    _reset()
    parser.parse(codigo_fuente, lexer=lexer.clone())
    return func_dir, cuadruplos, mem_mgr
