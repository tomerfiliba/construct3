import struct as _struct
from construct3.packers import Adapter, Noop, Struct, Raw, Member, PackerError
from construct3.lib import this


class ValidationError(PackerError):
    pass


class Const(Adapter):
    __slots__ = ["value"]
    def __init__(self, value):
        Adapter.__init__(self, Noop)
        self.value = value
    def encode(self, obj, ctx):
        return self.val
    def decode(self, obj, ctx):
        return self.val

class OneOf(Adapter):
    __slots__ = ["values"]
    def __init__(self, pkr, values):
        Adapter.__init__(self, pkr)
        self.values = values
    def decode(self, obj, ctx):
        if obj not in self.values:
            raise ValidationError("%r must be in %r" % (obj, self.values))
        return obj
    encode = decode

class NoneOf(Adapter):
    __slots__ = ["values"]
    def __init__(self, pkr, values):
        Adapter.__init__(self, pkr)
        self.values = values
    def decode(self, obj, ctx):
        if obj in self.values:
            raise ValidationError("%r must not be in %r" % (obj, self.values))
        return obj
    encode = decode

class Signature(Adapter):
    __slots__ = ["value"]
    def __init__(self, value):
        Adapter.__init__(self, Raw(len(value)))
        self.value = value
    def decode(self, obj, ctx):
        if obj != self.value:
            raise ValidationError("%r must be %r" % (obj, self.value))
        return obj
    def encode(self, obj, ctx):
        return self.value

class LengthValue(Adapter):
    __slots__ = ()
    def __init__(self, lengthpkr):
        Adapter.__init__(self, Struct(
            Member("length", lengthpkr), 
            Member("data", Raw(this.length)),
            )
        )
    def decode(self, obj, ctx):
        return obj["data"]
    def encode(self, obj, ctx):
        return {"length" : len(obj), "data" : obj}

class StringAdapter(Adapter):
    __slots__ = ["encoding"]
    def __init__(self, underlying, encoding):
        Adapter.__init__(self, underlying)
        self.encoding = encoding
    def decode(self, obj, ctx):
        return obj.decode(self.encoding)
    def encode(self, obj, ctx):
        return obj.encode(self.encoding)

class Formatted(Adapter):
    __slots__ = ["fmt"]
    FORMAT = None
    def __init__(self):
        self.fmt = _struct.Struct(self.FORMAT)
        Adapter.__init__(self, Raw(self.fmt.size))
    def encode(self, obj, ctx):
        return self.fmt.pack(obj)
    def decode(self, obj, ctx):
        return self.fmt.unpack(obj)[0]



