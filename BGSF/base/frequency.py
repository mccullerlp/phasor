# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
import numpy as np

import declarative

from . import bases

from . import multi_unit_args as mua

from .import units


def generate_F_Hz():
    @declarative.group_dproperty
    def F_Hz(desc):
        return mua.generate_refval_attribute(
            desc,
            ubunch = units.frequency,
            stems = ['F', ],
            ooa_name = 'frequency',
            preferred_attr = 'frequency',
            default_attr = 'frequency',
            prototypes = ['full'],
        )
    return F_Hz


class Frequency(
        bases.FrequencyBase,
        bases.SystemElementBase
):

    F_Hz = generate_F_Hz()

    @declarative.dproperty
    def F_center_Hz(self, val = declarative.NOARG):
        if val is declarative.NOARG:
            val = self.F_Hz.ref
        val = self.ooa_params.setdefault('F_center_Hz', val)
        return val

    def __init__(
            self,
            F_width_Hz  = 0,
            order       = None,
            **kwargs
    ):
        super(Frequency, self).__init__(**kwargs)

        bases.OOA_ASSIGN(self).F_width_Hz  = F_width_Hz
        bases.OOA_ASSIGN(self).order = order
        return
