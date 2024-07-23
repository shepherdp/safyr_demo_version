from errors import *


DGT = '1234567890'
LWR = 'abcdefghijklmnopqrstuvwxyz'
UPR = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
PNC = '+-*/=_?/\\|><.,;:\'"&^%$#@![]{}()~'
OPS = '+-*/=%^?!><&|~:.@;'
CON = '{}[]()'
WHT = '\n\t '

KWDS = ['use', 'by', 'var', 'end', 'const', 'global',
        '?', '!?', '!',
        'if', 'elif', 'else',
        'while', 'for', 'when',
        'return', 'continue', 'break',
        'int', 'flt', 'str', 'lst']

BIGRAPHS = ['+=', '-=', '*=', '/=', '^=', '%=',
            '++', '--', '==', '!=', '<=', '>=',
            '<~', '~>', '~&', '~|', '><', '!?',
            '</', '/>', '..', ':=']

OPNAMES = {'+': 'PLS',
           '-': 'MNS',
           '*': 'MUL',
           '/': 'DIV',
           '%': 'MOD',
           '^': 'POW',
           '&': 'AND',
           '|': 'OR',
           '~': 'NOT',
           '[': 'LBR',
           ']': 'RBR',
           '(': 'LPR',
           ')': 'RPR',
           '{': 'LCR',
           '}': 'RCR',
           '@': 'AT',
           '.': 'DOT',
           '=': 'ASG',
           ':=': 'ASG',
           '+=': 'ASG',
           '-=': 'ASG',
           '*=': 'ASG',
           '/=': 'ASG',
           '%=': 'ASG',
           '^=': 'ASG',
           '<': 'LT',
           '>': 'GT',
           '<=': 'LE',
           '>=': 'GE',
           '!=': 'NE',
           '==': 'EQ',
           '<~': 'INJ',
           '~&': 'NAND',
           '~|': 'NOR',
           '><': 'XOR',
           '..': 'RNG',
           '</': 'LSLC',
           '/>': 'RSLC'
           }


class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self):
        self.idx += 1
        self.col += 1
        return self

    def __repr__(self):
        return f'idx: {self.idx} line: {self.ln} col: {self.col} name: {self.fn}'

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, other):
        return self == other

    def __repr__(self):
        if self.value is not None: return f'{self.type}:{self.value}'
        return f'{self.type}'

    def __eq__(self, other):
        return self.value == other.value and self.type == other.type


class Lexer:
    def __init__(self):

        self.state = 'new'
        self.pos = 0
        self.token = ''
        self.tokens = []
        self.input = ''
        self.t = {}
        self.name = ''

        self.linenum = 0
        self.colnum = 0
        self.linestart = 0
        self.currline = ''
        self.start_pos = Position(0, 0, 0, self.name, self.input)
        self.end_pos = self.start_pos.copy()

        self.load_rules()

    def load_rules(self):
        # state notes
        # new: ready to start a new token or skip whitespace
        # int: currently building integer token
        # flt: currently building float token
        # con: container token; ends after a single character
        # ops: operator token; can end after one or two characters
        # st1: currently building single-quoted string
        # st2: currently building double-quoted string
        # sym: currently building symbol (var name or keyword)
        # fin: done building current token
        # xxx: fail
        states = ['new', 'int', 'flt', 'con', 'ops', 'dec',
                  'st1', 'st2', 'sym', 'fin', 'xxx', 'cmt']

        # with open('lexer.rules', 'r') as f:
        #     data = f.read()
        #     i = 0
        #     while True:
        #         d = data[i:i+12]
        #         if not d:
        #             break
        #         line = data[i:i+11]
        #         i += 12
        #         line = line.split('~')
        #         s, c, s_, d = line[0], line[1], line[2], int(line[3])
        #         if s not in self.t:
        #             self.t[s] = {}
        #         if c not in self.t[s]:
        #             self.t[s][c] = [s_, d]

        for s in states:
            self.t[s] = {}
        # initialize transitions for each state on seeing a digit
        for c in DGT:
            for s_ in ['new', 'int']:
                self.t[s_][c] = ['int', 1]
            for s_ in ['con', 'ops']:
                self.t[s_][c] = ['fin', 0]
            for s_ in ['flt', 'st1', 'st2', 'sym']:
                self.t[s_][c] = [s_, 1]
            self.t['dec'][c] = ['flt', 1]

        # initialize transitions for each state on seeing a letter
        for c in UPR + LWR:
            for s_ in ['con', 'ops', 'dec']:
                self.t[s_][c] = ['fin', 0]
            for s_ in ['int', 'flt']:
                self.t[s_][c] = ['xxx', 0]
            for s_ in ['new', 'sym']:
                self.t[s_][c] = ['sym', 1]
            for s_ in ['st1', 'st2']:
                self.t[s_][c] = [s_, 1]

        # initialize transitions for each state on seeing a punctuation mark
        for c in PNC:
            for s_ in ['new', 'int', 'flt', 'ops', 'sym']:
                self.t[s_][c] = ['xxx', 0]
            for s_ in ['st1', 'st2']:
                self.t[s_][c] = [s_, 1]
            self.t['con'][c] = ['fin', 0]
            self.t['dec'][c] = ['fin', 0]
            self.t['flt'][c] = ['fin', 0]

        # initialize transitions for each state on seeing an operator (overrides transitions from PNC)
        for c in OPS:
            for s_ in ['con', 'int', 'flt', 'sym']:
                self.t[s_][c] = ['fin', 0]
            for s_ in ['st1', 'st2']:
                self.t[s_][c] = [s_, 1]
            self.t['new'][c] = ['ops', 1]
            self.t['ops'][c] = ['fin', 1]
            self.t['dec']['.'] = ['fin', 1]
            self.t['flt']['.'] = ['fin', 0]

        # initialize transitions for each state on seeing a container symbol (overrides transitions from PNC)
        for c in CON:
            for s_ in ['con', 'int', 'flt', 'ops', 'sym']:
                self.t[s_][c] = ['fin', 0]
            for s_ in ['st1', 'st2']:
                self.t[s_][c] = [s_, 1]
            self.t['new'][c] = ['con', 1]

        # initialize transitions for each state on seeing whitespace
        for c in WHT:
            for s_ in ['new', 'st1', 'st2']:
                self.t[s_][c] = [s_, 1]
            for s_ in ['int', 'flt', 'ops', 'sym']:
                self.t[s_][c] = ['fin', 1]
            self.t['con'][c] = ['fin', 0]
            self.t['dec'][c] = ['fin', 1]

        # special transitions, e.g. closing off a string when the appropriate quote is encountered
        self.t['new']['.'] = ['dec', 1]
        self.t['int']['.'] = ['flt', 1]
        self.t['new']["'"] = ['st1', 1]
        self.t['new']['"'] = ['st2', 1]
        self.t['st1']["'"] = ['fin', 1]
        self.t['st2']['"'] = ['fin', 1]
        self.t['ops']['~'] = ['fin', 1]
        self.t['ops']['.'] = ['fin', 1]

        for s in ['int', 'flt', 'con', 'ops', 'dec', 'sym', 'fin', 'xxx', 'cmt']:
            self.t[s][';'] = ['fin', 0]
        for s in ['st1', 'st2']:
            self.t[s][';'] = [s, 1]
        self.t['new'][';'] = ['cmt', 1]
        for c in UPR + LWR + DGT + PNC + ' \t':
            self.t['cmt'][c] = ['cmt', 1]
        self.t['cmt']['\n'] = ['new', 1]

    # load new text and reset variables for new input
    def load(self, text, name=''):
        self.input = text
        self.state = 'new'
        self.pos = 0
        self.token = ''
        self.tokens = []
        if name:
            self.name = name

    # move the read head by amt spaces
    def move(self, amt):
        self.pos += amt

    # set token back to empty and state to new after a token has been processed
    def reset_token(self):
        self.token = ''
        self.state = 'new'

    # execute a single processing step
    def transition(self):

        try:
            line = self.input[self.linestart:self.linestart + self.input[self.linestart:].index('\n')]
            self.currline = line
        except ValueError:
            self.currline = self.input[self.linestart:]

        # grab current character
        c = self.input[self.pos]

        # print(f'POS {self.pos}: {c}')
        if self.state == 'new':
            self.start_pos = Position(self.pos, self.linenum, self.colnum, self.name, self.currline)

        # unhandled character
        if c not in self.t[self.state]:
            self.end_pos = Position(self.pos, self.linenum, self.colnum+1, self.name, self.currline)
            raise IllegalInputCharacterError(self.start_pos, self.end_pos, f'Character [{c}] not supported.')

        # get new state and number of steps to move
        s_, delta = self.t[self.state][c]

        # need to update state diagram so I don't have to kludge together like this
        if self.token == '=' and c == "'":
            s_, delta = 'fin', 0
        elif self.token == '=' and c == '"':
            s_, delta = 'fin', 0

        # fail state
        if s_ == 'xxx':
            self.end_pos = Position(self.pos, self.linenum, self.colnum+1, self.name, self.currline)
            raise IllegalTokenFormatError(self.start_pos, self.end_pos,
                                          f'Encountered character [{c}] in state [{self.state}]')

        # skip over current character
        elif s_ == 'new' and self.state == 'new':
            pass

        elif s_ == 'cmt':
            self.state = s_

        # finished with current token
        elif s_ == 'fin':
            # add current character to token if necessary
            self.end_pos = Position(self.pos, self.linenum, self.colnum, self.name, self.currline)
            if self.token == c == '~':
                delta = 0
            if self.state == 'ops' and (self.token + c not in BIGRAPHS):
                delta = 0
            if c not in WHT:
                if delta:
                    self.token += c
                    self.end_pos.idx += 1
                    self.end_pos.col += 1

            # store current token and reset for next
            self.tokens.append(self.get_token())
            self.reset_token()

        # add current character to token and change state
        else:
            self.token += c
            self.state = s_

        # track line and column numbers for error reporting
        if c == '\n':
            if self.state[:2] == 'st':
                raise UnmatchedQuoteError(self.start_pos, self.end_pos, 'Unmatched quotation mark')
            self.end_pos = Position(self.pos, self.linenum, self.colnum, self.name, self.currline)
            self.linenum += 1
            self.colnum = 0
            self.currline = ''
            self.linestart = self.pos + 1
            self.token = ''
            self.tokens.append(Token('BREAK', None, pos_start=self.start_pos, pos_end=self.end_pos))
        else:
            self.colnum += delta

        # move the read head to prepare for the next step
        self.move(delta)

    # take a raw text token and convert it to a Token object with the appropriate values
    def get_token(self):
        s = self.token
        self.end_pos = Position(self.pos, self.linenum, self.colnum, self.name, self.currline)
        # numerical token
        if s[0] in DGT + '.':
            if '.' in s:
                if s == '.':
                    return Token('DOT', s, pos_start=self.start_pos, pos_end=self.end_pos)
                if s == '..':
                    return Token('OPS', s, pos_start=self.start_pos, pos_end=self.end_pos)
                return Token('FLT', float(s), pos_start=self.start_pos, pos_end=self.end_pos)
            else:
                return Token('INT', int(s), pos_start=self.start_pos, pos_end=self.end_pos)

        # symbol token
        if s[0] in UPR + LWR:
            if s in KWDS:
                return Token('KWD', s, pos_start=self.start_pos, pos_end=self.end_pos)
            return Token('SYM', s, pos_start=self.start_pos, pos_end=self.end_pos)

        # string token
        if s[0] in '\'"':
            return Token('STR', s[1:-1], pos_start=self.start_pos, pos_end=self.end_pos)

        # operator or container token
        if s[0] in OPS + CON:
            if len(s) == 2 and s not in BIGRAPHS:
                raise IllegalTokenFormatError(self.start_pos, self.end_pos, f'Token [{s}] not supported.')
            if s in KWDS:
                if s in KWDS:
                    return Token('KWD', s, pos_start=self.start_pos, pos_end=self.end_pos)
            if s in OPNAMES:
                return Token(OPNAMES[s], s, pos_start=self.start_pos, pos_end=self.end_pos)
            return Token('OPS', s, pos_start=self.start_pos, pos_end=self.end_pos)

    def tokenize(self, text=None):
        if text:
            self.input = text
        # if self.input[-1] != '\n':
        #     self.input += '\n'
        # process entire input string
        while self.pos < len(self.input):
            self.transition()
        # if there is an active token when the end of the input is reached, store it
        if self.token:
            # handle unclosed quote in input
            if self.state in ['st1', 'st2']:
                self.end_pos = Position(self.pos, self.linenum, self.colnum+1, self.name, self.currline)
                raise UnmatchedQuoteError(self.start_pos, self.end_pos, 'Unmatched quotation mark')

            # add token to list
            self.tokens.append(self.get_token())
        self.tokens.append(Token('EOF', None,
                                 Position(self.pos, self.linenum, self.colnum, self.name,
                                          self.currline))
                           )
        return self.tokens
