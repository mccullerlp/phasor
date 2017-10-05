# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from collections import defaultdict
#import declarative

import numpy as np
import scipy
import scipy.linalg


def ratsvd(
        F_Hz,
        data,
        W = 1,
        F_nyquist = None,
        order_a   = None,
        order_b   = None,
        max_size  = None,
        ms_method = 'sum',
        aorder_min = None,
):
    assert(ms_method in ['stack', 'sum'])
    F_use = np.concatenate([F_Hz, -F_Hz])
    data_bal = np.concatenate([data, data.conjugate()])
    W_bal = W * np.ones_like(data)
    W_bal = np.concatenate([W_bal.real, W_bal.real])

    if max_size is None:
        interlacer = 1
    else:
        interlacer = len(data_bal) // max_size

    if order_a is None:
        order_a = 10
    if order_b is None:
        order_b = 10

    bsize = (len(data_bal) + interlacer - 1) // interlacer
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
    for i in range(2, order_a):
        order_a_try = i
        order_b_try = i
        #Z_a = np.vstack([Z**j for j in range(order_a_try)]).T
        Z_b = np.vstack([Z**j for j in range(order_b_try)]).T
        Z_a = np.vstack([Z**j for j in range(order_a_try)]).T

        M_b = np.einsum('ij,i->ij', Z_b_full,  W_bal)
        M_a = np.einsum('ij,i->ij', Z_a,  W_bal * data_bal)
        #M_b = np.einsum('ij,i->ij', Z_b_full, (1/F_exact))
        #M_a = np.einsum('ij,i->ij', Z_a, ones_like(F_exact))

        #type-1
        if order_a_try != 1:
            #ZZ = np.einsum('ij,jk->ik',  np.linalg.pinv(M_b[:, order_b_try:len(F_use)]), M_a[:, :order_a_try])
            if ms_method == 'sum':
                ZZ = np.zeros([bsize_prime - order_b_try, order_a_try], dtype = complex)
            else:
                stack = []
            for jj in range(interlacer):
                q, r = np.linalg.qr(M_b[jj::interlacer, :bsize], mode = 'complete')
                ZZsub = np.einsum(
                    'ij,jk->ik',
                    q[::, order_b_try:].T.conjugate(),
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
        if F_nyquist is not None:
            w, ah = scipy.signal.freqz(a_fit, [1], worN = F_use / F_nyquist * np.pi)
        else:
            w, ah = scipy.signal.freqs(a_fit, [1], worN = F_use * 2 * np.pi)
        R_b = np.einsum('ij,i->ij', Z_b,  W_bal / data_bal / ah)
        #print(R_b.shape)
        b_fit, res, rank, s = scipy.linalg.lstsq(R_b, W_bal * np.ones_like(data_bal))
        #b_fit = [1]
        #print(b_fit)
        if F_nyquist is not None:
            w, abh = scipy.signal.freqz(b_fit, a_fit, worN = F_use / F_nyquist * np.pi)
        else:
            w, abh = scipy.signal.freqs(b_fit, a_fit, worN = F_use * 2 * np.pi)
        res = np.sum(abs(W_bal * (abh/data_bal - 1))**2 + abs(W_bal * (data_bal/abh - 1))**2) / (2 * len(data_bal))
        type1 = (res, b_fit, a_fit, order_b_try, order_a_try, F_rescale)

        fits.append(type1)
    fits.sort(key = lambda v : v[0])
    return fits


