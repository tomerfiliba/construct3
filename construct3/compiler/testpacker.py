import struct as _struct
import struct as _struct
import struct as _struct
import struct as _struct

def test_unpack(stream):
    var0 = []
    var1, = _struct.unpack('B', stream.read(1))
    var0.append(var1)
    var2, = _struct.unpack('B', stream.read(1))
    var0.append(var2)
    var3 = []
    var4, = _struct.unpack('B', stream.read(1))
    var3.append(var4)
    var5, = _struct.unpack('B', stream.read(1))
    var3.append(var5)
    var6 = stream.read((((var4 + var5) + var1) + var2))
    var3.append(var6)
    var0.append(var3)
    return var0
