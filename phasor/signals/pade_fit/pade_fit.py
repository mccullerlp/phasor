# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from collections import defaultdict
import declarative

import numpy as np
import scipy
import scipy.linalg


def ratsvd(
        F_Hz,
        data,
        W = 1,
        W_a = None,
        F_nyquist = None,
        order_a   = None,
        order_b   = None,
        max_size  = None,
        ms_method = 'sum',
        aorder_min = None,
        order_a_min = 2,
        order_b_use = None,
):
    assert(ms_method in ['stack', 'sum'])
    F_use = np.concatenate([-F_Hz[::-1], F_Hz])
    data_bal = np.concatenate([data[::-1].conjugate(), data])
    W_bal = W * np.ones_like(data)
    W_bal = np.concatenate([W_bal[::-1].real, W_bal.real])

    if W_a is None:
        W_a_bal = W_bal
    else:
        W_a_bal = W_a * np.ones_like(data)
        W_a_bal = np.concatenate([W_a_bal[::-1].real, W_a_bal.real])

    if max_size is None:
        interlacer = 1
    else:
        interlacer = len(data_bal) // max_size

    if order_a is None:
        order_a = 10
    if order_b is None:
        order_b = 10

    bsize = (len(data_bal) + interlacer - 1) // interlacer
    print(len(data_bal), bsize, len(data_bal) % interlacer)
    bsize_prime = bsize
    if aorder_min is not None:
        bsize = max(bsize, aorder_min)

    if F_nyquist is not None:
        F_rescale = F_nyquist
        Z = np.exp(-1j * np.pi * F_use / F_nyquist)
    else:
        F_rescale = max(F_use) / 2
        F_use = F_use / F_rescale
        Z = 1j * np.pi * F_use
    #Z_a_full = np.vstack([Z**j for j in range(bsize)]).T
    Z_b_full = np.vstack([Z**j for j in range(bsize)]).T

    fits = []

    for i in range(order_a_min, order_a):
        order_a_try = i
        order_b_try = order_b
        if order_b_use is not None:
            Z_b = np.vstack([Z**j for j in range(order_b_use)]).T
        else:
            Z_b = np.vstack([Z**j for j in range(order_b_try)]).T
        Z_a = np.vstack([Z**j for j in range(order_a_try)]).T

        M_b = np.einsum('ij,i->ij', Z_b_full,  W_a_bal)
        M_a = np.einsum('ij,i->ij', Z_a,  W_a_bal * data_bal)

        #type-1
        if order_a_try != 1:
            #ZZ = np.einsum('ij,jk->ik',  np.linalg.pinv(M_b[:, order_b_try:len(F_use)]), M_a[:, :order_a_try])
            if ms_method == 'sum':
                ZZ = np.zeros([bsize_prime - 1 - order_b_try, order_a_try], dtype = complex)
            else:
                stack = []
            for jj in range(interlacer):
                q, r = np.linalg.qr(M_b[jj::interlacer, :bsize - 1])
                ZZsub = np.einsum(
                    'ij,jk->ik',
                    q[::, order_b_try:].T.conjugate(),
                    #np.linalg.pinv(M_b[jj::interlacer, :bsize - 1]),
                    M_a[jj::interlacer, :order_a_try]
                )
                if ms_method == 'sum':
                    ZZ += ZZsub
                else:
                    stack.append(ZZsub)
            if ms_method == 'stack':
                ZZ = np.vstack(stack)

            U, S, V = scipy.linalg.svd(ZZ)
            a_fit = V.T[:order_a_try, -1].real
        else:
            a_fit = np.array([1])

        #restabalize
        roots = []
        prev_len = len(a_fit)
        for R in np.roots(a_fit):
            if abs(R) > 1:
                R = 1/R
            roots.append(R)
        a_fit = np.poly(roots)
        if len(a_fit) < prev_len:
            a_fit = np.concatenate([a_fit, [0]*(prev_len - len(a_fit))])

        ah = np.einsum('ij,j->i', Z_a,  a_fit)
        R_b = np.einsum('ij,i->ij', Z_b,  W_bal / data_bal / ah)
        #print(R_b.shape)
        b_fit, res, rank, s = scipy.linalg.lstsq(R_b, W_bal)
        b_fit = b_fit.real
        roots = []
        #for R in np.roots(b_fit):
        #    if abs(R) > 1:
        #        R = 1/R
        #    roots.append(R)
        #b_fit = np.poly(roots)

        bh = np.einsum('ij,j->i', Z_b,  b_fit)
        abh = bh / ah
        debias_reweight = 1/(.001 + W_bal**2)
        resA = W_bal * (abh/data_bal - 1)
        resB = W_bal * (data_bal/abh - 1) * debias_reweight
        res = np.sum(abs(resA)**2 + abs(resB)**2) / (2 * len(data_bal))
        type1_results = declarative.Bunch(
            residuals   = res,
            a_fit       = a_fit,
            b_fit       = b_fit,
            data_fit    = abh,
            data        = data_bal,
            F_bal       = F_use,
            resA        = resA,
            resB        = resB,
            order_b     = order_b_try,
            order_a     = order_a_try,
            F_rescale   = F_rescale,
            W_bal       = W_bal,
            F_nyquist   = F_nyquist,
        )

        if np.isfinite(res):
            fits.append(type1_results)
    fits.sort(key = lambda v : v.residuals)
    return fits


