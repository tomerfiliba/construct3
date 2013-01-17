from six import b
from construct3.packers import Switch, _contextify, Range, Raw, Struct, Bitwise
from construct3.adapters import LengthValue, StringAdapter, Mapping, Padding


def If(cond, thenpkr, elsepkr):
    return Switch(lambda ctx, cond = _contextify(cond): bool(cond(ctx)), 
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

def AlignedStruct(*members):
    """
    Algorithm taken from http://en.wikipedia.org/wiki/Data_structure_alignment#Computing_padding
    
    Example::
    
        s = AlignedStruct(
            "a" / word8,               # 0
            # padding (1)              # 1
            "b" / word16,              # 2-3
            "c" / word16,              # 4-5
            # padding (2)              # 6-7
            "d" / word32,              # 8-11
            "e" / word8,               # 12
            "f" / BitStruct(           # 13
                "x" / nibble,
                "y" / nibble,
            )
            # padding (2)              # 14-15
            # total size = 16
        )
    """
    members2 = []
    offset = 0
    largest = 0
    # align each member to its native size, e.g., int32 is aligned to 4-bytes
    for name, pkr in members:
        align = pkr.sizeof()
        largest = max(align, largest)
        padding = (align - offset % align) % align
        offset += align + padding
        if padding > 0:
            members2.append(Padding(padding))
        members2.append((name, pkr))
    # the struct must be aligned to its largest member
    if offset % largest != 0:
        members2.append(Padding(largest - offset % largest))
    return Struct(*members2)
















