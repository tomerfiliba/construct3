from construct3.packers import Switch, contextify
from construct3.adapters import LengthValue, StringAdapter, Formatted, OneOf
from construct3.lib import singleton


@singleton
class u_int8(Formatted):
    """Unsigned 8-bit integer"""
    FORMAT = "B"

@singleton
class s_int8(Formatted):
    """Signed 8-bit integer"""
    FORMAT = "b"

@singleton
class ub_int16(Formatted):
    """Unsigned big-endian 16-bit integer"""
    FORMAT = "!H"

@singleton
class sb_int16(Formatted):
    """Signed big-endian 16-bit integer"""
    FORMAT = "!h"

@singleton
class ul_int16(Formatted):
    """Unsigned little-endian 16-bit integer"""
    FORMAT = "<H"

@singleton
class sl_int16(Formatted):
    """Signed little-endian 16-bit integer"""
    FORMAT = "<h"

@singleton
class ub_int32(Formatted):
    """Unsigned big-endian 32-bit integer"""
    FORMAT = "!L"

@singleton
class sb_int32(Formatted):
    """Signed big-endian 32-bit integer"""
    FORMAT = "!l"

@singleton
class ul_int32(Formatted):
    """Unsigned little-endian 32-bit integer"""
    FORMAT = "<L"

@singleton
class sl_int32(Formatted):
    """Signed little-endian 32-bit integer"""
    FORMAT = "<l"

@singleton
class ub_int64(Formatted):
    """Unsigned big-endian 64-bit integer"""
    FORMAT = "!Q"

@singleton
class sb_int64(Formatted):
    """Signed big-endian 64-bit integer"""
    FORMAT = "!q"

@singleton
class ul_int64(Formatted):
    """Unsigned little-endian 64-bit integer"""
    FORMAT = "<Q"

@singleton
class sl_int64(Formatted):
    """Signed little-endian 64-bit integer"""
    FORMAT = "<q"

@singleton
class b_float32(Formatted):
    """Big-endian 32-bit floating point number"""
    FORMAT = "!f"

@singleton
class b_float64(Formatted):
    """Big-endian 64-bit floating point number"""
    FORMAT = "!d"

@singleton
class l_float32(Formatted):
    """Little-endian 32-bit floating point number"""
    FORMAT = "<f"

@singleton
class l_float64(Formatted):
    """Little-endian 64-bit floating point number"""
    FORMAT = "<d"


def If(cond, thenpkr, elsepkr):
    return Switch(lambda ctx, cond = contextify(cond): bool(cond(ctx)), 
        {True : thenpkr, False : elsepkr})

def PascalString(lengthpkr, encoding = "utf8"):
    return StringAdapter(LengthValue(lengthpkr), "utf8")









