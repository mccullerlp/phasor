"""
"""
from __future__ import division, print_function
import numpy as np
import declarative

from ... import optics
from ... import base
from ... import signals
from ... import readouts
#from ... import system

class VCOTest(optics.OpticalCouplerBase):
    f_dict = None

    @declarative.dproperty
    def F_AOM1(self):
        val = base.Frequency(
            F_Hz  = 200e6,
            order = 1,
        )
        return val

    @declarative.dproperty
    def generate(self):
        val = signals.SignalGenerator(
            F = self.F_AOM1,
            amplitude = 1,
        )
        return val

    @declarative.dproperty
    def modulate(self):
        val = signals.Modulator()
        return val

    @declarative.dproperty
    def mix(self):
        val = signals.Mixer()
        return val

    @declarative.dproperty
    def AC_I(self, val = None):
        val = readouts.ACReadout(
            portN = self.mix.R_I.o,
            portD  = self.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def AC_IQ(self, val = None):
        val = readouts.ACReadout(
            portN = self.mix.R_Q.o,
            portD  = self.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def AC_QI(self, val = None):
        val = readouts.ACReadout(
            portN = self.mix.R_Q.o,
            portD  = self.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def AC_Q(self, val = None):
        val = readouts.ACReadout(
            portN = self.mix.R_Q.o,
            portD  = self.modulate.Mod_phase.i,
        )
        return val

    def __build__(self):
        super(VCOTest, self).__build__()
        self.generate.Out.bond(
            self.modulate.In,
        )
        self.mix.LO.bond(self.generate.Out)
        self.modulate.Out.bond(
            self.mix.I,
        )


class VCO(optics.OpticalCouplerBase):
    f_dict = None

    @declarative.dproperty
    def generate(self):
        val = signals.SignalGenerator(
            f_dict = self.f_dict,
            amplitude = 1,
        )
        return val

    @declarative.dproperty
    def modulate(self):
        val = signals.Modulator()
        return val

    def __build__(self):
        super(VCO, self).__build__()
        self.generate.Out.bond(
            self.modulate.In,
        )
        self.Out = self.modulate.Out

#FROM dcc E0900492
class AOM1X(optics.OpticalCouplerBase):
    VCO2_use = False

    def __build__(self):
        super(AOM1X, self).__build__()
        self.AOM1.Drv.bond(
            self.VCO_AOM1.Out,
        )
        if self.VCO2_use:
            self.VCO_AOM1.modulate.Mod_amp.bond(
                self.VCO_AOM2.Out
            )
        self.Fr = self.AOM1.FrA
        self.Bk = self.AOM1.BkB
        self.Bk2 = self.AOM1.BkA

    @declarative.dproperty
    def AOM1(self, val = None):
        val = optics.AOM(
            N_ode = 5,
        )
        return val

    @declarative.dproperty
    def F_AOM1(self):
        val = base.Frequency(
            F_Hz  = 100e6,
            order = 1,
        )
        return val

    @declarative.dproperty
    def VCO_AOM1(self):
        val = VCO(
            f_dict = {
                self.F_AOM1 : 1,
            }
        )
        return val

    @declarative.dproperty
    def F_AOM2(self):
        val = base.Frequency(
            F_Hz  = 1e3,
            order = 1,
        )
        return val

    @declarative.dproperty
    def VCO_AOM2(self):
        val = VCO(
            f_dict = {
                #self.F_AOM2 : 1,
                self.system.F_AC : 1,
            }
        )
        return val


class AOM1XTestStand(optics.OpticalCouplerBase):
    VCO2_use = False

    @declarative.dproperty
    def aoms(self, val = None):
        val = AOM1X(
            VCO2_use = self.VCO2_use,
        )
        return val

    @declarative.dproperty
    def PSLR(self, val = None):
        val = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )
        return val

    @declarative.dproperty
    def PSLRs(self, val = None):
        val = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )
        return val

    @declarative.dproperty
    def PD_R(self, val = None):
        val = optics.MagicPD()
        return val

    @declarative.dproperty
    def hPD_R(self, val = None):
        val = optics.HiddenVariableHomodynePD(
            source_port = self.PSLRs.Fr.o,
            include_quanta = True,
        )
        return val

    @declarative.dproperty
    def DC_R(self, val = None):
        val = readouts.DCReadout(
            port = self.PD_R.Wpd.o,
        )
        return val

    @declarative.dproperty
    def AC_R(self, val = None):
        val = readouts.ACReadout(
            portN = self.PD_R.Wpd.o,
            portD  = self.aoms.VCO_AOM1.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def AC_hR(self, val = None):
        val = readouts.HomodyneACReadout(
            portNI = self.hPD_R.rtQuantumI.o,
            portNQ = self.hPD_R.rtQuantumQ.o,
            portD  = self.aoms.VCO_AOM1.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def mix(self):
        val = signals.Mixer()
        return val

    def __build__(self):
        super(AOM1XTestStand, self).__build__()

        self.PSLR.Fr.bond_sequence(
            self.aoms.Fr,
        )
        if self.VCO2_use:
            self.mix.LO.bond(self.aoms.VCO_AOM2.Out)
        self.PD_R.Wpd.bond(self.mix.I)

        self.my.DC_RR = readouts.DCReadout(
            port = self.mix.R_I.o,
        )

        self.aoms.Bk.bond_sequence(
            self.PD_R.Fr,
            #self.hPD_R.Fr,
        )
        return
