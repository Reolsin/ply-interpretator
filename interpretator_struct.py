maxint = 2147483647

class Tmp:

    def __init__(self, type: type, data):
        self.type = type
        self.data = data

    def __repr__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

    def extend(self, other):
        self.data.extend(other)

class Var:

    def __init__(self, id: str, type: type, const: bool, n: int, expr, data = None) -> None:
        self.id = id
        self.type = type
        self.const = const
        self.dimensions = n
        self.expr = expr
        self.data = data

    def run_var_init(self, program, function):
        if self.expr:
            if self.dimensions == 2:
                self.data = [Tmp(self.type, [Tmp(self.type, get_expr(expr, self.type, 0, program, function).data) for expr in arr]) for arr in self.expr]
            elif self.dimensions == 1:
                self.data = [Tmp(self.type, get_expr(expr, self.type, 0, program, function).data) for expr in self.expr]
            else:
                self.data = get_expr(self.expr, self.type, 0, program, function).data

    def copy(self):
        return Var(self.id, self.type, self.const, self.dimensions, self.expr, self.data)

    def __str__(self):
        return 'var inst, id: {}, type: {}'.format(self.id, self.type)

    def __repr__(self):
        return 'Var | ID: {} | Data: {}\t'.format(self.id, self.data)


class Function:
    
    def __init__(self, id, default_pars, script, default_vars) -> None:
        self.id = id
        self.vars = dict()
        self.def_pars = default_pars
        self.def_vars = default_vars
        self.script = script
        self.cur_inst = [0, 'declarating function ' + self.id]

    def run_func_init(self, program):
        for par, expr in self.def_pars:
            tmp = expr.Solve(program, None)
            check_dim_int(tmp, 0)
            self.vars[par] = Var(par, tmp.type, False, 0, None, tmp.data)
        self.def_pars = [i[0] for i in self.def_pars]

        for var, expr in self.def_vars:
            tmp = expr.Solve(program, None)
            check_dim_int(tmp, 0)
            self.vars[var] = Var(var, tmp.type, False, 0, None, tmp.data)
        self.def_vars = [i[0] for i in self.def_vars]

    def check_call(self, pars, vars, program, function):
        self.cur_inst = [0, 'calling function ' + self.id]
        if len(self.def_pars) != len(pars):
            raise Exception('Expected {} args, but {} stated'.format(len(self.def_pars), len(pars)))
        if len(self.def_vars) != len(vars):
            raise Exception('Expected {} outputs, but {} stated'.format(len(self.def_vars), len(vars)))
        for i in range(len(vars)):
            if vars[i]:
                if type(vars[i]) == Brackets:
                    check_type(self.vars[self.def_vars[i]], Tmp(vars[i]._type(program, function, 0), None))
                else:
                    check_type(self.vars[self.def_vars[i]], get_var(vars[i], program, function))
        for i in range(len(pars)):
            if pars[i]:
                check_type(self.vars[self.def_pars[i]], Tmp(pars[i]._type(program, function, 0), None))

    def duplicate(self):
        tmp = Function(self.id, [i for i in self.def_pars], self.script, [i for i in self.def_vars])
        tmp.vars = {ident:self.vars[ident].copy() for ident in self.vars}
        return tmp

    def run(self, args, program):
        for i in range(len(args)):
            if args[i]:
                self.vars[self.def_pars[i]].data = args[i]
        for i in range(len(self.script)):
            self.cur_inst = [i+1, self.script[i]]
            self.script[i].interpretate(program, self)

        return [self.vars[ident].data for ident in self.def_vars]

    def __str__(self):
        return 'function {}, in inst #{}, in {}'.format(self.id, self.cur_inst[0], self.cur_inst[1])

def get_dim(var):
    if type(var) == Tmp:
        if type(var.data) == list and type(var.data[0]) == list: return 2
        elif type(var.data) == list: return 1
        else: return 0
    else:
        return var.dimensions

def check_dim(first, second):
    d1 = get_dim(first)
    d2 = get_dim(second)
    if d1 == d2: return True
    else: raise Exception('Incorrect type, dimensions')

def check_dim_int(first, int):
    d1 = get_dim(first)
    if d1 == int: return True
    else: raise Exception('Incorrect type, dimensions')

def check_type(first, second):
    if first.type == second.type:
        return True
    else: raise Exception('Incorrect types.')

def get_const(var):
    if type(var) == Tmp:
        return False
    else:
        return var.const

def check_const(var):
    if type(var) == Tmp:
        return False
    elif var.const:
        raise Exception('Try to change const.')
    else: return False

def get_var(ident, program, function) -> Var:
    if function:
        var = function.vars.get(ident)
        if not var:
            var = program.vars.get(ident)
    else:
        var = program.vars.get(ident)
    if not var:
        raise Exception('Variable not declarated')
    return var

def get_decvar(ident, program, function) -> Var:
    if function:
        var = function.vars.get(ident)
        if not var:
            var = program.vars.get(ident)
    else:
        var = program.vars.get(ident)
    if not var:
        raise Exception('Variable not declarated.')
    if var.data == None:
        raise Exception('Variable has no data.')
    return var

def get_expr(expr, type, dim_int, program, function) -> Tmp:
    tmp = expr.Solve(program, function)
    if tmp.type != type or not check_dim_int(tmp, dim_int):
        raise Exception('Expected {} type, but {} got.'.format(type, tmp.type))
    return tmp

class Expression:
    pass

class VAL(Expression):

    def __init__(self, type, val):
        self.type = type
        self.ident = val

    def __repr__(self) -> str:
        return str(self.ident)

    def Solve(self, program, function) -> Tmp:
        if self.type == Var:
            return get_decvar(self.ident, program, function)
        else:
            return Tmp(self.type, self.ident)

    def _type(self, program, function, d):
        if self.type == Var:
            tmp = get_decvar(self.ident, program, function)
            if check_dim_int(tmp, d):
                return tmp.type
            else:
                raise Exception('Incorrect type, dimensions')
        else:
            return self.type

class GT(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} > {} )'.format(self.left, self.right)

    def Solve(self, program, function) -> Tmp:
        left = get_expr(self.left, int, 0, program, function)
        right = get_expr(self.right, int, 0, program, function)
        return Tmp(bool, left.data > right.data)

    def _type(self, program=None, function=None, d = 0):
        return bool

class LT(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} < {} )'.format(self.left, self.right)
    
    def Solve(self, program, function) -> Tmp:
        left = get_expr(self.left, int, 0, program, function)
        right = get_expr(self.right, int, 0, program, function)
        return Tmp(bool, left.data < right.data)

    def _type(self, program=None, function=None, d = 0):
        return bool

class OR(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} OR {} )'.format(self.left, self.right)

    def Solve(self, program, function) -> Tmp:
        left = get_expr(self.left, bool, 0, program, function)
        right = get_expr(self.right, bool, 0, program, function)
        return Tmp(bool, left.data or right.data)

    def _type(self, program=None, function=None, d = 0):
        return bool

class NOT(Expression):

    def __init__(self, val):
        self.val = val

    def __repr__(self) -> str:
        return '( NOT {} )'.format(self.val)

    def Solve(self, program, function) -> Tmp:
        var = get_expr(self.val, bool, 0, program, function)
        return Tmp(bool, not var.data)

    def _type(self, program=None, function=None, d = 0):
        return bool

class INC(Expression):

    def __init__(self, val):
        self.expr = val

    def __repr__(self) -> str:
        return '++{}'.format(self.expr)

    def Solve(self, program, function) -> Tmp:
        var = get_expr(self.expr, int, 0, program, function)
        check_const(var)
        var.data += 1
        return Tmp(int, var.data)

    def _type(self, program=None, function=None, d = 0):
        return int

class DEC(Expression):

    def __init__(self, val):
        self.expr = val

    def __repr__(self) -> str:
        return '--{}'.format(self.expr)

    def Solve(self, program, function) -> Tmp:
        var = get_expr(self.expr, int, 0, program, function)
        check_const(var)
        var.data -= 1
        return Tmp(int, var.data)

    def _type(self, program=None, function=None, d = 0):
        return int

class Oper(Expression):

    def __init__(self, operator, first, second):
        self.operator = operator
        self.first = first
        self.second = second

    def __repr__(self):
        return '[{}: {}, {}]'.format(self.operator, self.first, self.second)

    def Solve(self, program, function) -> Tmp:
        if self.operator == 'PUSH':
            type = bool
            data = program.push(self.first)
        elif self.operator == 'GET':
            type = int
            data = program.get(self.first)
        elif self.operator == 'MOVE':
            type = bool
            data = program.move(self.first)
        elif self.operator == 'SIZE':
            var = get_decvar(self.first, program, function)
            type = int
            if self.second:
                check_dim_int(var, 2)
                tmp = get_expr(self.second, int, 0, program, function).data
                data = len(var.data[tmp])
            else:
                if get_dim(var) > 0:
                    data = len(var.data)
                else: raise Exception('Var isnt array.')
        return Tmp(type, data)

    def _type(self, program=None, function=None, d = 0):
        if self.operator == 'PUSH' or self.operator == 'MOVE':
            return bool
        elif self.operator == 'GET' or self.operator == 'SIZE':
            return int

class Assign:

    def __init__(self, a: Expression, b: Expression):
        self.target = a
        self.expr = b

    def __str__(self) -> str:
        return '{} := {}'.format(self.target, self.expr)

    def run_assign(self, program, function: Function):
        tmp = self.expr.Solve(program, function)
        if type(self.target) == Brackets:
            var = self.target.Solve(program, function)
        else:
            var = get_var(self.target, program, function)
        if check_type(var, tmp) and not check_const(var) and check_dim(var, tmp):
            var.data = tmp.data

class EXTEND:
    
    def __init__(self, ident, expr1, expr2):
        self.ident = ident
        self.expr1 = expr1
        self.expr2 = expr2

    def run_extend(self, program, function: Function):
        tmp1 = get_expr(self.expr1, int, 0, program, function).data
        var = get_var(self.ident, program, function)
        if self.expr2:
            if var.data:
                check_dim_int(var, 2)
                tmp2 = get_expr(self.expr2, int, 0, program, function).data
                if tmp1 < len(var.data):
                    if tmp2 >= len(var.data[tmp1]):
                        var.data[tmp1].extend([Tmp(var.type, var.type()) for i in range(tmp2 - len(var.data[tmp1]))])
                    else: raise Exception('Runtime error.')
                else: raise Exception('Index out of range.')
            else: raise Exception('Array hasnt data.')
        else:
            if var.data:
                if tmp1 >= len(var.data):
                    if var.dimensions == 1:
                        var.data.extend([Tmp(var.type, var.type()) for i in range(tmp1 - len(var.data))])
                    else:
                        var.data.extend([Tmp(var.type,[]) for i in range(tmp1 - len(var.data))])
                else: raise Exception('Runtime error.')
            elif var.dimensions == 2:
                var.data = [Tmp(var.type, []) for i in range(tmp1)]
            elif var.dimensions == 1:
                var.data = [Tmp(var.type, var.type()) for i in range(tmp1)]
            else:
                check_dim_int(var, 1)

    def __str__(self):
        if self.expr2:
            return 'Extend: {}[{}].extend({})'.format(self.ident, self.expr1, self.expr2)
        else:
            return 'Extend: {}.extend({})'.format(self.ident, self.expr1)

class Brackets(Expression):

    def __init__(self, ident, i, j):
        self.ident = ident
        self.expr1 = i
        self.expr2 = j

    def __str__(self):
        out = '{}[{}]'.format(self.ident, self.expr1)
        if self.expr2:
            out += '[{}]'.format(self.expr2)
        return out

    def Solve(self, program, function) -> Tmp:
        var = get_decvar(self.ident, program, function)
        tmp1 = get_expr(self.expr1, int, 0, program, function).data
        if self.expr2 and check_dim_int(var, 2):
            tmp2 = get_expr(self.expr2, int, 0, program, function).data
            if tmp1 <= len(var.data) and tmp2 <= len(var.data[tmp1].data):
                return var.data[tmp1].data[tmp2]
            else: raise Exception('Index out of range.')
        elif get_dim(var) > 0:
            if tmp1 <= len(var.data):
                return var.data[tmp1]
            else: raise Exception('Index out of range.')
        else: raise Exception('Variable isnt array.')

    def _type(self, program, function):
        return get_decvar(self.ident, program, function).type

class Line:

    def __init__(self, statement) -> None:
        self.statement = statement

    def interpretate(self, program, function):
        line = self.statement
        if type(line) == Var:
            line.run_var_init(program, function)
            if function:
                function.vars[line.id] = line
            else:
                program.vars[line.id] = line
        elif type(line) == Function:
            if program.functions.get(line.id):
                raise Exception('Function already declarated.')
            line.run_func_init(program)
            program.functions[line.id] = line
        elif type(line) == Condition:
            line.run_cond(program, function)
        elif type(line) == While:
            line.run_while(program, function)
        elif type(line) == Fcall:
            line.run_fcall(program, function)
        elif type(line) == Assign:
            line.run_assign(program, function)
        elif isinstance(line, Expression):
            line.Solve(program, function)
        elif type(line) == EXTEND:
            line.run_extend(program, function)
        elif type(line) == Print:
            line.execute(program, function)

    def __str__(self):
        return str(self.statement)

class Condition:
    
    def __init__(self, expr, then, _else) -> None:
        self.expr = expr
        self.then = then
        self._else = _else
        self.cur_inst = [0, self.expr]

    def run_cond(self, program, function):
        if get_expr(self.expr, bool, 0, program, function).data:
            exe_gr = self.then
        else:
            exe_gr = self._else
        if exe_gr:
            for i in range(len(exe_gr)):
                self.cur_inst = [i+1, exe_gr[i]]
                exe_gr[i].interpretate(program, function)
    
    def __str__(self):
        return 'condition, in instance #{}; In {}'.format(self.cur_inst[0], self.cur_inst[1])

class While:
    
    def __init__(self, expr, do) -> None:
        self.expr = expr
        self.do = do
        self.cur_inst = [0, self.expr]

    def run_while(self, program, function):
        while get_expr(self.expr, bool, 0, program, function).data:
            for i in range(len(self.do)):
                self.cur_inst = [i+1, self.do]
                self.do[i].interpretate(program, function)

    def __str__(self):
        return 'while, in inst #{}; In {}'.format(self.cur_inst[0], self.cur_inst[1])

class Vector:

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, arg):
        return Vector(self.x + arg.x, self.y + arg.y)
    
    def __iadd__(self, arg):
        self.x += arg.x
        self.y += arg.y
        return self

    def __isub__(self, arg):
        self.x -= arg.x
        self.y -= arg.y
        return self

    def __eq__(self, arg):
        return self.x == arg.x and self.y == arg.y

    def rotate(self, direction):
        x, y = self.x, self.y
        if direction == 'F':
            pass
        elif direction == 'B':
            x, y = -x, -y
        elif direction == 'R':
            x, y = -y, x
        elif direction == 'L':
            x, y = y, -x
        return Vector(x, y)

class map_container:

    def __init__(self, map: list) -> None:
        self.map = map

    def get(self, pair: Vector):
        if (pair.y < len(self.map) and pair.y >= 0) and (pair.x < len(self.map[pair.y]) and pair.x >= 0):
            return self.map[pair.y][pair.x]
        else:
            return None
    
    def __getitem__(self, pair: Vector) -> str:
        tmp = self.get(pair)
        if tmp: return tmp
        else: return '#'

    def __setitem__(self, pair: Vector, val) -> str:
        tmp = self.get(pair)
        if tmp: self.map[pair.y][pair.x] = val


class Prog:

    def __init__(self, lines):
        self.vars = dict()
        self.functions = dict()
        self.script = lines

        self.map = None
        self.cur = Vector(0, 0)
        self.direct = Vector(1, 0)
        self.exit = Vector(0, 0)
        self.undo_stack = []
        self.root = []

        self.cur_inst = [0, 'Loading map.']
        self.exception = None

    def find_exit(self, file):
        tmp = [[i for i in line if i != '\n'] for line in file]
        self.map = map_container(tmp)
        self.cur = [Vector(j, i) for i in range(len(tmp)) for j in range(len(tmp[i])) if tmp[i][j] == 'S'].pop()
        self.exit = [Vector(j, i) for i in range(len(tmp)) for j in range(len(tmp[i])) if tmp[i][j] == 'F'].pop()
        self.map[self.cur] = ' '
        self.map[self.exit] = ' '
        if not self.map:
            raise Exception('Error in loading map.')
        self.robot_map = self.map
        for i in range(len(self.script)):
            self.cur_inst = [i+1, self.script[i]]
            self.script[i].interpretate(self, None)

    def check_func_decl(self, ident) -> Function:
        if self.functions.get(ident):
            return self.functions[ident]
        else: raise Exception('Function not declarated.')

    def push(self, direction):
        self.direct = self.direct.rotate(direction)

        if self.map[self.direct + self.cur] == '#':
            if self.map[self.direct + self.direct + self.cur] == '#':
                return False
            else:
                self.map[self.direct + self.cur] = ' '
                self.map[self.direct + self.direct + self.cur] = '#'
                self.undo_stack.append([self.direct + self.cur, self.direct + self.direct + self.cur])
        self.root.append(self.cur)
        self.cur += self.direct
        if self.cur == self.exit:
            self.exception = 'Robot found root.'
            raise
        return True

    def get(self, direction):
        tmp = self.direct.rotate(direction)
        x, y = self.exit.x - self.direct.x, self.exit.y - self.direct.y
        if tmp.x == 0:
            if y*tmp.y > 0 or y == 0: return y
            else: return maxint
        else:
            if x*tmp.x > 0 or x == 0: return x
            else: return maxint

    def move(self, direction):
        self.direct = self.direct.rotate(direction)

        if self.map[self.direct + self.cur] == '#':
            return False
        self.cur += self.direct
        self.undo_stack.clear()
        self.root.append(Vector(self.cur.x, self.cur.y))
        if self.cur == self.exit:
            self.exception = 'Robot found root.'
            print('\n'.join([''.join(['*' if Vector(j, i) in self.root else self.map.map[i][j] for j in range(len(self.map.map[i]))]) for i in range(len(self.map.map))]))
            raise
        return True

    def undo(self):
        tmp = self.undo_stack.pop()
        self.map[tmp[1]] = ' '
        self.map[tmp[0]] = '#'
        self.cur -= self.direct

    def set_exception(self, text):
        self.exception = 'Exception in program instance #{}. In {}. {}'.format(self.cur_inst[0], self.cur_inst[1], text)

    def __str__(self):
        return '\n'.join([str(i) for i in self.script])

class Fcall:

    def __init__(self, ident, pars, vars):
        self.ident = ident
        self.pars = pars # [expr...]
        self.vars = vars # [id...]

    def run_fcall(self, program: Prog, function: Function):
        self.cur_inst = 'function ' + self.ident + ' not declarated'
        func = program.check_func_decl(self.ident)
        self.cur_inst = func
        func.check_call(self.pars, self.vars, program, function)
        args = [expr.Solve(program, function).data if expr else None for expr in self.pars]
        func = func.duplicate()
        res = func.run(args, program)
        for i in range(len(self.vars)):
            if self.vars[i]:
                if type(self.vars[i]) == Brackets:
                    var = self.vars[i].Solve(program, function)
                    var.data = res[i]
                else:
                    var = get_var(self.vars[i], program, function)
                    check_const(var)
                    var.data = res[i]

    def __str__(self):
        return 'fcall, {}'.format(self.cur_inst)

class Print:

    def __init__(self, ident) -> None:
        self.ident = ident

    def execute(self, program, function):
        print(get_var(self.ident, program, function).__repr__())
