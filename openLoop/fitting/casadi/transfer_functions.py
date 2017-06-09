"""
"""
from __future__ import (division, print_function)
#from builtins import zip
import numpy as np
import operator

from ...math.complex import Complex
from ...math import dispatched as dmath
from ...math import dispatch_casadi as dcasadi


from . import visitors as VISIT
import casadi

import declarative
from declarative import bunch

from ...base.simple_units import (
    SimpleUnitfulGroup,
)

from .expressions import (
    FitterExpression,
)


class TransferACExpression(FitterExpression):
    def func_solve_map(self, f):
        return f

    def func_solve_map_inv(self, out_val):
        return out_val

    #TODO
    #def F_Hz_override(self):
    #    return

    @declarative.dproperty
    def ACReadout(self, val):
        return val.name_system

    @declarative.dproperty
    def ACData(self, val):
        return val

    @declarative.dproperty
    def SNR_limit(self, val = 0):
        return np.asarray(val)

    @declarative.dproperty
    def SNR_weights(self, val):
        val = np.asarray(val)
        return val

    @declarative.dproperty
    def SNR_phase_weights(self, val = None):
        if val is None:
            return self.SNR_weights
        return np.asarray(val)

    @declarative.dproperty
    def residuals_model(self, val = 'direct'):
        assert(val in ['bias_balance', 'direct', 'subtract', 'magnitude'])
        return val

    @declarative.mproperty
    def freq_Hz(self):
        return self.ACReadout.F_Hz.val

    def function(self, xfer):
        SNR_weights = np.copy(self.SNR_weights)

        #apply the SNR_limit
        SNR_weights[SNR_weights < self.SNR_limit] = 0

        SNR_phase_weights = np.copy(self.SNR_phase_weights)
        #apply the SNR_limit
        SNR_phase_weights[SNR_phase_weights < self.SNR_limit] = 0

        remapped_readout = xfer[self.ACReadout].AC_sensitivity

        if self.residuals_model == "direct":
            div = (remapped_readout / self.ACData)
            a_div = abs(div)
            residuals1 = dmath.log(a_div)
            residuals2 = div.imag / a_div
        elif self.residuals_model == "subtract":
            #need to multiply by either the data or the fit magnitude as the weights are in SNR
            sub = (remapped_readout / self.ACData - 1)
            residuals1 = sub.real
            residuals2 = sub.imag
        elif self.residuals_model == "magnitude":
            div = (remapped_readout / self.ACData)
            a_div = abs(div)
            residuals1 = dmath.log(a_div)
            residuals2 = 0
        elif self.residuals_model == "bias_balance":
            debias_reweight = 1 / (SNR_weights**2)
            ratio = (remapped_readout / self.ACData)
            upward_biased = ratio - 1
            downward_biased = (1/ratio - 1) * debias_reweight
            debiased_signal = ((upward_biased - downward_biased) / (1 + debias_reweight))
            #print("CHECK: ", debiased_signal)
            residuals1 = debiased_signal.real
            residuals2 = debiased_signal.imag
        else:
            raise RuntimeError("Unrecognized residuals model")

        residuals1 = residuals1 * SNR_weights
        residuals2 = residuals2 * SNR_phase_weights
        resid = casadi.dot(residuals1, residuals1) + casadi.dot(residuals2, residuals2)
        return resid


