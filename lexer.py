# lexer.py - Scanner (analizador léxico) para Patito
import ply.lex as lex

reserved = {
    'programa':     'PROGRAMA',
    'vars':         'VARS',
    'funcion':      'FUNCION',
    'entero':       'ENTERO',
    'flotante':     'FLOTANTE',
    'si':           'SI',
    'entonces':     'ENTONCES',
    'sino':         'SINO',
    'fin_si':       'FIN_SI',
    'mientras':     'MIENTRAS',
    'haz':          'HAZ',
    'fin_mientras': 'FIN_MIENTRAS',
    'imprime':      'IMPRIME',
    'principal':    'PRINCIPAL',
    'fin':          'FIN',
    'regresa':      'REGRESA',
}

tokens = list(reserved.values()) + [
    'ID',
    'CTE_ENTERO',
    'CTE_FLOTANTE',
    'CTE_STRING',
    'MAYOR_IGUAL',
    'MENOR_IGUAL',
    'IGUAL_IGUAL',
    'DIFERENTE',
    'MAYOR',
    'MENOR',
    'IGUAL',
    'MAS',
    'MENOS',
    'MULT',
    'DIV',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'SEMICOLON',
    'COMMA',
    'COLON',
]

t_MAYOR_IGUAL  = r'>='
t_MENOR_IGUAL  = r'<='
t_IGUAL_IGUAL  = r'=='
t_DIFERENTE    = r'!='
t_MAYOR        = r'>'
t_MENOR        = r'<'
t_IGUAL        = r'='
t_MAS          = r'\+'
t_MENOS        = r'-'
t_MULT         = r'\*'
t_DIV          = r'/'
t_LPAREN       = r'\('
t_RPAREN       = r'\)'
t_LBRACE       = r'\{'
t_RBRACE       = r'\}'
t_SEMICOLON    = r';'
t_COMMA        = r','
t_COLON        = r':'

t_ignore = ' \t\r'
t_ignore_COMMENT = r'\#[^\n]*'


def t_CTE_FLOAT(t):
    r'\d+\.\d+'
    t.type = 'CTE_FLOTANTE'
    t.value = float(t.value)
    return t


def t_CTE_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_CTE_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # strip quotes
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    raise SyntaxError(f"Carácter ilegal '{t.value[0]}' en línea {t.lexer.lineno}")


lexer = lex.lex()
