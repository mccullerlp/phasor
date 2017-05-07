# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

import declarative as decl

from . import bases
from . import ports
from . import standard_attrs


class Space(
        bases.OpticalCouplerBase,
        bases.SystemElementBase,
):
    @decl.dproperty
    def Fr(self):
        return ports.OpticalPort(sname = 'Fr', pchain = 'Bk')

    @decl.dproperty
    def Bk(self):
        return ports.OpticalPort(sname = 'Bk', pchain = 'Fr')

    length = standard_attrs.generate_length()

    _L_detune_default = ('L_detune_m', 0)
    L_detune = standard_attrs.generate_L_detune()

    def phase_lower(self, iwavelen_m, F):
        symbols = self.symbols
        return symbols.math.exp(-symbols.i2pi * (F * self.L_m.val / symbols.c_m_s + self.L_detune_m.val * iwavelen_m))

    def phase_raise(self, iwavelen_m, F):
        symbols = self.symbols
        return symbols.math.exp(symbols.i2pi * (F * self.L_m.val / symbols.c_m_s + self.L_detune_m.val * iwavelen_m))

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

