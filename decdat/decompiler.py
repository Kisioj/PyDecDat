import struct
from constants import Type, Flag, TYPE_2_STR, INT_FORMAT, FLOAT_FORMAT
from dat_token import Token
from tokenenum import TokenEnum

mainWinow = None


class Line:
    def __init__(self, stack_pointer, text):
        self.stack_pointer = stack_pointer
        self.text = text

    def __repr__(self):
        return f'<Line; stack_pointer: {self.stack_pointer}, text: {self.text}>'


def data_repr(element):
    if isinstance(element, str):
        return f'"{element}"'
    return f'{element}'


class DecompilerBytecode:
    def __init__(self, *args, return_param=False):

        self.tokens = None  # code
        self.current_token = None

        self.index = None
        self.lines = []

        self.return_param = return_param

        self.if_mark = []
        self.end_if = set()
        self.if_on = False

        self.decompile(*args)

    def decompile(self, address_start, address_end):
        self.tokens = Token.get_tokens_from_stack(address_start, address_end)
        self.index = len(self.tokens) - 1

        while self.index >= 0:
            self.current_token = self.tokens[self.index]
            op_type = self.current_token.op.type
            if op_type == TokenEnum.CALL:
                self.add_line(self.decompile_call() + ';')
            elif op_type == TokenEnum.RETURN:
                self.add_line(self.decompile_return())
            elif op_type == TokenEnum.PUSH:
                self.add_line(self.decompile_push() + ';')
            elif op_type in (TokenEnum.BINARY_OP, TokenEnum.UNARY_OP, TokenEnum.ASSIGN):
                self.add_line(self.decompile_operation() + ';')
            elif op_type == TokenEnum.JUMP:
                self.decompile_condition()
            else:
                raise Exception('Unknown Token')
            self.index -= 1

    def decompile_call(self):
        token = self.tokens[self.index]
        code = ''
        for symbol in reversed(token.symbol.children):
            self.index -= 1
            code = self.decompile_parameter(symbol.type) + ', ' + code
        return f'{token.symbol.local_name}({code.rstrip(", ")})'

    def decompile_parameter(self, symbol_type=None):
        op_type = self.current_op.type
        if op_type == TokenEnum.PUSH:
            return self.decompile_push(symbol_type)
        elif op_type == TokenEnum.CALL:
            return self.decompile_call()
        elif op_type in (TokenEnum.BINARY_OP, TokenEnum.UNARY_OP):
            return self.decompile_operation()
        raise Exception(f'Unknown parameter type: {op_type}')

    def decompile_return(self):
        code = 'return'
        if self.return_param:
            self.index -= 1
            code += ' ' + self.decompile_parameter(None)
        return code + ';'

    def decompile_push(self, symbol_type=None):
        # print("decompile_push index:", self.index)
        token = self.tokens[self.index]
        if token.symbol:
            symbol = token.symbol
            # print('symbol.name', symbol.name)

            if symbol.has_flag(Flag.CLASSVAR):
                # print('A')
                self.index -= 1
                next_token = self.tokens[self.index]
                if next_token.op == TokenEnum.TOK_SET_INSTANCE:
                    code = f'{next_token.symbol.local_name}.{symbol.local_name}'
                else:
                    code = symbol.local_name
                    self.index += 1

            elif symbol.name_startswith_upperdot():  # FIXME
                # print('B')
                if symbol.name.lower() in ('Яinstance_help', '˙instance_help', 'Ÿinstance_help'):
                    code = 'NULL'
                else:
                    # print(symbol.name, type(symbol.content[0]))
                    code = '"' + symbol.content[0] + '"'  # FIXME: maybe make it so conent isnt list if has one value only

            else:
                # print('C')
                code = symbol.local_name

            if token.offset:
                code += f'[{token.offset}]'

            return code

        if symbol_type in (Type.INSTANCE, Type.FUNC):
            # if token.int_param == -1:
            if token.int_param is None:
                if symbol_type == Type.FUNC:
                    return 'NOFUNC'
                return '-1'

            return mainWindow.dat.symbols[token.int_param].local_name

        elif symbol_type == Type.FLOAT:
            return str(struct.unpack(FLOAT_FORMAT, struct.pack(INT_FORMAT, token.int_param))[0])

        return str(token.int_param)

    def decompile_operation(self, parent_precedence=0):
        code = ''
        op = self.current_op

        has_brackets = op.precedence < parent_precedence
        if has_brackets:
            code += '('

        self.index -= 1
        if op.type == TokenEnum.UNARY_OP:
            code += op.operator
            if self.current_op.type in (TokenEnum.UNARY_OP, TokenEnum.BINARY_OP):
                code += self.decompile_operation(op.precedence)
            else:
                code += self.decompile_parameter()
        else:
            if self.current_op.type in (TokenEnum.UNARY_OP, TokenEnum.BINARY_OP):
                code += self.decompile_operation(op.precedence)
            else:
                code += self.decompile_parameter()

            code += f' {op.operator} '

            parameter_type = None
            if op == TokenEnum.TOK_ASSIGN_FLOAT:
                parameter_type = Type.FLOAT
            elif op == TokenEnum.TOK_ASSIGN_FUNC:
                parameter_type = Type.FUNC
            elif op == TokenEnum.TOK_ASSIGN_INSTANCE:
                parameter_type = Type.INSTANCE

            self.index -= 1
            if op.type == TokenEnum.BINARY_OP and self.current_op.type in (TokenEnum.UNARY_OP, TokenEnum.BINARY_OP):
                code += self.decompile_operation(op.precedence)
            else:
                code += self.decompile_parameter(symbol_type=parameter_type)

        if has_brackets:
            code += ')'

        return code

    def decompile_condition(self):
        token = self.tokens[self.index]
        tpos = token.int_param
        sub = 1
        add_semicolon = True
        t = 1

        if token.op == TokenEnum.TOK_JUMP:
            self.if_mark.append(token.stack_pointer)
            if tpos in self.end_if:
                return

            self.end_if.add(tpos)
            line = None
            if len(self.lines):
                line = self.lines[0]

            if line and line.text.startswith('if') and self.if_on:
                line.text = 'else ' + line.text
                return
            else:
                self.add_line('else {')

        else:
            if self.if_mark and self.if_mark[-1] == (tpos - 5):
                add_semicolon = False
                tpos = self.if_mark.pop()
                self.if_on = False

            else:
                self.if_on = True

            self.index -= 1
            self.add_line('if(' + self.decompile_parameter() + ') {')

        if len(self.lines) <= 1:
            sub = 0

        else:
            for t, line in enumerate(self.lines[1:], start=2):
                if line.stack_pointer >= tpos:
                    break
                line.text = '    ' + line.text
                if line is self.lines[-1]:
                    sub = 0

        self.lines.insert(
            t-sub,
            Line(
                stack_pointer=-0xbeef,
                text='}' + (';' if add_semicolon else '')
            )
        )

        if not add_semicolon:
            line = self.lines[t]
            if line.text.startswith('if'):
                line.text = 'else ' + line.text
                self.if_on = False

    def add_line(self, line):
        self.lines.insert(
            0,
            Line(
                stack_pointer=self.current_token.stack_pointer,
                text=line
            )
        )

    @property
    def current_op(self):
        return self.tokens[self.index].op


def get_code(symbol, assembly=False):
    if assembly:
        return get_assembly_code(symbol)

    elif symbol.type == Type.CLASS:
        return get_class_code(symbol)

    elif symbol.type == Type.FUNC and symbol.has_flag(Flag.CONST):
        return get_func_code(symbol)

    elif symbol.type in (Type.FLOAT, Type.INT, Type.STRING, Type.FUNC):
        if symbol.has_flag(Flag.CLASSVAR) or not symbol.has_flag(Flag.CONST):   # FIXME: is it even possible to have both flags at once?
            return get_var_code(symbol)
        else:
            return get_const_code(symbol)

    elif symbol.type == Type.INSTANCE:
        return get_instance_code(symbol)

    elif symbol.type == Type.PROTOTYPE:
        return get_prototype_code(symbol)


def get_assembly_code(symbol):
    if symbol.type == Type.FUNC and not symbol.has_flag(Flag.CONST) or symbol.has_flag(Flag.EXTERNAL):
        return

    if symbol.type in (Type.FUNC, Type.INSTANCE, Type.PROTOTYPE):
        return get_tokens(symbol)


def get_tokens(symbol):
    code = ''
    tokens = Token.get_tokens_from_stack(symbol.address_start, symbol.address_end)
    for token in tokens:
        code += f'{token.stack_pointer:06x}    '.upper()
        code += f'{token.op._name:<17s}   '

        if token.int_param:
            if token.op.type == TokenEnum.JUMP:
                code += f'{token.int_param:06x}'.upper()
            else:
                code += f'{token.int_param}'

        elif token.symbol:
            code += f'{token.symbol.name}'
            if token.op == TokenEnum.TOK_PUSH_ARRAY_VAR:
                code += f'[{token.offset}]'

            if token.symbol.has_flag(Flag.CONST) and token.op.type != TokenEnum.CALL:
                code += ', '

                if token.symbol.type == Type.STRING:
                    code += '"'

                if token.op == TokenEnum.TOK_PUSH_ARRAY_VAR:
                    code += str(token.symbol.content[token.offset])
                elif token.symbol.address_start is not None:
                    code += f'{token.symbol.address_start:06x}'.upper()
                else:
                    code += str(token.symbol.content[0])

                if token.symbol.type == Type.STRING:
                    code += '"'

        code += '\n'

    return code


def get_class_code(symbol):
    code = f'class {symbol.name} {{\n'
    for child_symbol in symbol.children:
        code += f'    {get_code(child_symbol)}\n'
    code += '};'
    return code


def get_func_code(symbol):
    code = f'func {TYPE_2_STR[symbol.return_type]} {symbol.name}('

    if symbol.count:  # FIXME is this even neccessary?
        parameters = []
        for parameter in symbol.children:
            parameters.append(get_code(symbol=parameter)[:-1])  # removing ;
        code += ', '.join(parameters)

    if symbol.has_flag(Flag.EXTERNAL):
        code += ');\n'
        return "// " + code

    code += ") {\n"

    code += get_body_code(symbol, does_return=bool(symbol.return_type))

    code += '};'
    return code


def get_var_code(symbol):
    optional_square_brackets = ''
    if symbol.count > 1:
        optional_square_brackets = f'[{symbol.count}]'

    return f'var {symbol.type_int_as_str} {symbol.local_name}{optional_square_brackets};'


def get_const_code(symbol):
    code = f'const {symbol.type_int_as_str} {symbol.local_name}'
    if symbol.count == 1:
        element = symbol.content[0]
        code += f' = {data_repr(element)};'

    elif symbol.count > 1:
        code += f'[{symbol.count}] = {{\n'

        for i, element in enumerate(symbol.content, start=1):
            code += f'    {data_repr(element)}'

            if i < len(symbol.content):
                code += ','
            code += '\n'
        code += '};'
    return code


def get_instance_code(symbol):
    if not symbol.has_flag(Flag.CONST):  # TODO: why not move this somewhere else, outside this function?
        return get_var_code(symbol)

    code = f'instance {symbol.name}({symbol.type_int_as_str}) {{\n'
    code += get_body_code(symbol)
    code += '};'
    return code


def get_prototype_code(symbol):
    code = f'prototype {symbol.name}({symbol.type_int_as_str}) {{\n'
    code += get_body_code(symbol)
    code += '};'
    return code


def get_body_code(symbol, does_return=False):  # addBytecode
    code = ''
    start = symbol.address_start + (symbol.count * 6)  # TODO: whats this symbol.count * 6 for? probably because calling parameter takes 6 bytes
    end = symbol.address_end - 1

    if symbol.is_instance and symbol.has_prototype:
        start += 5  # call

    for local_var in symbol.local_vars:
        code += f'    {get_code(local_var)}\n'

    func = DecompilerBytecode(start, end, return_param=does_return)
    for line in func.lines:
        code += f'    {line.text}\n'

    return code


