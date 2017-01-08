# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

from ..base.ports import (
    PortHolderInBase,
    PortHolderOutBase,
    ClassicalFreqKey,
)

class SignalPortHolderIn(PortHolderInBase):
    multiple_attach = True
    pass


class SignalPortHolderOut(PortHolderOutBase):
    multiple_attach = True
    pass
