# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import declarative

#from ..math.key_matrix import DictKey

from ..utilities.future_from_2 import str, super
from ..base.ports import (
    DictKey,
    FrequencyKey,
    ElementKey,
    PortKey,
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

    def _complete(self):
        if not super()._complete():
            prein = self.inst_preincarnation
            if prein is not None:
                for built, bpartner in zip(prein._bond_partners_building, prein._bond_partners):
                    if not built:
                        new_bpartner = self.root[bpartner.name_system]
                        self._bond_partners.append(new_bpartner)
                        assert(self.root is new_bpartner.root)
                        self._bond_partners_building.append(built)
        return

    @declarative.mproperty
    def bond_key(self):
        return self

    @declarative.mproperty
    def _bond_partners(self):
        return []

    @declarative.mproperty
    def _bond_partners_building(self):
        return []

    def bond_sequence(self, *others):
        return self.system.bond_sequence(self, *others)

    def bond(self, other):
        self.bond_inform(other.bond_key)
        other.bond_inform(self)

    def bond_inform(self, other_key):
        #TODO make this smarter
        self._bond_partners.append(other_key)
        if self.building:
            self._bond_partners_building.append(True)
        else:
            self._bond_partners_building.append(False)

    def bond_completion(self):
        if len(self._bond_partners) == 1:
            self.system.bond_completion_raw(self, self._bond_partners[0], self)
        elif len(self._bond_partners) == 0:
            raise RuntimeError("Must be Terminated")
        else:
            from .elements import Connection
            b_p_set = set(self._bond_partners)
            self.own.connection = Connection(
                N_ports = 1 + len(b_p_set)
            )
            self.system._include(self.connection)
            self.connection.pe_0.bond_inform(self)
            self.system.bond_completion_raw(self, self.connection.pe_0, self)
            self.connection.pe_0.bond_completion()
            for idx, partner in enumerate(b_p_set):
                #TODO not sure if ps_In like the connection object not knowing who it is bound to
                #maybe make a more explicit notification for the raw bonding
                port = self.connection.ports_electrical[idx + 1]
                #print("PORTSSS", port)
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
        self.own.terminator = self.t_terminator()
        self.system.bond(self, self.terminator.pe_A)
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
            return super().targets_list(typename)

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


