# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import declarative as decl

from phasor import electronics
from phasor import readouts
from . import vendor_opamps


class PDTransimpedance(electronics.ElectricalElementBase):
    def __build__(self):
        self.own.PD = electronics.CurrentSourceBalanced()
        self.own.C_PD = electronics.SeriesCapacitor(
            capacitance_Farads = 20e-12,
        )
        self.C_PD.pe_A.bond(self.PD.pe_A)
        self.C_PD.pe_B.bond(self.PD.pe_B)
        self.own.PDT = electronics.TerminatorShorted()
        self.PDT.pe_A.bond(self.PD.pe_B)

        self.own.RTransF = electronics.SeriesResistor(
            resistance_Ohms = 10e3,
        )

        self.own.amp = vendor_opamps.Ope_27()
        self.own.amp_in_p = electronics.TerminatorShorted()
        self.system.bond(self.amp_in_p.pe_A, self.amp.in_p)
        self.RTransF.pe_A.bond(self.amp.in_n)
        self.PD.pe_A.bond(self.amp.in_n)

        self.amp.out.bond(self.RTransF.pe_B)

        self.own.VOutTrans = electronics.VoltageReadout(
            terminal = self.amp.out,
        )
        self.own.VOutTrans_AC = readouts.ACReadout(
            portD = self.PD.ps_In.i,
            portN = self.VOutTrans.V.o,
        )

