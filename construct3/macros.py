from construct3.packers import Switch, contextify, Field
from construct3.adapters import LengthValue, StringAdapter, FormattedField, OneOf
from construct3.lib import singleton


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


def If(cond, thenpkr, elsepkr):
    return Switch(lambda ctx, cond = contextify(cond): bool(cond(ctx)), 
        {True : thenpkr, False : elsepkr})

def PascalString(lengthpkr, encoding = "utf8"):
    return StringAdapter(LengthValue(lengthpkr), "utf8")









