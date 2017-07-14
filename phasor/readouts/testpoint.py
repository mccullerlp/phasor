# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import declarative
#from phasor.utilities.print import print

#import numpy as np


from .. import base
from .noise import NoiseReadout

class Testpoint(base.SystemElementBase):
    """
    Need to make this able to specify if the Testpoint should be a numerator ("Type-A") or denominator ("Type-B")
    Currently Defaults to type-A
    """
    @declarative.dproperty
    def port(self, val = None):
        #TODO fix this import
        from .. import signals
        if val is None:
            if isinstance(self.parent, signals.SignalInPort):
                val = self.parent.i
            elif isinstance(self.parent, signals.SignalOutPort):
                val = self.parent.o
            elif isinstance(self.parent, signals.SignalNode):
                val = self.parent.o
            else:
                raise RuntimeError("Must specify port, or assign into a SignalInPort, SignalNode, or SignalOutPort Object")
        return val

    @declarative.mproperty
    def key(self):
        return base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({})})

    def system_setup_ports_initial(self, system):
        portsets = ['DC', 'DC_readouts', 'readouts']
        system.readout_port_needed(self.port, self.key, portsets)
        return

    @declarative.mproperty
    def DC(self):
        sbunch = self.system.solution.driven_solution_get(self.port_set)
        pk_view = (self.port, self.key)
        val = sbunch.solution[pk_view]
        return val.real

    @declarative.dproperty
    def noise(self):
        return NoiseReadout(
            portN = self.port,
        )

    @declarative.mproperty
    def F_Hz(self):
        return self.system.environment.F_AC.F_Hz

    @declarative.mproperty
    def AC_ASD(self):
        return self.AC_PSD**.5

    @declarative.mproperty
    def AC_PSD(self):
        return self.noise.CSD['R', 'R']

    @declarative.mproperty
    def AC_PSD_by_source(self):
        eachCSD = dict()
        for nobj, subCSD in list(self.noise.CSD_by_source.items()):
            nsum = subCSD['R', 'R']
            eachCSD[nobj] = nsum
        return eachCSD
