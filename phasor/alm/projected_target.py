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

from .beam import BeamTargetBase
from . import standard_attrs as attrs

class BeamTargetProjected(BeamTargetBase):
    @declarative.dproperty
    def qfit(self, val):
        return val

    @declarative.dproperty
    def beam_q(self):
        if self.ref_m.val is None:
            q_value = self.qfit.q_fit
        else:
            q_value = self.qfit.q_fit.propagate_distance(self.loc_m.val - self.ref_m.val)
        if self.env_reversed:
            q_value = q_value.reversed()
        return q_value

    _ref_default = ('ref_m', None)
    ref_m = attrs.generate_reference_m()

