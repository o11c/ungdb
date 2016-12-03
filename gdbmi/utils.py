class Constant(object):
    ''' Interned, but extensible, constants.

    For non-extensible constants, use the `enum` module.
    '''
    def __new__(cls, name):
        # First, make sure the cache is per-class.
        if '_cache' not in cls.__dict__:
            cache = cls._cache = {}
        else:
            cache = cls._cache
        # In Python2 this works, but it is broken by Python3's mappingproxy.
        #cache = cls.__dict__.setdefault('_cache', {})

        # Then, cache the individual name.
        try:
            rv = cache[name]
        except KeyError:
            # Avoid creating the object if there was an existing one.
            rv = cache[name] = object.__new__(cls)
            rv._init_once(name)
            if not cls._sealed:
                setattr(cls, name.upper(), rv)
        return rv
    _sealed = True
    def _init_once(self, name):
        # Because __init__ is called multiple times.
        self.name = name
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)
