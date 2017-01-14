"""
"""
from __future__ import division
from builtins import object

from ..base.bases import (
    ElementBase,
    NoiseBase,
    CouplerBase,
)

from ..base.elements import (
    SystemElementBase,
    OOA_ASSIGN,
)

import declarative as decl
#import numpy as np
#import warnings

from YALL.natsci.optics.dictionary_keys import (
    DictKey,
)

from . import ports
from . import elements


class OpAmp(elements.ElectricalElementBase):

    @decl.mproperty
    def in_p(self):
        return ports.ElectricalPortHolderInOut(self, 'in_p')

    @decl.mproperty
    def in_n(self):
        return ports.ElectricalPortHolderInOut(self, 'in_n')

    @decl.mproperty
    def out(self):
        return ports.ElectricalPortHolderInOut(self, 'out')

    def gain_by_freq(self, F):
        return 1

    def system_setup_coupling(self):
        matrix = ForewardDictMatrix()
        for f_key in self.system.F_key_basis:
            df_key = DictKey(F = f_key)
            matrix[
                df_key | self.in_p.i,
                df_key | self.in_p.o
            ] = 1
            matrix[
                df_key | self.in_n.i,
                df_key | self.in_n.o
            ] = 1
            matrix[
                df_key | self.out.i,
                df_key | self.out.o
            ] = -1
            gbf = self.gain_by_freq(
                F = f_key.frequency(),
            )
            matrix[
                df_key | self.in_p.i,
                df_key | self.out.o
            ] = gbf
            matrix[
                df_key | self.in_p.o,
                df_key | self.out.o
            ] = gbf
            matrix[
                df_key | self.in_n.i,
                df_key | self.out.o
            ] = -gbf
            matrix[
                df_key | self.in_n.o,
                df_key | self.out.o
            ] = -gbf

        matrix.insert(
            into = self.system.coupling_matrix,
            validate = self.system.dk_validate,
        )
        return


class VAmp(elements.ElectricalElementBase):
    Y_input = 0
    Z_output = 0

    @decl.mproperty
    def in_n(self):
        return ports.ElectricalPortHolderInOut(self, 'in_n')

    @decl.mproperty
    def out(self):
        return ports.ElectricalPortHolderInOut(self, 'out')

    def gain_by_freq(self, F):
        return 1

    def system_setup_coupling(self):
        matrix = ForewardDictMatrix()
        for f_key in self.system.F_key_basis:
            df_key = DictKey(F = f_key)
            matrix[
                df_key | self.in_n.i,
                df_key | self.in_n.o
            ] = ((1 - self.Y_input * self.Z_termination) / (1 + self.Y_input * self.Z_termination))
            matrix[
                df_key | self.out.i,
                df_key | self.out.o
            ] = ((self.Z_output - self.Z_termination) / (self.Z_output + self.Z_termination))

            gbf = self.gain_by_freq(
                F = f_key.frequency(),
            )

            matrix[
                df_key | self.in_n.i,
                df_key | self.out.o
            ] = -gbf
            matrix[
                df_key | self.in_n.o,
                df_key | self.out.o
            ] = -gbf

        matrix.insert(
            into = self.system.coupling_matrix,
            validate = self.system.dk_validate,
        )
        return





