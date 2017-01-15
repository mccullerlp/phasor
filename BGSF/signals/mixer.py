# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

import numpy as np

#from numbers import Number
#import warnings

from ..math.key_matrix import (
    DictKey,
)

from ..base import (
    CouplerBase,
    SystemElementBase,
)

from .ports import (
    SignalPortHolderIn,
    SignalPortHolderOut,
    ClassicalFreqKey,
)


class Mixer(CouplerBase, SystemElementBase):
    def __init__(
            self,
            **kwargs
    ):
        super(Mixer, self).__init__(**kwargs)
        self.LO  = SignalPortHolderIn(self,  x = 'LO')
        self.I   = SignalPortHolderIn(self,  x = 'I')
        self.R_I = SignalPortHolderOut(self, x = 'R_I')
        self.R_Q = SignalPortHolderOut(self, x = 'R_Q')
        return

    def system_setup_ports(self, ports_algorithm):
        for kfrom1, kfrom2 in ports_algorithm.symmetric_update(self.LO.i, self.I.i):
            f1 = kfrom1[ClassicalFreqKey]
            f2 = kfrom2[ClassicalFreqKey]
            f_new = f1 + f2
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.R_I.o, DictKey({ClassicalFreqKey: f_new}))
            ports_algorithm.port_coupling_needed(self.R_Q.o, DictKey({ClassicalFreqKey: f_new}))
        for kfrom1, kto2 in ports_algorithm.symmetric_update(self.LO.i, [self.R_I.o, self.R_Q.o]):
            f1 = kfrom1[ClassicalFreqKey]
            f2 = kto2[ClassicalFreqKey]
            f_new = f2 - f1
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.I.i, DictKey({ClassicalFreqKey: f_new}))
        for kfrom1, kto2 in ports_algorithm.symmetric_update(self.I.i, [self.R_I.o, self.R_Q.o]):
            f1 = kfrom1[ClassicalFreqKey]
            f2 = kto2[ClassicalFreqKey]
            f_new = f2 - f1
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.LO.i, DictKey({ClassicalFreqKey: f_new}))
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom1 in matrix_algorithm.port_set_get(self.LO.i):
            for kfrom2 in matrix_algorithm.port_set_get(self.I.i):
                f1 = kfrom1[ClassicalFreqKey]
                f2 = kfrom2[ClassicalFreqKey]
                f_new = f1 + f2
                if self.system.reject_classical_frequency_order(f_new):
                    continue

                freq_LO = self.system.classical_frequency_extract(kfrom1)
                kto = DictKey({ClassicalFreqKey: f_new})

                if not f_new.DC_is():
                    #TODO add inhomogenous term
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.LO.i,  kfrom1),
                        (self.I.i,   kfrom2),
                        (self.R_I.o, kto),
                        1 / 2,
                    )
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.LO.i,  kfrom1),
                        (self.I.i,   kfrom2),
                        (self.R_Q.o, kto),
                        self.system.i * np.sign(freq_LO) / 2,
                    )
                else:
                    #TODO add inhomogenous term
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.LO.i,  kfrom1),
                        (self.I.i,   kfrom2),
                        (self.R_I.o, kto),
                        1 / 4,
                    )
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.LO.i,  kfrom1),
                        (self.I.i,   kfrom2),
                        (self.R_Q.o, kto),
                        self.system.i * np.sign(freq_LO) / 4,
                    )
        return
