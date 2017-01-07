"""
"""
from __future__ import division, print_function
from . import visitors as VISIT
import casadi

from declarative.substrate import (
    Element,
)

from ...math.dispatch_casadi import *


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


class FitterBase(Element):

    def targets_recurse(self, typename):
        dmap = []
        for cname, cobj in self._registry_children.items():
            if isinstance(cobj, FitterBase):
                dmap.extend(cobj.targets_recurse(typename))
        target_ret = self.targets_list(typename)
        if target_ret is not None:
            dmap.append(target_ret)
        return dmap

    def targets_list(self, typename):
        if typename == VISIT.self:
            return self
        return None

