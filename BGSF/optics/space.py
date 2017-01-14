# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

import declarative as decl

from . import bases
from . import ports


class Space(ports.OpticalSymmetric2PortMixin, bases.OpticalCouplerBase, bases.SystemElementBase):
    @decl.dproperty
    def Fr(self):
        return ports.OpticalPortHolderInOut(self, x = 'Fr')

    @decl.dproperty
    def Bk(self):
        return ports.OpticalPortHolderInOut(self, x = 'Bk')

    @decl.dproperty
    def L_m(self, val):
        val = self.ooa_params.setdefault('L_m', val)
        return val

    @decl.dproperty
    def L_detune_m(self, val = 0):
        val = self.ooa_params.setdefault('L_detune_m', val)
        return val

    def phase_lower(self, iwavelen_m, F):
        system = self.system
        return system.math.exp(-system.i2pi * (F * self.L_m / system.c_m_s + self.L_detune_m * iwavelen_m))

    def phase_raise(self, iwavelen_m, F):
        system = self.system
        return system.math.exp(system.i2pi * (F * self.L_m / system.c_m_s + self.L_detune_m * iwavelen_m))

    @decl.mproperty
    def ports_optical(self):
        return [
            self.Fr,
            self.Bk,
        ]

    @decl.mproperty
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
                if kfrom.subkey_has(ports.LOWER):
                    cplg = self.phase_lower(iwavelen_m, freq)
                elif kfrom.subkey_has(ports.RAISE):
                    cplg = self.phase_raise(iwavelen_m, freq)
                else:
                    raise RuntimeError("Boo")
                matrix_algorithm.port_coupling_insert(port.i, kfrom, self.pmap[port].o, kfrom, cplg)
        return

