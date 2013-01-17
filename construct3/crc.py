from construct3.packers import Packer, Struct

class DigestingStream(object):
    __slots__ = ["stream", "digestor"]
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
    def _unpack(self, stream, ctx, cfg):
        return self.underlying._unpack(DigestingStream(stream, cfg.digestor), ctx, cfg)
    def _pack(self, obj, stream, ctx, cfg):
        self.underlying._pack(obj, DigestingStream(stream, cfg.digestor), ctx, cfg)

class DigestedStruct(Struct):
    def __init__(self, *members, **kwargs):
        self.digestor_factory = kwargs.pop("digestor_factory")
        Struct.__init__(self, *members, **kwargs)
    
    def _unpack(self, stream, ctx, cfg):
        digestor = self.digestor_factory()
        with cfg.set(digestor = digestor):
            obj = Struct._unpack(self, stream, ctx, cfg)
            obj["__digest__"] = digestor.digest()
        return obj




if __name__ == "__main__":
    from construct3 import int8
    from hashlib import md5
    
    d = DigestedStruct(
        "a" / Digested(int8),
        "b" / Digested(int8),
        "c" / Digested(int8),
        "d" / Digested(int8),
        digestor_factory = md5,
    )
    print d.unpack("ABCD")
    print repr(md5("ABCD").digest())




