# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from phasor.utilities.print import print
import declarative as decl

from ..base import (
    CouplerBase,
    SystemElementBase,
    NoiseBase,
    PTREE_ASSIGN,
)

class SignalElementBase(CouplerBase, SystemElementBase):
    @decl.mproperty
    def symbols(self):
        return self.system.symbols

