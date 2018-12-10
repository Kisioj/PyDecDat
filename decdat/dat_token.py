from tokenenum import TokenEnum

SYMBOL = 1
INT = 2


class Token:
    current_pos = None
    dat = None

    def __init__(self, token_enum, symbol=None, offset=None, int_param=None):  # FIXME
        self.stack_pointer = Token.current_pos
        self.op = token_enum
        self.symbol = symbol
        self.offset = offset  # FIXME is it array index
        self.int_param = int_param

    @staticmethod
    def get_symbol_param_token(op, symbol_index=None):
        symbol = Token.dat.symbols[symbol_index] if symbol_index else None
        return Token(op, symbol=symbol)

    @staticmethod
    def get_int_param_token(op, int_param):
        return Token(op, int_param=int_param)

    @staticmethod
    def get_call_token(symbol_address):
        symbol = Token.dat.get_symbol_by_address_start(address_start=symbol_address)
        return Token(TokenEnum.TOK_CALL, symbol=symbol)

    @staticmethod
    def get_array_token(symbol_index, offset):
        symbol = Token.dat.symbols[symbol_index] if symbol_index else None
        return Token(TokenEnum.TOK_PUSH_ARRAY_VAR, symbol=symbol, offset=offset)

    @staticmethod
    def get_tokens_from_stack(address_start, address_end):
        # FIXME this function is executed for instance vars and parameters, and it shouldn't
        tokens = []

        dat = Token.dat
        offset = address_start
        if address_start is None:
            return tokens

        try:
            offset < address_end
        except:
            pass
        while offset < address_end:
            Token.current_pos = offset
            op = TokenEnum(dat.get_stack_byte(offset))  # FIXME: should be token, and later, token.has_parameter
            if op.has_parameter:
                parameter = dat.get_stack_int(offset+1)

                if op == TokenEnum.TOK_CALL:
                    token = Token.get_call_token(symbol_address=parameter)

                elif op == TokenEnum.TOK_PUSH_ARRAY_VAR:
                    token = Token.get_array_token(symbol_index=parameter, offset=dat.get_stack_byte(offset+5))
                    offset += 1

                elif op in (TokenEnum.TOK_CALL_EXTERNAL, TokenEnum.TOK_PUSH_VAR, TokenEnum.TOK_PUSH_INSTANCE, TokenEnum.TOK_SET_INSTANCE):
                    token = Token.get_symbol_param_token(op, symbol_index=parameter)
                else:

                    token = Token.get_int_param_token(op, int_param=parameter)

                offset += 4

            else:
                token = Token(op)

            tokens.append(token)
            offset += 1

        return tokens

