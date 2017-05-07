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

from .AOM import AOM1XBasic
from .OPO import OPOaLIGO
from .SHG import SHGaLIGO
from .VCO import VCO


class FilterCavity16m(optics.OpticalCouplerBase):

    def M1(self, val = None):
        if val is None:
            val = optics.HarmonicMirror(
                mirror_H1 = optics.Mirror(
                    T_hr = 1 - .9985,
                    flip_sign = True,
                ),
                mirror_H2 = optics.Mirror(
                    T_hr = 1 - .999,
                ),
                AOI_deg = 0,
            )
        return val

    def M2(self, val = None):
        if val is None:
            val = optics.HarmonicMirror(
                mirror_H1 = optics.Mirror(
                    T_hr = .0000001,
                    flip_sign = True,
                    L_hr = 5e-6,
                ),
                mirror_H2 = optics.Mirror(
                    T_hr = 1 - .999,
                ),
                AOI_deg = 0,
            )
        return val

    def __build__(self):
        super(FilterCavity16m, self).__build__()
        self.M1.Fr.bond(self.M2.Fr)
        return


class ComboTestStand(optics.OpticalCouplerBase):
    """
    Shows the Squeezing performance
    """

    @declarative.dproperty
    def F_CLF(self):
        val = base.Frequency(
            F_Hz  = 3.14e6,
            order = 2,
        )
        return val

    @declarative.dproperty
    def PSLR(self):
        return optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1,
            multiple = 1,
            phase_deg = 0,
        )

    @declarative.dproperty
    def PD_R(self):
        return optics.MagicPD()

    @declarative.dproperty
    def PD_G(self):
        return optics.MagicPD()

    @declarative.dproperty
    def PD_CLF(self):
        return optics.MagicPD()

    @declarative.dproperty
    def opo(self):
        return OPOaLIGO()

    @declarative.dproperty
    def DC_R(self):
        return readouts.DCReadout(
            port = self.PD_R.Wpd.o,
        )

    @declarative.dproperty
    def DC_G(self):
        return readouts.DCReadout(
            port = self.PD_G.Wpd.o,
        )

    @declarative.dproperty
    def DC_CLF(self):
        return readouts.DCReadout(
            port = self.PD_CLF.Wpd.o,
        )

    @declarative.dproperty
    def DCI_CLF(self):
        return readouts.DCReadout(
            port = self.mix_clf_2x.R_I.o,
        )

    @declarative.dproperty
    def DCQ_CLF(self):
        return readouts.DCReadout(
            port = self.mix_clf_2x.R_Q.o,
        )

    @declarative.dproperty
    def mix_clf_hdyne_1xI(self):
        return signals.Mixer()

    @declarative.dproperty
    def mix_clf_hdyne_1xQ(self):
        return signals.Mixer()

    @declarative.dproperty
    def hPD_R(self):
        return optics.HiddenVariableHomodynePD(
            source_port = self.ditherPMRead.Bk.o,
            include_quanta = True,
        )

    @declarative.dproperty
    def mDC_readout(self):
        return optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 1,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
            ),
            AOI_deg = 45,
        )

    @declarative.dproperty
    def signal_clf(self):
        return signals.SignalGenerator(
            F = self.F_CLF,
            harmonic_gains = {
                2 : 1,
            }
        )
    @declarative.dproperty
    def mix_clf_2x(self):
        return signals.Mixer()

    @declarative.dproperty
    def hDCAmpI_CLF(self):
        return readouts.DCReadout(
            port = self.mix_clf_hdyne_1xI.R_I.o,
        )
    @declarative.dproperty
    def hDCAmpQ_CLF(self):
        return readouts.DCReadout(
            port = self.mix_clf_hdyne_1xI.R_Q.o,
        )

    @declarative.dproperty
    def hDCPhaseI_CLF(self):
        return readouts.DCReadout(
            port = self.mix_clf_hdyne_1xQ.R_I.o,
        )
    @declarative.dproperty
    def hDCPhaseQ_CLF(self):
        return readouts.DCReadout(
            port = self.mix_clf_hdyne_1xQ.R_Q.o,
        )

    @declarative.dproperty
    def AC_R(self):
        return readouts.HomodyneACReadout(
            portNI = self.hPD_R.rtQuantumI.o,
            portNQ = self.hPD_R.rtQuantumQ.o,
            portD  = self.ditherPM.Drv.i,
        )

    def __build__(self):
        super(ComboTestStand, self).__build__()

        self.my.BS_to_SHG = optics.Mirror(
            T_hr = .4
        )

        self.my.BS_to_SHG = optics.Mirror(
            T_hr = .4
        )

        self.mDC_readout.BkA.bond_sequence(
            self.PD_R.Fr,
            self.hPD_R.Fr,
        )

        self.PSLG.Fr.bond_sequence(
            self.ditherPM.Fr,
            self.opo.M1.BkA,
        )

        self.opo.M1.BkB.bond_sequence(
            self.mDC_readout.FrA,
        )
        self.opo.M2.BkA.bond_sequence(
            self.PSLR_clf.Fr,
        )
        self.opo.M2.BkB.bond_sequence(
            self.PD_CLF.Fr,
        )
        self.mix_clf_2x.LO.bond(self.signal_clf.OutH2)
        self.mix_clf_2x.I.bond(self.PD_CLF.Wpd)

        self.mix_clf_hdyne_1xI.LO.bond(self.signal_clf.Out)
        self.mix_clf_hdyne_1xI.I.bond(self.hPD_R.rtWpdI)
        self.mix_clf_hdyne_1xQ.LO.bond(self.signal_clf.Out)
        self.mix_clf_hdyne_1xQ.I.bond(self.hPD_R.rtWpdQ)

