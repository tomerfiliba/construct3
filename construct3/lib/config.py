from contextlib import contextmanager


class Config(object):
    @contextmanager
    def set(self, **kwargs):
        prev = self.__dict__.copy()
        self.__dict__.update(kwargs)
        yield
        self.__dict__ = prev
    def __getattr__(self, name):
        return None
    def __delattr__(self, name):
        self.__dict__.pop(name, None)


