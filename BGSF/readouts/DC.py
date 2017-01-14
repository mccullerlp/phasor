# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

#import numpy as np

from declarative import (
    mproperty,
)

from ..math.key_matrix import (
    DictKey,
    FrequencyKey,
)

from ..base import (
    SystemElementBase,
    OOA_ASSIGN,
    ClassicalFreqKey,
)

from .base import ReadoutViewBase


class DCReadout(SystemElementBase):
    def __init__(
            self,
            port,
            port_set = 'DC',
            **kwargs
    ):
        super(DCReadout, self).__init__(**kwargs)
        OOA_ASSIGN(self).port_set = port_set

        self.port = port
        self.key = DictKey({ClassicalFreqKey: FrequencyKey({})})
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'DC_readouts', 'readouts']
        system.readout_port_needed(self.port, self.key, portsets)
        return

    @mproperty
    def DC_readout(self):
        sbunch = self.system.solution.driven_solution_get(self.port_set)
        pk_view = (self.port, self.key)
        val = sbunch.solution[pk_view]
        return val.real
