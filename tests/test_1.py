from construct3 import Struct, Member as M, int16ub, int32ub, this, int8u, Raw

ipaddr = int8u[4]
print ipaddr
#
#x = u_int8 >> u_int8 >> u_int8 >> (u_int8 >> u_int8)
#print x
#y = u_int8/"a" >> u_int8/"b" >> u_int8/"c" >> (u_int8/"x" >> u_int8/"y")/"d"
#print y

z = int8u >> Raw(this[0])
print z
print z.unpack("\x05hello")

#s = Struct(
#    M(foo = ub_int16),
#    M(bar = ub_int32),
#    M(spam = Struct(
#        M(bacon = ub_int16),
#        M(eggs = ub_int16),
#    )),
#    M(viking = ub_int16[this.foo]),
#)
#
#obj = s.unpack("\x00\x03yyyyzzwwaabbcc")
#print obj
##obj["viking"].append(7)
#print repr(s.pack(obj))

#s = Struct(
#    int16ub/"foo",
#    int32ub/"bar",
#    Struct(
#        int32ub/"bacon",
#        int32ub/"eggs",
#    ) / "spam",
#)
#print s

