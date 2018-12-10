from enum import Enum


class TokenEnum(Enum):
    BINARY_OP =             -1
    UNARY_OP =              -2
    CALL =                  -3
    ASSIGN =                -4
    PUSH =                  -5
    JUMP =                  -6
    RETURN =                -7

    OP_ADD =                (0, "add", BINARY_OP, "+", 6)
    OP_SUBTRACT =           (1, "subtract", BINARY_OP, "-", 6)
    OP_MULTIPLY =           (2, "multiply", BINARY_OP, "*", 5)
    OP_DIVIDE =             (3, "divide", BINARY_OP, "/", 5)
    OP_MODULO =             (4, "modulo", BINARY_OP, "%", 5)
    OP_BINARY_OR =          (5, "binary_or", BINARY_OP, "|", 12)
    OP_BINARY_AND =         (6, "binary_and", BINARY_OP, "&", 10)
    OP_LESS =               (7, "less", BINARY_OP, "<", 8)
    OP_GREATER =            (8, "greater", BINARY_OP, ">", 8)
    OP_ASSIGN =             (9, "assign", ASSIGN, "=", 16)

    OP_LOGICAL_OR =         (11, "logical_or", BINARY_OP, "||", 14)
    OP_LOGICAL_AND =        (12, "logical_and", BINARY_OP, "&&", 13)
    OP_SHIFT_LEFT =         (13, "shift_left", BINARY_OP, "<<", 7)
    OP_SHIFT_RIGHT =        (14, "shift_right", BINARY_OP, ">>", 7)
    OP_LESS_OR_EQUAL =      (15, "less_or_equal", BINARY_OP, "<=", 8)
    OP_EQUAL =              (16, "equal", BINARY_OP, "==", 9)
    OP_NOT_EQUAL =          (17, "not_equal", BINARY_OP, "!=", 9)
    OP_GREATER_OR_EQUAL =   (18, "greater_or_equal", BINARY_OP, ">=", 8)
    OP_ASSIGN_ADD =         (19, "assign_add", ASSIGN, "+=", 16)
    OP_ASSIGN_SUBTRACT =    (20, "assign_subtract", ASSIGN, "-=", 16)
    OP_ASSIGN_MULTIPLY =    (21, "assign_multiply", ASSIGN, "*=", 16)
    OP_ASSIGN_DIVIDE =      (22, "assign_divide", ASSIGN, "/=", 16)

    OP_PLUS =               (30, "plus", UNARY_OP, "+", 3)
    OP_MINUS =              (31, "minus", UNARY_OP, "-", 3)
    OP_NOT =                (32, "not", UNARY_OP, "!", 3)
    OP_NEGATE =             (33, "negate", UNARY_OP, "~", 3)

    TOK_BRACE_ON =          40
    TOK_BRACE_OFF =         41
    TOK_SEMICOLON =         42
    TOK_COMMA =             43
    TOK_TAIL =              44  # TODO what's that
    TOK_NONE =              45

    TOK_FLOAT =             51
    TOK_VAR =               52
    TOK_OPERATOR =          53

    TOK_RETURN =            (60, "return", RETURN)
    TOK_CALL =              (61, "call", CALL, True)
    TOK_CALL_EXTERNAL =     (62, "call_external", CALL, True)
    TOK_POP_INT =           (63, "pop_int")
    TOK_PUSH_INT =          (64, "push_int", PUSH, True)
    TOK_PUSH_VAR =          (65, "push_var", PUSH, True)
    TOK_PUSH_STRING =       (66, "push_string", PUSH)
    TOK_PUSH_INSTANCE =     (67, "push_instance", PUSH, True)
    TOK_PUSH_INDEX =        (68, "push_index", PUSH)
    TOK_POP_VAR =           (69, "pop_var")
    TOK_ASSIGN_STRING =     (70, "assign_string", ASSIGN, "=", 16)
    TOK_ASSIGN_STRING_REF = (71, "assign_string_ref", ASSIGN, "=", 16)
    TOK_ASSIGN_FUNC =       (72, "assign_func", ASSIGN, "=", 16)
    TOK_ASSIGN_FLOAT =      (73, "assign_float", ASSIGN, "=", 16)
    TOK_ASSIGN_INSTANCE =   (74, "assign_instance", ASSIGN, "=", 16)
    TOK_JUMP =              (75, "jump", JUMP, True)
    TOK_JUMP_IF =           (76, "jump_if", JUMP, True)

    TOK_SET_INSTANCE =      (80, "set_instance", ASSIGN, True)

    TOK_SKIP =              90
    TOK_LABEL =             91
    TOK_FUNC =              92
    TOK_FUNC_END =          93
    TOK_CLASS =             94
    TOK_CLASS_END =         95
    TOK_INSTANCE =          96
    TOK_INSTANCE_END =      97
    TOK_NEW_STRING =        98

    TOK_FLAG_ARRAY =        180

    TOK_PUSH_ARRAY_VAR =    (245, "push_array_var", PUSH, True, True)

    def __init__(self, _id, _name=None, _type=None, *args):
        self._value2member_map_[_id] = self
        self._id = _id
        self._name = _name
        self._type = _type

        self.has_parameter = None
        self.flag = None

        self.operator = None
        self.precedence = None

        if args:
            self.post_init(*args)

    def post_init(self, par0=None, par1=False):
        if isinstance(par0, bool):
            self.has_parameter = par0
            self.flag = par1
        elif isinstance(par0, str):
            self.operator = par0
            self.precedence = par1
        else:
            raise Exception('Unexpexted argument type')

    @property
    def type(self):
        return TokenEnum(self._type)
