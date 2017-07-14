# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from builtins import range
import numpy as np
from phasor.math.complex import Complex


class TargetIdx(tuple):
    pass


TargetLeft  = TargetIdx(['left'])
TargetRight = TargetIdx(['right'])


def matrix_array_invert(mat):
    oshape = mat.shape
    if len(oshape) == 2:
        return mat**(-1)
    else:
        mat = mat.reshape(2, 2, -1)
        for idx in range(mat.shape[2]):
            mat[idx] = mat[idx]**(-1)
        mat = mat.reshape(oshape)
    return mat


def np_check_sorted(vals):
    if len(vals.shape) > 1:
        return False
    else:
        return np.all(vals[1:] > vals[:-1])


def matrix_space(L_m):
    return np.matrix([
        [1, L_m],
        [0, 1],
    ])


def matrix_focus(f_m, dL = 0):
    if f_m is None:
        mat = np.matrix([
            [1, 0],
            [0, 1],
        ])
    else:
        mat = np.matrix([
            [1,      0],
            [-1/f_m, 1],
        ])
    if not dL:
        return mat
    return matrix_space(dL) * mat * matrix_space(-dL)


def matrix_telescope(L1, R, dL = 0):
    L2 = R * L1
    mat = matrix_focus(-L2) * matrix_space(L1 - L2 - dL) * matrix_focus(L1)
    return mat


def eigen_q(mat):
    pe_A = mat[0, 0]
    pe_B = mat[0, 1]
    pe_C = mat[1, 0]
    pe_D = mat[1, 1]
    q = Complex((pe_A - pe_D)/(2 * pe_C), np.sqrt(-((pe_D-pe_A)**2 + 4 * pe_B * pe_C))/(2 * abs(pe_C)))
    return q


def targets_map_append(targets_map, tname, *targets):
    tlstlst = targets_map.get(tname, None)
    if tlstlst is None:
        tlstlst = []
        targets_map[tname] = tlstlst
    if targets:
        tlstlst.extend(targets)
    return tlstlst


def targets_map_fill(
        targets_map,
        subcomp,
        subidx,
        name = None,
):
    for target, t_idx_lst_lst in list(subcomp.targets_map.items()):
        tname_list = [target]
        if name is not None:
            tname_list.append("{0}.{1}".format(name, target))
        for tname in tname_list:
            tlstlst = targets_map_append(
                targets_map,
                tname,
            )
            for t_idx_lst in t_idx_lst_lst:
                tlstlst.append(TargetIdx(t_idx_lst + (subidx,)))
    return


def unit_str(val, unit, d=3, use_c = False):
    val = float(val)
    v = abs(val)
    if v > 1e3:
        prefix = 'k'
        div = 1e3
    elif v > 1:
        prefix = ''
        div = 1
    elif v > 1e-2 and use_c:
        prefix = 'c'
        div = 1e2
    elif v > 1e-3:
        prefix = 'm'
        div = 1e-3
    elif v > 1e-6:
        prefix = u'μ'
        div = 1e-6
    elif v > 1e-9:
        prefix = 'n'
        div = 1e-9
    elif v > 1e-15:
        prefix = 'f'
        div = 1e-15
    elif v > 1e-18:
        prefix = 'a'
        div = 1e-18
    elif v > 1e-21:
        prefix = 'z'
        div = 1e-21
    elif v == 0:
        div = 1
        prefix = ''
    nval = val / div
    if nval > 100:
        d -= 2
    elif nval > 10:
        d -= 1
    if d < 0:
        d = 0
    return u"{0:.{1}f}{2}{3}".format(val/div, d, prefix, unit)


def str_m(val, d=1, use_c = False):
    return unit_str(val, d=d, unit = 'm', use_c = use_c)
