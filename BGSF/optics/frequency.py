
# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

from ..base import (
    FrequencyBase,
    SystemElementBase,
)


class OpticalFrequency(SystemElementBase, FrequencyBase):
    iwavelen_m = None
    def __init__(
            self,
            wavelen_m,
            **kwargs
    ):
        super(OpticalFrequency, self).__init__(**kwargs)
        self.iwavelen_m = 1/wavelen_m
