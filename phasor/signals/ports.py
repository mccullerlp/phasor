# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from ..utilities.future_from_2 import str
#from phasor.utilities.print import print
import declarative

from ..base.ports import (
    PortInRaw,
    PortOutRaw,
    PortInOutRaw,
    PortNodeRaw,
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

class SignalNodePortRaw(PortNodeRaw):
    typename = 'signal_node'
    #TODO remove when possible
    multiple_attach = True

class SignalCommonPortBase(bases.SystemElementBase):
    @declarative.mproperty
    def bond_key(self):
        return self

    def bond(self, other):
        self.bond_inform(other.bond_key)
        other.bond_inform(self)

    def bond_sequence(self, *others):
        return self.system.bond_sequence(self, *others)

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

    def targets_list(self, typename):
        if typename == VISIT.bond_completion:
            #TODO make a system algorithm object for this
            self.bond_completion()
            return self
        else:
            return super(SignalCommonPortBase, self).targets_list(typename)

class SignalInPortBase(bases.SystemElementBase):
    def _complete(self):
        if not super(SignalInPortBase, self)._complete():
            prein = self.inst_preincarnation
            if prein is not None:
                for built, bpartner in zip(prein._bond_partners_in_building, prein._bond_partners_in):
                    if not built:
                        new_bpartner = self.root[bpartner.name_system]
                        self._bond_partners_in.append(new_bpartner)
                        assert(self.root is new_bpartner.root)
                        self._bond_partners_in_building.append(built)
        return

    @declarative.mproperty
    def _bond_partners_in(self):
        return []

    @declarative.mproperty
    def _bond_partners_in_building(self):
        return []

    def bond_inform(self, other_key):
        #TODO make this smarter
        self._bond_partners_in.append(other_key)
        if self.building:
            self._bond_partners_in_building.append(True)
        else:
            self._bond_partners_in_building.append(False)

    def bond_completion(self):
        for partner in self._bond_partners_in:
            self.system.bond_completion_raw(self, partner, self)
        return


class SignalInPort(
        SignalInPortRaw,
        SignalInPortBase,
        SignalCommonPortBase
):
    typename = 'signal_in'


class SignalOutPortBase(bases.SystemElementBase):
    def _complete(self):
        if not super(SignalOutPortBase, self)._complete():
            prein = self.inst_preincarnation
            if prein is not None:
                for built, bpartner in zip(prein._bond_partners_out_building, prein._bond_partners_out):
                    if not built:
                        new_bpartner = self.root[bpartner.name_system]
                        self._bond_partners_out.append(new_bpartner)
                        assert(self.root is new_bpartner.root)
                        self._bond_partners_out_building.append(built)
        return

    @declarative.mproperty
    def _bond_partners_out(self):
        return []

    @declarative.mproperty
    def _bond_partners_out_building(self):
        return []

    def bond_inform(self, other_key):
        #TODO make this smarter
        self._bond_partners_out.append(other_key)
        if self.building:
            self._bond_partners_out_building.append(True)
        else:
            self._bond_partners_out_building.append(False)

    def bond_completion(self):
        #it should have been autoterminated if anything
        for partner in self._bond_partners_out:
            self.system.bond_completion_raw(self, partner, self)
        return

class SignalOutPort(
        SignalOutPortRaw,
        SignalOutPortBase,
        SignalCommonPortBase
):
    typename = 'signal_out'


class SignalNode(SignalNodePortRaw, SignalInPortBase, SignalOutPortBase, SignalCommonPortBase):
    typename = 'signal_node'

    def bond_inform(self, other_key):
        #TODO make this smarter
        if other_key.typename == 'signal_in':
            self._bond_partners_out.append(other_key)
            if self.building:
                self._bond_partners_out_building.append(True)
            else:
                self._bond_partners_out_building.append(False)
        elif other_key.typename == 'signal_out':
            self._bond_partners_in.append(other_key)
            if self.building:
                self._bond_partners_in_building.append(True)
            else:
                self._bond_partners_in_building.append(False)
        else:
            raise RuntimeError("Can't handle port of type: {0}".format(other_key.typename))

    def bond_completion(self):
        #it should have been autoterminated if anything
        for partner in self._bond_partners_out:
            self.system.bond_completion_raw(self, partner, self)
        for partner in self._bond_partners_in:
            self.system.bond_completion_raw(self, partner, self)
        return
