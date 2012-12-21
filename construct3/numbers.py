import sys
import struct as _struct
from construct3.lib import singleton
from construct3.packers import Adapter, Raw
from construct3.lib.binutil import num_to_bits, swap_bytes, bits_to_num


class Formatted(Adapter):
    __slots__ = ["fmt"]
    FORMAT = None
    def __init__(self):
        self.fmt = _struct.Struct(self.FORMAT)
        Adapter.__init__(self, Raw(self.fmt.size))
    def __repr__(self):
        return self.__class__.__name__
    def encode(self, obj, ctx):
        return self.fmt.pack(obj)
    def decode(self, obj, ctx):
        return self.fmt.unpack(obj)[0]

@singleton
class int8u(Formatted):
    """Unsigned 8-bit integer"""
    FORMAT = "B"

@singleton
class int8s(Formatted):
    """Signed 8-bit integer"""
    FORMAT = "b"

@singleton
class int16ub(Formatted):
    """Unsigned big-endian 16-bit integer"""
    FORMAT = "!H"

@singleton
class int16sb(Formatted):
    """Signed big-endian 16-bit integer"""
    FORMAT = "!h"

@singleton
class int16ul(Formatted):
    """Unsigned little-endian 16-bit integer"""
    FORMAT = "<H"

@singleton
class int16sl(Formatted):
    """Signed little-endian 16-bit integer"""
    FORMAT = "<h"

@singleton
class int32ub(Formatted):
    """Unsigned big-endian 32-bit integer"""
    FORMAT = "!L"

@singleton
class int32sb(Formatted):
    """Signed big-endian 32-bit integer"""
    FORMAT = "!l"

@singleton
class int32ul(Formatted):
    """Unsigned little-endian 32-bit integer"""
    FORMAT = "<L"

@singleton
class int32sl(Formatted):
    """Signed little-endian 32-bit integer"""
    FORMAT = "<l"

@singleton
class int64ub(Formatted):
    """Unsigned big-endian 64-bit integer"""
    FORMAT = "!Q"

@singleton
class int64sb(Formatted):
    """Signed big-endian 64-bit integer"""
    FORMAT = "!q"

@singleton
class int64ul(Formatted):
    """Unsigned little-endian 64-bit integer"""
    FORMAT = "<Q"

@singleton
class int64sl(Formatted):
    """Signed little-endian 64-bit integer"""
    FORMAT = "<q"

@singleton
class float32b(Formatted):
    """Big-endian 32-bit floating point number"""
    FORMAT = "!f"

@singleton
class float64b(Formatted):
    """Big-endian 64-bit floating point number"""
    FORMAT = "!d"

@singleton
class float32l(Formatted):
    """Little-endian 32-bit floating point number"""
    FORMAT = "<f"

@singleton
class float64l(Formatted):
    """Little-endian 64-bit floating point number"""
    FORMAT = "<d"

byte = int8u
int8 = int8s
if sys.byteorder == "little":
    int16 = int16sl
    int32 = int32sl
    int64 = int64sl
    float32 = float32l
    float64 = float64l
else:
    int16 = int16sb
    int32 = int32sb
    int64 = int64sb
    float32 = float32b
    float64 = float64b

class Bits(Adapter):
    __slots__ = ["width", "swapped", "signed", "bytesize"]
    def __init__(self, width, swapped = False, signed = False, bytesize = 8):
        Adapter.__init__(self, Raw(width))
        self.width = width
        self.swapped = swapped
        self.signed = signed
        self.bytesize = bytesize
    def encode(self, obj, context):
        if obj < 0 and not self.signed:
            raise ValueError("%r is negative, but field is not signed" % (obj,))
        obj2 = num_to_bits(obj, width = self.width)
        if self.swapped:
            obj2 = swap_bytes(obj2, bytesize = self.bytesize)
        return obj2
    def decode(self, obj, context):
        if self.swapped:
            obj = swap_bytes(obj, bytesize = self.bytesize)
        return bits_to_num(obj, signed = self.signed)

bit = Bits(1)
nibble = Bits(4)
octet = Bits(8)













