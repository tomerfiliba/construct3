from construct3 import Struct, Member as M, ub_int16, ub_int32


s = Struct(
    M(foo = ub_int16),
    M(bar = ub_int32),
    M(spam = Struct(
        M(bacon = ub_int16),
        M(eggs = ub_int16),
    ))
)

obj = s.unpack("xxyyyyzzww")
print obj
print s.pack(obj)
