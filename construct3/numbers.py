import sys
import struct as _struct
from construct3.lib import singleton
from construct3.packers import Adapter, Raw, Sequence
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
class uint8(Formatted):
    """Unsigned 8-bit integer"""
    FORMAT = "B"

@singleton
class sint8(Formatted):
    """Signed 8-bit integer"""
    FORMAT = "b"

@singleton
class uint16b(Formatted):
    """Unsigned big-endian 16-bit integer"""
    FORMAT = "!H"

@singleton
class sint16b(Formatted):
    """Signed big-endian 16-bit integer"""
    FORMAT = "!h"

@singleton
class uint16l(Formatted):
    """Unsigned little-endian 16-bit integer"""
    FORMAT = "<H"

@singleton
class sint16l(Formatted):
    """Signed little-endian 16-bit integer"""
    FORMAT = "<h"

@singleton
class uint32b(Formatted):
    """Unsigned big-endian 32-bit integer"""
    FORMAT = "!L"

@singleton
class sint32b(Formatted):
    """Signed big-endian 32-bit integer"""
    FORMAT = "!l"

@singleton
class uint32l(Formatted):
    """Unsigned little-endian 32-bit integer"""
    FORMAT = "<L"

@singleton
class sint32l(Formatted):
    """Signed little-endian 32-bit integer"""
    FORMAT = "<l"

@singleton
class uint64b(Formatted):
    """Unsigned big-endian 64-bit integer"""
    FORMAT = "!Q"

@singleton
class sint64b(Formatted):
    """Signed big-endian 64-bit integer"""
    FORMAT = "!q"

@singleton
class uint64l(Formatted):
    """Unsigned little-endian 64-bit integer"""
    FORMAT = "<Q"

@singleton
class sint64l(Formatted):
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

uint24b = Adapter(Sequence(uint8, uint16b), 
    decode = lambda obj, _: (obj[0] << 16) | obj[1],
    encode = lambda obj, _: (obj >> 16, obj & 0xffff))
sint24b = TwosComplement(uint24b, 24)
uint24l = Adapter(uint24b, 
    decode = lambda obj, _: ((obj >> 16) & 0xff) | (obj & 0xff00) | ((obj & 0xff) << 16),
    encode = lambda obj, _: ((obj >> 16) & 0xff) | (obj & 0xff00) | ((obj & 0xff) << 16))
sint24l = TwosComplement(uint24l, 24)

class MaskedInteger(Adapter):
    r"""
    >>> m = MaskedInteger(uint16l,
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

#=======================================================================================================================
# aliases
#=======================================================================================================================
word8 = uint8
int8 = sint8
if sys.byteorder == "little":
    int16 = sint16l
    int24 = sint24l
    int32 = sint32l
    int64 = sint64l
    float32 = float32l
    float64 = float64l
    word16 = uint16l
    word24 = uint24l
    word32 = uint32l
    word64 = uint64l
else:
    int16 = sint16b
    int24 = sint24b
    int32 = sint32b
    int64 = sint64b
    float32 = float32b
    float64 = float64b
    word16 = uint16b
    word24 = uint24b
    word32 = uint32b
    word64 = uint64b





