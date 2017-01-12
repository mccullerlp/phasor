# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function

from ..base import (
    PortHolderBase,
)

from ..optics import (
    ClassicalFreqKey,
    OpticalFrequency,
    OpticalFreqKey,
)

from .base import LinearSystem


class OpticalSystem(LinearSystem):
    def __build__(self):
        super(OpticalSystem, self).__build__()

        self.sled.environment.my.F_carrier_1064 = OpticalFrequency(
            wavelen_m = 1064e-9,
            name = u'λIR',
        )
        self.F_carrier_1064 = self.sled.environment.F_carrier_1064
        return

    def optical_frequency_extract(self, key):
        iwavelen_m = 0
        freq_Hz = 0
        for F, n in list(key[ClassicalFreqKey].F_dict.items()):
            freq_Hz += n * F.F_Hz
        for F, n in list(key[OpticalFreqKey].F_dict.items()):
            iwavelen_m += n * F.iwavelen_m
        return iwavelen_m, freq_Hz

    def _optical_link_sequence_generic(self, funcname, idx_L, idx_R, first, *args):
        arg_iter = iter(args)
        if isinstance(first, PortHolderBase):
            next_src = first
        else:
            next_src = getattr(first, funcname)()[idx_R]
        for arg in arg_iter:
            if isinstance(arg, PortHolderBase):
                self.link(next_src, arg)
                break
            else:
                connection_pair = getattr(arg, funcname)()
                self.link(next_src, connection_pair[idx_L])

                #this signals that it is not the through device like a laser source or PD
                if len(connection_pair) == 1:
                    break
                else:
                    next_src = connection_pair[idx_R]
        # arg iter should be exhausted if we called break on the last one or didn't call break, so check with a for-loop on it
        for arg_past_end in arg_iter:
            raise RuntimeError("link sequence defined past a non-through element, {0}".format(arg))
        return

    def optical_link_sequence_EtoW(self, first, *args):
        return self._optical_link_sequence_generic('orient_optical_portsEW', 0, -1, first, *args)

    def optical_link_sequence_WtoE(self, first, *args):
        return self._optical_link_sequence_generic('orient_optical_portsEW', -1, 0, first, *args)

    def optical_link_sequence_NtoS(self, first, *args):
        return self._optical_link_sequence_generic('orient_optical_portsNS', 0, -1, first, *args)

    def optical_link_sequence_StoN(self, first, *args):
        return self._optical_link_sequence_generic('orient_optical_portsNS', -1, 0, first, *args)

    def optical_link_sequence_LtoR(self, first, *args):
        return self.optical_link_sequence_WtoE(first, *args)

    def optical_link_sequence_RtoL(self, first, *args):
        return self.optical_link_sequence_EtoW(first, *args)

    def optical_link_sequence_TtoB(self, first, *args):
        return self.optical_link_sequence_NtoS(first, *args)

    def optical_link_sequence_BtoT(self, first, *args):
        return self.optical_link_sequence_StoN(first, *args)
