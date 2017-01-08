# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
import numpy as np
import scipy.optimize

from declarative import (
    #first_non_none,
    OverridableObject,
    mproperty,
    #dproperty,
    NOARG,
)

from .beam_param import (
    ComplexBeamParam
)

from YALL.utilities.mpl.autoniceplot import (
    #AutoPlotSaver,
    mplfigB,
    #asavefig,
)


class QFit(OverridableObject):
    wavelen_nm = 1064

    @mproperty
    def R_um(self, arg):
        arg = np.array(arg)
        return arg

    @mproperty
    def R_m(self, arg = NOARG):
        if arg is NOARG:
            arg = self.R_um * 1e-6
        else:
            arg = np.array(arg)
        return arg

    @mproperty
    def Z_in(self, arg):
        arg = np.array(arg)
        return arg

    @mproperty
    def Z_m(self, arg = NOARG):
        if arg is NOARG:
            arg = self.Z_in * .0254
        else:
            arg = np.array(arg)
        return arg

    @mproperty
    def Z0_ZR_init(self, arg = NOARG):
        if arg is NOARG:
            Z0 = -(np.max(self.Z_m) + np.min(self.Z_m)) / 2
            ZR = (np.max(self.Z_m) - np.min(self.Z_m)) / 2
            arg = (Z0, ZR)
        return arg

    def waist_func(self, z, z_0, z_R):
        return (self.wavelen_nm * 1e-9 / (np.pi * z_R) * ((z + z_0)**2 + z_R**2))**.5

    def waist_func_fit(self, z):
        return self.waist_func(z, *self.Z0_ZR_fit)

    @mproperty
    def Z0_ZR_fit(self):
        (z0, zR), hess = scipy.optimize.curve_fit(self.waist_func, self.Z_m, self.R_m, p0 = self.Z0_ZR_init)
        return (z0, zR)

    @mproperty
    def q_fit(self):
        return ComplexBeamParam.from_Z_ZR(
            self.Z0_ZR_fit[0],
            self.Z0_ZR_fit[1],
            wavelen = self.wavelen_nm * 1e-9,
        )

    @mproperty
    def q_init(self):
        return ComplexBeamParam.from_Z_ZR(
            self.Z0_ZR_init[0],
            self.Z0_ZR_init[1],
            wavelen = self.wavelen_nm * 1e-9,
        )

    def rep(self, place_in = 0):
        print(self.Z0_ZR_fit)
        try:
            print ("ComplexBeamParam.from_Z_ZR({0}, {1}, wavelen = {2})".format(
                self.Z0_ZR_fit[0] + place_in * .0254,
                self.Z0_ZR_fit[1],
                self.wavelen_nm * 1e-9,
            ))
        except Exception as e:
            print(e)

    def plot(self, init = False):
        F = mplfigB()
        F.ax0.scatter(self.Z_in, self.R_m * 1e6, color = 'red')

        diff = max(self.Z_m) - min(self.Z_m)
        Z_pts = np.linspace(min(self.Z_m) - diff/4, max(self.Z_m) + diff/4, 100)
        F.ax0.plot(Z_pts / .0254, 1e6 * self.q_fit.propagate_distance(Z_pts).W, color = 'orange')
        if init:
            F.ax0.plot(Z_pts / .0254, 1e6 * self.q_init.propagate_distance(Z_pts).W, color = 'green')
        return F
