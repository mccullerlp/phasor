# -*- coding: utf-8 -*-
from __future__ import (division, print_function)
from builtins import object

import declarative as decl

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
    def __init__(
            self,
            element,
            x,
            parent,
            **kwargs
    ):
        super(OpticalPortHolderInOut, self).__init__(parent = parent, **kwargs)
        self.element = parent
        self._x = x
        self.i = DictKey({
            ElementKey: self.element,
            self._port_key: x + u'⥳',
        })
        self.o = DictKey({
            ElementKey: self.element,
            self._port_key: x + u'⥲',
        })
        self.element.owned_ports[self.i] = self
        self.element.owned_ports[self.o] = self
        okey = self.element.owned_port_keys.setdefault(self.key, self)
        assert(okey is self)

    def autoterminations(self, port_map):
        #I don't like having to import from here, but what can you do...
        from .vacuum import VacuumTerminator
        port_map[self.i] = (self, VacuumTerminator)

    @decl.mproperty
    def key(self):
        return self._x

    def __repr__(self):
        return u"{0}.{1}".format(self.element, self._x)
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

