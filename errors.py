# Class definitions for errors


class SyntaxError(Exception):
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def __repr__(self):
        mystr = f'{self.error_name}: {self.details}\n'
        mystr += f'  File {self.pos_start.fn}, line {self.pos_start.ln + 1}, col {self.pos_end.col}'
        mystr += '\n  ~>   ' + self.pos_start.ftxt
        mystr += '\n       ' + ' ' * self.pos_start.col
        mystr += '^' * (self.pos_end.col - self.pos_start.col)
        return mystr

    def __str__(self):
        mystr = f'{self.error_name}: {self.details}\n'
        mystr += f'  File {self.pos_start.fn}, line {self.pos_start.ln + 1}, col {self.pos_end.col}'
        mystr += '\n  ~>   ' + self.pos_start.ftxt
        mystr += '\n       ' + ' ' * self.pos_start.col
        mystr += '^' * (self.pos_end.col - self.pos_start.col)
        return mystr


class IllegalInputCharacterError(SyntaxError):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'IllegalInputCharacterError', details)

class IllegalTokenFormatError(SyntaxError):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'IllegalTokenFormatError', details)


class UnmatchedQuoteError(SyntaxError):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'UnmatchedQuoteError', details)


class InvalidSyntaxError(SyntaxError):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'InvalidSyntaxError', details)


class UnclosedScopeError(SyntaxError):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'UnclosedScopeError', details)


class BuiltinViolationError(SyntaxError):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'BuiltinViolationError', details)


class ConstantViolationError(SyntaxError):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'ConstantViolationError', details)


class StaticViolationError(SyntaxError):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'StaticViolationError', details)


class InvalidSpecifierError(SyntaxError):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'InvalidSpecifierError', details)


class VariableAccessError(SyntaxError):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'VariableAccessError', details)


class RuntimeError(SyntaxError):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'RuntimeError', details)
        self.context = context
        result = self.generate_traceback()

    def __str__(self):
        mystr = self.generate_traceback()
        mystr += super().__str__()
        return mystr

    def __repr__(self):
        mystr = self.generate_traceback()
        mystr += super().__str__()
        return mystr

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result
