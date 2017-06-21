# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from phasor.utilities.print import print
import declarative
from collections import defaultdict

from ..base import (
    CouplerBase,
)

from . import ports

from .bases import (
    SystemElementBase,
    PTREE_ASSIGN,
)


class TransferFunctionMIMO(CouplerBase, SystemElementBase):
    def __init__(
            self,
            port_pair_xfers,
            max_freq = None,
            **kwargs
    ):
        super(TransferFunctionMIMO, self).__init__(**kwargs)
        self.ps_In  = declarative.Bunch()
        self.O  = declarative.Bunch()

        PTREE_ASSIGN(self).max_freq = max_freq
        PTREE_ASSIGN(self).port_pair_xfers = port_pair_xfers

        for (iname, oname), xfer in list(self.port_pair_xfers.items()):
            if iname not in self.ps_In:
                self.ps_In[iname] = ports.SignalInPort(sname = iname)
            if oname not in self.O:
                self.O[iname] = ports.SignalOutPort(sname = oname)
        return

    def system_setup_ports(self, ports_algorithm):
        for (iname, oname), xfer in list(self.port_pair_xfers.items()):
            for kfrom in ports_algorithm.port_update_get(self.ps_In[iname].i):
                if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                    continue
                ports_algorithm.port_coupling_needed(self.O[oname].o, kfrom)
            for kto in ports_algorithm.port_update_get(self.O[oname].o):
                if self.system.classical_frequency_test_max(kto, self.max_freq):
                    continue
                ports_algorithm.port_coupling_needed(self.ps_In[iname].i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        dd = defaultdict(dict)
        for (iname, oname), xfer in list(self.port_pair_xfers.items()):
            dd[iname][oname] = xfer

        for iname, oxD in list(dd.items()):
            for kfrom in matrix_algorithm.port_set_get(self.ps_In[iname].i):
                if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                    continue
                freq = self.system.classical_frequency_extract(kfrom)
                for oname, xfer in list(oxD.items()):
                    pgain = xfer(freq)
                    matrix_algorithm.port_coupling_insert(
                        self.ps_In[iname].i,
                        kfrom,
                        self.O[oname].o,
                        kfrom,
                        pgain,
                    )
        return
