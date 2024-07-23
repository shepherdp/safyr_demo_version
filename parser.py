from errors import *
from lexer import Token


class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'"{self.tok}"'

    def __str__(self):
        return f'"{self.tok}"'


class CapsuleNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.elements = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.elements = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end


class MapNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements

        self.pos_start = pos_start
        self.pos_end = pos_end


class UseNode:
    def __init__(self, fname):
        self.fname = fname

        self.pos_start = self.fname.pos_start
        self.pos_end = self.fname.pos_end

    def __repr__(self):
        return f'<{self.fname}>'


class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return f'{self.var_name_tok}'


class VarAssignNode:
    def __init__(self, var_name_tok, op_tok, value_node,
                 const=False, statictype=None):
        self.var_name_tok = var_name_tok
        self.op_tok = op_tok
        self.value_node = value_node
        self.const = const
        self.statictype = statictype

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end

    def __repr__(self):
        return f'({self.var_name_tok} {self.op_tok} {self.value_node})'


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end


class ForNode:
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class WhenNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.target = condition_node.left_node.var_name_tok.value

        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class ReturnNode:
    def __init__(self, return_node, pos_start, pos_end):
        self.return_node = return_node
        self.pos_start = pos_start
        self.pos_end = pos_end


class FunctionDefinitionNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node, auto_return):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.auto_return = auto_return

        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end


class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end


class StructDefinitionNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node, auto_return):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.auto_return = auto_return

        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            # self.error = res.error
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self


class Parser:
    def __init__(self, tokens, symbol_table=None):
        self.warnings = []
        self.tokens = tokens
        self.symbol_table = symbol_table
        self.static = False
        if symbol_table:
            if self.symbol_table.get('static-typing').is_true():
                self.static = True
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if 0 <= self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def peek(self):
        if self.tok_idx < len(self.tokens) - 1:
            return self.tokens[self.tok_idx + 1]

    def parse(self):
        res = self.statements()
        if res.error:
            return res
        return res

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == 'BREAK':
            res.register_advancement()
            self.advance()

        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True

        # THIS IS AN ISSUE
        # Right now, if I try to put an expression on a line directly below a statement,
        # it doesn't get counted at all.
        # Just going to add another line to the test case for right now

        # EDIT
        # I added the 'if isinstance(...)' part below to fix this.
        # The idea is that if I get a one-liner like that, I need to assume
        # keep looking for more code.  This is kind of a band-aid, and the process
        # of checking for more statements needs to be refactored to be more
        # robust.  For now, this just says 'If I saw an import statement last,
        # assume there could be more lines.'

        while True:
            newline_count = 0
            while self.current_tok.type == 'BREAK':
                res.register_advancement()
                self.advance()
                newline_count += 1
            if isinstance(statements[-1], UseNode):
                newline_count += 1
            if newline_count == 0:
                more_statements = False
            if self.current_tok.type == 'EOF':
                more_statements = False

            if not more_statements: break
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(CapsuleNode(
            statements,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.matches(Token('KWD', 'use')):
            res.register_advancement()
            self.advance()

            if self.current_tok.type == 'SYM':
                fname = self.current_tok
                res.register_advancement()
                self.advance()
            else:
                raise InvalidSyntaxError(pos_start, self.current_tok.pos_end,
                                         f'Expected file identifier')

            if self.current_tok.matches(Token('BREAK', None)):
                res.register_advancement()
                self.advance()
            elif self.current_tok.matches(Token('EOF', None)):
                pass
            else:
                raise InvalidSyntaxError(pos_start, self.current_tok.pos_end,
                                         f'Expected newline')

            return res.success(UseNode(fname))

        if self.current_tok.matches(Token('KWD', 'return')):
            res.register_advancement()
            self.advance()
            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))

        if self.current_tok.matches(Token('KWD', 'continue')):
            res.register_advancement()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))

        if self.current_tok.matches(Token('KWD', 'break')):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))


        expr = res.register(self.expr())
        if res.error:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start,
                                                  self.current_tok.pos_end,
                                                  'Expected expression.'))

        return res.success(expr)

    def expr(self):
        res = ParseResult()
        warn_msg = ''

        statictype = 'default'
        constvar = False

        # check for constant declaration
        if self.current_tok.matches(Token('KWD', 'const')):
            constvar = True
            res.register_advancement()
            self.advance()

        # warning about unnecessary var keyword
        if self.current_tok.matches(Token('KWD', 'var')):
            if not self.static:
                warn_msg = f'kwd <var> has no effect'
            statictype = 'var'
            res.register_advancement()
            self.advance()

        # check for explicit type definition
        if self.current_tok.value in ['int', 'flt', 'str', 'lst', 'map']:
            statictype = self.current_tok.value
            res.register_advancement()
            self.advance()

        if self.current_tok.type == 'SYM' and self.peek().type == 'ASG':

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error: return res
            if warn_msg:
                self.warnings.append(warn_msg)

            return res.success(VarAssignNode(var_name, op_tok, expr,
                                             const=constvar, statictype=statictype))

        node = res.register(self.bin_op(self.comp_expr, (('AND', '&'), ('OR', '|'),
                                                         ('NAND', '~&'), ('NOR', '~|'),
                                                         ('XOR', '><'))))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected keyword, identifier, or control flow structure."
            ))

        if warn_msg:
            self.warnings.append(warn_msg)

        return res.success(node)

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(Token('NOT', '~')):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(self.arith_expr, ('EQ', 'NE', 'LT', 'GT', 'LE', 'GE')))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected int, float, identifier, '+', '-', '(', '[', 'IF', 'FOR', 'WHILE', 'FUN' or 'NOT'"
            ))

        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, ('PLS', 'MNS'))

    def term(self):
        return self.bin_op(self.factor, ('MUL', 'DIV', 'MOD'))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in ('PLS', 'MNS'):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        return self.bin_op(self.call, ('POW', 'AT', 'LSLC', 'RSLC', 'DOT'), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == 'LPR':
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == 'RPR':
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
                    ))

                while self.current_tok.type != 'RPR':

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                    if self.current_tok.type == 'EOF':
                        return res.failure(InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end,
                            f"Expected ',' or ')'"
                        ))

                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in ('INT', 'FLT'):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == 'STR':
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type == 'SYM':
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == 'LPR':
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == 'RPR':
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        elif tok.type == 'LBR':
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)

        elif tok.type == 'LCR':
            list_expr = res.register(self.map_expr())
            if res.error: return res
            return res.success(list_expr)

        elif tok.matches(Token('KWD', '?')) or tok.matches(Token('KWD', 'if')):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        elif tok.matches(Token('KWD', 'for')):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)

        elif tok.matches(Token('KWD', 'while')):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

        elif tok.matches(Token('KWD', 'when')):
            when_expr = res.register(self.when_expr())
            if res.error: return res
            return res.success(when_expr)

        elif tok.matches(Token('DOT', '.')):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)

        elif tok.matches(Token('OPS', ':')):
            struct_def = res.register(self.struct_def())
            if res.error: return res
            return res.success(struct_def)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, identifier, '+', '-', '(', '[', IF', 'FOR', 'WHILE', 'FUN'"
        ))

    def map_expr(self):
        res = ParseResult()
        elements = {}
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != 'LCR':
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == 'RCR':
            res.register_advancement()
            self.advance()
        else:
            while self.current_tok.type not in ['RCR', 'EOF']:
                key = res.register(self.expr())
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected '}', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
                    ))

                if not self.current_tok.matches(Token('OPS', ':')):
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ':'"
                    ))

                res.register_advancement()
                self.advance()

                value = res.register(self.expr())
                if res.error: return res

                elements[key] = value

                while self.current_tok.matches(Token('BREAK', None)):
                    res.register_advancement()
                    self.advance()

            if self.current_tok.type != 'RCR':
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ']'"
                ))

            res.register_advancement()
            self.advance()

        return res.success(MapNode(
            elements,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != 'LBR':
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '['"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == 'RBR':
            res.register_advancement()
            self.advance()
        else:
            while self.current_tok.type not in ['RBR', 'EOF']:
                element_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ']', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
                    ))

            if self.current_tok.type != 'RBR':
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ']'"
                ))

            res.register_advancement()
            self.advance()

        return res.success(ListNode(
            element_nodes,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases('?'))
        if res.error: return res
        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases('!?')

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(Token('KWD', '!')):
            res.register_advancement()
            self.advance()

            if self.current_tok.type == 'BREAK':
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

                if self.current_tok.matches(Token('KWD', 'end')):
                    res.register_advancement()
                    self.advance()
                else:
                    raise InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end,
                                             'Expected "end"')

            else:
                expr = res.register(self.expr())
                if res.error: return res
                else_case = (expr, False)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        while self.current_tok.type == 'BREAK':
            res.register_advancement()
            self.advance()

        if self.current_tok.matches(Token('KWD', '!?')):
            all_cases = res.register(self.if_expr_b())
            if res.error: return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error: return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(Token('KWD', case_keyword)):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{case_keyword}'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(Token('OPS', ':')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == 'BREAK':
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_tok.matches(Token('KWD', 'end')):
                res.register_advancement()
                self.advance()
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
            else:
                raise UnclosedScopeError(self.current_tok.pos_start, self.current_tok.pos_end,
                                         "Expected 'end'")

        else:
            expr = res.register(self.statement())
            if res.error: return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(Token('KWD', 'for')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'FOR'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != 'SYM':
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected identifier"
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.value != '=':
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '='"
            ))

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(Token('OPS', '..')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '..'"
            ))

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error: return res

        if self.current_tok.matches(Token('OPS', '..')):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error: return res
        else:
            step_value = None

        if not self.current_tok.matches(Token('OPS', ':')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == 'BREAK':
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(Token('KWD', 'end')):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected 'end'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = res.register(self.statement())
        if res.error: return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(Token('KWD', 'while')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'while'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(Token('OPS', ':')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == 'BREAK':
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(Token('KWD', 'end')):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected 'end'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error: return res

        return res.success(WhileNode(condition, body, False))

    def when_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(Token('KWD', 'when')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'when'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(Token('OPS', ':')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == 'BREAK':
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(Token('KWD', 'end')):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected 'end'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(WhenNode(condition, body, True))

        body = res.register(self.statement())
        if res.error: return res

        return res.success(WhenNode(condition, body, False))

    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(Token('DOT', '.')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '.'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == 'SYM':
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != 'LBR':
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '['"
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != 'LBR':
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected identifier or '['"
                ))

        res.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_tok.type == 'SYM':

            while self.current_tok.type == 'SYM':

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != 'RBR':
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ']'"
                ))
        else:
            if self.current_tok.type != 'RBR':
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected identifier or ']'"
                ))

        res.register_advancement()
        self.advance()

        # <~ follows optional brackets
        if self.current_tok.type == 'INJ':
            res.register_advancement()
            self.advance()

            # statements start on next line
            if self.current_tok.type == 'BREAK':
                res.register_advancement()
                self.advance()

                body = res.register(self.statements())
                if res.error: return res

                # function definition must end with if
                if not self.current_tok.matches(Token('KWD', 'end')):
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected 'end'"
                    ))

                # advance past end
                res.register_advancement()
                self.advance()

                # return multi line function definition
                return res.success(FunctionDefinitionNode(
                    var_name_tok,
                    arg_name_toks,
                    body,
                    False))

            # one-line functions auto-return, so ignore the return keyword if it was included
            if self.current_tok.matches(Token('KWD', 'return')):
                res.register_advancement()
                self.advance()

            body = res.register(self.expr())
            if res.error: return res

            return res.success(FunctionDefinitionNode(
                var_name_tok,
                arg_name_toks,
                body,
                True
            ))

        # fail if no injection operator
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected NEWLINE"
        ))

    def struct_def(self):
        res = ParseResult()

        if not self.current_tok.matches(Token('OPS', ':')):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == 'SYM':
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != 'LBR':
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected '['"
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != 'LBR':
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected identifier or '['"
                ))

        res.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_tok.type == 'SYM':

            while self.current_tok.type == 'SYM':

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != 'RBR':
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ']'"
                ))
        else:
            if self.current_tok.type != 'RBR':
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected identifier or ']'"
                ))

        res.register_advancement()
        self.advance()

        # { follows optional brackets
        if self.current_tok.type == 'LCR':
            res.register_advancement()
            self.advance()

            # statements start on next line
            if self.current_tok.type == 'BREAK':
                res.register_advancement()
                self.advance()

                body = res.register(self.statements())
                if res.error: return res

                # function definition must end with if
                if not self.current_tok.type == 'RCR':
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected '}'"
                    ))

                # advance past end
                res.register_advancement()
                self.advance()

                # return multi line function definition
                return res.success(StructDefinitionNode(
                    var_name_tok,
                    arg_name_toks,
                    body,
                    True))

        # fail if no injection operator
        return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected NEWLINE"
        ))

    ###################################

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
