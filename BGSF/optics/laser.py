# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

from ..base.utilities import (
    type_test
)

from ..math.key_matrix.dictionary_keys import (
    DictKey,
    FrequencyKey,
)

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
    OOA_ASSIGN,
)

from .ports import (
    OpticalPortHolderOut,
    RAISE, LOWER,
    PolS, PolP,
    OpticalFreqKey,
    ClassicalFreqKey,
    OpticalNonOriented1PortMixin,
)

from .frequency import (
    OpticalFrequency,
)

from .vacuum import (
    OpticalVacuumFluctuation,
)


class Laser(OpticalNonOriented1PortMixin, OpticalCouplerBase, SystemElementBase):
    def __init__(
        self,
        F,
        power_W,
        multiple = 1,
        polarization = 'S',
        classical_fdict = None,
        phased = False,
        **kwargs
    ):
        super(Laser, self).__init__(**kwargs)
        type_test(F, OpticalFrequency)
        self.F = F

        OOA_ASSIGN(self).polarization = polarization
        OOA_ASSIGN(self).power_W = power_W

        if self.polarization == 'S':
            self.polk  = PolS
        elif self.polarization == 'P':
            self.polk  = PolP

        self.multiple = multiple
        self.polarization = polarization
        self.Fr = OpticalPortHolderOut(self, x = 'Fr')
        self.optical_fdict = {self.F : self.multiple}
        if classical_fdict is None:
            self.classical_fdict = {}
        else:
            self.classical_fdict = classical_fdict
        self.fkey = DictKey({
            OpticalFreqKey: FrequencyKey(self.optical_fdict),
            ClassicalFreqKey: FrequencyKey(self.classical_fdict),
        })
        self.phased = phased
        #TODO, not sure I like these semantics
        self._fluct = self.system._subsled_construct(
            element     = self,
            name        = '_fluct',
            constructor = OpticalVacuumFluctuation(port = self.Fr),
        )
        return

    def linked_elements(self):
        return (
            self.F,
            self._fluct,
        )

    def system_setup_ports_initial(self, ports_algorithm):
        ports_algorithm.coherent_sources_needed(self.Fr.o, self.fkey | self.polk | LOWER)
        ports_algorithm.coherent_sources_needed(self.Fr.o, self.fkey | self.polk | RAISE)
        return

    def system_setup_ports(self, ports_algorithm):
        return

    def system_setup_coupling(self, matrix_algorithm):
        field_rtW = self.system.math.sqrt(self.power_W)
        if self.phased:
            matrix_algorithm.coherent_sources_insert(self.Fr.o, self.fkey | self.polk | LOWER, field_rtW * self.system.i)
            matrix_algorithm.coherent_sources_insert(self.Fr.o, self.fkey | self.polk | RAISE, -field_rtW * self.system.i)
        else:
            matrix_algorithm.coherent_sources_insert(self.Fr.o, self.fkey | self.polk | LOWER, field_rtW)
            matrix_algorithm.coherent_sources_insert(self.Fr.o, self.fkey | self.polk | RAISE, field_rtW)
        return

