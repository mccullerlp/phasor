# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
import numpy as np

oldprint = print
def print(*args):
    pargs = []
    for a in args:
        try:
            if isinstance(a, np.array):
                rep = a
            else:
                rep = unicode(a, 'utf-8')
        except TypeError:
            rep = repr(a)
        pargs.append(rep)
    oldprint(*args)
