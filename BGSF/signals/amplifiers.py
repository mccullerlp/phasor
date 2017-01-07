# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

from ..base import (
    CouplerBase,
)

from declarative.bunch import (
    Bunch,
)

from .bases import (
    SystemElementBase,
    OOA_ASSIGN,
)

from .ports import (
    SignalPortHolderIn,
    SignalPortHolderOut,
)

from collections import defaultdict

class DistributionAmplifier(CouplerBase, SystemElementBase):
    def __init__(
            self,
            port_gains,
            **kwargs
    ):
        super(DistributionAmplifier, self).__init__(**kwargs)
        OOA_ASSIGN(self).port_gains = port_gains

        self.I  = SignalPortHolderIn(self,  x = 'LO')

        for pname in self.port_gains:
            setattr(self, pname, SignalPortHolderOut(self, x = pname))
        return

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.I.i):
            for pname in self.port_gains:
                port = getattr(self, pname)
                ports_algorithm.port_coupling_needed(port.o, kfrom)
        for pname in self.port_gains:
            port = getattr(self, pname)
            for kto in ports_algorithm.port_update_get(port.o):
                ports_algorithm.port_coupling_needed(self.I.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.I.i):
            for pname, pgain in self.port_gains.iteritems():
                port = getattr(self, pname)
                matrix_algorithm.port_coupling_insert(self.I.i,  kfrom, port.o, kfrom, pgain)
        return


class SummingAmplifier(CouplerBase, SystemElementBase):
    def __init__(
            self,
            port_gains,
            **kwargs
    ):
        super(SummingAmplifier, self).__init__(**kwargs)
        OOA_ASSIGN(self).port_gains = port_gains

        self.O  = SignalPortHolderOut(self,  x = 'LO')

        for pname in self.port_gains:
            setattr(self, pname, SignalPortHolderIn(self, x = pname))
        return

    def system_setup_ports(self, ports_algorithm):
        for kto in ports_algorithm.port_update_get(self.O.o):
            for pname in self.port_gains:
                port = getattr(self, pname)
                ports_algorithm.port_coupling_needed(port.i, kto)
        for pname in self.port_gains:
            port = getattr(self, pname)
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(self.O.o, kfrom)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for pname, pgain in self.port_gains.iteritems():
            port = getattr(self, pname)
            for kfrom in matrix_algorithm.port_set_get(port.i):
                matrix_algorithm.port_coupling_insert(port.i,  kfrom, self.O.o, kfrom, pgain)
        return


class MatrixAmplifier(CouplerBase, SystemElementBase):
    def __init__(
            self,
            port_pair_gains,
            **kwargs
    ):
        super(DistributionAmplifier, self).__init__(**kwargs)
        OOA_ASSIGN(self).port_pair_gains = port_pair_gains

        self.I  = Bunch()
        self.O  = Bunch()

        dd = defaultdict(dict)
        for (iname, oname), xfer in self.port_pair_xfers.iteritems():
            dd[iname][oname] = xfer
        self._dd = dd

        for (iname, oname), xfer in self.port_pair_gains.iteritems():
            if iname not in self.I:
                self.I[iname] = SignalPortHolderIn(self,  x = iname)
            if oname not in self.O:
                self.O[iname] = SignalPortHolderOut(self, x = oname)
        return

    def system_setup_ports(self, ports_algorithm):
        for (iname, oname), xfer in self.port_pair_gains.iteritems():
            for kfrom in ports_algorithm.port_update_get(self.I[iname].i):
                ports_algorithm.port_coupling_needed(self.O[oname].o, kfrom)
            for kto in ports_algorithm.port_update_get(self.O[oname].o):
                ports_algorithm.port_coupling_needed(self.I[iname].i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for iname, oxD in self._dd.iteritems():
            for kfrom in matrix_algorithm.port_set_get(self.I[iname].i):
                for oname, xfer in oxD.iteritems():
                    matrix_algorithm.port_coupling_insert(
                        self.I[iname].i,
                        kfrom,
                        self.O[oname].o,
                        kfrom,
                        xfer,
                    )
        return
