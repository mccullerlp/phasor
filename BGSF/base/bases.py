# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function

import declarative as decl
from declarative.utilities import SuperBase
import declarative.substrate as dsubstrate
from . import visitors as VISIT


class Element(dsubstrate.Element):
    def __mid_init__(self):
        super(Element, self).__mid_init__()
        with self.building:
            self.__build__()

    def __build__(self):
        return

    def targets_recurse(self, typename):
        dmap = []
        for cname, cobj in list(self._registry_children.items()):
            if isinstance(cobj, Element):
                dmap.extend(cobj.targets_recurse(typename))
        target_ret = self.targets_list(typename)
        if target_ret is not None:
            dmap.append(target_ret)
        return dmap

    def targets_list(self, typename):
        if typename == VISIT.self:
            return self
        return None
    #def insert(self, obj, name = None, invalidate = True):
    #    print("INSERT", obj, name, invalidate)
    #    super(Element, self).insert(obj, name = name, invalidate = invalidate)
    #    print("REG: ", self._registry_children)


class RootElement(Element, dsubstrate.RootElement):
    pass


class ElementBase(Element, SuperBase):
    def __init__(
        self,
        **kwargs
    ):
        self.owned_ports = dict()
        self.owned_port_keys = dict()
        super(ElementBase, self).__init__(**kwargs)

    def __repr__(self):
        if self.name is not None:
            return "{cls}({name})".format(cls = self.__class__.__name__, name = self.name)
        return self.__class__.__name__ + '(<unknown>)'

    @decl.dproperty
    def system(self):
        sys = self.parent.system
        return sys

    @decl.dproperty
    def _include(self, val = decl.NOARG):
        if val is decl.NOARG:
            self.system.include(self)

    @decl.mproperty
    def fully_resolved_name_tuple(self):
        if self.parent is None:
            ptup = ()
        else:
            ptup = self.parent.fully_resolved_name_tuple
        if self.name_child is not None:
            ptup = ptup + (self.name_child,)
        return ptup


class CouplerBase(ElementBase):
    def system_setup_coupling(self, system):
        return
    def system_setup_ports(self, system):
        return
    def system_setup_noise(self, system):
        return


class NoiseBase(ElementBase):
    pass


class FrequencyBase(ElementBase):
    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return id(self) < id(other)
    pass


