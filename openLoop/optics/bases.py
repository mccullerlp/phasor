# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function

import declarative as decl

from ..base.bases import (
    NoiseBase,
    CouplerBase,
    SystemElementBase,
    PTREE_ASSIGN,
)

class OpticalElementBase(SystemElementBase):
    @decl.mproperty
    def symbols(self):
        return self.system.symbols


class OpticalNoiseBase(NoiseBase, OpticalElementBase):
    pass


class OpticalCouplerBase(CouplerBase, OpticalElementBase):
    pass
