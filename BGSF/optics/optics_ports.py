from __future__ import division
from collections import namedtuple

from .dictionary_keys import DictKey
from .optics_bases import OpticalCouplerBase
from declarative import (
    mproperty,
)


class PortHolderBase(object):
    __slots__ = ('element',)


class PortHolderIn(PortHolderBase):
    __slots__ = ('i')
    def __init__(self, element, i):
        self.element = element
        self.i = DictKey(obj = self.element, port = i)


class PortHolderOut(PortHolderBase):
    __slots__ = ('o')
    def __init__(self, element, o):
        self.element = element
        self.o = DictKey(obj = self.element, port = o)


class PortHolderInOut(PortHolderBase):
    __slots__ = ('i', 'o')
    def __init__(self, element, i, o):
        self.element = element
        self.i = DictKey(obj = self.element, port = i)
        self.o = DictKey(obj = self.element, port = o)

