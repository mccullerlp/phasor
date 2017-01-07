"""
"""
from __future__ import division


class OpticalElementBase(object):
    optical_types = None
    name = None

    def __init__(self, name = None):
        if name is not None:
            self.name = name

    def linked_elements(self):
        return ()

    def __repr__(self):
        if self.name is not None:
            return self.name
        return self.__class__.__name__ + '(<unknown>)'


class FrequencyBase(OpticalElementBase):
    pass


class OpticalLinkBase(OpticalElementBase):
    pass

class OpticalCouplerBase(OpticalElementBase):
    pass
