import struct as _struct
from srcgen.python import PythonModule, STMT, DEF, IMPORT, FROM_IMPORT, IF, FOR, WHILE, DOC, SEP
from construct3.packers import Packer, Struct, Sequence, Raw, CtxConst
from construct3.numbers import Formatted
import itertools
from construct3.lib.thisexpr import ExprMixin, Path, BinExpr, UniExpr, opnames
from contextlib import contextmanager


_registry = {}

def register(pkr_cls):
    def deco(cls):
        _registry[pkr_cls] = cls
        return cls
    return deco

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

_used_vars = set()
_all_vars = frozenset(range(1000))
@contextmanager
def freevar(prefix = "var"):
    varid = min(_all_vars - _used_vars)
    _used_vars.add(varid)
    yield "var%d" % (varid,)
    _used_vars.discard(varid)

@register(Struct)
class StructVisitor(BaseVisitor):
    @classmethod
    def generate_unpacker(cls, pkr, streamvar, ctxvar):
        pass

@register(Sequence)
class SequenceVisitor(BaseVisitor):
    @classmethod
    def setup(cls, pkr):
        IMPORT("struct as _struct")

    @classmethod
    def generate_unpacker(cls, pkr, streamvar, ctxvar):
        with freevar("tmp") as res, freevar("ctx") as ctx: 
            STMT("{0} = []", res)
            STMT("{0} = {{'_': {1}}}", ctx, ctxvar)
            for i, pkr2 in enumerate(pkr.members):
                tmp = _generate_unpacker(pkr2, streamvar, ctx)
                STMT("{0}.append({1})", res, tmp)
                STMT("{0}[{1}] = {2}", ctx, i, tmp)
            return res

@register(Formatted)
class FormattedVisitor(BaseVisitor):
    @classmethod
    def generate_unpacker(cls, pkr, streamvar, ctxvar):
        with freevar("tmp") as res:
            STMT("{0}, = _struct.unpack({1!r}, {2}.read({3}))", res, pkr.FORMAT, streamvar, _struct.calcsize(pkr.FORMAT))
            return res

#@register(Packer)
#class PackerVisitor(BaseVisitor):
#    @classmethod
#    def generate_unpacker(cls, pkr, streamvar, ctxvar):
#        STMT("{0!r}", pkr)


def _generate_expr(expr, ctxvar):
    if isinstance(expr, Path):
        path = []
        p = expr
        while p and p._Path__parent:
            path.append("[%r]" % (p._Path__name,))
            p = p._Path__parent
        return ctxvar + "".join(reversed(path))
    elif isinstance(expr, BinExpr):
        return "(%s %s %s)" % (_generate_expr(expr.lhs, ctxvar), opnames[expr.op], _generate_expr(expr.rhs, ctxvar))
    elif isinstance(expr, UniExpr):
        return "%s%s" % (opnames[expr.op], _generate_expr(expr.operand, ctxvar))
    else:
        return repr(expr)

@register(Raw)
class RawVisitor(BaseVisitor):
    @classmethod
    def generate_unpacker(cls, pkr, streamvar, ctxvar):
        with freevar("tmp") as res:
            if isinstance(pkr.length, CtxConst):
                STMT("{0} = {1}.read({2})", res, streamvar, pkr.length.value)
            elif isinstance(pkr.length, ExprMixin):
                STMT("{0} = {1}.read({2})", res, streamvar, _generate_expr(pkr.length, ctxvar))
            else:
                raise ValueError("opaque lambda")
                #STMT("{0} = stream.read({1})", res, pkr.length)
            return res
        
def _get_visitor(pkr):
    for cls in type(pkr).mro():
        if cls in _registry:
            return _registry[cls]
    raise TypeError("Cannot generate code for %r" % (pkr,))

def _generate_unpacker(pkr, streamvar, ctxvar):
    return _get_visitor(pkr).generate_unpacker(pkr, streamvar, ctxvar)

def generate(pkr, name):
    with PythonModule(name) as mod:
        _get_visitor(pkr).setup(pkr)
        SEP()
        with DEF("%s_unpack" % (name,), ["stream"]):
            with freevar("ctx") as ctxvar:
                STMT("{0} = {{}}", ctxvar)
                res = _generate_unpacker(pkr, "stream", ctxvar)
                STMT("return {0}", res)
        #with DEF("%s_pack" % (name,), ["obj"]):
        #    _get_visitor(pkr).generate_unpacker()
    return mod



if __name__ == "__main__":
    from construct3.lib import this
    from construct3.numbers import byte, int16sb, int64ul
    testpkr = Sequence(byte, Raw(this[0]))
    mod = generate(testpkr, "test")
    print mod
    
    code = compile(str(mod), "testpacker.py", "exec")
    eval(code)
    from io import BytesIO
    data = BytesIO("\x05helloXXX")
    print test_unpack(data)

#import struct as _struct
#
#def test_unpack(stream):
#    var0 = {}
#    var1 = []
#    var2 = {'_': var0}
#    var3, = _struct.unpack('B', stream.read(1))
#    var1.append(var3)
#    var2[0] = var3
#    var3 = stream.read(var2[0])
#    var1.append(var3)
#    var2[1] = var3
#    return var1
#
#[5, 'hello']













