import struct as _struct
import struct as _struct

def test_unpack(stream):
    var0 = {}
    var1, = _struct.unpack('B', stream.read(1))
    var0['len'] = var1
    var2, = _struct.unpack('B', stream.read(1))
    var0['gth'] = var2
    var3 = stream.read((var1 + var2))
    var0['data'] = var3
    return var0
