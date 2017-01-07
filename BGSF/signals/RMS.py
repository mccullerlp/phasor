# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

#import numpy as np

#from numbers import Number
#import warnings

from ..math.key_matrix import (
    DictKey,
    FrequencyKey,
)

from ..base import (
    CouplerBase,
)

from .bases import (
    SystemElementBase,
)

from .ports import (
    SignalPortHolderIn,
    SignalPortHolderOut,
    ClassicalFreqKey,
)


class MeanSquareMixer(CouplerBase, SystemElementBase):
    def __init__(
            self,
            **kwargs
    ):
        super(MeanSquareMixer, self).__init__(**kwargs)
        self.I   = SignalPortHolderIn(self,  x = 'I')
        self.MS = SignalPortHolderOut(self, x = 'MS')
        return

    def system_setup_ports(self, system):
        for kfrom in system.port_update_get(self.I.i):
            f_key = kfrom[ClassicalFreqKey]
            kfromN = kfrom.replace_keys({ClassicalFreqKey: -f_key})
            if system.reject_classical_frequency_order(-f_key):
                continue
            system.port_coupling_needed(self.I.i, kfromN)
        #only outputs the total MS at DC
        kto = DictKey({ClassicalFreqKey : FrequencyKey({})})
        system.port_coupling_needed(self.MS.o, kto)
        return

    def system_setup_coupling(self, system):
        kto = DictKey({ClassicalFreqKey : FrequencyKey({})})
        already_keys = set()
        for kfromP in system.port_set_get(self.I.i):
            if kfromP in already_keys:
                continue
            already_keys.add(kfromP)
            f_key = kfromP[ClassicalFreqKey]
            if f_key.DC_is():
                system.port_coupling_insert(
                    self.I.i, kfromP,
                    self.MS.o, kto,
                    1, (self.I.i, kfromP),
                )
            else:
                kfromN = kfromP.replace_keys({ClassicalFreqKey: -f_key})
                already_keys.add(kfromN)
                if system.reject_classical_frequency_order(-f_key):
                    continue
                system.nonlinear_triplet_insert(
                    (self.I.i, kfromP),
                    (self.I.i, kfromN),
                    (self.MS.o, kto),
                    1 / 2,
                )
        return


class SquareRootFunction(CouplerBase, SystemElementBase):
    def __init__(
            self,
            **kwargs
    ):
        super(SquareRootFunction, self).__init__(**kwargs)
        self.I   = SignalPortHolderIn(self,  x = 'I')
        self.sqroot = SignalPortHolderOut(self, x = 'sqroot')
        return

    def system_setup_ports(self, system):
        for kfrom in system.port_update_get(self.I.i):
            f_key = kfrom[ClassicalFreqKey]
            kfromN = kfrom.replace_keys({ClassicalFreqKey: -f_key})
            if system.reject_classical_frequency_order(-f_key):
                continue
            system.port_coupling_needed(self.I.i, kfromN)
        #only outputs the total RMS at DC
        kto = DictKey({ClassicalFreqKey : FrequencyKey({})})
        system.port_coupling_needed(self.RMS.o, kto)
        return

    def system_setup_coupling(self, system):
        kto = DictKey({ClassicalFreqKey : FrequencyKey({})})
        already_keys = set()
        for kfromP in system.port_set_get(self.I.i):
            if kfromP in already_keys:
                continue
            already_keys.add(kfromP)
            f_key = kfromP[ClassicalFreqKey]
            if f_key.DC_is():
                system.port_coupling_insert(
                    self.I.i, kfromP,
                    self.RMS.o, kto,
                    1, (self.I.i, kfromP),
                )
            else:
                kfromN = kfromP.replace_keys({ClassicalFreqKey: -f_key})
                already_keys.add(kfromN)
                if system.reject_classical_frequency_order(-f_key):
                    continue
                system.nonlinear_triplet_insert(
                    (self.I.i, kfromP),
                    (self.I.i, kfromN),
                    (self.RMS.o, kto),
                    1 / 2,
                )
        return

class RMSMixer(CouplerBase, SystemElementBase):
    #TODO
    def __init__(
            self,
            **kwargs
    ):
        super(RMSMixer, self).__init__(**kwargs)
        self.I   = SignalPortHolderIn(self,  x = 'I')
        self.RMS = SignalPortHolderOut(self, x = 'RMS')
        self.system.virtual_link
        raise NotImplementedError()
        return

    def system_setup_ports(self, system):
        for kfrom in system.port_update_get(self.I.i):
            f_key = kfrom[ClassicalFreqKey]
            kfromN = kfrom.replace_keys({ClassicalFreqKey: -f_key})
            if system.reject_classical_frequency_order(-f_key):
                continue
            system.port_coupling_needed(self.I.i, kfromN)
        #only outputs the total RMS at DC
        kto = DictKey({ClassicalFreqKey : FrequencyKey({})})
        system.port_coupling_needed(self.RMS.o, kto)
        return

    def system_setup_coupling(self, system):
        kto = DictKey({ClassicalFreqKey : FrequencyKey({})})
        already_keys = set()
        for kfromP in system.port_set_get(self.I.i):
            if kfromP in already_keys:
                continue
            already_keys.add(kfromP)
            f_key = kfromP[ClassicalFreqKey]
            if f_key.DC_is():
                system.port_coupling_insert(
                    self.I.i, kfromP,
                    self.RMS.o, kto,
                    1, (self.I.i, kfromP),
                )
            else:
                kfromN = kfromP.replace_keys({ClassicalFreqKey: -f_key})
                already_keys.add(kfromN)
                if system.reject_classical_frequency_order(-f_key):
                    continue
                system.nonlinear_triplet_insert(
                    (self.I.i, kfromP),
                    (self.I.i, kfromN),
                    (self.RMS.o, kto),
                    1 / 2,
                )
        return
