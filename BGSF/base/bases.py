# -*- coding: utf-8 -*-
"""
"""
from __future__ import division

from declarative import (
    dproperty,
)
from declarative.utilities import SuperBase
import declarative.substrate as dsubstrate


class Element(dsubstrate.Element):
    def __post_init__(self):
        super(Element, self).__post_init__()
        with self.building:
            self.__build__()

    def __build__(self):
        return


class RootElement(Element, dsubstrate.RootElement):
    pass


class ElementBase(Element, SuperBase):
    name = None

    def __init__(
        self,
        **kwargs
    ):
        self.owned_ports = dict()
        self.owned_port_keys = dict()
        super(ElementBase, self).__init__(**kwargs)

    def linked_elements(self):
        return ()

    def __repr__(self):
        if self.name is not None:
            return self.name
        return self.__class__.__name__ + '(<unknown>)'

    @dproperty
    def system(self):
        return self.parent.system


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
    pass


