from constants import Flag, Type, TYPE_2_STR, FLAGS, FLAG_2_STR, EXTERNALS_TO_FIX


class DatSymbol:
    next_id = 0

    address_start = None
    address_end = None
    class_offset = None
    content = None
    name = None

    def __init__(self, dat, file):
        self.dat = dat
        self.id = DatSymbol.next_id
        self.sort_table_id = None  # id which was in sort_table
        self.parent = None
        self.return_type = None
        DatSymbol.next_id += 1

        self.has_name = file.read_int()
        if self.has_name:
            self.name = file.read_string().lower()

        self.offset = file.read_int()  # offset (CLASSVAR), size (CLASS), return_type (FUNC)
        properties = file.read_int()  # bitfield

        self.count = properties & 0x00000FFF  # uses 12 bits

        self.type = (properties >> 12) & 0x0000000F  # uses 4 bits
        self.flags = (properties >> 16) & 0x0000003F  # uses 3 bits
        self.space = (properties >> 17) & 0x00000001  # uses 1 bit

        self.file_index = file.read_int() & 0x0007FFFF  # uses 19 bits
        self.line_start = file.read_int() & 0x0007FFFF  # uses 19 bits
        self.line_count = file.read_int() & 0x0007FFFF  # uses 19 bits
        self.char_start = file.read_int() & 0x0007FFFF  # uses 24 bits
        self.char_count = file.read_int() & 0x0007FFFF  # uses 24 bits

        if self.type in (Type.FLOAT, Type.INT, Type.STRING) and self.has_flag(Flag.CONST) and not self.has_flag(Flag.CLASSVAR):
            self.name = self.name.upper()

        if self.type == Type.FUNC:
            self.return_type = self.offset

        self.local_name = self.name
        self.is_local = '.' in self.name  # local variable or parameter

        if self.is_local:
            *_, self.local_name = self.name.split('.')

        if self.flags & Flag.CLASSVAR == 0:
            if self.type in (Type.FLOAT, Type.INT, Type.STRING):
                self.content = [
                    file.read_type(data_type=self.type)
                    for _ in range(self.count)
                ]
            elif self.type == Type.CLASS:
                self.class_offset = file.read_int()
            elif self.type in (Type.INSTANCE,) and self.count:  # FIXME because function argument had function type:
                self.content =  file.read_int()
            elif self.type in (Type.FUNC, Type.PROTOTYPE, Type.INSTANCE):
                self.address_start = file.read_int()

        self.parent_index = file.read_int()

    @property
    def children(self):  # TODO: arguments for functions, local vars for class
        return [
            self.dat.symbols[i]
            for i in range(self.id + 1, self.id + 1 + self.count)
        ]

    @property
    def is_regular(self):
        return not self.is_local and not self.name.startswith('˙')

    def has_flag(self, flag):
        return self.flags & flag > 0

    @property
    def flags_as_str(self):
        return ', '.join([
            FLAG_2_STR[flag]
            for flag in FLAGS
            if self.has_flag(flag)
        ])

    @property
    def type_int_as_str(self):
        type_2_str = dict(TYPE_2_STR)
        type_2_str[Type.PROTOTYPE] = self.parent.name if self.parent else '__class'
        type_2_str[Type.INSTANCE] = self.parent.name if self.parent else '__class'
        return type_2_str.get(self.type)

    @property
    def type_as_str(self):
        if self.type in (Type.INSTANCE, Type.PROTOTYPE):
            of = '__class'
            if self.parent_index != -1:
                of = self.dat.symbols[self.parent_index].name
            return f'{TYPE_2_STR[self.type]}({of})'

        elif self.type == Type.FUNC and self.has_flag(Flag.CONST):
            return f'func {TYPE_2_STR[self.offset]}'

        elif self.type == Type.CLASS:
            return TYPE_2_STR[self.type]

        else:
            var_type = 'var'
            if self.has_flag(Flag.CONST):
                var_type = 'const'
            return f'{var_type} {TYPE_2_STR[self.type]}'

    @property
    def is_instance(self):
        return self.type == Type.INSTANCE

    @property
    def has_prototype(self):
        return self.parent.type == Type.PROTOTYPE

    @property
    def address(self):
        if self.address_end is not None:
            return f'{self.address_start}    -    {self.address_end}    (size: {self.address_end-self.address_start})'

    @property
    def local_vars(self):  # this doesn't seem to work good
        var_id = self.id + self.count + 1

        if var_id >= len(self.dat.symbols) - 1:
            return []

        var_symbols = []
        while True:
            if var_id >= len(self.dat.symbols) - 1:
                break
            symbol = self.dat.symbols[var_id]
            if not symbol.name.startswith(self.name + '.'):
                break
            var_symbols.append(symbol)
            var_id += 1

        return var_symbols

