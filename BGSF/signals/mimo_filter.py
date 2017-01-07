# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

import numpy as np

#from numbers import Number
#import warnings

from ..base import (
    CouplerBase,
)

from .ports import (
    SignalPortHolderIn,
    SignalPortHolderOut,
)

from .bases import (
    SystemElementBase,
    OOA_ASSIGN,
)

from declarative.bunch import (
    Bunch,
)

from collections import defaultdict


class TransferFunctionMIMO(CouplerBase, SystemElementBase):
    def __init__(
            self,
            port_pair_xfers,
            max_freq = None,
            **kwargs
    ):
        super(TransferFunctionMIMO, self).__init__(**kwargs)
        self.I  = Bunch()
        self.O  = Bunch()

        OOA_ASSIGN(self).max_freq = max_freq
        OOA_ASSIGN(self).port_pair_xfers = port_pair_xfers

        for (iname, oname), xfer in self.port_pair_xfers.iteritems():
            if iname not in self.I:
                self.I[iname] = SignalPortHolderIn(self,  x = iname)
            if oname not in self.O:
                self.O[iname] = SignalPortHolderOut(self, x = oname)
        return

    def system_setup_ports(self, ports_algorithm):
        for (iname, oname), xfer in self.port_pair_xfers.iteritems():
            for kfrom in ports_algorithm.port_update_get(self.I[iname].i):
                if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                    continue
                ports_algorithm.port_coupling_needed(self.O[oname].o, kfrom)
            for kto in ports_algorithm.port_update_get(self.O[oname].o):
                if self.system.classical_frequency_test_max(kto, self.max_freq):
                    continue
                ports_algorithm.port_coupling_needed(self.I[iname].i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        dd = defaultdict(dict)
        for (iname, oname), xfer in self.port_pair_xfers.iteritems():
            dd[iname][oname] = xfer

        for iname, oxD in dd.iteritems():
            for kfrom in matrix_algorithm.port_set_get(self.I[iname].i):
                if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                    continue
                freq = self.system.classical_frequency_extract(kfrom)
                for oname, xfer in oxD.iteritems():
                    pgain = xfer(freq)
                    matrix_algorithm.port_coupling_insert(
                        self.I[iname].i,
                        kfrom,
                        self.O[oname].o,
                        kfrom,
                        pgain,
                    )
        return
