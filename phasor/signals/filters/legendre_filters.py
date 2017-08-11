# -*- coding: utf-8 -*-
"""
from https://gist.github.com/endolith/c80f9e6bf3b407c2f567

Created on Mon Jul 14 22:54:48 2014

References:
odd-order: Papoulis A., “Optimum Filters with Monotonic Response,”
            Proc. IRE, 46, No. 3, March 1958, pp. 606-609
even-order: Papoulis A., ”On Monotonic Response Filters,” Proc. IRE, 47,
            No. 2, Feb. 1959, 332-333 (correspondence section)
Bond C., Optimum “L” Filters: Polynomials, Poles and Circuit Elements, 2004
Bond C., Notes on “L” (Optimal) Filters, 2011
"""

from __future__ import division, print_function
import numpy as np
from numpy import polynomial
from numpy.polynomial import Polynomial as P
from numpy import asarray
from fractions import Fraction as F

try:
    from mpmath import mp
    mpmath_available = True
except ImportError:
    mpmath_available = False


def optimum_poly(N):
    """
    Output "optimum" L_n(ω) polynomial coefficients as a list of
    arbitrary-precision integers

    Example:
    optimum_poly(5)
    Out[141]: [20, 0, -40, 0, 28, 0, -8, 0, 1, 0, 0]

    This means L_5(ω) = 20ω^10 - 40ω^8 + 28ω^6 - 8ω^4 + ω^2

    Listed in https://oeis.org/A245320

    for N in range(12):
        print(', '.join(str(x) for x in optimum_poly(N)[::-2]))

    """
    # Legendre polynomial coefficients are rational, and "optimum" polynomial
    # coefficients are integers, so we use Fraction objects throughout to get
    # exact results. There is probably a more direct way using integers, but
    # this at least matches the procedure described in the papers.

    if N == 0:
        # Results in a 0-order "do-nothing" filter: H(s) = 1/(1 + 0) = 1
        return np.array([0])

    if N % 2:  # odd N
        k = (N - 1)//2
        a = np.arange(1, 2*(k + 1) + 1, 2)
        # a0 = 1, a1 = 3, a2 = 5, ...
        # denominator sqrt(2)(k+1) has been pulled outside the square
    else:  # even N
        k = (N - 2)//2
        a = np.arange(1, 2*(k + 1) + 1, 2)
        # a0 = 1, a1 = 3, a2 = 5, ...
        # denominator sqrt((k+1)(k+2)) has been pulled outside the square
        if k % 2:  # odd k
            # a0 = a2 = a4 = ··· = 0
            a[::2] = 0
        else:  # even k
            # a1 = a3 = a5 = ··· = 0
            a[1::2] = 0

    # Use Fraction objects to generate exact sum of Legendre polynomials
    a = [F(i) for i in a]
    domain = [F(-1), F(1)]
    v = polynomial.Legendre(a, domain)  # v(x) = a0 + a1P1(x) + ... + akPk(x)

    # Convert from sum of Legendre polynomials to power series polynomial
    v = v.convert(domain, polynomial.Polynomial)

    # Square and bring out squared denominators of a_n
    if N % 2:  # odd N
        # sum(a_n * P_n(x))**2
        integrand = v**2 / (2*(k + 1)**2)
    else:  # even N
        # (x + 1) * sum(a_n * P_n(x))**2
        integrand = P([F(1), F(1)]) * v**2 / ((k + 1) * (k + 2))

    # Integrate (using fractions; indefint.integ() returns floats)
    indefint = P(polynomial.polynomial.polyint(integrand.coef), domain)

    # Evaluate integral from -1 to 2*omega**2 - 1
    defint = indefint(P([F(-1), F(0), F(2)])) - indefint(-1)

    # Fractions have been cancelled; outputs are all integers
    # Return in order of decreasing powers of omega
    return [int(x) for x in defint.coef[::-1]]


def _roots(a):
    """
    Find the roots of a polynomial, using mpmath.polyroots if available,
    or numpy.roots if not
    """

    N = (len(a) - 1)//2  # Order of the filter

    if mpmath_available:
        # Overkill: "The user may have to manually set the working precision
        # higher than the desired accuracy for the result, possibly much
        # higher."
        mp.dps = 150
        """
        TODO: How many digits are necessary for float equivalence?  Does it
        vary with order?
        """
        p, err = mp.polyroots(a, maxsteps=1000, error=True)
        if err > 1e-32:
            raise ValueError("Legendre filter cannot be accurately computed "
                             "for order %s" % N)
        p = asarray(p).astype(complex)
    else:
        p = np.roots(a)
        if N > 25:
            # Bessel and Legendre filters seem to fail above N = 25
            raise ValueError("Legendre filter cannot be accurately computed "
                             "for order %s" % N)
    return p


def legendreap(N):
    """
    Return (z,p,k) zero, pole, gain for analog prototype of an Nth-order
    "Optimum L", or Legendre-Papoulis filter.

    This filter is optimized for the maximum possible cut-off slope while
    still having a monotonic passband.

    The filter is normalized for an angular (e.g. rad/s) cutoff frequency of 1.
    """
    # Magnitude squared function is M^2(w) = 1 / (1 + L_n(w^2))
    a = optimum_poly(N)
    a[-1] = 1

    # Substitute s = jw --> -s^2 = w^2 to get H(s^2)
    # = step backward through polynomial and negate powers 2, 6, 10, 14, ...
    a[-3::-4] = [-x for x in a[-3::-4]]

    z = []

    # Find poles of transfer function
    p = _roots(a)

    # Throw away right-hand side poles to produce Hurwitz polynomial H(s)
    p = p[p.real < 0]

    # Normalize for unity gain at DC
    k = float(np.prod(np.abs(p)))

    return asarray(z), asarray(p), k


def tests():
    from numpy.testing import (assert_array_equal, assert_array_almost_equal,
                               assert_raises)
    from sos_stuff import cplxreal

    global mpmath_available

    mpmath_available = False
    assert_raises(ValueError, legendreap, 26)

    for mpmath_available in False, True:
        bond_appendix = [
            [0, 1],
            [0, 0, 1],
            [0, 1, -3, 3],
            [0, 0, 3, -8, 6],
            [0, 1, -8, 28, -40, 20],
            [0, 0, 6, -40, 105, -120, 50],
            [0, 1, -15, 105, -355, 615, -525, 175],
            [0, 0, 10, -120, 615, -1624, 2310, -1680, 490],
            [0, 1, -24, 276, -1624, 5376, -10416, 11704, -7056, 1764],
            [0, 0, 15, -280, 2310, -10416, 27860, -45360, 44100, -23520, 5292]
            ]

        for N in range(10):
            assert_array_equal(bond_appendix[N], optimum_poly(N+1)[::-2])
            assert_array_equal(0, optimum_poly(N)[1::2])

        # papoulis example
        b = [0.577]
        a = [1, 1.310, 1.359, 0.577]

        b2, a2 = zpk2tf(*legendreap(3))

        assert_array_almost_equal(b, b2, decimal=3)
        assert_array_almost_equal(a, a2, decimal=3)

        b = [0.224]
        a = [1, 1.55, 2.203, 1.693, 0.898, 0.224]

        b2, a2 = zpk2tf(*legendreap(5))

        assert_array_almost_equal(b, b2, decimal=3)
        assert_array_almost_equal(a, a2, decimal=2)

        bond_poles = [
            [-1.0000000000],
            [-0.7071067812 + 0.7071067812j],
            [-0.3451856190 + 0.9008656355j, -0.6203318171],
            [-0.2316887227 + 0.9455106639j, -0.5497434238 + 0.3585718162j],
            [-0.1535867376 + 0.9681464078j, -0.3881398518 + 0.5886323381j,
             -0.4680898756],
            [-0.1151926790 + 0.9779222345j, -0.3089608853 + 0.6981674628j,
             -0.4389015496 + 0.2399813521j],
            [-0.0862085483 + 0.9843698067j, -0.2374397572 + 0.7783008922j,
             -0.3492317849 + 0.4289961167j, -0.3821033151],
            [-0.0689421576 + 0.9879709681j, -0.1942758813 + 0.8247667245j,
             -0.3002840049 + 0.5410422454j, -0.3671763101 + 0.1808791995j],
            [-0.0550971566 + 0.9906603253j, -0.1572837690 + 0.8613428506j,
             -0.2485528957 + 0.6338196200j, -0.3093854331 + 0.3365432371j,
             -0.3256878224],
            [-0.0459009826 + 0.9923831857j, -0.1325187825 + 0.8852617693j,
             -0.2141729915 + 0.6945377067j, -0.2774054135 + 0.4396461638j,
             -0.3172064580 + 0.1454302513j]
            ]

        for N in range(10):
            p1 = np.sort(bond_poles[N])
            p2 = np.sort(np.concatenate(cplxreal(legendreap(N+1)[1])))
            assert_array_almost_equal(p1, p2, decimal=10)


if __name__ == "__main__":
    from scipy.signal import freqs, zpk2tf, buttap
    import matplotlib.pyplot as plt

    N = 10

    plt.figure()
    plt.suptitle('{}-order Optimum L filter vs Butterworth'.format(N))

    for prototype, lstyle in ((buttap, 'k:'), (legendreap, 'b-')):
        z, p, k = prototype(N)
        b, a = zpk2tf(z, p, k)
        w, h = freqs(b, a, np.logspace(-1, 1, 1000))

        plt.subplot(2, 1, 1)
        plt.semilogx(w, 20*np.log10(h), lstyle)

        plt.subplot(2, 1, 2)
        plt.semilogx(w, abs(h), lstyle)

    plt.subplot(2, 1, 1)
    plt.ylim(-150, 10)
    plt.ylabel('dB')

    plt.grid(True, color='0.7', linestyle='-', which='major')
    plt.grid(True, color='0.9', linestyle='-', which='minor')

    plt.subplot(2, 1, 2)
    plt.ylim(-.1, 1.1)
    plt.ylabel('$|H(s)|$')

    plt.grid(True, color='0.7', linestyle='-', which='major')
    plt.grid(True, color='0.9', linestyle='-', which='minor')
