"""
"""
from __future__ import division, print_function
import declarative
import numpy as np
from ... import optics
from ... import base
from ... import signals
from ... import readouts
#from ... import system

from .AOM import AOM2XaLIGO
from .OPO import OPOaLIGO


class AOMnOPOTestStand(optics.OpticalCouplerBase):
    """
    Shows the Squeezing performance
    """
    @declarative.dproperty
    def aoms(self, val = None):
        val = AOM2XaLIGO()
        return val

    @declarative.dproperty
    def PSL_CLF(self, val = None):
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
            phase_deg = 45,
        )
        return val

    @declarative.dproperty
    def PD_R(self, val = None):
        val = optics.MagicPD()
        return val

    @declarative.dproperty
    def hPD_R(self, val = None):
        val = optics.HiddenVariableHomodynePD(
            source_port = self.ditherPMRead.Bk.o,
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

    @declarative.dproperty
    def include_PM(self, val = True):
        """
        Number of iterations to use in the ODE solution
        """
        val = self.ooa_params.setdefault('include_PM', val)
        return val

    def __build__(self):
        super(AOMnOPOTestStand, self).__build__()

        self.my.PSLG = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = .02,
            multiple = 2,
            phase_deg = 0,
        )
        self.my.PSLGs = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            multiple = 2,
            phase_deg = 90,
        )

        self.my.PD_G = optics.MagicPD()
        self.my.PD_CLF  = optics.MagicPD(
            include_readouts = True,
        )

        self.my.opo = OPOaLIGO()

        if self.include_PM:
            self.my.F_PM = base.Frequency(
                F_Hz  = 1e6,
                order = 1,
            )
            self.my.generateF_PM = signals.SignalGenerator(
                F = self.F_PM,
                amplitude = 0,
            )

            self.my.generateF_PMRead = signals.SignalGenerator(
                F = self.F_PM,
                amplitude = 0,
            )

        self.my.ditherPM = optics.PM()
        self.my.ditherPMRead = optics.PM()
        self.my.hPD_G = optics.HiddenVariableHomodynePD(
            source_port = self.PSLGs.Fr.o,
            include_quanta = True,
        )

        self.my.mDC_readout = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 1,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
            ),
            AOI_deg = 45,
        )

        self.PSL_CLF.Fr.bond_sequence(
            self.aoms.Fr,
        )

        self.aoms.Bk.bond_sequence(
            self.opo.M2.BkA,
        )

        if self.include_PM:
            self.ditherPM.Drv.bond(self.generateF_PM.Out)

        if self.include_PM:
            self.ditherPMRead.Drv.bond(self.generateF_PMRead.Out)

        self.PSLRs.Fr.bond(self.my.ditherPMRead.Fr)
        self.PSLG.Fr.bond_sequence(
            self.ditherPM.Fr,
            self.opo.M1.BkA,
        )
        self.opo.M1.BkB.bond_sequence(
            self.my.mDC_readout.FrA,
        )

        self.opo.M2.BkB.bond_sequence(
            self.PD_CLF.Fr,
        )

        self.my.mDC_readout.FrB.bond_sequence(
            self.PD_G.Fr,
            self.hPD_G.Fr,
        )
        self.my.mDC_readout.BkA.bond_sequence(
            self.PD_R.Fr,
            self.hPD_R.Fr,
        )
        self.my.DC_G = readouts.DCReadout(
            port = self.PD_G.Wpd.o,
        )
        if self.ooa_params.setdefault('include_AC', True):
            self.my.AC_G = readouts.HomodyneACReadout(
                portNI = self.hPD_G.rtQuantumI.o,
                portNQ = self.hPD_G.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.my.AC_R = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumI.o,
                portNQ = self.hPD_R.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.my.AC_RGI = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumI.o,
                portNQ = self.hPD_G.rtQuantumI.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.my.AC_RGQ = readouts.HomodyneACReadout(
                portNI = self.hPD_R.rtQuantumQ.o,
                portNQ = self.hPD_G.rtQuantumQ.o,
                portD  = self.ditherPM.Drv.i,
            )
            self.my.AC_N = readouts.NoiseReadout(
                port_map = dict(
                    RI = self.hPD_R.rtQuantumI.o,
                    RQ = self.hPD_R.rtQuantumQ.o,
                    GI = self.hPD_G.rtQuantumI.o,
                    GQ = self.hPD_G.rtQuantumQ.o,
                )
            )



