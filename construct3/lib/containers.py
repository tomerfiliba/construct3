import itertools
import six
_counter = itertools.count()

class Container(dict):
    __slots__ = ["__order__"]
    def __init__(self, iterable = (), **kwargs):
        dict.__setattr__(self, "__order__", {})
        self.update(iterable, **kwargs)
    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        if key not in self.__order__:
            self.__order__[key] = six.next(_counter)
    def __delitem__(self, key):
        dict.__delitem__(self, key)
        del self.__order__[key]
    def update(self, iterable, **kwargs):
        for k, v in iterable:
            self[k] = v
        for k, v in kwargs.items():
            self[k] = v
    def pop(self, key, *default):
        dict.pop(self, key, *default)
        self.__order__.pop(key, None)
    __getattr__ = dict.__getitem__
    __setattr__ = __setitem__
    __delattr__ = __delitem__
    def __iter__(self):
        items = list(self.__order__.items())
        items.sort(key = lambda item: item[1])
        return (k for k, _ in items)
    def keys(self):
        return list(iter(self))
    def values(self):
        return [self[k] for k in self]
    def items(self):
        for k in self:
            yield k, self[k]
    iterkeys = keys
    itervalues = values
    iteritems = items
    def __repr__(self):
        if not self:
            return "%s()" % (self.__class__.__name__,)
        attrs = "\n  ".join("%s = %s" % (k, "\n  ".join(repr(v).splitlines())) 
            for k, v in self.items())
        return "%s:\n  %s" % (self.__class__.__name__, attrs)


if __name__ == "__main__":
    c = Container(aa = 6, b = 7, c = Container(d = 8, e = 9, f = 10))
    del c.aa
    c.aa = 0
    c.xx = Container()
    print [c, c, c]




