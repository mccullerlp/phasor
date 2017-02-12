# -*- coding: utf-8 -*-
from __future__ import (division, print_function)
from builtins import object

import declarative as decl

from ..math.key_matrix import DictKey

from ..base.ports import(
    ElementKey,
    PortKey,
    MechKey,
    ClassicalFreqKey,
    PortHolderInBase,
    PortHolderOutBase,
    PortHolderInOutBase,
    MechanicalPortHolderIn,
    MechanicalPortHolderOut,
)  # NOQA

from ..signals.ports import(
    SignalPortHolderIn,
    SignalPortHolderOut,
)

QuantumKey = u'Ψ'
RAISE = DictKey({QuantumKey: u'↑'})
LOWER = DictKey({QuantumKey: u'↓'})

PolKEY = u'⤱'
PolS = DictKey({PolKEY: 'S'})
PolP = DictKey({PolKEY: 'P'})

OpticalFreqKey = u'F⇝'


class OpticalPortHolderInOut(PortHolderInOutBase):
    def autoterminations(self, port_map):
        #I don't like having to import from here, but what can you do...
        from .vacuum import VacuumTerminator
        port_map[self.i] = (self, VacuumTerminator)


class OpticalDegenerate4PortMixin(object):

    @decl.dproperty
    def AOI_deg(self, val = 0):
        val = self.ooa_params.setdefault('AOI_deg', val)
        return val

    @decl.mproperty
    def is_4_port(self):
        if self.AOI_deg == 0:
            val = False
        else:
            val = True
        return val
