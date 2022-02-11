from tokenenum import TokenEnum

SYMBOL = 1
INT = 2


class Token:
    current_pos = None
    dat = None

    def __init__(self, token_enum, symbol=None, offset=None, int_param=None, dat=None):  # FIXME
        self.stack_pointer = Token.current_pos
        self.op = token_enum
        self.symbol = symbol
        self.offset = offset  # FIXME is it array index
        self.int_param = int_param

    @staticmethod
    def get_symbol_param_token(op, symbol_index=None, dat=None):
        symbol = dat.symbols[symbol_index] if symbol_index else None
        return Token(op, symbol=symbol, dat=dat)

    @staticmethod
    def get_int_param_token(op, int_param, dat=None):
        return Token(op, int_param=int_param, dat=dat)

    @staticmethod
    def get_call_token(symbol_address, dat=None):
        symbol = dat.get_symbol_by_address_start(address_start=symbol_address)
        return Token(TokenEnum.TOK_CALL, symbol=symbol, dat=dat)

    @staticmethod
    def get_array_token(symbol_index, offset, dat=None):
        symbol = dat.symbols[symbol_index] if symbol_index else None
        return Token(TokenEnum.TOK_PUSH_ARRAY_VAR, symbol=symbol, offset=offset, dat=dat)

    @staticmethod
    def get_tokens_from_stack(address_start, address_end, dat=None):
        # FIXME this function is executed for instance vars and parameters, and it shouldn't
        tokens = []

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
                    token = Token.get_call_token(symbol_address=parameter, dat=dat)

                elif op == TokenEnum.TOK_PUSH_ARRAY_VAR:
                    token = Token.get_array_token(symbol_index=parameter, offset=dat.get_stack_byte(offset+5), dat=dat)
                    offset += 1

                elif op in (TokenEnum.TOK_CALL_EXTERNAL, TokenEnum.TOK_PUSH_VAR, TokenEnum.TOK_PUSH_INSTANCE, TokenEnum.TOK_SET_INSTANCE):
                    token = Token.get_symbol_param_token(op, symbol_index=parameter, dat=dat)
                else:

                    token = Token.get_int_param_token(op, int_param=parameter, dat=dat)

                offset += 4

            else:
                token = Token(op, dat=dat)

            tokens.append(token)
            offset += 1

        return tokens

