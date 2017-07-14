# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
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
        self.generate.ps_Out.bond(
            self.modulate.ps_In,
        )
        self.ps_Out = self.modulate.ps_Out


class AOM2VCO(optics.OpticalCouplerBase):
    VCO2_use = False

    def __build__(self):
        super(AOM2VCO, self).__build__()
        self.AOM1.Drv.bond(
            self.VCO_AOM1.ps_Out,
        )
        if self.VCO2_use:
            self.VCO_AOM1.modulate.Mod_amp.bond(
                self.VCO_AOM2.ps_Out
            )
        self.po_Fr = self.AOM1.po_FrA
        self.po_Bk = self.AOM1.po_BkB

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


class AOM2VCOBasic(optics.OpticalCouplerBase):
    VCO2_use = False

    def __build__(self):
        super(AOM2VCOBasic, self).__build__()
        self.AOM1.Drv.bond(
            self.VCO_AOM1.ps_Out,
        )
        if self.VCO2_use:
            self.VCO_AOM1.modulate.Mod_amp.bond(
                self.VCO_AOM2.ps_Out
            )
        self.po_Fr = self.AOM1.po_Fr
        self.po_Bk = self.AOM1.po_Bk

    @declarative.dproperty
    def AOM1(self, val = None):
        val = optics.AOMBasic()
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
            source_port = self.aoms.po_Bk.o,
            include_quanta = False,
            include_relative = True,
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
            portNI = self.hPD_R.rtWpdI.o,
            portNQ = self.hPD_R.rtWpdQ.o,
            portD  = self.aoms.VCO_AOM1.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def AC_R_Q_phase(self, val = None):
        val = readouts.ACReadout(
            portN = self.hPD_R.RadQ.o,
            portD  = self.aoms.VCO_AOM1.modulate.Mod_phase.i,
        )
        return val

    @declarative.dproperty
    def AC_R_I_phase(self, val = None):
        val = readouts.ACReadout(
            portN = self.hPD_R.RinI.o,
            portD  = self.aoms.VCO_AOM1.modulate.Mod_phase.i,
        )
        return val

    @declarative.dproperty
    def AC_R_Q_amp(self, val = None):
        val = readouts.ACReadout(
            portN = self.hPD_R.RadQ.o,
            portD  = self.aoms.VCO_AOM1.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def AC_R_I_amp(self, val = None):
        val = readouts.ACReadout(
            portN = self.hPD_R.RinI.o,
            portD  = self.aoms.VCO_AOM1.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def mix(self):
        val = signals.Mixer()
        return val

    def __build__(self):
        super(AOM2VCOTestStand, self).__build__()

        self.PSLR.po_Fr.bond_sequence(
            self.aoms.po_Fr,
        )
        if self.VCO2_use:
            self.mix.LO.bond(self.aoms.VCO_AOM2.ps_Out)
        self.PD_R.Wpd.bond(self.mix.ps_In)

        self.own.DC_RR = readouts.DCReadout(
            port = self.mix.ps_R_I.o,
        )

        self.aoms.po_Bk.bond_sequence(
            self.PD_R.po_Fr,
            self.hPD_R.po_Fr,
        )
        return


class AOMTestStand(optics.OpticalCouplerBase):
    def __build__(self):
        super(AOMTestStand, self).__build__()
        self.own.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )
        self.own.F_LO = base.Frequency(
            F_Hz  = 200e6,
            order = 1,
        )

        self.own.PD_R1 = optics.MagicPD()
        self.own.PD_R2 = optics.MagicPD()

        self.own.LO = signals.SignalGenerator(
            F         = self.F_LO,
            amplitude = 1,
        )

        self.own.aom = optics.AOM(
            N_ode = 100,
        )
        self.aom.Drv.bond(self.LO.ps_Out)

        self.PSL.po_Fr.bond_sequence(
            self.aom.po_FrA,
        )
        self.aom.po_BkA.bond(self.PD_R1.po_Fr)
        self.aom.po_BkB.bond(self.PD_R2.po_Fr)

        self.own.DC_R1 = readouts.DCReadout(
            port = self.PD_R1.Wpd.o,
        )
        self.own.DC_R2 = readouts.DCReadout(
            port = self.PD_R2.Wpd.o,
        )


class AOMTestStandBasic(optics.OpticalCouplerBase):
    def __build__(self):
        super(AOMTestStandBasic, self).__build__()
        self.own.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
        )
        self.own.F_LO = base.Frequency(
            F_Hz  = 200e6,
            order = 1,
        )

        self.own.PD_R1 = optics.MagicPD()

        self.own.LO = signals.SignalGenerator(
            F         = self.F_LO,
            amplitude = 1,
        )

        self.own.aom = optics.AOMBasic()
        self.aom.Drv.bond(self.LO.ps_Out)

        self.PSL.po_Fr.bond_sequence(
            self.aom.po_Fr,
        )
        self.aom.po_Bk.bond(self.PD_R1.po_Fr)

        self.own.DC_R1 = readouts.DCReadout(
            port = self.PD_R1.Wpd.o,
        )
        self.own.DC_Drv = readouts.DCReadout(
            port = self.aom.Drv_Pwr.MS.o,
        )


class AOM2VCOTestStandBasic(AOM2VCOTestStand):
    @declarative.dproperty
    def aoms(self, val = None):
        val = AOM2VCOBasic(
            VCO2_use = self.VCO2_use,
        )
        return val
