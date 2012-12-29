import struct as _struct
from srcgen.python import PythonModule, STMT, DEF, IMPORT, FROM_IMPORT, IF, FOR, WHILE, DOC, SEP
from construct3.packers import Packer, Struct, Sequence, Raw, CtxConst, Adapter, noop
from construct3.numbers import Formatted
from construct3.lib.thisexpr import Path, BinExpr, UniExpr, opnames


_registry = {}
def register(pkr_cls):
    def deco(cls):
        _registry[pkr_cls] = cls
        return cls
    return deco

def _get_visitor(pkr):
    for cls in type(pkr).mro():
        if cls in _registry:
            return _registry[cls]
    raise TypeError("Cannot generate code for %r" % (pkr,))

class BaseVisitor(object):
    @classmethod
    def setup(cls, pkr):
        pass
    @classmethod
    def generate_unpacker(cls, pkr, streamvar, ctxvar):
        raise NotImplementedError()
    @classmethod
    def generate_packer(cls, pkr, streamvar, ctxvar):
        raise NotImplementedError()

class Variable(object):
    _all_vars = frozenset(range(5000))
    _used_vars = set()
    def __init__(self):
        self.id = min(self._all_vars - self._used_vars)
        self._used_vars.add(self.id)
    def __enter__(self):
        pass
    def __exit__(self, t, v, tb):
        self.free()
    def free(self):
        self._used_vars.discard(self.id)
        self.id = None
    def __del__(self):
        self.free()
    def __str__(self):
        if self.id is None:
            raise ValueError("Variable has been freed")
        return "var%d" % (self.id,)
    __repr__ = __str__
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, other):
        return str(self) == str(other)
    def __ne__(self, other):
        return str(self) != str(other)
    def __add__(self, other):
        return str(self) + other

def _path_to_list(path):
    elems = []
    while path and path._Path__parent:
        elems.insert(0, path._Path__name)
        path = path._Path__parent
    return elems

def _generate_expr(expr, ctx):
    if isinstance(expr, CtxConst):
        return repr(expr.value)
    elif isinstance(expr, Path):
        path = _path_to_list(expr)
        while path:
            if path[0] in ctx:
                ctx = ctx[path[0]]
                path.pop(0)
            else:
                break
        #return "%s%s" % (ctx["this"], "".join("[%r]" % (p,) for p in path))
        return "%s%s" % (ctx, "".join("[%r]" % (p,) for p in path))
    elif isinstance(expr, BinExpr):
        return "(%s %s %s)" % (_generate_expr(expr.lhs, ctx), opnames[expr.op], _generate_expr(expr.rhs, ctx))
    elif isinstance(expr, UniExpr):
        return "%s%s" % (opnames[expr.op], _generate_expr(expr.operand, ctx))
    elif isinstance(expr, (bool, int, float, long, str, unicode)):
        return repr(expr)
    else:
        raise ValueError(expr)

#=======================================================================================================================
@register(Sequence)
class SequenceVisitor(BaseVisitor):
    @classmethod
    def setup(cls, pkr):
        for pkr2 in pkr.members:
            _get_visitor(pkr2).setup(pkr2)

    @classmethod
    def generate_unpacker(cls, pkr, streamvar, ctx):
        res = Variable()
        STMT("{0} = []", res)
        ctx2 = {"_" : ctx}
        for i, pkr2 in enumerate(pkr.members):
            tmp = _generate_unpacker(pkr2, streamvar, ctx2)
            ctx2[i] = tmp
            STMT("{0}.append({1})", res, tmp)
        return res

@register(Adapter)
class AdapterVisitor(BaseVisitor):
    @classmethod
    def setup(cls, pkr):
        _get_visitor(pkr.underlying).setup(pkr.underlying)
        FROM_IMPORT(pkr.__class__.__module__, pkr.__class__.__name__)

    @classmethod
    def generate_unpacker(cls, pkr, streamvar, ctx):
        res = _generate_unpacker(pkr.underlying, streamvar, ctx)
        STMT("{0} = {1.__class__.__name__}.decode.im_func(None, {0}, {{}})", res, pkr)
        return res

@register(Formatted)
class FormattedVisitor(BaseVisitor):
    @classmethod
    def setup(cls, pkr):
        IMPORT("struct as _struct")

    @classmethod
    def generate_unpacker(cls, pkr, streamvar, ctx):
        res = Variable()
        STMT("{0}, = _struct.unpack({1!r}, {2}.read({3}))", res, pkr.FORMAT, streamvar, 
            _struct.calcsize(pkr.FORMAT))
        return res

@register(Raw)
class RawVisitor(BaseVisitor):
    @classmethod
    def generate_unpacker(cls, pkr, streamvar, ctx):
        res = Variable()
        STMT("{0} = {1}.read({2})", res, streamvar, _generate_expr(pkr.length, ctx))
        return res

@register(type(noop))
class NoopsVisitor(BaseVisitor):
    @classmethod
    def generate_unpacker(cls, pkr, streamvar, ctx):
        pass

#=======================================================================================================================

def _generate_unpacker(pkr, streamvar, ctxvar):
    return _get_visitor(pkr).generate_unpacker(pkr, streamvar, ctxvar)

def generate(pkr, name):
    with PythonModule(name) as mod:
        _get_visitor(pkr).setup(pkr)
        SEP()
        with DEF("%s_unpack" % (name,), ["stream"]):
            ctx = {}
            res = _generate_unpacker(pkr, "stream", ctx)
            STMT("return {0}", res)
    return mod



if __name__ == "__main__":
    from construct3.lib import this
    from construct3.numbers import byte
    from construct3.adapters import LengthValue
    testpkr = Sequence(byte, byte, Sequence(byte, byte, Raw(this[0] + this[1] + this._[0] + this._[1])))
    #testpkr = LengthValue(byte >> Raw(this[0]))
    mod = generate(testpkr, "test")
    print testpkr
    mod.dump("testpacker.py")
    import testpacker
    from io import BytesIO
    #data = BytesIO("\x05helloXX")
    data = BytesIO("\x01\x01\x01\x02helloXX")
    print testpacker.test_unpack(data)




