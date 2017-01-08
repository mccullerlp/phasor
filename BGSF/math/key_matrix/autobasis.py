"""
"""

from __future__ import division
from ..math import dispatched as dmath
dmath #  silence lint

RAISE = DictKey(Op = 'raising')
LOWER = DictKey(Op = 'lowering')

def keyvect_cplx_to_real(kv):
    donekeys = set()
    for key in list(kv.keys()):
        if key in donekeys:
            continue
        xkey = key.has_any_remove(RAISE, LOWER)
        if xkey is None:
            continue
        RKEY = xkey | RAISE
        LKEY = xkey | LOWER
        donekeys.add(RKEY)
        donekeys.add(LKEY)
    return


def keymatrix_cplx_to_real(km):
    return
