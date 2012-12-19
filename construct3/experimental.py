from construct3.packers import Packer, Struct


class DigestingStream(object):
    def __init__(self, stream, digestor):
        self.stream = stream
        self.digestor = digestor
    def read(self, count):
        data = self.stream.read(count)
        self.digestor.update(data)
        return data
    def write(self, data):
        self.digestor.update(data)
        self.stream.write(data)

class Digested(Packer):
    def __init__(self, underlying):
        self.underlying = underlying
    def _unpack(self, stream, ctx):
        return self.underlying._unpack(DigestingStream(stream, ctx["_"]["__digestor__"]), ctx)
    def _pack(self, obj, stream, ctx):
        self.underlying._pack(obj, DigestingStream(stream, ctx["_"]["__digestor__"]), ctx)

class DigestedStruct(Struct):
    def __init__(self, *members, **kwargs):
        self.digestor_factory = kwargs.pop("digestor_factory")
        Struct.__init__(self, *members, **kwargs)
    
    def _unpack(self, stream, ctx):
        digestor = ctx["__digestor__"] = self.digestor_factory()
        obj = Struct._unpack(self, stream, ctx)
        del ctx["__digestor__"]
        return obj, digestor

#class Modified(Packer):
#    def __init__(self, underlying, ctx_modifier):
#        self.underlying = underlying
#        self.ctx_modifier = ctx_modifier
#    def _unpack(self, stream, ctx):
#        ctx2 = ctx.copy()
#        self.ctx_modifier(ctx2)
#        return self.underlying._unpack(stream, ctx2)
#
#def DigestedStruct(*members, **kwargs):
#    digestor_factory = kwargs.pop("digestor_factory")
#    return Modified(Struct(*members, **kwargs),
#                    lambda ctx: ctx.update(__digestor__ = digestor_factory()))

if __name__ == "__main__":
    from construct3.macros import ub_int64
    from hashlib import md5

    d = DigestedStruct(
        ("foo", Digested(ub_int64)),
        ("bar", ub_int64),
        ("spam", Digested(ub_int64)),
        digestor_factory = md5
    )
    obj, dig = d.unpack("abcdefgh12345678ABCDEFGH")
    print obj
    print dig.hexdigest()
    print dig.hexdigest() == md5("abcdefghABCDEFGH").hexdigest()

    #{'foo': 7017280452245743464L, 'bar': 3544952156018063160L, 'spam': 4702394921427289928L}
    #43fe52a72b78c5cbc8cfab2165a7f862
    #True











