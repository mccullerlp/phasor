# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

from declarative import (
    mproperty,
)

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
    OOA_ASSIGN,
)

from .ports import (
    OpticalPortHolderInOut,
    #QuantumKey,
    RAISE, LOWER,
    OpticalSymmetric2PortMixin,
)


class Space(OpticalSymmetric2PortMixin, OpticalCouplerBase, SystemElementBase):
    def __init__(
        self,
        L_m,
        L_detune_m = 0,
        **kwargs
    ):
        super(Space, self).__init__(**kwargs)

        OOA_ASSIGN(self).L_m          = L_m
        OOA_ASSIGN(self).L_detune_m   = L_detune_m
        self.Fr = OpticalPortHolderInOut(self, x = 'Fr')
        self.Bk = OpticalPortHolderInOut(self, x = 'Bk')
        return

    def phase_lower(self, iwavelen_m, F):
        system = self.system
        return system.math.exp(-system.i2pi * (F * self.L_m / system.c_m_s + self.L_detune_m * iwavelen_m))

    def phase_raise(self, iwavelen_m, F):
        system = self.system
        return system.math.exp(system.i2pi * (F * self.L_m / system.c_m_s + self.L_detune_m * iwavelen_m))

    @mproperty
    def ports_optical(self):
        return [
            self.Fr,
            self.Bk,
        ]

    @mproperty
    def pmap(self):
        return {
            self.Fr : self.Bk,
            self.Bk : self.Fr,
        }

    def system_setup_ports(self, ports_algorithm):
        for port in self.ports_optical:
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom)
            for kto in ports_algorithm.port_update_get(port.o):
                ports_algorithm.port_coupling_needed(self.pmap[port].i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for port in self.ports_optical:
            for kfrom in matrix_algorithm.port_set_get(port.i):
                iwavelen_m, freq = self.system.optical_frequency_extract(kfrom)
                if kfrom.subkey_has(LOWER):
                    cplg = self.phase_lower(iwavelen_m, freq)
                elif kfrom.subkey_has(RAISE):
                    cplg = self.phase_raise(iwavelen_m, freq)
                else:
                    raise RuntimeError("Boo")
                matrix_algorithm.port_coupling_insert(port.i, kfrom, self.pmap[port].o, kfrom, cplg)
        return

