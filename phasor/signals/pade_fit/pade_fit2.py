# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from collections import defaultdict
import declarative

import numpy as np
import scipy
import scipy.linalg


def ZPKarray(ZPK):
    Z, P, K = ZPK
    Z = np.asarray(Z)
    P = np.asarray(P)
    return Z, P, K


def XpolyZPK(F_use, F_nyquist, ZPK):
    ZPK = ZPKarray(ZPK)
    if F_nyquist is not None:
        X = np.exp(1j * np.pi * F_use / F_nyquist)

        def root_transform(ZPK, stabilize = False):
            Z, P, K = ZPK
            if stabilize:
                select = (abs(P) > 0)
                P[select] = 1 / P[select].conjugate()
            return Z, P, K

        def coeffclean(c):
            c.imag = 0

        poly = declarative.Bunch()
        poly.root_transform  = root_transform
        poly.valfromroots    = np.polynomial.polynomial.polyvalfromroots
        poly.roots           = np.polynomial.polynomial.polyroots
        poly.fromroots       = np.polynomial.polynomial.polyfromroots
        poly.val             = np.polynomial.polynomial.polyval
        poly.fit             = np.polynomial.polynomial.polyfit
        poly.vander          = np.polynomial.polynomial.polyvander
        poly.coeffclean      = coeffclean
        return X, poly, ZPK
    else:
        F_max = abs(np.max(F_use))

        Z, P, K = ZPK
        trans = -1j / (F_max * 2 * np.pi)
        Z = trans * Z
        P = trans * P
        ZPKtrans = Z, P, K

        def root_transform(ZPK, stabilize = False):
            ZPK = ZPKarray(ZPK)
            Z, P, K = ZPK
            #rescale from 0-1 on REAL line to the imaginary line
            trans = 2j * np.pi * F_max
            Z = trans * Z
            P = trans * P

            if stabilize:
                select = (P.real > 0)
                P.real[select] *= -1
            return Z, P, K

        X = F_use / F_max

        def chebvalfromroots(X, roots):
            c = np.polynomial.chebyshev.chebfromroots(roots)
            return np.polynomial.chebyshev.chebval(X, c)

        def coeffclean(c):
            if len(c) >= 2:
                c[::2].imag = 0
                c[1::2].real = 0
            elif len(c) == 1:
                c[::2].imag = 0
            return

        poly = declarative.Bunch()
        poly.root_transform  = root_transform
        poly.valfromroots    = chebvalfromroots
        poly.roots           = np.polynomial.chebyshev.chebroots
        poly.fromroots       = np.polynomial.chebyshev.chebfromroots
        poly.val             = np.polynomial.chebyshev.chebval
        poly.fit             = np.polynomial.chebyshev.chebfit
        poly.vander          = np.polynomial.chebyshev.chebvander
        poly.coeffclean      = coeffclean
        return X, poly, ZPKtrans


def fit_pzpz(
    F_Hz,
    data,
    W = 1,
    W_a = None,
    W_final = None,
    npoles = None,
    nzeros = None,
    ZPK    = ((), (), 1),
    F_nyquist = None,
    max_size  = None,
    compute_residuals = True,
    n_iter = 10,
):
    if W_final is None:
        W_final = W
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
    )
    retB = fit_zeros_mod_poles(
        F_Hz      = F_Hz,
        data      = data,
        W         = W,
        W_a       = W_a,
        npoles    = npoles,
        nzeros    = nzeros,
        ZPK       = retB.ZPK,
        F_nyquist = F_nyquist,
        max_size  = max_size,
    )
    for i in range(n_iter):
        retB = fit_poles(
            F_Hz      = F_Hz,
            data      = data,
            W         = W,
            npoles    = npoles,
            nzeros    = nzeros,
            F_nyquist = F_nyquist,
            ZPK       = retB.ZPK,
            compute_residuals = compute_residuals,
        )
        retB = fit_zeros(
            F_Hz      = F_Hz,
            data      = data,
            W         = W,
            npoles    = npoles,
            nzeros    = nzeros,
            F_nyquist = F_nyquist,
            ZPK       = retB.ZPK,
            compute_residuals = compute_residuals,
        )
        print(retB.res)
    retB = fit_poles(
        F_Hz      = F_Hz,
        data      = data,
        W         = W_final,
        npoles    = npoles,
        nzeros    = nzeros,
        F_nyquist = F_nyquist,
        ZPK       = retB.ZPK,
        compute_residuals = compute_residuals,
    )
    retB = fit_zeros(
        F_Hz      = F_Hz,
        data      = data,
        W         = W_final,
        npoles    = npoles,
        nzeros    = nzeros,
        F_nyquist = F_nyquist,
        ZPK       = retB.ZPK,
        compute_residuals = compute_residuals,
    )
    retB.npoles = npoles
    retB.nzeros = nzeros
    return retB

def fit_zpzp(
    F_Hz,
    data,
    W = 1,
    W_a = None,
    npoles = None,
    nzeros = None,
    ZPK    = ((), (), 1),
    F_nyquist = None,
    max_size  = None,
    compute_residuals = True,
    n_iter = 10,
):
    retB = fit_zeros_mod_poles(
        F_Hz      = F_Hz,
        data      = data,
        W         = W,
        W_a       = W_a,
        npoles    = npoles,
        nzeros    = nzeros,
        ZPK       = ZPK,
        F_nyquist = F_nyquist,
        max_size  = max_size,
    )
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
    )
    for i in range(n_iter):
        retB = fit_zeros(
            F_Hz      = F_Hz,
            data      = data,
            W         = W,
            npoles    = npoles,
            nzeros    = nzeros,
            F_nyquist = F_nyquist,
            ZPK       = retB.ZPK,
            compute_residuals = compute_residuals,
        )
        retB = fit_poles(
            F_Hz      = F_Hz,
            data      = data,
            W         = W,
            npoles    = npoles,
            nzeros    = nzeros,
            F_nyquist = F_nyquist,
            ZPK       = retB.ZPK,
            compute_residuals = compute_residuals,
        )
        print(retB.res)
    retB.npoles = npoles
    retB.nzeros = nzeros
    return retB

def fit_zp(
    F_Hz,
    data,
    W = 1,
    W_a = None,
    npoles = None,
    nzeros = None,
    ZPK    = ((), (), 1),
    F_nyquist = None,
    max_size  = None,
    compute_residuals = True,
):
    retB = fit_zeros_mod_poles(
        F_Hz      = F_Hz,
        data      = data,
        W         = W,
        W_a       = W_a,
        npoles    = npoles,
        nzeros    = nzeros,
        ZPK       = ZPK,
        F_nyquist = F_nyquist,
        max_size  = max_size,
    )
    #print(retB.ZPK)
    retB = fit_poles(
        F_Hz      = F_Hz,
        data      = data,
        W         = W,
        npoles    = npoles,
        #nzeros    = nzeros,
        F_nyquist = F_nyquist,
        ZPK       = retB.ZPK,
        compute_residuals = compute_residuals,
    )
    retB.npoles = npoles
    retB.nzeros = nzeros
    return retB

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
    )
    retB = fit_zeros(
        F_Hz      = F_Hz,
        data      = data,
        W         = W,
        npoles    = npoles,
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
    npoles_min = 1,
    func = fit_pz,
):
    fits = []
    for npoles_try in range(npoles_min, npoles + 1):
        fits.append(
            func(
                F_Hz      = F_Hz,
                data      = data,
                W         = W,
                W_a       = W_a,
                npoles = npoles_try,
                nzeros    = nzeros,
                ZPK       = ZPK,
                F_nyquist = F_nyquist,
                max_size  = max_size,
                compute_residuals = True,
            )
        )
    fits.sort(key = lambda rB: rB.res)
    return fits


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
    F_use    = np.concatenate([-F_Hz[::-1], F_Hz])
    data_bal = np.concatenate([data[::-1].conjugate(), data])
    W_bal    = W * np.ones_like(data)
    W_bal    = np.concatenate([W_bal[::-1].real, W_bal.real])

    if W_a is None:
        W_a_bal = W_bal
    else:
        W_a_bal = W_a * np.ones_like(data)
        W_a_bal = np.concatenate([W_a_bal[::-1].real, W_a_bal.real])

    X, poly, ZPK = XpolyZPK(F_use, F_nyquist, ZPK)
    zeros_init, poles_init, gain_init = ZPK

    X_b = poly.vander(X, nzeros + 1)
    X_a = poly.vander(X, npoles + 1)
    bh = poly.valfromroots(X, zeros_init)
    ah = poly.valfromroots(X, poles_init)

    R_b = np.einsum('ij,i->ij', X_b,  W_a_bal / (data_bal * ah))
    M_b = np.einsum('ij,i->ij', X_b,  W_a_bal)
    #remove the effect of phasing
    R_b = np.hstack([(1j*F_use).reshape(-1,1), R_b])
    q, r = np.linalg.qr(R_b)

    #greatly deweights data with low SNR
    W_bal_corrected = W_a_bal  # * (1/(1 + W_bal**2))
    #W_bal_remapped = W_bal_corrected - np.einsum('ij,j->i', q, np.einsum('ij,i->j', q.conjugate(), W_bal_corrected))

    R_a = np.einsum('ij,i->ij', X_a,  W_bal_corrected * data_bal / bh)
    R_a = R_a - np.einsum('ij,jk->ik', q, np.einsum('ij,ik->jk', q.conjugate(), R_a))
    #print(R_b.shape)
    #a_fit, res, rank, s = scipy.linalg.lstsq(R_a, W_bal_remapped)
    #print(order_a, rank, s)
    #poly.coeffclean(a_fit)

    U, S, V = scipy.linalg.svd(R_a)
    print("POLES SVD: ", S[-4:])
    a_fit = V.T[:, -1]
    poly.coeffclean(a_fit)

    gain = 1/a_fit[0]

    poles = poly.roots(a_fit)
    ZPK = poly.root_transform((zeros_init, poles, gain), stabilize = True)

    retB = declarative.Bunch(
        ZPK         = ZPK,
        data        = data_bal,
        F_bal       = F_use,
        W_bal       = W_bal,
        F_nyquist   = F_nyquist,
    )

    return retB


def fit_zeros_mod_poles(
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
    F_use    = np.concatenate([-F_Hz[::-1], F_Hz])
    data_bal = np.concatenate([data[::-1].conjugate(), data])
    W_bal    = W * np.ones_like(data)
    W_bal    = np.concatenate([W_bal[::-1].real, W_bal.real])

    if W_a is None:
        W_a_bal = W_bal
    else:
        W_a_bal = W_a * np.ones_like(data)
        W_a_bal = np.concatenate([W_a_bal[::-1].real, W_a_bal.real])

    X, poly, ZPK = XpolyZPK(F_use, F_nyquist, ZPK)
    zeros_init, poles_init, gain_init = ZPK

    X_b = poly.vander(X, nzeros + 1)
    X_a = poly.vander(X, npoles + 1)
    bh = poly.valfromroots(X, zeros_init)
    ah = poly.valfromroots(X, poles_init)

    R_a = np.einsum('ij,i->ij', X_a,  W_a_bal / (data_bal / bh))
    M_a = np.einsum('ij,i->ij', X_a,  W_a_bal)
    q, r = np.linalg.qr(R_a)

    #greatly deweights data with low SNR
    W_bal_corrected = W_bal  # * (W_bal**2/(1 + W_bal**2))
    #W_bal_remapped = W_bal_corrected - np.einsum('ij,j->i', q, np.einsum('ij,i->j', q.conjugate(), W_bal_corrected))

    R_b = np.einsum('ij,i->ij', X_b,  W_bal_corrected / data_bal / ah)
    R_b = R_b - np.einsum('ij,jk->ik', q, np.einsum('ij,ik->jk', q.conjugate(), R_b))
    #print(R_b.shape)
    #b_fit, res, rank, s = scipy.linalg.lstsq(R_b, W_bal_remapped)
    #print(order_a, rank, s)
    U, S, V = scipy.linalg.svd(R_b)
    print("ZEROS SVD: ", S[-4:])
    b_fit = V.T[:, -1]
    poly.coeffclean(b_fit)

    gain = 1/b_fit[0]

    zeros = poly.roots(b_fit)
    ZPK = poly.root_transform((zeros, poles_init, gain), stabilize = False)

    retB = declarative.Bunch(
        ZPK         = ZPK,
        data        = data_bal,
        F_bal       = F_use,
        W_bal       = W_bal,
        F_nyquist   = F_nyquist,
    )

    return retB

def fit_poles(
    F_Hz,
    data,
    npoles,
    W = 1,
    nzeros = None,
    F_nyquist = None,
    ZPK = ((), (), 1),
    compute_residuals = True,
    **kwargs
):
    F_use = np.concatenate([-F_Hz[::-1], F_Hz])
    data_bal = np.concatenate([data[::-1].conjugate(), data])
    W_bal = W * np.ones_like(data)
    W_bal = np.concatenate([W_bal[::-1].real, W_bal.real])

    X, poly, ZPK = XpolyZPK(F_use, F_nyquist, ZPK)
    zeros_init, poles_init, gain_init = ZPK

    X_a = poly.vander(X, npoles + 1)
    bh = poly.valfromroots(X, zeros_init)

    #greatly deweights data with low SNR
    W_bal_corrected = W_bal# * (1/(1 + W_bal**2))
    R_a = np.einsum('ij,i->ij', X_a,  W_bal_corrected * data_bal / bh)
    #print(R_b.shape)
    a_fit, res, rank, s = scipy.linalg.lstsq(R_a, W_bal_corrected)
    poly.coeffclean(a_fit)
    gain = 1/a_fit[0]
    poles = poly.roots(a_fit)

    retB = declarative.Bunch(
        ZPK         = poly.root_transform((zeros_init, poles, gain)),
        data        = data_bal,
        F_bal       = F_use,
        W_bal       = W_bal,
        F_nyquist   = F_nyquist,
    )

    if compute_residuals:
        ah = poly.val(X, a_fit)
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
    npoles = None,
    F_nyquist = None,
    ZPK = ((), (), 1),
    compute_residuals = True,
    **kwargs
):
    ZPK = ZPKarray(ZPK)
    F_use = np.concatenate([-F_Hz[::-1], F_Hz])
    data_bal = np.concatenate([data[::-1].conjugate(), data])
    W_bal = W * np.ones_like(data)
    W_bal = np.concatenate([W_bal[::-1].real, W_bal.real])

    X, poly, ZPK = XpolyZPK(F_use, F_nyquist, ZPK)
    zeros_init, poles_init, gain_init = ZPK

    X_b = poly.vander(X, nzeros + 1)
    ah = poly.valfromroots(X, poles_init)

    #greatly deweights data with low SNR
    W_bal_corrected = W_bal  #* (W_bal**2/(1 + W_bal**2))
    #W_bal_corrected = W_bal
    R_b = np.einsum('ij,i->ij', X_b,  W_bal_corrected / (data_bal * ah))
    #print(R_b.shape)
    b_fit, res, rank, s = scipy.linalg.lstsq(R_b, W_bal_corrected)
    poly.coeffclean(b_fit)
    gain = b_fit[0]
    zeros = poly.roots(b_fit)

    retB = declarative.Bunch(
        ZPK         = poly.root_transform((zeros, poles_init, gain)),
        data        = data_bal,
        F_bal       = F_use,
        W_bal       = W_bal,
        F_nyquist   = F_nyquist,
    )

    if compute_residuals:
        bh = poly.val(X, b_fit)
        abh = bh / ah
        retB.data_fit    = abh
        debias_reweight = 1/(.001 + W_bal**2)
        retB.resA = W_bal * (abh/data_bal - 1)
        retB.resB = W_bal * (data_bal/abh - 1) * debias_reweight
        retB.res = np.sum((abs(retB.resA)**2 + abs(retB.resB)**2) / (1 + debias_reweight)) / (2 * len(data_bal))
    return retB
