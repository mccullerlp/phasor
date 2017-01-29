# -*- coding: utf-8 -*-
from __future__ import (division, print_function)
#from BGSF.utilities.print import print

from ..base.ports import (
    PortHolderInBase,
    PortHolderOutBase,
    ClassicalFreqKey,
)

from ..math.key_matrix import (
    DictKey,
)


class SignalPortHolderIn(PortHolderInBase):
    multiple_attach = True
    pass


class SignalPortHolderOut(PortHolderOutBase):
    multiple_attach = True
    pass
