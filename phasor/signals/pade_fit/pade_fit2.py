# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from collections import defaultdict
import declarative

import numpy as np
import scipy
import scipy.linalg


def fit_pz(
    F_Hz,
    data,
    W = 1,
    W_a = None,
    npoles = None,
    nzeros = None,
    ZPK    = ((), (), 1),
    F_nyquist = None,
    max_size  = None,
    ms_method = 'sum',
    compute_residuals = True,
):
    retB = fit_poles_mod_zeros(
        F_Hz      = F_Hz,
        data      = data,
        W         = W,
        W_a       = W_a,
        npoles    = npoles,
        nzeros    = nzeros,
        ZPK       = ZPK,
        F_nyquist = F_nyquist,
        max_size  = max_size,
        ms_method = ms_method,
    )
    #print(retB.ZPK)
    retB = fit_zeros(
        F_Hz      = F_Hz,
        data      = data,
        W         = W,
        #npoles    = npoles,
        nzeros    = nzeros,
        F_nyquist = F_nyquist,
        ZPK       = retB.ZPK,
        compute_residuals = compute_residuals,
    )
    retB.npoles = npoles
    retB.nzeros = nzeros
    return retB

def fit_series(
    F_Hz,
    data,
    W = 1,
    W_a = None,
    npoles = None,
    nzeros = None,
    ZPK    = ((), (), 1),
    F_nyquist = None,
    max_size  = None,
    ms_method = 'sum',
    npoles_min = 1,
):
    fits = []
    for npoles_try in range(npoles_min, npoles + 1):
        fits.append(
            fit_pz(
                F_Hz      = F_Hz,
                data      = data,
                W         = W,
                W_a       = W_a,
                npoles = npoles_try,
                nzeros    = nzeros,
                ZPK       = ZPK,
                F_nyquist = F_nyquist,
                max_size  = max_size,
                ms_method = ms_method,
                compute_residuals = True,
            )
        )
    fits.sort(key = lambda rB: rB.res)
    return fits


def fit_poles_mod_zeros_svd(
        F_Hz,
        data,
        W = 1,
        W_a = None,
        npoles = None,
        nzeros = None,
        ZPK    = ((), (), 1),
        F_nyquist = None,
        max_size  = None,
        ms_method = 'sum',
):
    zeros_init, poles_init, gain_init = ZPK

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

    bsize = (len(data_bal) + interlacer - 1) // interlacer
    #print(len(data_bal), bsize, len(data_bal) % interlacer)

    if F_nyquist is not None:
        Z = np.exp(1j * np.pi * F_use / F_nyquist)
    else:
        Z = 1j * np.pi * F_use

    order_a = npoles + 1
    order_b = nzeros + 1

    #Z_a_full = np.vstack([Z**j for j in range(bsize)]).T
    Z_b_full = np.vstack([Z**j for j in range(bsize)]).T
    Z_a = np.vstack([Z**j for j in range(order_a)]).T

    M_b = np.einsum('ij,i->ij', Z_b_full,  W_a_bal)
    M_a = np.einsum('ij,i->ij', Z_a,  W_a_bal * data_bal)

    #ZZ = np.einsum('ij,jk->ik',  np.linalg.pinv(M_b[:, order_b_try:len(F_use)]), M_a[:, :order_a_try])
    if ms_method == 'sum':
        ZZ = np.zeros([bsize - 1 - order_b, order_a], dtype = complex)
    else:
        stack = []
    for jj in range(interlacer):
        q, r = np.linalg.qr(M_b[jj::interlacer, :bsize - 1])
        ZZsub = np.einsum(
            'ij,jk->ik',
            q[::, order_b:].T.conjugate(),
            #np.linalg.pinv(M_b[jj::interlacer, :bsize - 1]),
            M_a[jj::interlacer, :order_a]
        )
        if ms_method == 'sum':
            ZZ += ZZsub
        else:
            stack.append(ZZsub)
    if ms_method == 'stack':
        ZZ = np.vstack(stack)

    U, S, V = scipy.linalg.svd(ZZ)
    a_fit = V.T[:, -1].real

    #stabilize
    roots = []
    for R in np.roots(a_fit):
        if abs(R) > 1:
            R = 1/R
        roots.append(R)
    gain = a_fit[0]

    retB = declarative.Bunch(
        ZPK         = (zeros_init, roots, gain),
        data        = data_bal,
        F_bal       = F_use,
        W_bal       = W_bal,
        F_nyquist   = F_nyquist,
    )

    return retB

def fit_poles_mod_zeros(
        F_Hz,
        data,
        W = 1,
        W_a = None,
        npoles = None,
        nzeros = None,
        ZPK    = ((), (), 1),
        F_nyquist = None,
        max_size  = None,
):
    zeros_init, poles_init, gain_init = ZPK

    F_use    = np.concatenate([-F_Hz[::-1], F_Hz])
    data_bal = np.concatenate([data[::-1].conjugate(), data])
    W_bal    = W * np.ones_like(data)
    W_bal    = np.concatenate([W_bal[::-1].real, W_bal.real])

    if W_a is None:
        W_a_bal = W_bal
    else:
        W_a_bal = W_a * np.ones_like(data)
        W_a_bal = np.concatenate([W_a_bal[::-1].real, W_a_bal.real])

    if F_nyquist is not None:
        Z = np.exp(1j * np.pi * F_use / F_nyquist)
    else:
        Z = 1j * np.pi * F_use

    order_a = npoles + 1
    order_b = nzeros + 1

    Z_b = np.vstack([Z**j for j in range(order_b)]).T
    Z_a = np.vstack([Z**j for j in range(order_a)]).T

    M_b = np.einsum('ij,i->ij', Z_b,  W_a_bal)
    q, r = np.linalg.qr(M_b)
    print(q.shape)

    #Z_b = np.vstack([Z**j for j in range(1 + len(zeros_init))]).T
    #bvec = np.polynomial.polynomial.polyfromroots(zeros_init)
    #bh = np.einsum('ij,j->i', Z_a,  bvec)
    bh = np.polynomial.polynomial.polyvalfromroots(Z, zeros_init)

    #greatly deweights data with low SNR
    W_bal_corrected = W_bal# * (1/(1 + W_bal**2))
    W_bal_remapped = W_bal_corrected - np.einsum('ij,j->i', q, np.einsum('ij,i->j', q.conjugate(), W_bal_corrected))

    R_a = np.einsum('ij,i->ij', Z_a,  W_bal_corrected * data_bal / bh)
    R_a = R_a - np.einsum('ij,jk->ik', q, np.einsum('ij,ik->jk', q.conjugate(), R_a))
    #print(R_b.shape)
    a_fit, res, rank, s = scipy.linalg.lstsq(R_a, W_bal_remapped)
    a_fit = a_fit.real
    gain = 1/a_fit[0]

    #stabilize
    roots = []
    for R in np.roots(a_fit):
        if abs(R) > 1:
            R = 1/R
        roots.append(R)
    gain = a_fit[0]

    retB = declarative.Bunch(
        ZPK         = (zeros_init, roots, gain),
        data        = data_bal,
        F_bal       = F_use,
        W_bal       = W_bal,
        F_nyquist   = F_nyquist,
    )

    return retB

def fit_poles(
    npoles,
    F_Hz,
    data,
    W = 1,
    F_nyquist = None,
    ZPK = ((), (), 1),
    compute_residuals = True,
):
    zeros_init, poles_init, gain_init = ZPK

    F_use = np.concatenate([-F_Hz[::-1], F_Hz])
    data_bal = np.concatenate([data[::-1].conjugate(), data])
    W_bal = W * np.ones_like(data)
    W_bal = np.concatenate([W_bal[::-1].real, W_bal.real])

    if F_nyquist is not None:
        Z = np.exp(-1j * np.pi * F_use / F_nyquist)
    else:
        Z = 1j * np.pi * F_use

    Z_a = np.vstack([Z**j for j in range(npoles + 1)]).T

    #Z_b = np.vstack([Z**j for j in range(1 + len(zeros_init))]).T
    #bvec = np.polynomial.polynomial.polyfromroots(zeros_init)
    #bh = np.einsum('ij,j->i', Z_a,  bvec)
    bh = np.polynomial.polynomial.polyvalfromroots(Z, zeros_init)

    #greatly deweights data with low SNR
    W_bal_corrected = W_bal * (1/(1 + W_bal**2))
    R_a = np.einsum('ij,i->ij', Z_a,  W_bal_corrected * data_bal / bh)
    #print(R_b.shape)
    a_fit, res, rank, s = scipy.linalg.lstsq(R_a, W_bal_corrected)
    a_fit = a_fit.real
    gain = 1/a_fit[0]
    poles = np.polynomial.polyroots(a_fit)

    retB = declarative.Bunch(
        ZPK         = (zeros_init, poles, gain),
        data        = data_bal,
        F_bal       = F_use,
        W_bal       = W_bal,
        F_nyquist   = F_nyquist,
    )

    if compute_residuals:
        ah = np.polynomial.polynomial.polyval(Z, a_fit)
        abh = bh / ah
        retB.data_fit    = abh
        debias_reweight = 1/(.001 + W_bal**2)
        retB.resA = W_bal * (abh/data_bal - 1)
        retB.resB = W_bal * (data_bal/abh - 1) * debias_reweight
        retB.res = np.sum((abs(retB.resA)**2 + abs(retB.resB)**2) / (1 + debias_reweight)) / (2 * len(data_bal))
    return retB


def fit_zeros(
    F_Hz,
    data,
    nzeros,
    W = 1,
    F_nyquist = None,
    ZPK = ((), (), 1),
    compute_residuals = True,
):
    zeros_init, poles_init, gain_init = ZPK

    F_use = np.concatenate([-F_Hz[::-1], F_Hz])
    data_bal = np.concatenate([data[::-1].conjugate(), data])
    W_bal = W * np.ones_like(data)
    W_bal = np.concatenate([W_bal[::-1].real, W_bal.real])

    if F_nyquist is not None:
        Z = np.exp(1j * np.pi * F_use / F_nyquist)
    else:
        Z = 1j * np.pi * F_use

    Z_b = np.vstack([Z**j for j in range(nzeros + 1)]).T

    #Z_a = np.vstack([Z**j for j in range(1 + len(poles_init))]).T
    #avec = np.polynomial.polynomial.polyfromroots(poles_init)
    #ah = np.einsum('ij,j->i', Z_a,  avec)
    ah = np.polynomial.polynomial.polyvalfromroots(Z, poles_init)

    #greatly deweights data with low SNR
    W_bal_corrected = W_bal * (W_bal**2/(1 + W_bal**2))
    #W_bal_corrected = W_bal
    R_b = np.einsum('ij,i->ij', Z_b,  W_bal_corrected / data_bal / ah)
    #print(R_b.shape)
    b_fit, res, rank, s = scipy.linalg.lstsq(R_b, W_bal_corrected)
    b_fit = b_fit.real
    gain = b_fit[0]
    zeros = np.polynomial.polynomial.polyroots(b_fit)

    retB = declarative.Bunch(
        ZPK         = (zeros, poles_init, gain),
        data        = data_bal,
        F_bal       = F_use,
        W_bal       = W_bal,
        F_nyquist   = F_nyquist,
    )

    if compute_residuals:
        bh = np.einsum('ij,j->i', Z_b,  b_fit)
        abh = bh / ah
        retB.data_fit    = abh
        debias_reweight = 1/(.001 + W_bal**2)
        retB.resA = W_bal * (abh/data_bal - 1)
        retB.resB = W_bal * (data_bal/abh - 1) * debias_reweight
        retB.res = np.sum((abs(retB.resA)**2 + abs(retB.resB)**2) / (1 + debias_reweight)) / (2 * len(data_bal))
    return retB

