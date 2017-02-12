# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
import numpy as np

from . import bases


class Frequency(bases.FrequencyBase, bases.SystemElementBase):
    def __init__(
            self,
            F_Hz,
            F_center_Hz = None,
            F_width_Hz  = 0,
            order       = None,
            groups      = {},
            **kwargs
    ):
        super(Frequency, self).__init__(**kwargs)

        bases.OOA_ASSIGN(self).F_Hz = F_Hz

        if F_center_Hz is None:
            F_center_Hz = (np.max(self.F_Hz) + np.min(self.F_Hz)) / 2

        bases.OOA_ASSIGN(self).F_center_Hz = F_center_Hz

        if F_width_Hz is None:
            F_center_Hz = (np.max(self.F_Hz) - np.min(self.F_Hz)) / 2

        bases.OOA_ASSIGN(self).F_width_Hz  = F_width_Hz

        bases.OOA_ASSIGN(self).order = order

        for group, b_incl in list(groups.items()):
            self.ooa_params.groups[group] = b_incl

        groups = set()
        for group, b_incl in list(self.ooa_params.groups.items()):
            if b_incl:
                groups.add(group)
        self.groups = groups
        return
