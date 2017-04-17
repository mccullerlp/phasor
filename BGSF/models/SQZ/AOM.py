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
class AOM2XaLIGO(optics.OpticalCouplerBase):

    def __build__(self):
        super(AOM2XaLIGO, self).__build__()
        self.AOM1.BkB.bond(
            self.AOM2.FrB
        )
        self.AOM1.Drv.bond(
            self.VCO_AOM1.Out,
        )
        self.AOM2.Drv.bond(
            self.VCO_AOM2.Out,
        )
        self.Fr = self.AOM1.FrA
        self.Bk = self.AOM2.BkA

    @declarative.dproperty
    def AOM1(self, val = None):
        val = optics.AOM()
        return val

    @declarative.dproperty
    def F_AOM1(self):
        val = base.Frequency(
            F_Hz  = 200e6,
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
    def AOM2(self, val = None):
        val = optics.AOM()
        return val

    @declarative.dproperty
    def F_CLF(self):
        val = base.Frequency(
            F_Hz  = 3.14e6,
            order = 1,
        )
        return val

    @declarative.dproperty
    def VCO_AOM2(self):
        val = VCO(
            f_dict = {
                self.F_AOM1 : 1,
                self.F_CLF : -1,
            }
        )
        return val


class AOM2XTestStand(optics.OpticalCouplerBase):
    @declarative.dproperty
    def aoms(self, val = None):
        val = AOM2XaLIGO()
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
    def AC_R_amp(self, val = None):
        val = readouts.ACReadout(
            portN = self.PD_R.Wpd.o,
            portD  = self.aoms.VCO_AOM1.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def AC_R_phase(self, val = None):
        val = readouts.ACReadout(
            portN = self.PD_R.Wpd.o,
            portD  = self.aoms.VCO_AOM1.modulate.Mod_phase.i,
        )
        return val

    #@declarative.dproperty
    #def AC_hR(self, val = None):
    #    val = readouts.HomodyneACReadout(
    #        portNI = self.hPD_R.rtQuantumI.o,
    #        portNQ = self.hPD_R.rtQuantumQ.o,
    #        portD  = self.aoms.VCO_AOM1.modulate.Mod_amp.i,
    #    )
    #    return val

    def __build__(self):
        super(AOM2XTestStand, self).__build__()

        self.PSLR.Fr.bond_sequence(
            self.aoms.Fr,
        )

        self.aoms.Bk.bond_sequence(
            self.PD_R.Fr,
            #self.hPD_R.Fr,
        )
        return
