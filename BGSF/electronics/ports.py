# -*- coding: utf-8 -*-
from __future__ import division, print_function
import declarative

#from ..math.key_matrix import DictKey

from ..base.ports import (
    DictKey,
    FrequencyKey,
    ElementKey,
    PortKey,
    MechKey,
    ClassicalFreqKey,
    PortHolderInBase,
    PortHolderOutBase,
    PortHolderInOutBase,
    PortInOutRaw,
    PortIndirect,
)  # NOQA

from ..signals.ports import (
    SignalPortHolderIn,
    SignalPortHolderOut,
)

from ..base import visitors as VISIT
from ..base import bases


class ElectricalPort(PortHolderInOutBase):
    def autoterminations(self, port_map):
        #I don't like having to import from here, but what can you do...
        from . import TerminatorOpen
        #TODO revisit, should maybe register "self" rather than "self.i"
        port_map[self.i] = (self, TerminatorOpen)


class ElectricalPortRaw(PortInOutRaw):
    typename = 'Electrical'


class ElectricalPort(ElectricalPortRaw, bases.SystemElementBase):
    _bond_partner = None
    typename = 'Electrical'

    @declarative.mproperty
    def bond_key(self):
        return self

    def bond(self, other):
        self.bond_inform(other.bond_key)
        other.bond_inform(self)

    def bond_inform(self, other_key):
        #TODO make this smarter
        if self._bond_partner is not None:
            raise RuntimeError("Multiple Bond Partners not Allowed")
        else:
            self._bond_partner = other_key

    def bond_completion(self):
        #it should have been autoterminated if anything
        assert(self._bond_partner is not None)

        #TODO make a system algorithm object for this
        self.system.bond_completion_raw(self, self._bond_partner, self)
        return

    def auto_terminate(self):
        """
        Only call if this port has not been bonded
        """
        from . import TerminatorOpen
        self.my.terminator = TerminatorOpen()
        self.system.bond(self, self.terminator.Fr)
        return (self, self.terminator)

    def targets_list(self, typename):
        if typename == VISIT.bond_completion:
            #TODO make a system algorithm object for this
            self.bond_completion()
            return self
        elif typename == VISIT.auto_terminate:
            if self._bond_partner is None:
                return self.auto_terminate()
        else:
            return super(ElectricalPort, self).targets_list(typename)

    pchain = None

    @declarative.mproperty
    def chain_next(self):
        if self.pchain is not None:
            if isinstance(self.pchain, str):
                return getattr(self.element, self.pchain)
            elif callable(self.pchain):
                return self.pchain()
            else:
                return self.pchain
        else:
            return None


