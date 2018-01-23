# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from phasor.utilities.print import print
import declarative

from .. import mechanical

from . import ports
from . import selectors


class MirrorSelectionStack(
    ports.OpticalDegenerate4PortMixin,
    selectors.OpticalSelectionStack,
):

    @declarative.dproperty
    def AOI_deg(self, val = 0):
        return val

    @declarative.dproperty
    def Z(self):
        # since the sub_elements will be bound, require more connections before autoterminating
        N = len(self.sub_element_map)
        mechport = mechanical.MechanicalPortDriven(
            t_terminator = mechanical.TerminatorShorted,
            require_N_autoterminate = N + 1,
        )
        return mechport

    @declarative.dproperty
    def port_set(self):
        if self.AOI_deg == 0:
            return set(['po_Fr', 'po_Bk'])
        else:
            return set(['po_FrA', 'po_FrB', 'po_BkA', 'po_BkB'])

    def __build__(self):
        super().__build__()

        for sname, sub_element in self.sub_element_map.items():
            self.Z.bond(sub_element.Z)

        #TODO, HACK!
        if self.AOI_deg == 0:
            self.po_Fr.pchain = self.po_Bk
            self.po_Bk.pchain = self.po_Fr
            self.po_FrA = self.po_Fr
            self.po_FrB = self.po_Fr
            self.po_BkA = self.po_Bk
            self.po_BkB = self.po_Bk
        else:
            self.po_FrA.pchain = self.po_BkA
            self.po_BkA.pchain = self.po_FrA
            self.po_FrB.pchain = self.po_BkB
            self.po_BkB.pchain = self.po_FrB

        #TODO, combine mechanicals


class PolarizingMirror(MirrorSelectionStack):
    @declarative.dproperty
    def mirror_P(self, val):
        #PropertyTransforming action
        val.adjust_safe(
            AOI_deg         = self.AOI_deg,
        )
        return val

    @declarative.dproperty
    def mirror_S(self, val):
        #PropertyTransforming action
        val.adjust_safe(
            AOI_deg         = self.AOI_deg,
        )
        return val

    @declarative.dproperty
    def sub_element_map(self):
        return dict(
            mirror_S = self.mirror_S,
            mirror_P = self.mirror_P,
        )

    @declarative.dproperty
    def select_map(self):
        return dict(
            mirror_S = ports.PolS,
            mirror_P = ports.PolP,
        )


class PolarizingSelector(selectors.GenericSelector):
    @declarative.dproperty
    def select_map(self):
        return dict(
            S = ports.PolS,
            P = ports.PolP,
        )


class HarmonicMirror(MirrorSelectionStack):
    @declarative.dproperty
    def kH1(self):
        return ports.DictKey({ports.OpticalFreqKey : self.system.FD_carrier_1064})

    @declarative.dproperty
    def kH2(self):
        return ports.DictKey({ports.OpticalFreqKey : 2 * self.system.FD_carrier_1064})

    @declarative.dproperty
    def mirror_H1(self, val):
        #PropertyTransforming action
        val.adjust_safe(
            AOI_deg         = self.AOI_deg,
        )
        return val

    @declarative.dproperty
    def mirror_H2(self, val):
        #PropertyTransforming action
        val.adjust_safe(
            AOI_deg         = self.AOI_deg,
        )
        return val

    @declarative.dproperty
    def sub_element_map(self):
        return dict(
            mirror_H1 = self.mirror_H1,
            mirror_H2 = self.mirror_H2,
        )

    @declarative.dproperty
    def select_map(self):
        return dict(
            mirror_H1 = self.kH1,
            mirror_H2 = self.kH2,
        )


class HarmonicSelector(selectors.GenericSelector):
    @declarative.dproperty
    def kH1(self):
        return ports.DictKey({ports.OpticalFreqKey : self.system.FD_carrier_1064})

    @declarative.dproperty
    def kH2(self):
        return ports.DictKey({ports.OpticalFreqKey : 2 * self.system.FD_carrier_1064})

    @declarative.dproperty
    def select_map(self):
        return dict(
            H1 = self.kH1,
            H2 = self.kH2,
        )

