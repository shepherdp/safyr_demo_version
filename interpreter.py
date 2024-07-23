from lexer import KWDS, Lexer
from parser import Parser, VarAssignNode
from typedef import *
from errors import *

import os


# wrapper class to pass meta information between AST nodes
class RTResult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, res):
        self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        # Note: this will allow you to continue and break outside the current function
        return (
                self.error or
                self.func_return_value or
                self.loop_should_continue or
                self.loop_should_break
        )

# base class for all functions
# handles function name, generating new execution context for tracebacks,
# verifying arguments
# need to add functionality for functions with * number of arguments
class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RTResult()

        if len(args) > len(arg_names):
            return res.failure(RuntimeError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into {self}",
                self.context
            ))

        if len(args) < len(arg_names):
            return res.failure(RuntimeError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} too few args passed into {self}",
                self.context
            ))

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return(): return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.auto_return = auto_return

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return(): return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value is None: return res

        retval = (value if self.auto_return else None) or res.func_return_value or Number.null
        return res.success(retval)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"

class StructGenerator(BaseFunction):
    
    def __init__(self, name, body_node, arg_names, auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.auto_return = auto_return

        self.properties = {}

        self.pos_start = self.body_node.pos_start
        self.pos_end = self.body_node.pos_end

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()
        exec_ctx.display_name = f'struct:{exec_ctx.display_name}'

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return(): return res

        names = [el.var_name_tok.value for el in self.body_node.elements if isinstance(el, VarAssignNode)]
        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        properties = {name: exec_ctx.symbol_table.get(name) for name in names}

        if res.should_return() and res.func_return_value is None: return res


        # this is the part that is causing the problem right now
        # i am returning self, which is basically a struct factory, not a struct object
        # functions return pretyped values, so I need to make a new class for struct objects,
        # and probably rename things accordingly.

        value = Struct(properties, exec_ctx)
        retval = (value if self.auto_return else None) or res.func_return_value or Number.null
        return res.success(retval)

    def copy(self):
        copy = StructGenerator(self.name, self.body_node, self.arg_names, self.auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.properties = self.properties
        copy.static = self.static
        copy.const = self.const
        return copy

    def __repr__(self):
        return f"<struct {self.name}>"


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.should_return(): return res

        return_value = res.register(method(exec_ctx))
        if res.should_return(): return res
        return res.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    #####################################

    def execute_print(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get('value')))
        return RTResult().success(Number(0))

    execute_print.arg_names = ['value']

    def execute_print_ret(self, exec_ctx):
        return RTResult().success(String(str(exec_ctx.symbol_table.get('value'))))

    execute_print_ret.arg_names = ['value']

    def execute_input(self, exec_ctx):
        text = input()
        return RTResult().success(String(text))

    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")
        return RTResult().success(Number(number))

    execute_input_int.arg_names = []

    def execute_clear(self, exec_ctx):
        os.system('cls' if os.name == 'nt' else 'cls')
        return RTResult().success(Number(0))

    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Number.true if is_number else Number.false)

    execute_is_function.arg_names = ["value"]

    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, List):
            return RTResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        list_.elements.append(value)
        return RTResult().success(Number(0))

    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, List):
            return RTResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(index, Number):
            return RTResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                "Second argument must be number",
                exec_ctx
            ))

        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                'Element at this index could not be removed from list because index is out of bounds',
                exec_ctx
            ))
        return RTResult().success(element)

    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RTResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(listB, List):
            return RTResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                exec_ctx
            ))

        listA.elements.extend(listB.elements)
        return RTResult().success(Number(0))

    execute_extend.arg_names = ["listA", "listB"]


BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.print_ret = BuiltInFunction("print_ret")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.extend = BuiltInFunction("extend")


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
        self.globals = []

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            # return self.parent.get(name)
            if name in self.parent.globals:
                return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        val = method(node, context)
        return val

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    ###################################

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value, t=node.tok.type).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_CapsuleNode(self, node, context):
        res = RTResult()
        elements = []
        for el in node.elements:
            ret = res.register(self.visit(el, context))
            elements.append(ret)
            if res.should_return(): return res
        if len(elements) == 1:
            return RTResult().success(
                elements[0].set_context(context).set_pos(node.pos_start, node.pos_end))
        return RTResult().success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []
        for el in node.elements:
            ret = res.register(self.visit(el, context))
            elements.append(ret)
            if res.should_return(): return res
        return RTResult().success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_MapNode(self, node, context):
        res = RTResult()
        elements = {}
        for key, val in node.elements.items():
            mykey = res.register(self.visit(key, context))
            myval = res.register(self.visit(val, context))
            elements[mykey] = myval

            if res.should_return(): return res

        return RTResult().success(
            Map(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return(): return res
        if isinstance(left, Struct):
            try: right = res.register(self.visit(node.right_node, left.context))
            except VariableAccessError:
                raise VariableAccessError(node.pos_start, node.pos_end,
                                          f"Struct has no property '{node.right_node.var_name_tok}'")
        else:
            right = res.register(self.visit(node.right_node, context))
        if res.should_return(): return res

        if node.op_tok.type == 'PLS': result, error = left.add(right)
        elif node.op_tok.type == 'MNS': result, error = left.sub(right)
        elif node.op_tok.type == 'MUL': result, error = left.mul(right)
        elif node.op_tok.type == 'DIV': result, error = left.div(right)
        elif node.op_tok.type == 'MOD': result, error = left.mod(right)
        elif node.op_tok.type == 'POW': result, error = left.pow(right)
        elif node.op_tok.type == 'EQ': result, error = left.eq(right)
        elif node.op_tok.type == 'NE': result, error = left.ne(right)
        elif node.op_tok.type == 'LT': result, error = left.lt(right)
        elif node.op_tok.type == 'GT': result, error = left.gt(right)
        elif node.op_tok.type == 'LE': result, error = left.le(right)
        elif node.op_tok.type == 'GE': result, error = left.ge(right)
        elif node.op_tok.type == 'AND': result, error = left.logand(right)
        elif node.op_tok.type == 'OR': result, error = left.logor(right)
        elif node.op_tok.type == 'NAND': result, error = left.lognand(right)
        elif node.op_tok.type == 'NOR': result, error = left.lognor(right)
        elif node.op_tok.type == 'XOR': result, error = left.logxor(right)
        elif node.op_tok.type == 'AT': result, error = left.at(right)
        elif node.op_tok.type == 'LSLC': result, error = left.sliceleft(right)
        elif node.op_tok.type == 'RSLC': result, error = left.sliceright(right)
        elif node.op_tok.type == 'DOT':
            result, error = right, None
            pass

        if error:
            return res.failure(error)
        else:
            # return res.success(result.set_pos(node.pos_start, node.pos_end))
            return res.success(result)

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return(): return res

        error = None

        if node.op_tok.type == 'MNS':
            number, error = number.mul(Number(-1))
        if node.op_tok.type == 'NOT':
            number, error = number.lognot(Number(-1))

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value

        # when I was writing this myself, this line was acting funky.  It would put the builtin function
        # into 'Special Variables' and then wouldn't recognize that it had a copy method when that got called a
        # few lines down.  I don't know what I did, but this is a note-to-self just in case something similar happens
        # in the future.
        value = context.symbol_table.get(var_name)

        if not value:
            raise VariableAccessError(node.pos_start, node.pos_end,
                                      f"'{var_name}' is not defined")

        if isinstance(value, Struct):
            value = value.copy().set_pos(node.pos_start, node.pos_end)
        elif context.display_name.startswith('struct'):
            value = value.set_pos(node.pos_start, node.pos_end)
        else:
            value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        op_tok = node.op_tok.value
        if var_name in KWDS + ['T', 'F']:
            raise BuiltinViolationError(node.pos_start, node.pos_end,
                                        f'Cannot overwrite keyword {var_name}.')
        value = res.register(self.visit(node.value_node, context))
        if res.should_return(): return res

        og_val = context.symbol_table.get(var_name)
        static_mode = context.symbol_table.get('static-typing').is_true()

        # handle new variable assignment
        if og_val is None:

            # if a static type is provided, check to make sure it isn't violated
            # note that float values will be truncated if cast to static int
            # this should execute no matter what type mode we are in
            if node.statictype not in ['var', 'default']:
                if value.type.lower() != node.statictype:
                    if isinstance(value, Number):
                        if node.statictype == 'int':
                            value.value = int(value.value)
                            value.type = 'INT'
                        elif node.statictype == 'flt':
                            value.value = float(value.value)
                            value.type = 'FLT'
                        else:
                            raise StaticViolationError(f'Cannot convert {value.value} to {node.statictype}')
                    else:
                        raise StaticViolationError(f'Cannot convert {value.value} to static {node.statictype}')
                value.static = True

            if static_mode:
                if node.statictype == 'var':
                    value.static = False
                else:
                    value.static = True
            else:
                if node.statictype not in ['var', 'default']:
                    value.static = True
                else:
                    value.static = False

            # if const keyword is used, set new value to constant
            if node.const:
                value.const = True

            # can only use bare assignment to create new value
            if op_tok == '=':
                context.symbol_table.set(var_name, value)
            else:
                raise Exception(f'Symbol {var_name} doesn\'t exist')
            return res.success(value)

        # variable already exists
        else:
            if og_val.const:
                raise ConstantViolationError(node.pos_start, node.pos_end,
                                             f'Cannot change value of constant variable {var_name}')

            if node.statictype != 'default' or node.const:
                raise InvalidSpecifierError(node.pos_start, node.pos_end,
                                            f'Specifiers not allowed on existing variable {var_name}.')

            # only check number conversion if variable is static
            # if in static mode and not otherwise specified, the variable should be set to
            # static automatically
            if og_val.static:
                if value.type != og_val.type:
                    if isinstance(value, Number):
                        if og_val.type == 'INT':
                            value.value = int(value.value)
                            value.type = 'INT'
                        elif og_val.type == 'FLT':
                            value.value = float(value.value)
                            value.type = 'FLT'
                        else:
                            raise StaticViolationError(node.pos_start, node.pos_end,
                                                       f'Cannot convert static {og_val.type} to {value.type}')

                        for t in value.triggers:
                            condition = res.register(self.visit(node.condition_node, context))
                            if condition.is_true():
                                result = res.register(self.visit(node.body_node, context))

                            if res.should_return(): return res

                        value.static = True
                    # if the new value's inferred type is different than the original value,
                    # throw an error
                    else:
                        raise StaticViolationError(node.pos_start, node.pos_end,
                                                   f'Cannot convert {var_name} [{og_val.type}] to {value.type}')
                value.static = True

            value.const = og_val.const
            value.triggers = og_val.triggers

        if op_tok == '=':

            context.symbol_table.set(var_name, value)

            for t in value.triggers:
                condition = res.register(self.visit(t.condition_node, context))
                if res.should_return(): return res

                if condition.is_true():
                    result = res.register(self.visit(t.body_node, context))

        elif op_tok == '+=': value = og_val.add(value)[0]
        elif op_tok == '-=': value = og_val.sub(value)[0]
        elif op_tok == '*=': value = og_val.mul(value)[0]
        elif op_tok == '/=': value = og_val.div(value)[0]
        elif op_tok == '%=': value = og_val.mod(value)[0]
        elif op_tok == '^=': value = og_val.pow(value)[0]
        else: raise Exception('Expected assignment operator')

        context.symbol_table.set(var_name, value)

        for t in value.triggers:
            condition = res.register(self.visit(t.condition_node, context))
            if res.should_return(): return res

            if condition.is_true():
                result = res.register(self.visit(t.body_node, context))

        return res.success(value)

    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr, ret in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return(): return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return(): return res
                return res.success(expr_value)

        if node.else_case:
            else_value = res.register(self.visit(node.else_case[0], context))
            if res.should_return(): return res
            return res.success(else_value)

        return res.success(None)

    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return(): return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.should_return(): return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.should_return(): return res
        else:
            if start_value.value < end_value.value: step_value = Number(1)
            else: step_value = Number(-1)

        i = start_value.value

        # go forwards or backwards depending on step
        if step_value.value >= 0: condition = lambda: i < end_value.value
        else: condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            result = res.register(self.visit(node.body_node, context))
            if res.should_return() and not res.loop_should_continue and not res.loop_should_break: return res
            if res.loop_should_continue: continue
            if res.loop_should_break: break

            elements.append(result)

        return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return(): return res

            if not condition.is_true(): break

            result = res.register(self.visit(node.body_node, context))
            if res.should_return() and not res.loop_should_continue and not res.loop_should_break: return res
            if res.loop_should_continue: continue
            if res.loop_should_break: break

            elements.append(result)

        return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_WhenNode(self, node, context):
        res = RTResult()
        elements = []

        val = context.symbol_table.get(node.target)
        if val is None:
            raise VariableAccessError(node.left_node.pos_start, node.left_node.pos_end,
                                      f'Variable {node.target} does not exist')

        context.symbol_table.symbols[node.target].triggers.append(node)

        return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ContinueNode(self, node, context):
        return RTResult().success_continue()

    def visit_BreakNode(self, node, context):
        a = RTResult().success_break()
        return a

    def visit_ReturnNode(self, node, context):
        res = RTResult()
        if node.return_node:
            val = res.register(self.visit(node.return_node, context))
            if res.should_return(): return res
        else: val = Number.null
        return res.success_return(val)

    def visit_UseNode(self, node, context):
        res = RTResult()
        name = node.fname.value
        from os import path
        f = open(f'C:\\Users\\pvshe\\PycharmProjects\\safyr\\{name}.sfr', 'r')
        code = f.read()
        f.close()

        ast = Parser(Lexer().tokenize(code)).parse()
        if ast.error:
            raise SyntaxError(node.fname.pos_start, node.fname.pos_end,
                              f'Error parsing file {name}')

        result = self.visit(ast.node, context)
        return res.success(result.value)


    def visit_FunctionDefinitionNode(self, node, context):
        res = RTResult()
        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [a.value for a in node.arg_name_toks]

        func_val = Function(func_name, body_node, arg_names, node.auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
        if node.var_name_tok:
            context.symbol_table.set(func_name, func_val)

        return res.success(func_val)

    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return(): return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for a in node.arg_nodes:
            args.append(res.register(self.visit(a, context)))
            if res.should_return(): return res

        retval = res.register(value_to_call.execute(args))
        if res.should_return(): return res

        if isinstance(retval, Struct):
            return res.success(retval.copy().set_pos(node.pos_start, node.pos_end))
        return res.success(retval.copy().set_pos(node.pos_start, node.pos_end).set_context(context))

    def visit_StructDefinitionNode(self, node, context):
        res = RTResult()
        struct_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [a.value for a in node.arg_name_toks]

        struct_val = StructGenerator(struct_name, body_node,
                                     arg_names, node.auto_return).set_context(context).set_pos(node.pos_start,
                                                                                               node.pos_end)
        if node.var_name_tok:
            context.symbol_table.set(struct_name, struct_val)

        return res.success(struct_val)

