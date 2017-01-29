# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from BGSF.utilities.print import print
import declarative as decl

from ..base import (
    ElementBase,
    CouplerBase,
    SystemElementBase,
    OOA_ASSIGN,
)

class SignalElementBase(CouplerBase, ElementBase):
    @decl.mproperty
    def symbols(self):
        return self.system.symbols

