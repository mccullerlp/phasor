"""
"""
import numpy as np

from . import dispatched
import collections
mod_locals = locals()

for name in dir(dispatched):
    mfunc = getattr(dispatched, name)
    if name in ['np']:
        continue
    if isinstance(mfunc, collections.Callable):
        mod_locals[name] = np.vectorize(mfunc)

