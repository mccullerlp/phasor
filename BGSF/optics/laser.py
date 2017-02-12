# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
import declarative as decl

from ..base.utilities import (
    type_test
)

from ..math.key_matrix.dictionary_keys import (
    DictKey,
    FrequencyKey,
)

from . import bases
from . import ports
from . import frequency
from . import vacuum


class Laser(bases.OpticalCouplerBase, bases.SystemElementBase):

    @decl.dproperty
    def Fr(self):
        return ports.OpticalPortHolderInOut(self, x = 'Fr')

    @decl.dproperty
    def polarization(self, val = 'S'):
        val = self.ooa_params.setdefault('polarization', val)
        return val

    @decl.dproperty
    def polk(self):
        if self.polarization == 'S':
            ret  = ports.PolS
        elif self.polarization == 'P':
            ret  = ports.PolP
        return ret

    @decl.dproperty
    def _fluct(self):
        return vacuum.OpticalVacuumFluctuation(port = self.Fr)

    phased = False
    multiple = 1

    @decl.dproperty
    def classical_fdict(self, val = None):
        if val is None:
            val = {}
        return val

    @decl.mproperty
    def optical_fdict(self):
        return {self.F : self.multiple}

    @decl.mproperty
    def fkey(self):
        return DictKey({
            ports.OpticalFreqKey: FrequencyKey(self.optical_fdict),
            ports.ClassicalFreqKey: FrequencyKey(self.classical_fdict),
        })

    @decl.dproperty
    def power_W(self, val):
        val = self.ooa_params.setdefault('power_W', val)
        return val

    @decl.dproperty
    def F(self, val):
        type_test(val, frequency.OpticalFrequency)
        return val

    def system_setup_ports_initial(self, ports_algorithm):
        ports_algorithm.coherent_sources_needed(self.Fr.o, self.fkey | self.polk | ports.LOWER)
        ports_algorithm.coherent_sources_needed(self.Fr.o, self.fkey | self.polk | ports.RAISE)
        return

    def system_setup_ports(self, ports_algorithm):
        return

    def system_setup_coupling(self, matrix_algorithm):
        field_rtW = self.symbols.math.sqrt(self.power_W)
        if self.phased:
            matrix_algorithm.coherent_sources_insert(self.Fr.o, self.fkey | self.polk | ports.LOWER, field_rtW * self.symbols.i)
            matrix_algorithm.coherent_sources_insert(self.Fr.o, self.fkey | self.polk | ports.RAISE, -field_rtW * self.symbols.i)
        else:
            matrix_algorithm.coherent_sources_insert(self.Fr.o, self.fkey | self.polk | ports.LOWER, field_rtW)
            matrix_algorithm.coherent_sources_insert(self.Fr.o, self.fkey | self.polk | ports.RAISE, field_rtW)
        return

