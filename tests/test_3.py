from construct3 import Struct, Sequence, int8, Embedded, Padding, Computed, this, anchor, Container


x = Struct(
    "a" / int8,
    "b" / int8,
    Padding(2),
    "c" / int8,
    Embedded(Struct(
        "d" / int8,
        "e" / int8,
        "x" / Computed(this.d - this.a),
    )),
    "f" / int8,
#    "g" / anchor,
)

#print x.unpack("ABppCDEF")
print repr(x.pack(Container(a=1,b=2,c=3,d=4,e=5,f=6)))

y = Sequence(
    int8,
    int8,
    Padding(2),
    int8,
    Embedded(Sequence(
        int8,
        int8,
        Computed(this[4] - this[0]),
    )),
    int8,
    anchor,
)

#print y.unpack("ABppCDEF")











