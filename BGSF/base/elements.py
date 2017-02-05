# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
from builtins import object
#import declarative

from .bases import ElementBase


import warnings


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
    warnings.warn("OOA_ASSIGN", DeprecationWarning)
    return OOABridge(obj, obj.ooa_params)


class SystemElementBase(ElementBase):
    """
    Physical elements MUST be assigned to a sled, even if it is the system sled.
    They have special object creation semantics such that the class does not fully
    create the object, it's creation is completed only on the sled
    """


class SystemElementSled(SystemElementBase):
    pass

