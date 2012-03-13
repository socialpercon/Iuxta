#!/usr/bin/env python
from contextlib import contextmanager
from functools import wraps
from time import time

def timed(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        start = time()
        result = f(*args, **kwds)
        elapsed = time() - start
        print "%s took %d time to finish"%(f.__name__, elapsed)
        return result
    return wrapper

@contextmanager
def measure(title="", verbose=True):
    t1 = time()
    yield t1
    t2 = time()
    if verbose: print "%s %0.2fs"%(title, t2-t1)
