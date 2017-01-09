
# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from BGSF.utilities.print import print

import declarative as decl

from ..base import (
    FrequencyBase,
    SystemElementBase,
)


class OpticalFrequency(SystemElementBase, FrequencyBase):

    @decl.dproperty
    def wavelen_m(self, val):
        return val

    @decl.mproperty
    def iwavelen_m(self, val):
        return 1/self.wavelen_m
