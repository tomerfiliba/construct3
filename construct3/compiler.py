import struct as _struct
from construct3.packers import Struct
from construct3.numbers import Formatted, byte


class VisitorError(Exception):
    pass

class CompilerVisitor(object):
    def __init__(self, packer):
        self._formatteds = {}
        print "import struct as _struct"
        for cls in Formatted.__subclasses__():
            name = "_fmt" + cls.FORMAT.replace("!", "b").replace("<", "l")
            self._formatteds[cls.FORMAT] = (name, _struct.calcsize(cls.FORMAT))
            print "%s = _struct.Struct(%r)" % (name, cls.FORMAT)
        self.visit(packer)
        
    def visit(self, packer):
        for cls in packer.__class__.mro():
            method = getattr(self, "visit_%s" % (cls.__name__,), None)
            if method:
                return method(packer)
        raise VisitorError("No visitor for %r" % (packer.__class__,))
    def visit_Struct(self, packer):
        print "ctx = {'_' : ctx}"
        print "obj = {}"
        for name, pkr in packer.members:
            print "obj[%r] = %s" % (name, self.visit(pkr))
    def visit_Formatted(self, packer):
        return "%s.unpack(stream.read(%r))" % self._formatteds[packer.FORMAT]


if __name__ == "__main__":
    x = byte / "a" >> byte / "b"
    CompilerVisitor(x)



