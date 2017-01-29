# -*- coding: utf-8 -*-
"""
"""
from __future__ import division

import declarative as decl

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

    @decl.mproperty
    def symbols(self):
        return self.system.symbols

    pass


class OpticalNoiseBase(NoiseBase, OpticalElementBase):
    pass


class OpticalCouplerBase(CouplerBase, OpticalElementBase):
    pass
