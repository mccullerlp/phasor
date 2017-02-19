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

    def __init__(
            self,
            F_center_Hz = None,
            F_width_Hz  = 0,
            order       = None,
            **kwargs
    ):
        super(Frequency, self).__init__(**kwargs)

        if F_width_Hz is None:
            F_center_Hz = (np.max(self.F_Hz) - np.min(self.F_Hz)) / 2

        bases.OOA_ASSIGN(self).F_width_Hz  = F_width_Hz

        bases.OOA_ASSIGN(self).order = order
        return
