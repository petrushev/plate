
from hashlib import md5 as hashlib_md5

def md5(text):
    if type(text)==unicode:
        text = text.encode('utf-8')
    text = str(text)
    m = hashlib_md5(text)
    return m.hexdigest()

class Memo(object):
    """Memoization singleton, holding cache for different function"""
    _cache = {}

    @classmethod
    def memo(cls, fc):
        """Memoization with cache by function"""
        try:
            fc_cache = cls._cache[id(fc)]
        except KeyError:
            fc_cache = cls._cache[id(fc)]={}
        def memoized(*args):
            try:
                return fc_cache[tuple(args)]
            except KeyError:
                res = fc(*args)
                fc_cache[tuple(args)]=res
                return res
        return memoized

memoize = Memo.memo
