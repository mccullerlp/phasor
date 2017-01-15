# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

#import numpy as np

import declarative as decl

from ..math.key_matrix import (
    DictKey,
    FrequencyKey,
)

from ..base import (
    SystemElementBase,
    OOA_ASSIGN,
    ClassicalFreqKey,
)


class DCReadout(SystemElementBase):

    @decl.dproperty
    def port_set(self, val = 'DC'):
        val = self.ooa_params.setdefault('port_set', val)
        return val

    @decl.dproperty
    def port(self, val):
        return val

    @decl.mproperty
    def key(self):
        return DictKey({ClassicalFreqKey: FrequencyKey({})})

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'DC_readouts', 'readouts']
        system.readout_port_needed(self.port, self.key, portsets)
        return

    @decl.mproperty
    def DC_readout(self):
        sbunch = self.system.solution.driven_solution_get(self.port_set)
        pk_view = (self.port, self.key)
        val = sbunch.solution[pk_view]
        return val.real
