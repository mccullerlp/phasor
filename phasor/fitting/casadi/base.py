# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import casadi

from ...math.dispatch_casadi import *

from ... import base


def casadi_sparsity_ravel(sym_vec):
    return casadi.vertcat(*sym_vec)

def casadi_sparsity_unravel(sym_vec, ret_vec):
    idx = 0
    retvv = []
    for sym in sym_vec:
        slen = sym.shape[0]
        retvv.append(
            ret_vec[idx:idx + slen]
        )
        idx += slen
    return retvv

def casadi_sparsity_slice(sym_vec):
    idx = 0
    retvv = []
    for sym in sym_vec:
        slen = sym.shape[0]
        if slen == 1:
            retvv.append(idx)
        else:
            retvv.append(slice(idx, idx+slen))
        idx += slen
    return retvv


class FitterBase(base.Element):
    pass
