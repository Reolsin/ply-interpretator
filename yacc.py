from lex import tokens
import ply.yacc as yacc
from interpretator_struct import *


def _OR(first, second) -> Expression:
    if type(first) == VAL and type(second) == VAL:
        if first.type == bool and second.type == bool:
            return VAL(bool, first.ident or second.ident)
        elif first.type == int or second.type == int:
            raise Exception('Incorrect types.')
        else:
            return OR(first, second)
    else:
        return OR(first, second)

def _GT(first, second) -> Expression:
    if type(first) == VAL and type(second) == VAL:
        if first.type == int and second.type == int:
            return VAL(bool, first.ident > second.ident)
        elif first.type == bool or second.type == bool:
            raise Exception('Incorrect types.')
        else:
            return GT(first, second)
    else:
        return GT(first, second)

def _LT(first, second) -> Expression:
    if type(first) == VAL and type(second) == VAL:
        if first.type == int and second.type == int:
            return VAL(bool, first.ident < second.ident)
        elif first.type == bool or second.type == bool:
            raise Exception('Incorrect types.')
        else:
            return LT(first, second)
    else:
        return LT(first, second)

def _NOT(first) -> Expression:
    if type(first) == VAL:
        if first.type == bool:
            return VAL(bool, not first.ident)
        elif first.type == int:
            raise Exception('Incorrect types.')
        else:
            return NOT(first)
    else:
        return NOT(first)

def _INC(first) -> Expression:
    if (type(first) == VAL and first.type == Var) or type(first) == Brackets:
        return INC(first)
    else:
        raise Exception('Incorrect types.')

def _DEC(first) -> Expression:
    if type(first) == VAL and first.type == Var:
        return DEC(first)
    else:
        raise Exception('Incorrect types.')


#-GRAMMAR------------------------------------------------------------

def p_prog(p):
    '''prog : prog line es'''
    if p[1]:
        if p[2]: 
            if type(p[2]) == list:
                p[1].script.extend(p[2])
            else:
                p[1].script.append(p[2])
        p[0] = p[1]
    else:
        if p[2]:
            if type(p[2]) == list:
                p[0] = Prog(p[2])
            else:
                p[0] = Prog([p[2]])
        else: p[0] = Prog([])

def p_prog_fdecl(p):
    '''prog : prog fdecl es'''
    if p[1]:
        if p[2]: 
            p[1].script.append(Line(p[2]))
        p[0] = p[1]
    elif p[2]:
            p[0] = Prog([Line(p[2])])
    else: p[0] = Prog([])
    

def p_prog_empty(p):
    '''prog : '''
    p[0] = None

def p_es(p):
    '''es : es es
          | ES'''

def p_line(p):
    '''line : sent
            | logic
            | fcall
            | decl
            | cdecl'''
    p[0] = Line(p[1])

def p_line_gr(p):
    '''line : group'''

def p_line_empty(p):
    '''line : '''
    p[0] = None

def p_sent_pr(p):
    '''sent : PRINT ID'''
    p[0] = Print(p[2])

def p_sent_eq(p):
    '''sent : ID EQ expr
            | access EQ expr'''
    p[0] = Assign(p[1], p[3])

def p_sent_extend(p):
    '''sent : EXTEND1 ID expr
            | EXTEND2 ID expr expr'''
    if len(p) == 5:
        p[0] = EXTEND(p[2], p[3], p[4])
    else:
        p[0] = EXTEND(p[2], p[3], None)

def p_sent_exun(p):
    '''sent : expr
            | UNDO'''
    p[0] = p[1]

def p_group(p):
    '''group : FOPEN lines line FCLOSE
             | FOPEN lines FCLOSE'''
    if len(p) == 5:
        if p[2]:
            if type(p[3]) == list:
                p[2].extend(p[3])
            else:
                p[2].append(p[3])
            p[0] = p[2]
        else:
            if type(p[3]) == list:
                p[0] = p[3]
            else:
                p[0] = [p[3]]
    else:
        if p[2]:
            p[0] = p[2]
        else:
            p[0] = []

def p_lines(p):
    '''lines : lines line es'''
    if p[1]:
        if p[2]:
            if type(p[2]) == list:
                p[1].extend(p[2])
            else:
                p[1].append(p[2])
        p[0] = p[1]
    elif p[2]:
        if type(p[2]) == list:
            p[0] = p[2]
        else:
            p[0] = [p[2]]
    else: 
        p[0] = None

def p_lines_empty(p):
    '''lines : '''
    p[0] = None

#-DECLARATIONS------------------------------------------------------------

def p_decl(p):
    '''decl : 2ldecl
            | 2adecl
            | 1ldecl
            | 1adecl
            | lvdecl
            | avdecl'''
    p[0] = p[1]

def p_cdecl(p):
    '''cdecl : cldecl
             | cadecl'''
    p[0] = p[1]

#-CONST-DECL------------------------------------------------------------

def p_cldecl(p):
    '''cldecl : CLVAR ID EQ expr'''
    p[0] = Var(p[2], bool, True, 0, p[4])

def p_cadecl(p):
    '''cadecl : CAVAR ID EQ expr'''
    p[0] = Var(p[2], int, True, 0, p[4])

#-VAR-DECL------------------------------------------------------------

def p_lvdecl(p):
    '''lvdecl : LVAR ID
              | LVAR ID EQ expr'''
    if len(p) == 5:
        p[0] = Var(p[2], bool, False, 0, p[4])
    else:
        p[0] = Var(p[2], bool, False, 0, None)

def p_avdecl(p):
    '''avdecl : AVAR ID
              | AVAR ID EQ expr'''
    if len(p) == 5:
        p[0] = Var(p[2], int, False, 0, p[4])
    else:
        p[0] = Var(p[2], int, False, 0, None)

#-ARR-DECL------------------------------------------------------------

def p_1ldecl(p):
    '''1ldecl : L1ARR ID
              | L1ARR ID EQ SOPEN vals SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], bool, False, 1, None)
    else:
        p[0] = Var(p[2], bool, False, 1, p[5])

def p_1adecl(p):
    '''1adecl : A1ARR ID
              | A1ARR ID EQ SOPEN vals SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], int, False, 1, None)
    else:
        p[0] = Var(p[2], int, False, 1, p[5])

def p_2ldecl(p):
    '''2ldecl : L2ARR ID
              | L2ARR ID EQ SOPEN arrs SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], bool, False, 2, None)
    else:
        p[0] = Var(p[2], bool, False, 2, p[5])

def p_2adecl(p):
    '''2adecl : A2ARR ID
              | A2ARR ID EQ SOPEN arrs SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], int, False, 2, None)
    else:
        p[0] = Var(p[2], int, False, 2, p[5])

def p_vals(p):
    '''vals : expr COMA vals
            | expr'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_arrs(p):
    '''arrs : vals COMD arrs
            | COMD arrs
            | vals'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[2].append([])
        p[0] = p[2]
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]

def p_arrs_empty(p):
    '''arrs : '''
    p[0] = [[]]

#-FUNC-DECL------------------------------------------------------------

def p_fdecl(p):
    '''fdecl : fovars FUNCTION ID fivars group'''
    p[0] = Function(p[3], p[4], p[5], p[1])

def p_fovars(p):
    '''fovars : ID EQ expr'''
    p[0] = [[p[1], p[3]]]

def p_fovars_br(p):
    '''fovars : SOPEN fvars SCLOSE'''
    p[0] = p[2]

def p_fivars(p):
    '''fivars : OPEN fvars CLOSE'''
    p[0] = p[2]

def p_fvars(p):
    '''fvars : ID EQ expr
             | ID EQ expr COMA fvars'''
    if len(p) == 6 and p[5]:
        p[0] = [[p[1], p[3]]] + p[5]
    else:
        p[0] = [[p[1], p[3]]]

def p_fvars_empty(p):
    '''fvars : '''
    p[0] = None

#-EXPRESSIONS------------------------------------------------------------

def p_expr(p):
    '''expr : oper
            | ACONST
            | LCONST
            | ID
            | NOT expr
            | INCDEC expr
            | expr GTLT expr
            | expr OR expr
            | OPEN expr CLOSE'''
    if len(p) == 2:
        if type(p[1]) == Oper or type(p[1]) == Brackets:
            p[0] = p[1]
        elif p[1] == 'TRUE' or p[1] == 'FALSE':
            if p[1] == 'TRUE': p[1] = True
            else: p[1] = False
            p[0] = VAL(bool, p[1])
        elif p[1].isdigit():
            p[0] = VAL(int, int(p[1]))
        else:
            p[0] = VAL(Var, p[1])
    elif len(p) == 3:
        if p[1] == 'INC':
            p[0] = _INC(p[2])
        elif p[1] == 'DEC':
            p[0] = _DEC(p[2])
        else:
            p[0] = _NOT(p[2])
    else:
        if p[2] == 'GT':
            p[0] = _GT(p[1], p[3])
        elif p[2] == 'LT':
            p[0] = _LT(p[1], p[3])
        elif p[2] == 'OR':
            p[0] = _OR(p[1], p[3])
        else:
            p[0] = p[2]

def p_oper(p):
    '''oper : MOVE
            | GET
            | PUSH
            | SIZE1 ID
            | SIZE2 ID expr
            | access'''
    if len(p) == 2:
        if type(p[1]) == Brackets:
            p[0] = p[1]
        elif p[1][0:4] == 'PUSH':
            p[0] = Oper('PUSH', p[1][4], None)
        elif p[1][0:3] == 'GET':
            p[0] = Oper('GET', p[1][3], None)
        elif p[1] == 'FORW' or p[1] == 'BACK' or p[1] == 'RIGHT' or p[1] == 'LEFT':
            p[0] = Oper('MOVE', p[1][0], None)
        else:
            p[0] = p[1]
    elif p[1] == 'SIZE1':
        p[0] = Oper('SIZE', p[2], None)
    elif p[1] == 'SIZE2':
        p[0] = Oper('SIZE', p[2], p[3])


def p_access(p):
    '''access : ID OPEN expr COMA expr CLOSE
              | ID OPEN expr CLOSE'''
    if len(p) == 5:
        p[0] = Brackets(p[1], p[3], None)
    else:
        p[0] = Brackets(p[1], p[3], p[5])


#-LOGIC------------------------------------------------------------

def p_logic(p):
    '''logic : cond
             | loop'''
    p[0] = p[1]

def p_cond(p):
    '''cond : IF expr sent else
            | IF expr group else'''
    if type(p[3]) != list:
        p[3] = [Line(p[3])]
    if p[4]:
        p[0] = Condition(p[2], p[3], p[4])
    else:
        p[0] = Condition(p[2], p[3], p[4])

def p_else(p):
    '''else : ELSE sent
            | ELSE group'''
    if type(p[2]) != list:
        p[2] = [Line(p[2])]
    p[0] = p[2]
    
def p_else_empty(p):
    '''else : '''
    p[0] = None

def p_loop(p):
    '''loop : WHILE expr DO sent
            | WHILE expr DO group'''
    if type(p[4]) != list:
        p[4] = [Line(p[4])]
    p[0] = While(p[2], p[4])

#-CALLS------------------------------------------------------------

def p_fcall(p):
    '''fcall : SOPEN vars SCLOSE EQ ID OPEN pars CLOSE'''
    p[0] = Fcall(p[5], p[7], p[2])

def p_vars(p):
    '''vars : ID COMA vars
            | COMA vars
            | access COMA vars
            | access
            | ID'''
    if len(p) == 4:
        p[3].append(p[1])
        p[0] = p[3]
    elif len(p) == 3:
        p[2].append(None)
        p[0] = p[2]
    else:
        p[0] = [p[1]]

def p_vars_empty(p):
    '''vars : '''
    p[0] = [None]

def p_pars(p):
    '''pars : expr COMA pars
            | COMA pars
            | expr'''
    if len(p) == 4:
        p[3].append(p[1])
        p[0] = p[3]
    elif len(p) == 3:
        p[2].append(None)
        p[0] = p[2]
    else:
        p[0] = [p[1]]

def p_pars_empty(p):
    '''pars : '''
    p[0] = [None]

#-PARSER------------------------------------------------------------

def p_error(p):
    print('Parsing error:\nsymbol: {}, line: {}, number: {}'.format(p.value, p.lineno, p.lexpos))

parser = yacc.yacc()

