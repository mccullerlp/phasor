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
    PortInOutRaw,
    PortIndirect,
)  # NOQA

from ..signals.ports import (
    SignalInPort,
    SignalOutPort,
)

from ..base import visitors as VISIT
from ..base import bases


class ElectricalPortRaw(PortInOutRaw):
    typename = 'Electrical'


class ElectricalPort(ElectricalPortRaw, bases.SystemElementBase):
    typename = 'Electrical'

    @declarative.mproperty
    def bond_key(self):
        return self

    @declarative.mproperty
    def _bond_partners(self):
        return []

    def bond(self, other):
        self.bond_inform(other.bond_key)
        other.bond_inform(self)

    def bond_inform(self, other_key):
        #TODO make this smarter
        self._bond_partners.append(other_key)

    def bond_completion(self):
        if len(self._bond_partners) == 1:
            self.system.bond_completion_raw(self, self._bond_partners[0], self)
        elif len(self._bond_partners) == 0:
            raise RuntimeError("Must be Terminated")
        else:
            from .elements import Connection
            self.my.connection = Connection(
                N_ports = 1 + len(self._bond_partners)
            )
            self.system._include(self.connection)
            self.connection.p0.bond_inform(self)
            self.system.bond_completion_raw(self, self.connection.p0, self)
            self.connection.p0.bond_completion()
            for idx, partner in enumerate(self._bond_partners):
                #TODO not sure if I like the connection object not knowing who it is bound to
                #maybe make a more explicit notification for the raw bonding
                port = self.connection.ports_electrical[idx + 1]
                print("PORTSSS", port)
                self.system.bond_completion_raw(self, partner, port)
        return

    @declarative.mproperty
    def t_terminator(self, val = declarative.NOARG):
        if val is declarative.NOARG:
            from . import TerminatorOpen
            val = TerminatorOpen
        return val

    def auto_terminate(self):
        """
        Only call if this port has not been bonded
        """
        self.my.terminator = self.t_terminator()
        self.system.bond(self, self.terminator.Fr)
        return (self, self.terminator)

    def targets_list(self, typename):
        if typename == VISIT.bond_completion:
            #TODO make a system algorithm object for this
            self.bond_completion()
            return self
        elif typename == VISIT.auto_terminate:
            if not self._bond_partners:
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


