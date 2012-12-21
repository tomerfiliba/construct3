from construct3 import (Struct, Adapter, Enum, int8u, this, Computed, int16ub, Raw, Padding, flag, 
    BitStruct, Bits, nibble)

ipaddr = Adapter(int8u[4], 
    decode = lambda obj, ctx: ".".join(str(x) for x in obj),
    encode = lambda obj, ctx: [int(x) for x in obj.split(".")]
)

ipv4_header = Struct(
    "foo" / BitStruct(
        "version" / nibble,
        "header_length" / Adapter(nibble, decode = lambda obj, ctx: obj * 4, encode = lambda obj, ctx: obj / 4),
    ),
    "tos" / BitStruct(
        "precedence" / Bits(3),
        "minimize_delay" / flag,
        "high_throuput" / flag,
        "high_reliability" / flag,
        "minimize_cost" / flag,
        Padding(1),
    ),
    Padding(2),
    "total_length" / int16ub,
#    Computed(this.total_length - this.foo.header_length) / "payload_length",
#    int16ub / "identification",
#    BitStruct(
#        (Padding(1) >> flag / "dont_fragment" >> flag / "more_fragments") / "flags",
#        Bits(13) / "frame_offset",
#    ) / "crap",
#    int8u / "ttl",
#    Enum(int8u, ICMP = 1, TCP = 6, UDP = 17) / "protocol",
#    int16ub / "checksum",
#    ipaddr / "source",
#    ipaddr / "destination",
#    Raw(this.header_length - 20) / "options",
)


if __name__ == "__main__":
    cap = "4500003ca0e3000080116185c0a80205d474a126".decode("hex")
    obj = ipv4_header.unpack(cap)
    print (obj)
    print (repr(ipv4_header.pack(obj)))









