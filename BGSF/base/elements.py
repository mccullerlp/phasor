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


class SledConstructorInternal(object):
    __slots__ = ('cls', 'args', 'kwargs')
    def __init__(self, cls, args, kwargs):
        self.cls    = cls
        self.args   = args
        self.kwargs = kwargs

    #the "None" parameters are to prevent accidental override of these from the kwargs
    def adjust_safe(
            self,
            name           = None,
            parent = None,
            _sled_root     = None,
            **kwargs
    ):
        for aname, aval in list(kwargs.items()):
            prev = self.kwargs.setdefault(aname, aval)
            if prev != aval:
                raise RuntimeError("Assigning Constructor item {0}, to {1}, but previously assigned {2}".format(aname, aval, prev))

    #the "None" parameters are to prevent accidental override of these from the kwargs
    def adjust_defer(
            self,
            name           = None,
            parent = None,
            _sled_root     = None,
            **kwargs
    ):
        for aname, aval in list(kwargs.items()):
            self.kwargs.setdefault(aname, aval)

    #the "None" parameters are to prevent accidental override of these from the kwargs
    def adjust(
            self,
            name           = None,
            parent = None,
            _sled_root     = None,
            **kwargs
    ):
        for aname, aval in list(kwargs.items()):
            self.kwargs[aname] = aval

    def construct(
            self,
            parent,
            name,
            **kwargs_stack
    ):
        kwargs = dict(self.kwargs)
        kwargs.update(kwargs_stack)
        args   = self.args
        cls    = self.cls
        if 'name' not in kwargs:
            kwargs['name'] = name
        kwargs['parent'] = parent
        inst = super(SystemElementBase, cls).__new__(
            cls,
            *args,
            **kwargs
        )
        #because of the deferred construction, the __init__ function must be explicitely called
        try:
            inst.__init__(
                *args,
                **kwargs
            )
        except TypeError:
            print(inst, args, kwargs)
            raise
        return inst


PropertyTransforming.register(SledConstructorInternal)


def OOA_ASSIGN(obj):
    return OOABridge(obj, obj.ooa_params)


class SystemElementBase(ElementBase):
    """
    Physical elements MUST be assigned to a sled, even if it is the system sled.
    They have special object creation semantics such that the class does not fully
    create the object, it's creation is completed only on the sled
    """
    def __new__(
        cls, *args, **kwargs
    ):
        #TODO, not sure if I am happy with the _sled_root semantics
        sled_root = kwargs.get('_sled_root', False)
        if not sled_root:
            #TODO make this a class returned that gives sane error messages
            #for users not realizing the dispatch must happen
            constr = SledConstructorInternal(cls, args, kwargs)
            return constr
        else:
            inst = super(SystemElementBase, cls).__new__(
                cls,
                *args,
                **kwargs
            )
            #the __init__ function must not be explicitely called because python does this for us
            return inst

    def __init__(
            self,
            parent,
            name,
            vparent = None,
            _sled_root = False,
            **kwargs
    ):
        self.parent     = parent
        self.name       = name
        if vparent is None:
            vparent = parent
        if name is not None:
            self.ooa_params = vparent.ooa_params[name]
        else:
            self.ooa_params = vparent.ooa_params
        self.system     = vparent.system
        #annotation for automatic defect studies
        OOA_ASSIGN(self).type = self.__class__
        super(SystemElementBase, self).__init__(**kwargs)

    def __init_ooa__(
        self,
        parent,
        name,
        vparent = None,
        **kwargs
    ):
        """can call during init to ensure that methods are available for OOA_ASSIGN to operate. Idempotent"""
        if name == 'PD_P':
            assert(parent is not None)
        self.parent = parent
        if vparent is None:
            vparent = parent
        self.ooa_params = vparent.ooa_params[name]
        self.system     = vparent.system
        self.name           = name

    def linked_elements(self):
        return ()

    def __repr__(self):
        if self.name is not None:
            return self.name
        return self.__class__.__name__ + '(<unknown>)'

    @mproperty
    def fully_resolved_name_tuple(self):
        if self.parent is None:
            ptup = ()
        else:
            ptup = self.parent.fully_resolved_name_tuple
        if self.name is not None:
            ptup = ptup + (self.name,)
        return ptup

    @mproperty
    def fully_resolved_name(self):
        return ".".join(self.fully_resolved_name_tuple)

    def __setattr__(self, name, item):
        if isinstance(item, SledConstructorInternal):
            constructed_item = self.system._subsled_construct(self, name, item)
            super(SystemElementBase, self).__setattr__(name, constructed_item)
        else:
            super(SystemElementBase, self).__setattr__(name, item)
        return

    def include(self, name, constructor):
        constructed_item = self.system._subsled_construct(self, name, constructor)
        self.__dict__[name] = constructed_item
        return constructed_item


class SystemElementSled(SystemElementBase):
    pass

