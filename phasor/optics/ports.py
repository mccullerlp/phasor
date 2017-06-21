# -*- coding: utf-8 -*-
from __future__ import (division, print_function)
#from builtins import object

import declarative as declarative

from ..base import visitors as VISIT

from ..base.ports import(
    DictKey,
    FrequencyKey,
    ElementKey,
    PortKey,
    ClassicalFreqKey,
    PortInOutRaw,
    PortIndirect,
)

from ..signals.ports import(
    SignalInPort,
    SignalOutPort,
)

from . import bases

QuantumKey = u'Ψ'
RAISE = DictKey({QuantumKey: u'↑'})
LOWER = DictKey({QuantumKey: u'↓'})

PolKEY = u'⤱'
PolS = DictKey({PolKEY: 'S'})
PolP = DictKey({PolKEY: 'P'})

OpticalFreqKey = u'F⇝'


class OpticalDegenerate4PortMixin(object):

    @declarative.dproperty
    def AOI_deg(self, val = 0):
        val = self.ctree.setdefault('AOI_deg', val)
        return val

    @declarative.mproperty
    def is_4_port(self):
        if self.AOI_deg == 0:
            val = False
        else:
            val = True
        return val


class OpticalPortRaw(PortInOutRaw):
    typename = 'optical'


class OpticalPort(OpticalPortRaw, bases.SystemElementBase):
    _building_bonded = True
    _bond_partner = None
    typename = 'optical'

    def _complete(self):
        if not super(OpticalPort, self)._complete():
            prein = self.inst_preincarnation
            if prein is not None:
                if prein._bond_partner is not None and not prein._building_bonded:
                    #auto-insert bond partner as it was inserted during building
                    getnew = self.root[prein._bond_partner.name_system]
                    self._bond_partner = getnew
                    assert(self.root is getnew.root)
        return

    @declarative.mproperty
    def bond_key(self):
        return self

    def bond(self, other):
        self.bond_inform(other.bond_key)
        other.bond_inform(self)

    def bond_sequence(self, *others):
        return self.system.bond_sequence(self, *others)

    def bond_inform(self, other_key):
        #default to not storing an override since most bonds will occur during building
        if not self.building:
            self._building_bonded = False

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
        from .vacuum import VacuumTerminator
        self.own.terminator = VacuumTerminator()
        self.system.bond(self, self.terminator.po_Fr)
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
            return super(OpticalPort, self).targets_list(typename)

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


