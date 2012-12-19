from construct3.lib import singleton
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO


class PackerError(Exception):
    pass
class RawError(PackerError):
    pass
class ArrayError(PackerError):
    pass
class SwitchError(PackerError):
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
        return self._unpack(BytesIO(buf), {})
    def _unpack(self, stream, ctx):
        raise NotImplementedError()

    def sizeof(self, ctx = None):
        return self._sizeof(ctx if ctx else {})
    def _sizeof(self, ctx):
        raise NotImplementedError()


@singleton
class Noop(Packer):
    __slots__ = ()
    def _pack(self, obj, stream, ctx):
        pass
    def _unpack(self, stream, ctx):
        return None
    def _sizeof(self, ctx = None):
        return 0

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

    def _pack(self, obj, stream, ctx):
        obj2 = self.encode(obj, ctx)
        self.underlying._pack(obj2, stream, ctx)
    def _unpack(self, stream, ctx):
        obj = self.underlying._unpack(stream, ctx)
        return self.decode(obj, ctx)
    def _sizeof(self, ctx):
        return self.underlying._sizeof(ctx)
    
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


class Raw(Packer):
    __slots__ = ["length"]
    def __init__(self, length):
        self.length = contextify(length)
    def __repr__(self):
        return "Raw(%r)" % (self.length,)
    def _pack(self, obj, stream, ctx):
        length = self.length(ctx)
        if len(obj) != length:
            raise RawError("expected buffer of length %d, got %d" % (length, len(obj)))
        stream.write(obj)
    def _unpack(self, stream, ctx):
        length = self.length(ctx)
        data = stream.read(length)
        if len(data) != length:
            raise RawError("expected buffer of length %d, got %d" % (length, len(data)))
        return data
    def _sizeof(self, ctx):
        return self.length(ctx)


def Member(*args, **kwargs):
    if (args and kwargs) or (not args and not kwargs):
        raise TypeError("This function takes either two positional arguments or a single keyword attribute", args, kwargs)
    if args:
        if len(args) != 2:
            raise TypeError("Expected exactly two positional arguments", args)
        else:
            return args
    else:
        if len(kwargs) != 1:
            raise TypeError("Expected exactly one keyword argument", kwargs)
        return kwargs.popitem()

class Struct(Packer):
    __slots__ = ["members", "container_factory"]
    
    def __init__(self, *members, **kwargs):
        self.members = members
        self.container_factory = kwargs.pop("container_factory", dict)
        if kwargs:
            raise TypeError("invalid keyword argument(s): %s" % (", ".join(kwargs.keys()),))
        names = set()
        for mem in members:
            if not hasattr(mem, "__len__") or len(mem) != 2 or not isinstance(mem[1], Packer):
                raise TypeError("Struct members must be 2-tuples of (name, Packer): %r" % (mem,))
            if mem[0] in names:
                raise TypeError("Member %r already exists in this struct" % (mem[0],))
            if mem[0]:
                names.add(mem[0])

    def __repr__(self):
        return "Struct(%s)" % (", ".join(repr(m) for m in self.members),)
    
    def _unpack(self, stream, ctx):
        obj = self.container_factory()
        ctx2 = {"_" : ctx}
        for mem_name, mem_packer in self.members:
            obj2 = mem_packer._unpack(stream, ctx2)
            ctx2[mem_name] = obj[mem_name] = obj2
        return obj
    
    def _pack(self, obj, stream, ctx):
        ctx2 = {"_" : ctx}
        for mem_name, mem_packer in self.members:
            obj2 = ctx2[mem_name] = obj[mem_name]
            mem_packer._pack(obj2, stream, ctx2)
    
    def _sizeof(self, ctx):
        ctx2 = {"_" : ctx}
        return sum(mem_packer.sizeof(ctx2) for _, mem_packer in self.members)


class Sequence(Packer):
    __slots__ = ["members", "container_factory"]
    
    def __init__(self, *members, **kwargs):
        self.members = members
        self.container_factory = kwargs.pop("container_factory", list)
        if kwargs:
            raise TypeError("invalid keyword argument(s): %s" % (", ".join(kwargs.keys()),))
        for mem in members:
            if not isinstance(mem, Packer):
                raise TypeError("sequence members must be Packers: %r" % (mem,))

    def __repr__(self):
        return "Sequence(%s)" % (", ".join(repr(m) for m in self.members),)
    
    def _unpack(self, stream, ctx):
        obj = self.container_factory()
        ctx2 = {"_" : ctx}
        for i, packer in enumerate(self.members):
            obj2 = packer._unpack(stream, ctx2)
            ctx2[i] = obj[i] = obj2
        return obj
    
    def _pack(self, obj, stream, ctx):
        ctx2 = {"_" : ctx}
        for i, Packer in enumerate(self.members):
            obj2 = ctx2[i] = obj[i]
            Packer._pack(obj2, stream, ctx2)
    
    def _sizeof(self, ctx):
        ctx2 = {"_" : ctx}
        return sum(mem_packer._sizeof(ctx2) for _, mem_packer in self.members)


class Array(Packer):
    __slots__ = ["count", "itempkr"]
    def __init__(self, count, itempkr):
        self.count = contextify(count)
        self.itempkr = itempkr
    
    def __repr__(self):
        return "Array(%r, %r)" % (self.count, self.itempkr)
    
    def _pack(self, obj, stream, ctx):
        count = self.count(ctx)
        if len(obj) != count:
            raise ArrayError("expected %d items, found %d", count, len(obj))
        ctx2 = {"_" : ctx}
        for i, item in enumerate(obj):
            ctx2[i] = item
            self.itempkr._pack(item, stream, ctx2)
    
    def _unpack(self, stream, ctx):
        count = self.count(ctx)
        ctx2 = {"_" : ctx}
        obj = [None] * count
        for i in range(count):
            obj2 = self.itempkr._unpack(stream, ctx2)
            obj[i] = ctx2[i] = obj2
        return obj

    def _sizeof(self, ctx):
        return self.count(ctx) * self.itempkr._sizeof({"_" : ctx})


class While(Packer):
    __slots__ = ["cond", "itempkr"]
    def __init__(self, cond, itempkr):
        self.cond = contextify(cond)
        self.itempkr = itempkr
    
    def __repr__(self):
        return "While(%r, %r)" % (self.cond, self.itempkr)
    
    def _pack(self, obj, stream, ctx):
        ctx2 = {"_" : ctx}
        for i, item in enumerate(obj):
            ctx2[i] = item
            self.itempkr._pack(item, stream, ctx2)
            if not self.cond(ctx2):
                break
    
    def _unpack(self, stream, ctx):
        ctx2 = {"_" : ctx}
        obj = []
        i = 0
        while True:
            obj2 = ctx2[i] = self.itempkr._unpack(stream, ctx2)
            if not self.cond(ctx2):
                break
            obj.append(obj2)
            i += 1
        return obj
    
    def _sizeof(self):
        raise NotImplementedError("Cannot compute sizeof for 'While'")


class Switch(Packer):
    __slots__ = ["expr", "cases", "default"]
    def __init__(self, expr, cases, default = None):
        self.expr = contextify(expr)
        self.cases = cases
        self.default = default
    
    def _choose_packer(self, ctx):
        val = self.expr(ctx)
        if val in self.cases:
            return self.cases[val]
        elif self.default:
            return self.default
        else:
            raise SwitchError("cannot find a handler for value", val)
    
    def _pack(self, obj, stream, ctx):
        pkr = self._choose_packer(ctx)
        pkr._pack(obj, stream, ctx)
    
    def _unpack(self, stream, ctx):
        pkr = self._choose_packer(ctx)
        return pkr._unpack(stream, ctx)

    def _sizeof(self, ctx):
        return self._choose_packer(ctx)._sizeof(ctx)







