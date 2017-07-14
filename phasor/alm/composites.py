# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import declarative

from .utils import (
    str_m,
    TargetIdx,
    TargetRight,
)

from .beam import (
    CLensInterface,
    CSpace,
)

from .system import (
    CSystemStack,
)

from .substrates import (
    substrate_fused_silica,
    substrate_environment,
)

from . import standard_attrs as attrs

class PLCX(CSystemStack):
    substrate_inner = substrate_fused_silica
    substrate_outer = substrate_environment

    L_m = attrs.generate_L_m()
    R_m = attrs.generate_R_m()

    @declarative.dproperty
    def interface1(self):
        return CLensInterface(
            ROC_preferred = self.ROC_preferred,
            substrate_from = self.substrate_outer,
            substrate_to   = self.substrate_inner,
            loc_m = None,
        )

    @declarative.dproperty
    def space(self):
        return CSpace(
            L_preferred = self.L_preferred,
            substrate = self.substrate_inner,
            loc_m = None,
        )

    @declarative.dproperty
    def interface2(self):
        return CLensInterface(
            ROC_preferred = None,
            substrate_from = self.substrate_inner,
            substrate_to   = self.substrate_outer,
            loc_m = None,
        )

    @declarative.mproperty
    def components(self):
        return [
            self.interface1,
            self.space,
            self.interface2,
        ]

    def lens_description(self, z, from_target):
        f_m = -1/self.matrix[1, 0]
        return declarative.Bunch(
            f_m = f_m,
            width_m = self.width_m * (-1 if from_target == TargetRight else 1),
            z = z,
            type = 'lens',
            str = 'PLCX R_m={R_m} f_m = {f_m}'.format(R_m = str_m(self.R_m.val), f_m = str_m(f_m)),
        )

    def system_data_targets(self, typename):
        dmap = {}
        if typename == 'lens_description':
            dmap[TargetIdx()] = self.lens_description
        return dmap


class CXCX(CSystemStack):
    substrate_inner = substrate_fused_silica
    substrate_outer = substrate_environment

    L_m = attrs.generate_L_m()
    R1_m = attrs.generate_R_m(variant = '1')
    R2_m = attrs.generate_R_m(variant = '2')

    @declarative.dproperty
    def interface1(self):
        return CLensInterface(
            ROC_preferred = self.ROC1_preferred,
            substrate_from = self.substrate_outer,
            substrate_to   = self.substrate_inner,
        )
    @declarative.dproperty
    def space(self):
        return CSpace(
            L_preferred = self.L_preferred,
            substrate = self.substrate_inner,
        )

    @declarative.dproperty
    def interface2(self):
        return CLensInterface(
            ROC_preferred  = -self.ROC2_preferred,
            substrate_from = self.substrate_inner,
            substrate_to   = self.substrate_outer,
        )

    @declarative.mproperty
    def components(self):
        return [
            self.interface1,
            self.space,
            self.interface2,
        ]

    def lens_description(self, z, from_target):
        f_m = -1/self.matrix[1, 0]
        return declarative.Bunch(
            f_m = f_m,
            width_m = self.width_m * (-1 if from_target == TargetRight else 1),
            R1_m = self.R1_m.val,
            R2_m = self.R2_m.val,
            z = z,
            type = 'lens',
            str = 'CXCX R1_m={R1_m} R2_m={R2_m} f_m = {f_m}'.format(
                R1_m = str_m(self.R1_m.val),
                R2_m = str_m(self.R2_m.val),
                f_m  = str_m(f_m)
            ),
        )

    def system_data_targets(self, typename):
        dmap = {}
        if typename == 'lens_description':
            dmap[TargetIdx()] = self.lens_description
        return dmap

