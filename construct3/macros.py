from six import b
from construct3.packers import Switch, contextify, Range, Raw, Struct, Bitwise
from construct3.adapters import LengthValue, StringAdapter, Mapping


def If(cond, thenpkr, elsepkr):
    return Switch(lambda ctx, cond = contextify(cond): bool(cond(ctx)), 
        {True : thenpkr, False : elsepkr})

def PascalString(lengthpkr, encoding = "utf8"):
    return StringAdapter(LengthValue(lengthpkr), encoding)

def Array(count, itempkr):
    return Range(count, count, itempkr)

def Bijection(pkr, enc_mapping, default = NotImplemented):
    dec_mapping = dict((v, k) for k, v in enc_mapping.items())
    if default is not NotImplemented:
        enc_default = enc_mapping[default]
        dec_default = dec_mapping[enc_default]
    else:
        enc_default = dec_default = NotImplemented
    return Mapping(pkr, dec_mapping, enc_mapping, dec_default, enc_default)

def Enum(pkr, **kwargs):
    return Bijection(pkr, kwargs, kwargs.pop("__default__", NotImplemented))

flag = Bijection(Raw(1), {True : b("\x01"), False : b("\x00")}, False)

def BitStruct(*args, **kwargs):
    return Bitwise(Struct(*args, **kwargs))

def Optional(pkr):
    return pkr[0:1]

raw = Raw(1)

