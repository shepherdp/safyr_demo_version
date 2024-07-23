from errors import RuntimeError, InvalidSyntaxError

class Value:
    def __init__(self, t=None, static=False, const=False):
        self.set_pos()
        self.set_context()
        self.value = None
        self.type = t
        self.static = static
        self.const = const
        self.triggers = []

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def add(self, other):
        return None, self.illegal_op(other)

    def sub(self, other):
        return None, self.illegal_op(other)

    def mul(self, other):
        return None, self.illegal_op(other)

    def div(self, other):
        return None, self.illegal_op(other)

    def mod(self, other):
        return None, self.illegal_op(other)

    def pow(self, other):
        return None, self.illegal_op(other)

    def eq(self, other):
        return None, self.illegal_op(other)

    def ne(self, other):
        return None, self.illegal_op(other)

    def lt(self, other):
        return None, self.illegal_op(other)

    def gt(self, other):
        return None, self.illegal_op(other)

    def le(self, other):
        return None, self.illegal_op(other)

    def ge(self, other):
        return None, self.illegal_op(other)

    def logand(self, other):
        return None, self.illegal_op(other)

    def logor(self, other):
        return None, self.illegal_op(other)

    def lognand(self, other):
        return None, self.illegal_op(other)

    def lognor(self, other):
        return None, self.illegal_op(other)

    def logxor(self, other):
        return None, self.illegal_op(other)

    def lognot(self, other):
        return None, self.illegal_op(other)

    def at(self, other):
        return None, self.illegal_op(other)

    def sliceleft(self, other):
        return None, self.illegal_op(other)

    def sliceright(self, other):
        return None, self.illegal_op(other)

    def copy(self):
        copy = Value(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def illegal_op(self, other=None):
        if other:
            return RuntimeError(self.pos_start, other.pos_end,
                           'Illegal operation',
                           self.context)

    def __repr__(self):
        return str(self.value)

class Number(Value):
    def __init__(self, value, t=None):
        super().__init__(t=t if t else 'INT')
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Number):
            return self.value == other.value and self.type == other.type
        return False

    def __hash__(self):
        return self.value.__hash__()

    def add(self, other):
        if isinstance(other, Number):
            ret = self.copy()
            ret.value = self.value + other.value
            return ret.set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def sub(self, other):
        if isinstance(other, Number):
            ret = self.copy()
            ret.value = self.value - other.value
            return ret.set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def mul(self, other):
        if isinstance(other, Number):
            ret = self.copy()
            ret.value = self.value * other.value
            return ret.set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def div(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RuntimeError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )
            ret = self.copy()
            ret.value = self.value / other.value
            return ret.set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def mod(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RuntimeError(
                    other.pos_start, other.pos_end,
                    'Modulo by zero',
                    self.context
                )

            ret = self.copy()
            ret.value = self.value % other.value
            return ret.set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def pow(self, other):
        if isinstance(other, Number):
            ret = self.copy()
            ret.value = self.value ** other.value
            return ret.set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def le(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def ge(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def logand(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def logor(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def lognand(self, other):
        if isinstance(other, Number):
            return Number(int(not(self.value and other.value))).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def lognor(self, other):
        if isinstance(other, Number):
            return Number(int(not(self.value or other.value))).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def logxor(self, other):
        if isinstance(other, Number):
            return Number(int((self.value and not other.value) or (not self.value and other.value))
                          ).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def lognot(self, other):
        if isinstance(other, Number):
            return Number(1 if self.value == 0 else 0).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def at(self, other):
        # @ operator returns the other-th digit from the left on a Number
        myrepr = str(self.value)
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(myrepr):
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                     "Index out of range")
        elem = Number(int(myrepr[other.value]))
        return elem, None

    def copy(self):
        copy = Number(self.value)
        copy.static = self.static
        copy.const = self.const
        copy.triggers = self.triggers
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0


Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)

class String(Value):
    def __init__(self, value):
        super().__init__(t='STR')
        self.value = value

    def __eq__(self, other):
        if isinstance(other, String):
            return self.value == other.value
        return False

    def __hash__(self):
        return self.value.__hash__()

    def add(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def sub(self, other):
        if isinstance(other, String):
            return String(self.value.replace(other.value, '')).set_context(self.context), None
        else:
            return None, Value.illegal_op(self.pos_start, other.pos_end)

    def mul(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_op(self, other)

    def at(self, other):
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(self.value):
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                     "Index out of range")
        elem = String(self.value[other.value])
        return elem, None

    def sliceleft(self, other):
        val = other.value
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(self.value):
            val = len(self.value)
        newlist = self.copy()
        newlist.value = newlist.value[:val]
        return newlist, None

    def sliceright(self, other):
        val = other.value
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(self.value):
            val = len(self.value)
        newlist = self.copy()
        newlist.value = newlist.value[-val:]
        return newlist, None

    def copy(self):
        copy = String(self.value)
        copy.static = self.static
        copy.const = self.const
        copy.triggers = self.triggers
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != ''

    def __repr__(self):
        return f'"{self.value}"'

    def __str__(self):
        return f'"{self.value}"'

    def __eq__(self, other):
        return self.value == other.value if other is not None else False

class List(Value):
    def __init__(self, elements):
        super().__init__(t='LST')
        self.elements = elements

    def add(self, other):
        newlist = self.copy()
        newlist.elements.append(other)
        return newlist, None

    def sub(self, other):
        newlist = self.copy()
        while other in newlist.elements:
            newlist.elements.remove(other)
        return newlist, None

    def at(self, other):
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(self.elements):
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                     "Index out of range")
        elem = self.elements[other.value].copy()
        return elem, None

    def sliceleft(self, other):
        val = other.value
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(self.elements):
            val = len(self.elements)
        newlist = self.copy()
        newlist.elements = newlist.elements[:val]
        return newlist, None

    def sliceright(self, other):
        val = other.value
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(self.elements):
            val = len(self.elements)
        newlist = self.copy()
        newlist.elements = newlist.elements[-val:]
        return newlist, None

    def copy(self):
        copy = List(self.elements)
        copy.static = self.static
        copy.const = self.const
        copy.triggers = self.triggers
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.elements)

    def __eq__(self, other):
        if not isinstance(other, List):
            return False
        if len(self.elements) != len(other.elements):
            return False
        for i in range(len(self.elements)):
            if self.elements[i] != other.elements[i]:
                return False
        return True

class Map(Value):
    def __init__(self, elements):
        super().__init__(t='MAP')
        self.elements = elements

    def copy(self):
        copy = Map(self.elements)
        copy.static = self.static
        copy.const = self.const
        copy.triggers = self.triggers
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.elements)
    
    
class Struct(Value):
    def __init__(self, properties, context):
        super().__init__('')
        self.properties = properties
        self.context = context

    def __repr__(self):
        return f'{self.properties}'

    def copy(self):
        copy = Struct(self.properties, self.context)
        copy.static = self.static
        copy.const = self.const
        copy.triggers = self.triggers
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
