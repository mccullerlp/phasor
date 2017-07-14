# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from ..utilities.future_from_2 import str
#from phasor.utilities.print import print

import declarative

from .dictionary_keys import (
    DictKey,
    FrequencyKey,
)


from . import bases


ElementKey = u'▲'
PortKey = u'🔌'
PostBondKey = u'№'

ClassicalFreqKey = u'𝓕'


class PortRawBase(bases.SystemElementBase):
    typename = None

    @declarative.dproperty
    def sname(self, val = declarative.NOARG):
        if val is declarative.NOARG:
            val = self.name_child
        return val

    @declarative.dproperty
    def element(self):
        return self.parent


class PortInRaw(PortRawBase):
    @declarative.dproperty
    def i(self):
        #pkey = self.element.name_system + self.sname + '.i'
        pkey = DictKey({
            ElementKey : self.element.name_system,
            PortKey    : self.sname + u'⥳',
        })
        self.system.port_add(self.element, pkey)
        return pkey


class PortOutRaw(PortRawBase):
    @declarative.dproperty
    def o(self):
        #pkey = self.element.name_system + self.sname + '.o'
        pkey = DictKey({
            ElementKey: self.element.name_system,
            PortKey   : self.sname + u'⥲',
        })
        self.system.port_add(self.element, pkey)
        return pkey


class PortInOutRaw(PortRawBase):
    @declarative.dproperty
    def i(self):
        #pkey = self.element.name_system + self.sname + '.i'
        pkey = DictKey({
            ElementKey: self.element.name_system,
            PortKey    : self.sname + u'⥳',
        })
        self.system.port_add(self.element, pkey)
        return pkey

    @declarative.dproperty
    def o(self):
        #pkey = self.element.name_system + self.sname + '.o'
        pkey = DictKey({
            ElementKey: self.element.name_system,
            PortKey   : self.sname + u'⥲',
        })
        self.system.port_add(self.element, pkey)
        return pkey


class PortNodeRaw(PortRawBase):
    @declarative.dproperty
    def node(self):
        #pkey = self.element.name_system + self.sname + '.i'
        pkey = DictKey({
            ElementKey: self.element.name_system,
            PortKey    : self.sname + u'●',
        })
        self.system.port_add(self.element, pkey)
        return pkey

    @declarative.dproperty
    def i(self):
        return self.node

    @declarative.dproperty
    def o(self):
        return self.node


class PortIndirect(bases.SystemElementBase):
    """
    Holds an inner port and forwards bonding calls to it.
    Contains its own chain_next reference though.
    Used to expose inner ports in composite objects.
    """
    #Decide how this should remember port connection data for displaying

    @declarative.dproperty
    def inner_port(self, port):
        return port

    @declarative.mproperty
    def bond_key(self):
        return self.inner_port.bond_key

    def bond(self, other):
        self.inner_port.bond(other)

    def bond_inform(self, other_key):
        self.inner_port.bond_inform(other_key)

    def bond_completion(self):
        return self.inner_port.bond_completion()

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

