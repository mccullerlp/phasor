# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import declarative as decl

from ..base.utilities import (
    type_test
)

from . import bases
from . import ports
from . import frequency
from . import vacuum
from . import standard_attrs


class Laser(
        bases.OpticalCouplerBase,
        bases.SystemElementBase
):

    @decl.dproperty
    def po_Fr(self):
        return ports.OpticalPort()

    power = standard_attrs.generate_power()
    phase = standard_attrs.generate_rotate(name = 'phase')
    _phase_default = ('phase_rad', 0)

    @decl.dproperty
    def polarization(self, val = 'S'):
        val = self.ctree.setdefault('polarization', val)
        return val

    @decl.dproperty
    def F(self, val):
        type_test(val, frequency.OpticalFrequency)
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
        #TODO add realistic laser noise
        return vacuum.OpticalVacuumFluctuation(
            port = self.po_Fr
        )

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
        return ports.DictKey({
            ports.OpticalFreqKey: ports.FrequencyKey(self.optical_fdict),
            ports.ClassicalFreqKey: ports.FrequencyKey(self.classical_fdict),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        ports_algorithm.coherent_sources_needed(self.po_Fr.o, self.fkey | self.polk | ports.LOWER)
        ports_algorithm.coherent_sources_needed(self.po_Fr.o, self.fkey | self.polk | ports.RAISE)
        return

    def system_setup_ports(self, ports_algorithm):
        #TODO should separate "wanted" ports from "driven ports"
        #Must move inputs to outputs for AC sidebands
        for kto in ports_algorithm.port_update_get(self.po_Fr.o):
            ports_algorithm.port_coupling_needed(self.po_Fr.i, kto)
        for kfrom in ports_algorithm.port_update_get(self.po_Fr.i):
            ports_algorithm.port_coupling_needed(self.po_Fr.o, kfrom)
        return

    def system_setup_coupling(self, matrix_algorithm):
        field_rtW = self.symbols.math.sqrt(self.power_W.val)
        if self.phase_rad.val is not 0:
            cplg = self.symbols.math.exp(self.symbols.i * self.phase_rad.val)
            cplgC = self.symbols.math.exp(-self.symbols.i * self.phase_rad.val)
            matrix_algorithm.coherent_sources_insert(self.po_Fr.o, self.fkey | self.polk | ports.LOWER, field_rtW * cplg)
            matrix_algorithm.coherent_sources_insert(self.po_Fr.o, self.fkey | self.polk | ports.RAISE, field_rtW * cplgC)
        else:
            matrix_algorithm.coherent_sources_insert(self.po_Fr.o, self.fkey | self.polk | ports.LOWER, field_rtW)
            matrix_algorithm.coherent_sources_insert(self.po_Fr.o, self.fkey | self.polk | ports.RAISE, field_rtW)
        return

