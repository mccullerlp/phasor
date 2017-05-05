"""
"""
from __future__ import division, print_function
import numpy as np
import declarative

from ... import optics
from ... import base
from ... import signals
from ... import readouts
from ... import mechanical
#from ... import system

from ..LIGO import ligo_sled as LIGO

from .VCO import VCO
from .OPO import OPOaLIGO


#From E1500445
class FilterCavity16m(optics.OpticalCouplerBase):

    @declarative.dproperty
    def M1(self, val = None):
        if val is None:
            val = optics.HarmonicMirror(
                mirror_H1 = optics.Mirror(
                    T_hr = 60e-6,
                    #T_hr = 10*60e-6,
                    L_hr = 6e-6,
                ),
                mirror_H2 = optics.Mirror(
                    T_hr = 1500e-6,
                ),
                AOI_deg = 0,
            )
        return val

    @declarative.dproperty
    def S1(self, val = None):
        if val is None:
            val = optics.Space(L_m = 16)
        return val

    @declarative.dproperty
    def M2(self, val = None):
        if val is None:
            val = optics.HarmonicMirror(
                mirror_H1 = optics.Mirror(
                    T_hr = 1e-6,
                    #T_hr = 60e-6 + 1e-6,
                    L_hr = 6e-6,
                ),
                mirror_H2 = optics.Mirror(
                    T_hr = 1500e-6,
                ),
                AOI_deg = 0,
            )
        return val

    def __build__(self):
        try:
            super(FilterCavity16m, self).__build__()
            self.my.PD = optics.MagicPD()
            self.my.DC = readouts.DCReadout(
                port = self.PD.Wpd.o,
            )
            self.M1.Fr.bond_sequence(
                self.PD.Fr,
                self.S1.Fr,
                self.M2.Fr,
            )
            self.Fr = self.M1.Bk
            self.Bk = self.M2.Bk
            return
        except Exception as E:
            print(repr(E))


class FCOPO_stand(optics.OpticalCouplerBase):
    """
    Shows the Squeezing performance
    """

    @declarative.dproperty
    def FC(self):
        return FilterCavity16m()

    @declarative.dproperty
    def OPO(self):
        return OPOaLIGO()

    @declarative.dproperty
    def OPO_OUT_DC(self):
        return optics.HarmonicSelector()

    @declarative.dproperty
    def SQZ_G(self):
        return optics.Laser(
            F         = self.system.F_carrier_1064,
            power_W   = .02,
            multiple  = 2,
            phase_deg = -90,
        )

    @declarative.dproperty
    def ditherPM(self):
        return optics.PM()

    @declarative.dproperty
    def SQZ_R(self):
        return optics.Laser(
            F         = self.system.F_carrier_1064,
            power_W   = 1,
            multiple  = 1,
            phase_deg = 90,
        )

    @declarative.dproperty
    def faraday_FC_sqz(self):
        val = optics.OpticalCirculator(
            N_ports = 3,
        )
        return val

    @declarative.dproperty
    def faraday_LIGO(self):
        val = optics.OpticalCirculator(
            N_ports = 3,
        )
        return val

    @declarative.dproperty
    def BS_IN_loss(self):
        return optics.Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = .10,
            AOI_deg = 45,
        )

    @declarative.dproperty
    def hdyne_FC_out(self):
        return optics.HiddenVariableHomodynePD(
            source_port = self.SQZ_R.Fr.o,
            include_quanta = True,
        )

    @declarative.dproperty
    def hdyne_OPO_out(self):
        return optics.HiddenVariableHomodynePD(
            source_port = self.SQZ_R.Fr.o,
            include_quanta = True,
        )

    def __build__(self):
        try:
            super(FCOPO_stand, self).__build__()

            self.SQZ_G.Fr.bond_sequence(
                self.OPO.M1.BkA,
            )

            self.OPO.M1.BkB.bond_sequence(
                self.OPO_OUT_DC.Fr,
            )

            base.OOA_ASSIGN(self).use_FC = True
            if self.use_FC:
                self.OPO_OUT_DC.Bk_H1.bond_sequence(
                    self.hdyne_OPO_out.Fr,
                    self.faraday_FC_sqz.P0,
                )

                self.faraday_FC_sqz.P1.bond_sequence(
                    self.FC.Fr
                )

                self.faraday_FC_sqz.P2.bond_sequence(
                    self.hdyne_FC_out.Fr,
                    self.BS_IN_loss.FrA,
                    self.faraday_LIGO.P0,
                )
            else:
                self.OPO_OUT_DC.Bk_H1.bond_sequence(
                    self.hdyne_OPO_out.Fr,
                    self.hdyne_FC_out.Fr,
                    self.BS_IN_loss.FrA,
                    self.faraday_LIGO.P0,
                )

            self.TO_aLIGO  = self.faraday_LIGO.P1
            self.TO_output = self.faraday_LIGO.P2

            self.my.AC_SQZ = readouts.HomodyneACReadout(
                portNI = self.hdyne_OPO_out.rtQuantumI.o,
                portNQ = self.hdyne_OPO_out.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )

            self.my.AC_FC = readouts.HomodyneACReadout(
                portNI = self.hdyne_FC_out.rtQuantumI.o,
                portNQ = self.hdyne_FC_out.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
        except Exception as E:
            print(repr(E))


class LIGOSQZFCOperation(base.SystemElementBase):
    @declarative.dproperty
    def SQZ_FC(self):
        return FCOPO_stand()

    def __build__(self):
        super(LIGOSQZFCOperation, self).__build__()
        self.my.LIGO = LIGO.LIGODetector()
        self.my.input  = LIGO.LIGOInputBasic()
        self.my.output = LIGO.LIGOOutputHomodyne(
            LIGO_obj  = self.LIGO,
            input_obj = self.input,
        )

        self.system.bond_sequence(
            self.input.INPUT_ATTACH_POINT,
            self.LIGO.INPUT_ATTACH_POINT,
        )

        self.LIGO.OUTPUT_ATTACH_POINT.bond(
            self.SQZ_FC.TO_aLIGO,
        )
        self.SQZ_FC.TO_output.bond_sequence(
            self.output.OUTPUT_ATTACH_POINT,
        )



#seismic = 2e-8 / F**2
