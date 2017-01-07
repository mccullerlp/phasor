# -*- coding: utf-8 -*-
"""
"""
from __future__ import division

from ..base.bases import (
    ElementBase,
    NoiseBase,
    CouplerBase,
)

from ..base.elements import (
    SystemElementBase,
    OOA_ASSIGN,
)

class OpticalElementBase(ElementBase):
    pass


class OpticalNoiseBase(NoiseBase, OpticalElementBase):
    pass


class OpticalCouplerBase(CouplerBase, OpticalElementBase):
    pass
