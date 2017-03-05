# -*- coding: utf-8 -*-
from __future__ import division, print_function
#from BGSF.utilities.print import print

import declarative

from .dictionary_keys import (
    DictKey,
    FrequencyKey,
)


from . import bases


ElementKey = u'▲'
PortKey = u'🔌'
MechKey = u'⌖'
PostBondKey = u'№'

ClassicalFreqKey = u'𝓕'


class PortHolderBase(declarative.OverridableObject):
    _port_key = PortKey

    multiple_attach = False

    def autoterminations(self, port_map):
        return

    @declarative.mproperty
    def key(self):
        return self._x

    pchain = None

    @declarative.mproperty
    def chain_next(self):
        if self.pchain is not None:
            if isinstance(self.pchain, str):
                return getattr(self.element, self.pchain)
            else:
                return self.pchain
        else:
            return None


class PortHolderInBase(PortHolderBase):
    def __init__(
            self,
            element,
            x,
            **kwargs
    ):
        super(PortHolderInBase, self).__init__(**kwargs)
        self.element = element
        self._x = x
        self.i = DictKey({
            ElementKey: self.element,
            self._port_key: x + u'⥳',
        })
        self.element.owned_ports[self.i] = self
        okey = self.element.owned_port_keys.setdefault(self.key, self)
        assert(okey is self)

    @declarative.mproperty
    def key(self):
        return self._x

    def __repr__(self):
        return u"{0}.{1}".format(self.element, self._x)


class PortHolderOutBase(PortHolderBase):
    def __init__(
            self,
            element,
            x,
            **kwargs
    ):
        super(PortHolderOutBase, self).__init__(**kwargs)
        self.element = element
        self._x = x
        self.o = DictKey({
            ElementKey: self.element,
            self._port_key: x + u'⥲',
        })
        self.element.owned_ports[self.o] = self
        okey = self.element.owned_port_keys.setdefault(self.key, self)
        assert(okey is self)

    @declarative.mproperty
    def key(self):
        return self._x

    def __repr__(self):
        return "{0}.{1}".format(self.element, self._x)


class PortHolderInOutBase(PortHolderBase):
    def __init__(
            self,
            element,
            x,
            **kwargs
    ):
        super(PortHolderInOutBase, self).__init__(**kwargs)
        self.element = element
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

    @declarative.mproperty
    def key(self):
        return self._x

    def __repr__(self):
        return u"{0}.{1}".format(self.element, self._x)


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
        pkey = DictKey({
            ElementKey : self.element,
            PortKey    : self.sname + u'⥳',
        })
        self.system.port_add(self.element, pkey)
        return pkey


class PortOutRaw(PortRawBase):
    @declarative.dproperty
    def o(self):
        pkey = DictKey({
            ElementKey: self.element,
            PortKey   : self.sname + u'⥲',
        })
        self.system.port_add(self.element, pkey)
        return pkey


class PortInOutRaw(PortRawBase):
    @declarative.dproperty
    def i(self):
        pkey = DictKey({
            ElementKey : self.element,
            PortKey    : self.sname + u'⥳',
        })
        self.system.port_add(self.element, pkey)
        return pkey

    @declarative.dproperty
    def o(self):
        pkey = DictKey({
            ElementKey: self.element,
            PortKey   : self.sname + u'⥲',
        })
        self.system.port_add(self.element, pkey)
        return pkey


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

