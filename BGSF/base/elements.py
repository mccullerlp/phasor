# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
from builtins import object

from .bases import ElementBase

from declarative import (
    mproperty,
)

from declarative.properties import PropertyTransforming


class OOABridge(object):
    __slots__ = ('_dict', '_obj',)

    def __init__(self, obj, mydict):
        self._obj = obj
        self._dict = mydict

    def __setitem__(self, key, item):
        try:
            item = self._dict.setdefault(key, item)
            setattr(self._obj, key, item)
            return item
        except TypeError:
            raise TypeError("Can't insert {0} into {1} at key {2}".format(item, self._dict, key))

    def __setattr__(self, key, item):
        if key in self.__slots__:
            return super(OOABridge, self).__setattr__(key, item)
        return self.__setitem__(key, item)


def OOA_ASSIGN(obj):
    return OOABridge(obj, obj.ooa_params)


class SystemElementBase(ElementBase):
    """
    Physical elements MUST be assigned to a sled, even if it is the system sled.
    They have special object creation semantics such that the class does not fully
    create the object, it's creation is completed only on the sled
    """

    @mproperty
    def fully_resolved_name_tuple(self):
        if self.parent is None:
            ptup = ()
        else:
            ptup = self.parent.fully_resolved_name_tuple
        if self.name_child is not None:
            ptup = ptup + (self.name_child,)
        return ptup

    @mproperty
    def fully_resolved_name(self):
        ret = ".".join(self.fully_resolved_name_tuple)
        return ret

    def __setattr__(self, name, item):
        if isinstance(item, PropertyTransforming):
            setattr(self.my, name, item)
        else:
            super(SystemElementBase, self).__setattr__(name, item)
        return

    def include(self, name, constructor):
        constructed_item = self.system._subsled_construct(self, name, constructor)
        self.__dict__[name] = constructed_item
        return constructed_item


class SystemElementSled(SystemElementBase):
    pass

