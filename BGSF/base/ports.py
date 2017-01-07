# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

from .elements import SystemElementBase

from ..math.key_matrix import DictKey


ElementKey = u'▲'
PortKey = u'🔌'
MechKey = u'⌖'

ClassicalFreqKey = u'F'


class PortHolderBase(object):
    __slots__ = ('element',)
    _port_key = PortKey

    multiple_attach = False

    def autoterminations(self, port_map):
        return


class PortHolderInBase(PortHolderBase):
    __slots__ = ('i', '_x')
    def __init__(self, element, x):
        if not (isinstance(element, SystemElementBase)):
            print(element)
            assert(False)
        self.element = element
        self._x = x
        self.i = DictKey({
            ElementKey: self.element,
            self._port_key: x + u'⥳',
        })
        self.element.owned_ports[self.i] = self
        okey = self.element.owned_port_keys.setdefault(self.key, self)
        assert(okey is self)

    @property
    def key(self):
        return self._x

    def __repr__(self):
        return u"{0}.{1}".format(self.element, self._x.encode('utf-8')).encode('utf-8')


class PortHolderOutBase(PortHolderBase):
    __slots__ = ('o', '_x')
    def __init__(self, element, x):
        if not (isinstance(element, SystemElementBase)):
            print(element)
            assert(False)
        self.element = element
        self._x = x
        self.o = DictKey({
            ElementKey: self.element,
            self._port_key: x + u'⥲',
        })
        self.element.owned_ports[self.o] = self
        okey = self.element.owned_port_keys.setdefault(self.key, self)
        assert(okey is self)

    @property
    def key(self):
        return self._x

    def __repr__(self):
        return "{0}.{1}".format(self.element, self._x)


class PortHolderInOutBase(PortHolderBase):
    __slots__ = ('i', 'o', '_x')
    def __init__(self, element, x):
        if not (isinstance(element, SystemElementBase)):
            print(element)
            assert(False)
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

    @property
    def key(self):
        return self._x

    def __repr__(self):
        return u"{0}.{1}".format(self.element, self._x).encode('utf-8')


class MechanicalPortHolderIn(PortHolderInBase):
    pass


class MechanicalPortHolderOut(PortHolderOutBase):
    pass
