from lexer import Lexer
from parser import Parser
from interpreter import *
from sys import exit

static = 0

class Shell:

    def __init__(self):
        print('Initializing Safyr Shell Environment')
        print('Type help for some example commands.')
        self.run()

    def run(self):
        global_symbol_table = SymbolTable()
        global_symbol_table.set("null", Number(0))
        global_symbol_table.set("T", Number(1))
        global_symbol_table.set("F", Number(0))
        global_symbol_table.set('static-typing', Number(static))

        global_symbol_table.set("print", BuiltInFunction.print)
        global_symbol_table.set("PRINT_RET", BuiltInFunction.print_ret)
        global_symbol_table.set("INPUT", BuiltInFunction.input)
        global_symbol_table.set("INPUT_INT", BuiltInFunction.input_int)
        global_symbol_table.set("CLEAR", BuiltInFunction.clear)
        global_symbol_table.set("CLS", BuiltInFunction.clear)
        global_symbol_table.set("IS_NUM", BuiltInFunction.is_number)
        global_symbol_table.set("IS_STR", BuiltInFunction.is_string)
        global_symbol_table.set("IS_LIST", BuiltInFunction.is_list)
        global_symbol_table.set("IS_FUN", BuiltInFunction.is_function)
        global_symbol_table.set("APPEND", BuiltInFunction.append)
        global_symbol_table.set("POP", BuiltInFunction.pop)
        global_symbol_table.set("EXTEND", BuiltInFunction.extend)

        context = Context('<program>')
        context.symbol_table = global_symbol_table
        context.symbol_table.globals = list(global_symbol_table.symbols.keys())

        while True:

            cmd = input('>> ')
            if cmd == 'q':
                break

            if cmd == 'help':
                print('Try typing one of the following commands to run the source files included:')
                print('run basic')
                print('run moduletest')
                print('run lists')
                print('run structs')
                print('run whentrigger')

            needsrun = False
            data = ''
            if cmd.startswith('run '):
                cmd = cmd[4:]
                if os.path.exists(cmd + '.sfr'):
                    with open(cmd + '.sfr', 'r') as f:
                        data = f.read()
                        needsrun = True
                else:
                    print(f'File not found: {cmd}')
            else:
                data = cmd

            if needsrun:
                lex = Lexer()
                try:
                    toks = lex.tokenize(data)
                except Exception as e:
                    print(f'Exception encountered in lexer:\n\t{e}')
                    continue

                par = Parser(toks, global_symbol_table)
                try:
                    ast = par.parse()
                    if ast.error:
                        print(f'Exception encountered in parser:\n\t{ast.error}')
                except Exception as e:
                    print(f'Exception encountered in parser:\n\t{e}')
                    continue

                context = Context('<program>')
                context.symbol_table = global_symbol_table
                try:
                    result = Interpreter().visit(ast.node, context)
                    if result.error:
                        print(f'Exception encountered in interpreter:\n\t{result.error}')
                        raise result.error
                        continue
                except Exception as e:
                    print(f'Exception encountered in interpreter:\n\t{e}')
                    raise e
                    continue

                result.value
