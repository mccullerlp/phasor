# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from phasor.utilities.print import print

#import numpy as np

import declarative as decl

from .. import base


class DCReadout(base.SystemElementBase):

    @decl.dproperty
    def port_set(self, val = 'DC'):
        val = self.ctree.setdefault('port_set', val)
        return val

    @decl.dproperty
    def port(self, val):
        return val

    @decl.mproperty
    def key(self):
        return base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({})})

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
