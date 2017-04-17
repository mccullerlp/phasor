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


class AOM2VCO(optics.OpticalCouplerBase):
    VCO2_use = False

    def __build__(self):
        super(AOM2VCO, self).__build__()
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


class AOM2VCOTestStand(optics.OpticalCouplerBase):
    VCO2_use = False

    @declarative.dproperty
    def aoms(self, val = None):
        val = AOM2VCO(
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
        super(AOM2VCOTestStand, self).__build__()

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


class AOMTestStand(optics.OpticalCouplerBase):
    def __build__(self):
        super(AOMTestStand, self).__build__()
        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )
        self.my.F_LO = base.Frequency(
            F_Hz  = 200e6,
            order = 1,
        )

        self.my.PD_R1 = optics.MagicPD()
        self.my.PD_R2 = optics.MagicPD()

        self.my.LO = signals.SignalGenerator(
            F         = self.F_LO,
            amplitude = 1,
        )

        self.my.aom = optics.AOM(
            N_ode = 100,
        )
        self.aom.Drv.bond(self.LO.Out)

        self.PSL.Fr.bond_sequence(
            self.aom.FrA,
        )
        self.aom.BkA.bond(self.PD_R1.Fr)
        self.aom.BkB.bond(self.PD_R2.Fr)

        self.my.DC_R1 = readouts.DCReadout(
            port = self.PD_R1.Wpd.o,
        )
        self.my.DC_R2 = readouts.DCReadout(
            port = self.PD_R2.Wpd.o,
        )
