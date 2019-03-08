# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np
import scipy.optimize
import declarative

from .beam_param import (
    ComplexBeamParam
)

from phasor.utilities.mpl.autoniceplot import (
    #AutoPlotSaver,
    mplfigB,
    #asavefig,
)

from . import target
from . import utils
from . import standard_attrs as attrs

class QFitBeamTarget(target.BeamTargetBase):
    @declarative.dproperty
    def qfit(self, val):
        return val

    @declarative.dproperty
    def beam_q(self):
        if self.ref_m.val is None:
            q_value = self.qfit.q_fit
        else:
            if self.reversed:
                q_value = self.qfit.q_fit.propagate_distance(-self.loc_m.val + self.ref_m.val)
            else:
                q_value = self.qfit.q_fit.propagate_distance(self.loc_m.val - self.ref_m.val)
        if self.env_reversed:
            q_value = q_value.reversed()
        return q_value

    _ref_default = ('ref_m', None)
    ref_m = attrs.generate_reference_m()


class QFit(declarative.OverridableObject):
    @declarative.dproperty
    def wavelen_nm(self, val):
        return val

    def as_target(self, **kwargs):
        return QFitBeamTarget(
            qfit = self,
            **kwargs
        )

    m2 = 1.00

    @declarative.mproperty
    def D_um(self, arg):
        arg = np.array(arg)
        return arg

    @declarative.mproperty
    def R_m(self, arg = declarative.NOARG):
        if arg is declarative.NOARG:
            arg = self.D_um * 1e-6 / 2
        else:
            arg = np.array(arg)
        return arg

    @declarative.mproperty
    def Z_in(self, arg):
        arg = np.array(arg)
        return arg

    @declarative.mproperty
    def Z_m(self, arg = declarative.NOARG):
        if arg is declarative.NOARG:
            arg = self.Z_in * .0254
        else:
            arg = np.array(arg)
        return arg

    @declarative.mproperty
    def Z0_ZR_init(self, arg = declarative.NOARG):
        if arg is declarative.NOARG:
            idx_W0 = np.argsort(self.R_m)
            W0 = self.R_m[idx_W0[0]]  * 1

            ZR = np.pi*W0**2/(self.wavelen_nm * 1e-9)
            Z0 = -np.mean(self.Z_m[idx_W0[:4]])
            arg = (Z0, ZR)
        return arg

    def waist_func(self, z, z_0, z_R):
        return (self.m2 * self.wavelen_nm * 1e-9 / (np.pi * z_R) * ((z + z_0)**2 + z_R**2))**.5

    def waist_func_fit(self, z):
        return self.waist_func(z, *self.Z0_ZR_fit)

    no_prefit = False
    @declarative.mproperty
    def Z0_ZR_fit(self):
        idx_W0 = np.argmin(self.R_m)
        init = self.Z0_ZR_init
        #do a prefit to try and find tiny waists using a subset of the data
        if idx_W0 > 1 and idx_W0 < len(self.R_m) - 1 and not self.no_prefit and len(self.R_m) > 3:
            #don't include the point
            if idx_W0 < len(self.R_m) / 2:
                idx_W0 += 1
                #ignore the actual point itself as it may be across a gap
                init, hess = scipy.optimize.curve_fit(
                    self.waist_func,
                    self.Z_m[idx_W0:],
                    self.R_m[idx_W0:],
                    p0 = self.Z0_ZR_init
                )
            else:
                init, hess = scipy.optimize.curve_fit(
                    self.waist_func,
                    self.Z_m[:idx_W0],
                    self.R_m[:idx_W0],
                    p0 = self.Z0_ZR_init
                )
        (z0, zR), hess = scipy.optimize.curve_fit(self.waist_func, self.Z_m, self.R_m, p0 = init)
        return (z0, zR)

    @declarative.mproperty
    def q_fit(self):
        return ComplexBeamParam.from_Z_ZR(
            self.Z0_ZR_fit[0],
            self.Z0_ZR_fit[1],
            wavelen = self.wavelen_nm * 1e-9,
        )

    @declarative.mproperty
    def q_init(self, initval = None):
        if initval is None:
            return ComplexBeamParam.from_Z_ZR(
                self.Z0_ZR_init[0],
                self.Z0_ZR_init[1],
                wavelen = self.wavelen_nm * 1e-9,
            )
        else:
            return initval

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

    def plot(
        self,
        init = False,
    ):
        F = mplfigB()
        diff = max(self.Z_m) - min(self.Z_m)
        Z_pts = np.linspace(min(self.Z_m) - diff/4, max(self.Z_m) + diff/4, 100)

        if int(self.wavelen_nm) == 1064:
            color_pts = 'red'
            color_fit = 'orange'
            color_init = 'purple'
        elif int(self.wavelen_nm) == 532:
            color_pts = 'blue'
            color_fit = 'green'
            color_init = 'purple'
        else:
            color_pts = 'blue'
            color_fit = 'black'
            color_init = 'purple'


        F.ax0.scatter(
            self.Z_in,
            self.D_um,
            color = color_pts,
            label = 'data',
        )

        fit_label = (u"Fit: waist {Zm} = {Zin:.1f}in\nZR={ZR}\nW0={W0}\nD0={D0}".format(
            Zm      = utils.str_m(-self.q_fit.Z, d = 3),
            Zin     = -self.q_fit.Z / .0254,
            ZR      = utils.str_m(self.q_fit.ZR, d = 4),
            W0      = utils.str_m(self.q_fit.W0, d = 4),
            D0      = utils.str_m(2 * self.q_fit.W0, d = 4),
        ))

        F.ax0.plot(
            Z_pts / .0254,
            self.m2**.5 * 2 * 1e6 * self.q_fit.propagate_distance(Z_pts).W,
            color = color_fit,
            label = fit_label,
        )
        if init:
            F.ax0.plot(
                Z_pts / .0254,
                self.m2**.5 * 2 * 1e6 * self.q_init.propagate_distance(Z_pts).W,
                color = color_init,
                label = 'Initial',
            )
        F.ax0.set_xlabel('Inches from reference')
        F.ax0.set_ylabel('2σ intensity\ndiameter[μm]')
        F.ax0.set_title('Beam Parameter Fit (at {0:.0f}nm)'.format(self.wavelen_nm))
        F.ax0.legend(loc = 'best')
        return F

