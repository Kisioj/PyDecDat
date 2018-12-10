import struct

from constants import BYTE_FORMAT, INT_FORMAT
from dat_symbol import DatSymbol
from filewrapper import FileWrapper


class Dat:
    def __init__(self, file_path):
        DatSymbol.next_id = 0

        with open(file_path, 'rb') as file:
            file = FileWrapper(file)

            # read head
            version = file.read_byte()

            # read sorted table
            symbols_len = file.read_int()

            print(symbols_len)
            print(file.offset)
            sort_table = {
                file.read_int(): index
                for index, _ in enumerate(range(symbols_len))
            }
            print(file.offset)

            # read symbols
            symbols = []
            for i in range(symbols_len):
                symbol = DatSymbol(dat=self, file=file)
                symbol.sort_table_id = sort_table[symbol.id]
                if symbol.parent_index != -1:
                    symbol.parent = symbols[symbol.parent_index]
                symbols.append(symbol)

            regular_symbols = [
                symbol
                for symbol in symbols
                if symbol.is_regular
            ]
            self.symbols = symbols

            # read stack
            stack_len = file.read_int()
            self.stack = file.read_bytes(stack_len)

            addressable_symbols = [  # TODO: maybe change name to functions?
                symbol
                for symbol in symbols
                if symbol.address_start is not None
            ]
            addressable_symbols.sort(key=lambda symbol: symbol.address_start)

            addresses = [
                symbol.address_start
                for symbol in addressable_symbols
            ]
            addresses.append(stack_len)
            addresses.sort()

            for i, symbol in enumerate(addressable_symbols):
                symbol.address_end = addresses[i + 1]

            self.address_start_2_symbol = {
                symbol.address_start: symbol
                for symbol in addressable_symbols
            }

            print('DAT file loaded')
            print('version', version)
            print('list_len', symbols_len)
            print('len(sort_table)', len(sort_table))
            print('len(regular_symbols)', len(regular_symbols))
            print('stack_len', stack_len)

    def get_stack_byte(self, offset):
        return self.get_stack_data(offset, byte_count=1, data_type=BYTE_FORMAT)

    def get_stack_int(self, offset):
        return self.get_stack_data(offset, byte_count=4, data_type=INT_FORMAT)

    def get_stack_data(self, offset, byte_count, data_type):
        data = self.stack[offset:offset+byte_count]
        # print(data, offset, byte_count, data_type, len(self.stack))
        return struct.unpack(data_type, data)[0]

    def get_symbol_by_address_start(self, address_start):
        return self.address_start_2_symbol[address_start]
