# -*- coding: utf-8 -*-
"""
"""
from __future__ import division


class ElementBase(object):
    name = None

    def __init__(
            self,
    ):
        self.owned_ports = dict()
        self.owned_port_keys = dict()

    def linked_elements(self):
        return ()

    def __repr__(self):
        if self.name is not None:
            return self.name
        return self.__class__.__name__ + '(<unknown>)'


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


