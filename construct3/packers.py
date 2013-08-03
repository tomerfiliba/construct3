from construct3.lib import singleton
import sys
from construct3.lib.binutil import BitStreamReader, BitStreamWriter
from construct3.lib.containers import Container
from construct3.lib.config import Config
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO

import six
from six.moves import xrange


class PackerError(Exception):
    pass
class RawError(PackerError):
    pass
class RangeError(PackerError):
    pass
class SwitchError(PackerError):
    pass


class Packer(object):
    __slots__ = ()
    def pack(self, obj):
        stream = BytesIO()
        self._pack(obj, stream, {}, Config())
        return stream.getvalue()
    def pack_to_stream(self, obj, stream):
        self._pack(obj, stream, {}, Config())
    def _pack(self, obj, stream, ctx, cfg):
        raise NotImplementedError()

    def unpack(self, buf_or_stream):
        if not hasattr(buf_or_stream, "read"):
            buf_or_stream = BytesIO(buf_or_stream)
        return self._unpack(buf_or_stream, {}, Config())
    def _unpack(self, stream, ctx, cfg):
        raise NotImplementedError()

    def sizeof(self, ctx = None, cfg = None):
        return self._sizeof(ctx or {}, cfg or Config())
    def _sizeof(self, ctx, cfg):
        raise NotImplementedError()
    
    #
    # short hands
    #
    def __getitem__(self, count):
        if isinstance(count, slice):
            if count.step:
                raise ValueError("Slice must not contain as step: %r" % (count,))
            return Range(count.start, count.stop, self)
        elif isinstance(count, six.integer_types) or hasattr(count, "__call__"):
            return Range(count, count, self)
        else:
            raise TypeError("Expected a number, a contextual expression or a slice thereof, got %r" % (count,))
    def __rtruediv__(self, name):
        if name is not None and not isinstance(name, str):
            raise TypeError("`name` must be a string or None, got %r" % (name,))
        return (name, self)
    __rdiv__ = __rtruediv__


@singleton
class noop(Packer):
    __slots__ = ()
    def __repr__(self):
        return "noop"
    def _pack(self, obj, stream, ctx, cfg):
        pass
    def _unpack(self, stream, ctx, cfg):
        return None
    def _sizeof(self, ctx, cfg):
        return 0

class CtxConst(object):
    __slots__ = ["value"]
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return repr(self.value)
    def __call__(self, ctx):
        return self.value

def _contextify(value):
    if hasattr(value, "__call__"):
        return value
    else:
        return CtxConst(value)

class Adapter(Packer):
    #__slots__ = ["underlying", "_decode", "_encode"]
    def __init__(self, underlying, decode = None, encode = None):
        self.underlying = underlying

        if not hasattr(self, '_decode') and decode is None:
            self._decode = decode

        if not hasattr(self, '_encode') and encode is None:
            self._encode = encode

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.underlying)

    def _pack(self, obj, stream, ctx, cfg):
        obj2 = self.encode(obj, ctx)
        self.underlying._pack(obj2, stream, ctx, cfg)
    def _unpack(self, stream, ctx, cfg):
        obj = self.underlying._unpack(stream, ctx, cfg)
        return self.decode(obj, ctx)
    def _sizeof(self, ctx, cfg):
        return self.underlying._sizeof(ctx, cfg)
    
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
        self.length = _contextify(length)
    def __repr__(self):
        return "Raw(%r)" % (self.length,)
    def _pack(self, obj, stream, ctx, cfg):
        length = self.length(ctx)
        if len(obj) != length:
            raise RawError("Expected buffer of length %d, got %d" % (length, len(obj)))
        stream.write(obj)
    def _unpack(self, stream, ctx, cfg):
        length = self.length(ctx)
        data = stream.read(length)
        if len(data) != length:
            raise RawError("Expected buffer of length %d, got %d" % (length, len(data)))
        return data
    def _sizeof(self, ctx, cfg):
        return self.length(ctx)

def Named(*args, **kwargs):
    if (args and kwargs) or (not args and not kwargs):
        raise TypeError("This function takes either two positional arguments or a single keyword attribute", 
            args, kwargs)
    elif args:
        if len(args) != 2:
            raise TypeError("Expected exactly two positional arguments", args)
        elif not isinstance(args[0], str):
            raise TypeError("The first argument must be a string, got %r" % (args[0],))
        elif not isinstance(args[1], Packer):
            raise TypeError("The second argument must be a Packer, got %r" % (args[1],))
    else:
        if len(kwargs) != 1:
            raise TypeError("Expected exactly one keyword argument", kwargs)
        args = kwargs.popitem()
        if not isinstance(args[1], Packer):
            raise TypeError("The second argument must be a Packer, got %r" % (args[1],))
    if isinstance(args[1], UnnamedPackerMixin):
        raise TypeError("%s cannot take a name" % (args[1].__class__.__name__,))
    return tuple(args)

class UnnamedPackerMixin(object):
    # make us look like a tuple
    __slots__ = ()
    def __iter__(self):
        yield None
        yield self
    def __len__(self):
        return 2
    def __getitem__(self, index):
        return None if index == 0 else self
    def __rtruediv__(self, other):
        raise TypeError("%s cannot take a name" % (self.__class__.__name__,))
    __rdiv__ = __rtruediv__


class Embedded(UnnamedPackerMixin, Packer):
    __slots__ = ["underlying"]
    def __init__(self, underlying):
        self.underlying = underlying
    def _unpack(self, stream, ctx, cfg):
        with cfg.set(embedded = True):
            return self.underlying._unpack(stream, ctx, cfg)
    def _pack(self, obj, stream, ctx, cfg):
        with cfg.set(embedded = True):
            self.underlying._pack(obj, stream, ctx, cfg)
    def _sizeof(self, ctx, cfg):
        with cfg.set(embedded = True):
            return self.underlying._sizeof(ctx, cfg)

class Struct(Packer):
    __slots__ = ["members", "container_factory"]
    
    def __init__(self, *members, **kwargs):
        self.members = members
        self.container_factory = kwargs.pop("container_factory", None)
        if kwargs:
            raise TypeError("invalid keyword argument(s): %s" % (", ".join(kwargs.keys()),))
        names = set()
        for mem in members:
            if (not hasattr(mem, "__len__") or len(mem) != 2 or
                    not isinstance(mem[0], (type(None), str)) or not isinstance(mem[1], Packer)):
                raise TypeError("Struct members must be 2-tuples of (name, Packer): %r" % (mem,))
            if mem[0] in names:
                raise TypeError("Member %r already exists in this struct" % (mem[0],))
            if mem[0]:
                names.add(mem[0])

    def __repr__(self):
        return "Struct(%s)" % (", ".join(repr(m) for m in self.members),)
    
    def _unpack(self, stream, ctx, cfg):
        factory = self.container_factory or cfg.container_factory or Container
        if cfg.embedded:
            ctx2 = ctx
            obj = cfg.container
            del cfg.embedded
        else:
            ctx2 = {"_" : ctx}
            obj = factory()
        with cfg.set(container = obj, ctx = ctx2, container_factory = factory):
            for name, pkr in self.members:
                cfg.name = name
                obj2 = pkr._unpack(stream, ctx2, cfg)
                if name:
                    ctx2[name] = obj[name] = obj2
        return obj
    
    def _pack(self, obj, stream, ctx, cfg):
        if cfg.embedded:
            ctx2 = ctx
            obj = cfg.container
            del cfg.embedded
        else:
            ctx2 = {"_" : ctx}
        with cfg.set(container = obj, ctx = ctx2):
            for name, pkr in self.members:
                cfg.name = name
                if not name:
                    obj2 = None
                else:
                    obj2 = ctx2[name] = obj[name]
                pkr._pack(obj2, stream, ctx2, cfg)
    
    def _sizeof(self, ctx, cfg):
        if cfg.embedded:
            ctx2 = ctx
            del cfg.embedded
        else:
            ctx2 = {"_" : ctx}
        return sum(pkr.sizeof(ctx2, cfg) for _, pkr in self.members)


class Sequence(Packer):
    __slots__ = ["members", "container_factory"]
    
    def __init__(self, *members, **kwargs):
        self.members = members
        self.container_factory = kwargs.pop("container_factory", list)
        if kwargs:
            raise TypeError("Invalid keyword argument(s): %s" % (", ".join(kwargs.keys()),))
        for mem in members:
            if not isinstance(mem, Packer):
                raise TypeError("Sequence members must be Packers: %r" % (mem,))

    def __repr__(self):
        return "Sequence(%s)" % (", ".join(repr(m) for m in self.members),)
    
    def _unpack(self, stream, ctx, cfg):
        factory = self.container_factory or cfg.container_factory or Container
        if cfg.embedded:
            ctx2 = ctx
            obj = cfg.container
            i = cfg.name + 1
            del cfg.embedded
            embedded = True
        else:
            ctx2 = {"_" : ctx}
            obj = factory()
            i = 0
            embedded = False
        with cfg.set(container = obj, ctx = ctx, container_factory = factory):
            for pkr in self.members:
                cfg.name = i
                obj2 = pkr._unpack(stream, ctx2, cfg)
                if obj2 is not None:
                    obj.append(obj2)
                    ctx2[i] = obj2
                    i += 1
        return None if embedded else obj
    
    def _pack(self, obj, stream, ctx, cfg):
        from construct3.adapters import Padding
        ctx2 = {"_" : ctx}
        i = 0
        for pkr in self.members:
            if isinstance(pkr, Padding):
                pkr._pack(None, stream, ctx2)
            else:
                obj2 = ctx2[i] = obj[i]
                pkr._pack(obj2, stream, ctx2)
                i += 1
    
    def _sizeof(self, ctx, cfg):
        if cfg.embedded:
            ctx2 = ctx
            del cfg.embedded
        else:
            ctx2 = {"_" : ctx}
        return sum(pkr._sizeof(ctx2) for pkr in self.members)


class Range(Packer):
    __slots__ = ["mincount", "maxcount", "itempkr"]
    def __init__(self, mincount, maxcount, itempkr):
        self.mincount = _contextify(mincount)
        self.maxcount = _contextify(maxcount)
        self.itempkr = itempkr
    
    def __repr__(self):
        return "Range(%r, %r, %r)" % (self.mincount, self.maxcount, self.itempkr)
    
    def _pack(self, obj, stream, ctx, cfg):
        mincount = self.mincount(ctx)
        if mincount is None:
            mincount = 0
        maxcount = self.maxcount(ctx)
        if maxcount is None:
            maxcount = sys.maxsize
        assert maxcount >= mincount
        if len(obj) < mincount or len(obj) > maxcount:
            raise RangeError("Expected %s items, found %s" % (
                mincount if mincount == maxcount else "%s..%s" % (mincount, maxcount), len(obj)))
        ctx2 = {"_" : ctx}
        for i, item in enumerate(obj):
            ctx2[i] = item
            #import ipdb; ipdb.set_trace()
            self.itempkr._pack(item, stream, ctx2, cfg)
    
    def _unpack(self, stream, ctx, cfg):
        mincount = self.mincount(ctx)
        if mincount is None:
            mincount = 0
        maxcount = self.maxcount(ctx)
        if maxcount is None:
            maxcount = sys.maxsize
        assert maxcount >= mincount
        ctx2 = {"_" : ctx}
        obj = []
        for i in xrange(maxcount):
            try:
                obj2 = self.itempkr._unpack(stream, ctx2, cfg)
            except PackerError as ex:
                if i >= mincount:
                    break
                else:
                    raise RangeError("Expected %s items, found %s\nUnderlying exception: %r" % (
                        mincount if mincount == maxcount else "%s..%s" % (mincount, maxcount), i, ex))
            ctx2[i] = obj2
            obj.append(obj2)
        return obj

    def _sizeof(self, ctx, cfg):
        return self.count(ctx) * self.itempkr._sizeof({"_" : ctx}, cfg)


class While(Packer):
    __slots__ = ["cond", "itempkr"]
    def __init__(self, cond, itempkr):
        self.cond = cond
        self.itempkr = itempkr
    
    def __repr__(self):
        return "While(%r, %r)" % (self.cond, self.itempkr)
    
    def _pack(self, obj, stream, ctx, cfg):
        ctx2 = {"_" : ctx}
        for i, item in enumerate(obj):
            ctx2[i] = item
            self.itempkr._pack(item, stream, ctx2)
            if not self.cond(ctx2):
                break
    
    def _unpack(self, stream, ctx, cfg):
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
        raise NotImplementedError("Cannot compute sizeof of %r" % (self,))


class Switch(Packer):
    __slots__ = ["expr", "cases", "default"]
    def __init__(self, expr, cases, default = NotImplemented):
        self.expr = expr
        self.cases = cases
        self.default = default
    
    def _choose_packer(self, ctx):
        val = self.expr(ctx)
        if val in self.cases:
            return self.cases[val]
        elif self.default is not NotImplemented:
            return self.default
        else:
            raise SwitchError("Cannot find a handler for %r" % (val,))
    
    def _pack(self, obj, stream, ctx, cfg):
        pkr = self._choose_packer(ctx)
        pkr._pack(obj, stream, ctx, cfg)
    
    def _unpack(self, stream, ctx, cfg):
        pkr = self._choose_packer(ctx)
        return pkr._unpack(stream, ctx, cfg)

    def _sizeof(self, ctx, cfg):
        return self._choose_packer(ctx)._sizeof(ctx, cfg)

#=======================================================================================================================
# Stream-related
#=======================================================================================================================
class Bitwise(Packer):
    def __init__(self, underlying):
        self.underlying = underlying
    def __repr__(self):
        return "Bitwise(%r)" % (self.underlying,)
    def _unpack(self, stream, ctx, cfg):
        stream2 = BitStreamReader(stream)
        obj = self.underlying._unpack(stream2, ctx, cfg)
        stream2.close()
        return obj
    def _pack(self, obj, stream, ctx, cfg):
        stream2 = BitStreamWriter(stream)
        self.underlying._pack(obj, stream2, ctx, cfg)
        stream2.close()
    def _sizeof(self, ctx, cfg):
        return self.underlying._sizeof(ctx, cfg) // 8

@singleton
class anchor(Packer):
    __slots__ = ()
    def __repr__(self):
        return "anchor"
    def _unpack(self, stream, ctx, cfg):
        return stream.tell()
    def _pack(self, obj, stream, ctx, cfg):
        ctx[cfg.name] = stream.tell()
    def _sizeof(self, ctx, cfg):
        return 0

class Pointer(Packer):
    __slots__ = ["underlying", "offset"]
    def __init__(self, offset, underlying):
        self.underlying = underlying
        self.offset = _contextify(offset)
    def __repr__(self):
        return "Pointer(%r, %r)" % (self.offset, self.underlying)
    def _unpack(self, stream, ctx, cfg):
        newpos = self.offset(ctx)
        origpos = stream.tell()
        stream.seek(newpos)
        obj = self.underlying._unpack(stream, ctx, cfg)
        stream.seek(origpos)
        return obj
    def _pack(self, obj, stream, ctx, cfg):
        newpos = self.offset(ctx)
        origpos = stream.tell()
        stream.seek(newpos)
        self.underlying._pack(obj, stream, ctx, cfg)
        stream.seek(origpos)
    def _sizeof(self, ctx, cfg):
        return 0



