# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from builtins import object

import declarative as decl

#from ..math.key_matrix import DictKey

from ..base.ports import (
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

from ..signals.ports import (
    SignalPortHolderIn,
    SignalPortHolderOut,
)


class ElectricalPortHolderIn(PortHolderInBase):
    pass


class ElectricalPortHolderOut(PortHolderOutBase):
    pass


class ElectricalPortHolderInOut(PortHolderInOutBase):
    def autoterminations(self, port_map):
        #I don't like having to import from here, but what can you do...
        from .elements import TerminatorOpen
        port_map[self] = (self, TerminatorOpen)


