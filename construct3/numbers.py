import sys
import struct as _struct
from construct3.lib import singleton
from construct3.packers import Adapter, Raw
from construct3.lib.binutil import num_to_bits, swap_bytes, bits_to_num
from construct3.lib.containers import Container


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

#=======================================================================================================================
# aliases
#=======================================================================================================================
byte = word8 = int8u
int8 = int8s
if sys.byteorder == "little":
    int16 = int16sl
    int32 = int32sl
    int64 = int64sl
    float32 = float32l
    float64 = float64l
    word16 = int16ul
    word32 = int32ul
    word64 = int64ul
else:
    int16 = int16sb
    int32 = int32sb
    int64 = int64sb
    float32 = float32b
    float64 = float64b
    word16 = int16ub
    word32 = int32ub
    word64 = int64ub


#=======================================================================================================================
# bitwise stuff
#=======================================================================================================================
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

#=======================================================================================================================
# weird stuff (24-bit integers, etc)
#=======================================================================================================================
class TwosComplement(Adapter):
    __slots__ = ["maxval", "midval"]
    def __init__(self, underlying, bits):
        Adapter.__init__(self, underlying)
        self.maxval = 1 << bits
        self.midval = self.maxval >> 1
    def encode(self, obj, ctx):
        return obj + self.maxval if obj < 0 else obj
    def decode(self, obj, ctx):
        return obj - self.maxval if obj & self.midval else obj

int24ub = Adapter(byte >> int16ub, 
    decode = lambda obj, _: (obj[0] << 16) | obj[1],
    encode = lambda obj, _: (obj >> 16, obj & 0xffff))
int24sb = TwosComplement(int24ub, 24)
int24ul = Adapter(int24ub, 
    decode = lambda obj, _: ((obj >> 16) & 0xff) | (obj & 0xff00) | ((obj & 0xff) << 16),
    encode = lambda obj, _: ((obj >> 16) & 0xff) | (obj & 0xff00) | ((obj & 0xff) << 16))
int24sl = TwosComplement(int24ul, 24)

class MaskedInteger(Adapter):
    r"""
    >>> m = MaskedInteger(int16ul,
    ...     bottom4 = (0, 4), 
    ...     upper12 = (4, 12),
    ... )
    >>> print m.unpack("\x17\x02")
    Container:
      bottom4 = 7
      upper12 = 33
    >>> print repr(m.pack(Container(upper12 = 33, bottom4 = 7)))
    '\x17\x02'
    """
    __slots__ = ["fields"]
    def __init__(self, underlying, **fields):
        Adapter.__init__(self, underlying)
        self.fields = [(k, offset, (1 << size) - 1) for k, (offset, size) in fields.items()]
    def encode(self, obj, ctx):
        num = 0
        for name, offset, mask in self.fields:
            num |= (obj[name] & mask) << offset
        return num
    def decode(self, obj, ctx):
        return Container((name, (obj >> offset) & mask) for name, offset, mask in self.fields)



















