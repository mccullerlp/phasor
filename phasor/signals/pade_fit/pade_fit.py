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
        order_b   = None
):
    F_use = np.concatenate([F_Hz, -F_Hz])
    data_bal = np.concatenate([data, data.conjugate()])
    W_bal = W * np.ones_like(data)
    W_bal = np.concatenate([W_bal.real, W_bal.real])

    if F_nyquist is None:
        F_nyquist = np.max(F_Hz)

    if order_a is None:
        order_a = 10
    if order_b is None:
        order_b = 10

    Z = np.exp(-1j * np.pi * F_use / F_nyquist)
    Z_a_full = np.vstack([Z**j for j in range(len(F_use))]).T
    Z_b_full = np.vstack([Z**j for j in range(len(F_use))]).T

    fits = []
    for i in range(2, order_a):
        order_a_try = i
        order_b_try = i
        #Z_a = np.vstack([Z**j for j in range(order_a_try)]).T
        Z_b = np.vstack([Z**j for j in range(order_b_try)]).T

        M_b = np.einsum('ij,i->ij', Z_b_full,  W_bal)
        M_a = np.einsum('ij,i->ij', Z_a_full,  W_bal * data_bal)
        #M_b = np.einsum('ij,i->ij', Z_b_full, (1/F_exact))
        #M_a = np.einsum('ij,i->ij', Z_a, ones_like(F_exact))

        #type-1
        if order_a_try != 1:

            #ZZ = np.einsum('ij,jk->ik',  np.linalg.pinv(M_b[:, order_b_try:len(F_use)]), M_a[:, :order_a_try])
            q, r = np.linalg.qr(M_b[:])
            q = q
            ZZ = np.einsum('ij,jk->ik',  np.linalg.pinv(q[:, order_b_try:len(F_use)]), M_a[:, :order_a_try])

            U, S, V = scipy.linalg.svd(ZZ)
            a_fit = V.T[:order_a_try, -1]
        else:
            a_fit = np.array([1])
        w, ah = scipy.signal.freqz(a_fit, [1], worN = F_use / F_nyquist * np.pi)
        R_b = np.einsum('ij,i->ij', Z_b,  W_bal / data_bal / ah)
        #print(R_b.shape)
        b_fit, res, rank, s = scipy.linalg.lstsq(R_b, W_bal * np.ones_like(data_bal))
        #b_fit = [1]
        #print(b_fit)
        w, abh = scipy.signal.freqz(b_fit, a_fit, worN = F_use / F_nyquist * np.pi)
        res = np.sum(abs(W_bal * (abh/data_bal - 1))**2 + abs(W_bal * (data_bal/abh - 1))**2) / (2 * len(data_bal))
        type1 = (res, b_fit, a_fit, order_b_try, order_a_try, 'type1')
        type_use = type1
        print(res, np.roots(a_fit))

        ##type-2
        #if order_a_try != 1:
        #    ZZ = np.einsum('ij,jk->ik', np.linalg.pinv(M_a[:, :order_a_try]), M_b[:, order_b_try:])
        #    U, S, V = scipy.linalg.svd(ZZ)
        #    a_fit = (U.T[:order_a_try, -1])
        #else:
        #    a_fit = np.array([1])
        #    w, ah = scipy.signal.freqz(a_fit, [1], worN = F_use / F_nyquist * np.pi)
        #R_b = np.einsum('ij,i->ij', Z_b,  W_bal / data_bal / ah)
        ##print(R_b.shape)
        #b_fit, res, rank, s = scipy.linalg.lstsq(R_b, W * np.ones_like(data_bal))
        ##b_fit = [1]
        #w, abh = scipy.signal.freqz(b_fit, a_fit, worN = F_use / F_nyquist * np.pi)
        #res = np.sum(abs(W_bal * (abh/data_bal - 1))**2 + abs(W_bal * (data_bal/abh - 1))**2) / (2 * len(data_bal))
        #type2 = (res, b_fit, a_fit, order_b_try, order_a_try, 'type2')
        #print(res, np.roots(a_fit))

        #if type1[0] < type2[0]:
        #    type_use = type1
        #else:
        #    type_use = type2

        fits.append(type_use)
    fits.sort(key = lambda v : v[0])
    return fits


