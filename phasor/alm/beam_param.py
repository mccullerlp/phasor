# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from ..utilities.future_from_2 import object

import numpy as np
from ..math.complex import Complex
from ..math import dispatched as dmath
from .utils import str_m

class ComplexBeamParam(object):
    """
    All distances should be in the same units as the wavelength.
    """
    pi = np.pi
    ps_In = 1j
    complex = Complex
    nominal_wavelen = 1.064e-6
    gouy_phasor = 1

    def __init__(
            self,
            value,
            wavelen = None,
            gouy_phasor = None,
    ):
        self.value = self.complex(value)
        if wavelen is None:
            wavelen = self.nominal_wavelen
        if gouy_phasor is not None:
            self.gouy_phasor = gouy_phasor
        self.wavelen = wavelen

    @classmethod
    def from_Z_W0(
            cls,
            Z,
            W0,
            wavelen = None,
            gouy_phasor = None,
    ):
        if wavelen is None:
            wavelen = cls.nominal_wavelen
        ZR = cls.pi*W0**2/wavelen
        return cls(
            Z + cls.ps_In*ZR,
            wavelen = wavelen,
            gouy_phasor = gouy_phasor,
        )

    @classmethod
    def from_Z_ZR(
            cls,
            Z,
            ZR,
            wavelen = None,
            gouy_phasor = None,
    ):
        return cls(
            Z + cls.ps_In*ZR,
            wavelen = wavelen,
            gouy_phasor = gouy_phasor,
        )

    @classmethod
    def from_dRad_Z(
            cls,
            theta,
            Z,
            wavelen = None,
            gouy_phasor = None,
    ):
        if wavelen is None:
            wavelen = cls.nominal_wavelen
        W0 = 2 * wavelen / (cls.pi * theta)
        return cls.from_Z_W0(
            Z,
            W0,
            wavelen = wavelen,
            gouy_phasor = gouy_phasor,
        )

    @property
    def W0(self):
        ZR = dmath.im(self.value)
        return dmath.sqrt(self.wavelen * ZR / self.pi)

    @property
    def Z(self):
        return dmath.re(self.value)

    @property
    def ZR(self):
        return dmath.im(self.value)

    @property
    def W(self):
        return dmath.sqrt(-self.wavelen/(dmath.im(1/self.value) * self.pi))

    @property
    def R(self):
        return 1/(dmath.re(1/self.value))

    @property
    def R_inv(self):
        return (dmath.re(1/self.value))

    @property
    def divergence_rad(self):
        return 2 * self.wavelen / (self.pi * self.W0)

    @property
    def k(self):
        return 2 * self.pi / self.wavelen

    def propagate_matrix(self, abcd_mat):
        a = abcd_mat[0, 0]
        b = abcd_mat[0, 1]
        c = abcd_mat[1, 0]
        d = abcd_mat[1, 1]
        determinant = a*d - b*c

        tanPhiA = self.wavelen * b
        tanPhiB = (a + b*self.R_inv)*self.pi*self.W**2

        #gouy_rad = np.arctan2(tanPhiA, tanPhiB)
        return self.__class__(
            (self.value * a + b)/(self.value * c + d),
            wavelen = self.wavelen * determinant,
            gouy_phasor = self.gouy_phasor * (tanPhiB + tanPhiA*1j),
        )

    def propagate_distance(self, L_m):
        a = 1
        b = L_m
        c = 0
        d = 1
        determinant = a*d - b*c

        tanPhiA = self.wavelen * b
        tanPhiB = (a + b*self.R_inv)*self.pi*self.W**2

        #gouy_rad = np.arctan2(tanPhiA, tanPhiB)
        return self.__class__(
            (self.value * a + b)/(self.value * c + d),
            wavelen = self.wavelen * determinant,
            gouy_phasor = self.gouy_phasor * (tanPhiB + tanPhiA*1j),
        )

    def __complex__(self):
        return self.value

    def overlap_with(self, other):
        return (
            (self.value * other.value.conjugate()) / (other.value.conjugate() - self.value)
            * (2 * self.wavelen / (other.W * self.W * self.pi))
        ) * -self.ps_In

    def __str__(self):
        if self.R_inv != 0:
            R_str = u"{0}".format(str_m(self.R))
        else:
            R_str = u"1/0"
        return (u"Q(ZR={ZR}, Z={Z}, W0={W0}, W={W}, R={R}, λ={wavelen:.0f}nm)".format(
            ZR      = str_m(self.ZR),
            Z       = str_m(self.Z),
            W0      = str_m(self.W0),
            W       = str_m(self.W),
            wavelen = self.wavelen*1e9,
            R       = R_str,
        ))

    def reversed(self):
        return self.__class__(
            value = -self.value.conjugate(),
            wavelen = self.wavelen,
            gouy_phasor = self.gouy_phasor
        )


def beam_shape_1D(x, x_cbp, trans, tilt):
    """
    .. todo:: check the that the tilt and shift sign conventions make sense
    """
    cbp = complex(x_cbp)
    k = 2*np.pi / x_cbp.wavelen
    return (2/np.pi)**.25 * (1/x_cbp.W)**.5 * np.exp(-1j * k * (x + trans) ** 2 / (2*cbp) + 2*np.pi * 1j * x/x_cbp.wavelen * np.sin(tilt))


def beam_transverse(x, y, x_cbp, y_cbp = None, x_trans = 0, y_trans = 0, x_tilt = 0, y_tilt = 0):
    if y_cbp is None:
        y_cbp = x_cbp

    return np.outer(
        beam_shape_1D(y, y_cbp, trans = y_trans, tilt = y_tilt),
        beam_shape_1D(x, x_cbp, trans = x_trans, tilt = x_tilt),
    )


