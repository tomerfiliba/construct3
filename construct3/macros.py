from construct3.packers import Switch, contextify, Range, Raw, Struct, Bitwise
from construct3.adapters import LengthValue, StringAdapter, Mapping
from construct3.lib.binutil import int_to_byte


def If(cond, thenpkr, elsepkr):
    return Switch(lambda ctx, cond = contextify(cond): bool(cond(ctx)), 
        {True : thenpkr, False : elsepkr})

def PascalString(lengthpkr, encoding = "utf8"):
    return StringAdapter(LengthValue(lengthpkr), encoding)

def Array(count, itempkr):
    return Range(count, count, itempkr)

def Bijection(pkr, dec_mapping, default = NotImplemented):
    return Mapping(pkr, dec_mapping, default, {v:k for k, v in dec_mapping.items()}, default)

def Enum(pkr, **kwargs):
    return Bijection(pkr, kwargs, kwargs.pop("__default__", NotImplemented))

def Flag(truth = 1, falsehood = 0, default = False):
    return Bijection(Raw(1), {True : int_to_byte(truth), False : int_to_byte(falsehood)}, default)

flag = Flag()

def BitStruct(*args, **kwargs):
    return Bitwise(Struct(*args, **kwargs))

def Optional(pkr):
    return pkr[0:1]



