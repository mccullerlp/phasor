# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

from .bases import (
    #OpticalCouplerBase,
    #SystemElementBase,
    OOA_ASSIGN,
)

from .ports import (
    PolS, PolP,
    OpticalDegenerate4PortMixin,
)

from .selectors import OpticalSelectionStack

from ..base.elements import (SledConstructorInternal)


class MirrorSelectionStack(
    OpticalDegenerate4PortMixin,
    OpticalSelectionStack,
):
    def __init__(
        self,
        sub_element_map,
        select_map,
        AOI_deg = 0,
        facing_cardinal = None,
        **kwargs
    ):
        if AOI_deg == 0:
            port_set = set(['Fr', 'Fr'])
        else:
            port_set = set(['FrA', 'FrB', 'BkA', 'BkB'])

        #TODO make better error messages
        for mname, mconstr in sub_element_map.iteritems():
            assert(isinstance(mconstr, SledConstructorInternal))
            mconstr.adjust_safe(
                AOI_deg         = AOI_deg,
                facing_cardinal = facing_cardinal,
            )
            mconstr.adjust_defer(**kwargs)

        super(MirrorSelectionStack, self).__init__(
            sub_element_map = sub_element_map,
            select_map      = select_map,
            port_set        = port_set,
            AOI_deg         = AOI_deg,
            facing_cardinal = facing_cardinal,
            **kwargs
        )
        #TODO, combine mechanicals


class PolarizingMirror(MirrorSelectionStack):
    def __init__(
        self,
        mirror_P,
        mirror_S,
        **kwargs
    ):
        super(PolarizingMirror, self).__init__(
            sub_element_map = dict(
                pol_P = mirror_P,
                pol_S = mirror_S,
            ),
            select_map = dict(
                pol_S = PolS,
                pol_P = PolP,
            ),
            **kwargs
        )


class HarmonicMirror(MirrorSelectionStack):
    def __init__(
        self,
        mirror_H1,
        mirror_H2,
        **kwargs
    ):
        kH1 = self.system.F_carrier_1064
        kH2 = 2 * kH1
        super(HarmonicMirror, self).__init__(
            sub_element_map = dict(
                H1 = mirror_H1,
                H2 = mirror_H2,
            ),
            select_map = dict(
                H1 = kH1,
                H2 = kH2,
            ),
            **kwargs
        )




