import struct as _struct
from construct3.lib import singleton
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO


class PackerError(Exception):
    pass
class FieldError(PackerError):
    pass
class ArrayError(PackerError):
    pass
class SwitchError(PackerError):
    pass
class ValidationError(PackerError):
    pass


class Packer(object):
    __slots__ = ()
    def pack(self, obj):
        stream = BytesIO()
        self._pack(obj, stream, {})
        return stream.getvalue()
    def _pack(self, obj, stream, ctx):
        raise NotImplementedError()

    def unpack(self, buf):
        return self._unpack(BytesIO(buf))
    def _unpack(self, stream, ctx):
        raise NotImplementedError()

@singleton
class Noop(Packer):
    __slots__ = ()
    def _pack(self, stream, obj, ctx):
        pass
    def _unpack(self, stream, ctx):
        return None

class CtxConst(object):
    __slots__ = ["value"]
    def __init__(self, value):
        self.value = value
    def __call__(self, ctx):
        return self.value
    def __repr__(self):
        return repr(self.value)

def contextify(value):
    if hasattr(value, "__call__"):
        return value
    else:
        return CtxConst(value)

class Adapter(Packer):
    __slots__ = ["underlying", "_decode", "_encode"]
    def __init__(self, underlying, decode = None, encode = None):
        self.underlying = underlying
        self._decode = decode
        self._encode = encode

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.underlying)

    def _pack(self, stream, obj, ctx):
        obj2 = self.encode(obj, ctx)
        self.underlying._pack(stream, obj2, ctx)
    def _unpack(self, stream, ctx):
        obj = self.underlying._unpack(stream, ctx)
        return self.decode(obj, ctx)
    
    def encode(self, obj, ctx):
        if self._encode:
            return self._encode(obj, ctx)
        else:
            return obj
    def decode(self, obj, ctx):
        if self._decode:
            return self._decode(obj, ctx)
        else:
            return obj

class Field(Packer):
    __slots__ = ["length"]
    def __init__(self, length):
        self.length = contextify(length)
    def __repr__(self):
        return "Field(%r)" % (self.length,)
    def _pack(self, stream, obj, ctx):
        length = self.length(ctx)
        if len(obj) != length:
            raise FieldError("expected buffer of length %d, got %d" % (length, len(obj)))
        stream.write(obj)
    def _unpack(self, stream, ctx):
        length = self.length(ctx)
        data = stream.read(length)
        if len(data) != length:
            raise FieldError("expected buffer of length %d, got %d" % (length, len(data)))
        return data

class FormattedField(Adapter):
    __slots__ = ["fmt"]
    FORMAT = None
    def __init__(self):
        self.fmt = _struct.Struct(self.FORMAT)
        Adapter.__init__(self, Field(self.fmt.size))
    def encode(self, obj, ctx):
        return self.fmt.pack(obj)
    def decode(self, obj, ctx):
        return self.fmt.unpack(obj)[0]

@singleton
class u_int8(FormattedField):
    """Unsigned 8-bit integer"""
    FORMAT = "B"

@singleton
class s_int8(FormattedField):
    """Signed 8-bit integer"""
    FORMAT = "b"

@singleton
class ub_int16(FormattedField):
    """Unsigned big-endian 16-bit integer"""
    FORMAT = "!H"

@singleton
class sb_int16(FormattedField):
    """Signed big-endian 16-bit integer"""
    FORMAT = "!h"

@singleton
class ul_int16(FormattedField):
    """Unsigned little-endian 16-bit integer"""
    FORMAT = "<H"

@singleton
class sl_int16(FormattedField):
    """Signed little-endian 16-bit integer"""
    FORMAT = "<h"

@singleton
class ub_int32(FormattedField):
    """Unsigned big-endian 32-bit integer"""
    FORMAT = "!L"

@singleton
class sb_int32(FormattedField):
    """Signed big-endian 32-bit integer"""
    FORMAT = "!l"

@singleton
class ul_int32(FormattedField):
    """Unsigned little-endian 32-bit integer"""
    FORMAT = "<L"

@singleton
class sl_int32(FormattedField):
    """Signed little-endian 32-bit integer"""
    FORMAT = "<l"

@singleton
class ub_int64(FormattedField):
    """Unsigned big-endian 64-bit integer"""
    FORMAT = "!Q"

@singleton
class sb_int64(FormattedField):
    """Signed big-endian 64-bit integer"""
    FORMAT = "!q"

@singleton
class ul_int64(FormattedField):
    """Unsigned little-endian 64-bit integer"""
    FORMAT = "<Q"

@singleton
class sl_int64(FormattedField):
    """Signed little-endian 64-bit integer"""
    FORMAT = "<q"

@singleton
class b_float32(FormattedField):
    """Big-endian 32-bit floating point number"""
    FORMAT = "!f"

@singleton
class b_float64(FormattedField):
    """Big-endian 64-bit floating point number"""
    FORMAT = "!d"

@singleton
class l_float32(FormattedField):
    """Little-endian 32-bit floating point number"""
    FORMAT = "<f"

@singleton
class l_float64(FormattedField):
    """Little-endian 64-bit floating point number"""
    FORMAT = "<d"










