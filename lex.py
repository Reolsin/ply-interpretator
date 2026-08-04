from re import UNICODE, VERBOSE
import ply.lex as lex

tokens = (
    'OPEN', 'CLOSE', 'FOPEN', 'FCLOSE', 'SOPEN', 'SCLOSE', 'COMA', 'COMD', 'ES', 'EQ',
    'AVAR', 'LVAR', 'A1ARR', 'L1ARR', 'A2ARR', 'L2ARR',
    'CAVAR', 'CLVAR',
    'LCONST', 'ACONST',
    'MOVE', 'GET', 'PUSH', 'UNDO',
    'EXTEND1', 'EXTEND2', 'SIZE1', 'SIZE2',
    'IF', 'ELSE', 'WHILE', 'DO', 'FUNCTION',
    'INCDEC', 'NOT', 'OR', 'GTLT',
    'PRINT',
    'ID',
)


t_OPEN = r'\('
t_CLOSE = r'\)'
t_FOPEN = r'\{'
t_FCLOSE = r'\}'
t_SOPEN = r'\['
t_SCLOSE = r'\]'
t_COMA = r','
t_COMD = r';'
t_EQ = r'='
def t_ES(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

t_AVAR = r'UINT'
t_LVAR = r'BOOLEAN'
t_A1ARR = r'1DARRAYOFUINT'
t_L1ARR = r'1DARRAYOFBOOL'
t_A2ARR = r'2DARRAYOFUINT'
t_L2ARR = r'2DARRAYOFBOOL'

t_CAVAR = r'CUINT'
t_CLVAR = r'CBOOLEAN'

t_LCONST = r'TRUE|FALSE'
t_ACONST = r'0|[1-9][0-9]*'

t_MOVE = r'FORW|BACK|RIGHT|LEFT'
t_GET = r'GET(F|B|R|L)'
t_PUSH = r'PUSH(F|B|R|L)'
t_UNDO = r'UNDO'

t_EXTEND1 = r'EXTEND1'
t_EXTEND2 = r'EXTEND2'
t_SIZE1 = r'SIZE1'
t_SIZE2 = r'SIZE2'

t_IF = r'IF'
t_ELSE = r'ELSE'
t_WHILE = r'WHILE'
t_DO = r'DO'
t_FUNCTION = r'FUNCTION'

t_INCDEC = r'INC|DEC'
t_NOT = r'NOT'
t_OR = r'OR'
t_GTLT = r'GT|LT'

t_PRINT = r'PRINT'

t_ID = r'\b[a-z_]\w*'

t_ignore = ' \t\r\f'

def t_comment(t):
    r'\#.*'
    pass

def t_error(t):
    raise Exception("Error. Unexpected token: {}.".format(t.value))


lexer = lex.lex(reflags=UNICODE | VERBOSE)
