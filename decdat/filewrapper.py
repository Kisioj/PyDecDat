import struct

from constants import Type, INT_FORMAT, BYTE_FORMAT, FLOAT_FORMAT, BYTES_FORMAT, CHAR_FORMAT


class FileWrapper:
    def __init__(self, file):
        self.file = file
        self.offset = 0
        self.content = file.read()

    def __repr__(self):
        return '<file %02x - %d>' % (self.offset, self.offset)

    def read_byte(self):
        return self.read(byte_count=1, data_type=BYTE_FORMAT)

    def read_int(self):
        return self.read(byte_count=4, data_type=INT_FORMAT)

    def read_float(self):
        return round(self.read(byte_count=4, data_type=FLOAT_FORMAT), 4)

    def read_bytes(self, byte_count):
        return self.read(byte_count=byte_count, data_type=BYTES_FORMAT.format(byte_count))

    def read_string(self):
        result = b''
        while True:
            char = self.read(byte_count=1, data_type=CHAR_FORMAT)
            if char == b'\n':
                break
            result += char
        return result.decode(encoding='windows-1250')

    def read_type(self, data_type):
        method = FileWrapper.TYPE_2_READ_FUNC[data_type]
        return method(self)

    def read(self, byte_count, data_type):
        data = self.content[self.offset:self.offset+byte_count]
        self.offset += byte_count
        return struct.unpack(data_type, data)[0]  # check if this approach is faster than previous one

    TYPE_2_READ_FUNC = {
        Type.INT: read_int,
        Type.FLOAT: read_float,
        Type.STRING: read_string,
    }
