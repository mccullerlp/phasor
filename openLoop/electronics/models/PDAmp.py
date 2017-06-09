"""
"""
from __future__ import (division, print_function)

import declarative as decl

from openLoop import electronics
from openLoop import readouts
from . import vendor_opamps


class PDTransimpedance(electronics.ElectricalElementBase):
    def __build__(self):
        self.own.PD = electronics.CurrentSourceBalanced()
        self.own.C_PD = electronics.SeriesCapacitor(
            capacitance_Farads = 20e-12,
        )
        self.C_PD.A.bond(self.PD.A)
        self.C_PD.B.bond(self.PD.B)
        self.own.PDT = electronics.TerminatorShorted()
        self.PDT.A.bond(self.PD.B)

        self.own.RTransF = electronics.SeriesResistor(
            resistance_Ohms = 10e3,
        )

        self.own.amp = vendor_opamps.Op27()
        self.own.amp_in_p = electronics.TerminatorShorted()
        self.system.bond(self.amp_in_p.A, self.amp.in_p)
        self.RTransF.A.bond(self.amp.in_n)
        self.PD.A.bond(self.amp.in_n)

        self.amp.out.bond(self.RTransF.B)

        self.own.VOutTrans = electronics.VoltageReadout(
            terminal = self.amp.out,
        )
        self.own.VOutTrans_AC = readouts.ACReadout(
            portD = self.PD.I.i,
            portN = self.VOutTrans.V.o,
        )

