# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function

import declarative
from declarative.utilities import SuperBase
from declarative import bunch

from . import autograft
from . import visitors as VISIT
import warnings


class Element(autograft.Element):
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

    def ctree_as_yaml(self):
        import yaml
        db = bunch.DeepBunchSingleAssign()
        db.update_recursive(self.ctree)
        return yaml.dump(db._mydict_resolved)

    #def insert(self, obj, name = None, invalidate = True):
    #    print("INSERT", obj, name, invalidate)
    #    super(Element, self).insert(obj, name = name, invalidate = invalidate)
    #    print("REG: ", self._registry_children)


class RootElement(Element, autograft.RootElement):
    pass


#TODO: clean up semantic of the Element vs. ElementBase name
class SystemElementBase(Element, SuperBase):
    def __init__(
        self,
        **kwargs
    ):
        #TODO, eventually remove this
        self.owned_ports = dict()
        self.owned_port_keys = dict()
        super(SystemElementBase, self).__init__(**kwargs)

    def __repr__(self):
        if self.name is not None:
            return "{cls}({name})".format(cls = self.__class__.__name__, name = self.name)
        return self.__class__.__name__ + '(<unknown>)'

    @declarative.dproperty
    def system(self):
        sys = self.parent.system
        return sys

    @declarative.dproperty
    def _include(self, val = declarative.NOARG):
        if val is declarative.NOARG:
            self.system.include(self)

    @declarative.mproperty
    def fully_resolved_name_tuple(self):
        if self.parent is None:
            ptup = ()
        else:
            ptup = self.parent.fully_resolved_name_tuple
        if self.name_child is not None:
            ptup = ptup + (self.name_child,)
        return ptup


class CouplerBase(SystemElementBase):
    def system_setup_coupling(self, system):
        return
    def system_setup_ports(self, system):
        return
    def system_setup_noise(self, system):
        return


class NoiseBase(SystemElementBase):
    @declarative.mproperty
    def name_noise(self, val = None):
        if val is None:
            return self.name_system
        else:
            return val + '[{0}]'.format(self.name_system)
    pass


class FrequencyBase(SystemElementBase):
    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return id(self) < id(other)
    pass


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


def PTREE_ASSIGN(obj):
    warnings.warn("PTREE_ASSIGN", DeprecationWarning)
    return OOABridge(obj, obj.ctree)
