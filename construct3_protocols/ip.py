from construct3 import (Struct, Adapter, Enum, int8u, this, Computed, int16ub, Raw, Padding, flag, 
    BitStruct, Bits, nibble)

ipaddr = Adapter(int8u[4], 
    decode = lambda obj, ctx: ".".join(str(x) for x in obj),
    encode = lambda obj, ctx: [int(x) for x in obj.split(".")]
)

ipv4_header = Struct(
    +BitStruct(
        "version" / nibble,
        "header_length" / Adapter(nibble, decode = lambda obj, _: obj * 4, encode = lambda obj, _: obj / 4),
    ),
    "tos" / BitStruct(
        "precedence" / Bits(3),
        "minimize_delay" / flag,
        "high_throuput" / flag,
        "high_reliability" / flag,
        "minimize_cost" / flag,
        Padding(1),
    ),
    "total_length" / int16ub,
    "payload_length" / Computed(this.total_length - this.header_length),
    int16ub / "identification",
    +BitStruct(
        "flags" / Struct(
            Padding(1),
            "dont_fragment" / flag,
            "more_fragments" / flag,
        ),
        "frame_offset" / Bits(13),
    ),
    "ttl" / int8u,
    "protocol" / Enum(int8u, ICMP = 1, TCP = 6, UDP = 17),
    "checksum" / int16ub,
    "source" / ipaddr,
    "destination" / ipaddr,
    "options" / Raw(this.header_length - 20),
)


if __name__ == "__main__":
    cap = "4500003ca0e3000080116185c0a80205d474a126".decode("hex")
    obj = ipv4_header.unpack(cap)
    print (obj)
    #rebuilt = ipv4_header.pack(obj)
    #print (repr(rebuilt))
    #assert cap == rebuilt









