# -*- coding: utf-8 -*-
from __future__ import (division, print_function)
#from BGSF.utilities.print import print
import declarative

from ..base.ports import (
    PortInRaw,
    PortOutRaw,
    PortIndirect,
    ClassicalFreqKey,
    DictKey,
    FrequencyKey,
)

from ..base import visitors as VISIT
from ..base import bases


class SignalInPortRaw(PortInRaw):
    typename = 'signal_in'
    #TODO remove when possible
    multiple_attach = True

class SignalOutPortRaw(PortOutRaw):
    typename = 'signal_out'
    #TODO remove when possible
    multiple_attach = True


class SignalInPort(SignalInPortRaw, bases.SystemElementBase):
    typename = 'signal_in'

    def _complete(self):
        if not super(SignalInPort, self)._complete():
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
    def _bond_partners(self):
        return []

    @declarative.mproperty
    def _bond_partners_building(self):
        return []

    @declarative.mproperty
    def bond_key(self):
        return self

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
        for partner in self._bond_partners:
            self.system.bond_completion_raw(self, partner, self)
        return

    def targets_list(self, typename):
        if typename == VISIT.bond_completion:
            #TODO make a system algorithm object for this
            self.bond_completion()
            return self
        else:
            return super(SignalInPort, self).targets_list(typename)

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


class SignalOutPort(SignalOutPortRaw, bases.SystemElementBase):
    typename = 'signal_in'

    def _complete(self):
        if not super(SignalOutPort, self)._complete():
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
    def _bond_partners(self):
        return []

    @declarative.mproperty
    def _bond_partners_building(self):
        return []

    @declarative.mproperty
    def bond_key(self):
        return self

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
        #it should have been autoterminated if anything
        for partner in self._bond_partners:
            self.system.bond_completion_raw(self, partner, self)
        return

    def targets_list(self, typename):
        if typename == VISIT.bond_completion:
            #TODO make a system algorithm object for this
            self.bond_completion()
            return self
        else:
            return super(SignalOutPort, self).targets_list(typename)

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
