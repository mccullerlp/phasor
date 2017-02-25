# -*- coding: utf-8 -*-
from __future__ import (division, print_function)
from builtins import object

import declarative as decl

from ..base import visitors as VISIT

from ..base.ports import(
    DictKey,
    FrequencyKey,
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

from . import bases

QuantumKey = u'Ψ'
RAISE = DictKey({QuantumKey: u'↑'})
LOWER = DictKey({QuantumKey: u'↓'})

PolKEY = u'⤱'
PolS = DictKey({PolKEY: 'S'})
PolP = DictKey({PolKEY: 'P'})

OpticalFreqKey = u'F⇝'


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


class OpticalPortHolderInOut(bases.SystemElementBase):
    @decl.dproperty
    def sname(self, val = decl.NOARG):
        if val is decl.NOARG:
            val = self.name_child
        return val

    @decl.dproperty
    def element(self):
        return self.parent

    @decl.dproperty
    def i(self):
        pkey = DictKey({
            ElementKey: self.element,
            self._port_key: self.sname + u'⥳',
        })
        self.system.port_add(self.element, pkey)
        return pkey

    @decl.dproperty
    def o(self):
        pkey = DictKey({
            ElementKey: self.element,
            self._port_key: self.sname + u'⥲',
        })
        self.system.port_add(self.element, pkey)
        return pkey

    _bond_partner = None

    def bond(self, other):
        #TODO make this smarter
        if self._bond_partner is not None:
            raise RuntimeError("Multiple Bond Partners not Allowed")
        else:
            self._bond_partner = other

    def targets_list(self, typename):
        if typename == VISIT.ports_list:
            return [self.i, self.o]
        if typename == VISIT.ports_bond:
            #TODO do something about termination
            return [self.i, self.o]
        elif typename == VISIT.auto_terminate:
            if self._bond_partner is None:
                from .vacuum import VacuumTerminator
                self.my.terminator = VacuumTerminator()
                self.system.bond(self, self.terminator.Fr)
                return (self, self.terminator)
        return super(OpticalPortHolderInOut, self).targets_list(typename)

    _port_key = PortKey

    multiple_attach = False

    pchain = None

    @decl.mproperty
    def chain_next(self):
        if self.pchain is not None:
            if isinstance(self.pchain, str):
                return getattr(self.element, self.pchain)
            else:
                return self.pchain
        else:
            return None

