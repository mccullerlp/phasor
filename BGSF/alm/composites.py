"""
"""
from __future__ import division

from declarative import (
    mproperty,
    dproperty,
    group_dproperty,
    Bunch,
)

from ..base.multi_unit_args import (
    generate_refval_attribute,
)

from .utils import (
    str_m,
    TargetIdx,
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


class PLCX(CSystemStack):
    substrate_inner = substrate_fused_silica
    substrate_outer = substrate_environment

    @group_dproperty
    def L_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['L', 'length'],
            pname = 'length',
            preferred_attr = 'L_preferred',
            prototypes = ['full', 'base'],
        )

    @group_dproperty
    def R_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['R', 'ROC'],
            pname = 'ROC',
            preferred_attr = 'ROC_preferred',
            prototypes = ['full', 'base'],
        )

    @dproperty
    def interface1(self):
        return CLensInterface(
            ROC_preferred = self.ROC_preferred,
            substrate_from = self.substrate_outer,
            substrate_to   = self.substrate_inner,
            loc_m = None,
        )

    @dproperty
    def space(self):
        return CSpace(
            L_preferred = self.L_preferred,
            substrate = self.substrate_inner,
            loc_m = None,
        )

    @dproperty
    def interface2(self):
        return CLensInterface(
            ROC_preferred = None,
            substrate_from = self.substrate_inner,
            substrate_to   = self.substrate_outer,
            loc_m = None,
        )

    @mproperty
    def components(self):
        return [
            self.interface1,
            self.space,
            self.interface2,
        ]

    def lens_description(self, z, from_target):
        f_m = -1/self.matrix[1, 0]
        return Bunch(
            f_m = f_m,
            width_m = self.width_m,
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

    @group_dproperty
    def L_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['L', 'length'],
            pname = 'length',
            preferred_attr = 'L_preferred',
            prototypes = ['full', 'base'],
        )

    @group_dproperty
    def R1_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['R1', 'ROC1'],
            pname = 'ROC1',
            preferred_attr = 'ROC1_preferred',
            prototypes = ['full', 'base'],
        )

    @group_dproperty
    def R2_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['R2', 'ROC2'],
            pname = 'ROC2',
            preferred_attr = 'ROC2_preferred',
            prototypes = ['full', 'base'],
        )

    @dproperty
    def interface1(self):
        return CLensInterface(
            ROC_preferred = self.ROC1_preferred,
            substrate_from = self.substrate_outer,
            substrate_to   = self.substrate_inner,
        )
    @dproperty
    def space(self):
        return CSpace(
            L_preferred = self.L_preferred,
            substrate = self.substrate_inner,
        )

    @dproperty
    def interface2(self):
        return CLensInterface(
            ROC_preferred  = -self.ROC2_preferred,
            substrate_from = self.substrate_inner,
            substrate_to   = self.substrate_outer,
        )

    @mproperty
    def components(self):
        return [
            self.interface1,
            self.space,
            self.interface2,
        ]

    def lens_description(self, z, from_target):
        f_m = -1/self.matrix[1, 0]
        return Bunch(
            f_m = f_m,
            width_m = self.width_m,
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

