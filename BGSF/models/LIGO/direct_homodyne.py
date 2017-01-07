# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import print_function

import numpy as np

from declarative.bunch import (
    Bunch,
)

from ..optics import (
    Mirror,
    PD,
    MagicPD,
    Space,
    Laser,
)

from ..system.optical import (
    OpticalSystem,
)

from ..signals import (
    SignalGenerator,
    Mixer,
    DistributionAmplifier,
    SummingAmplifier,
    #TransferFunctionSISO,
    TransferFunctionSISOMechSingleResonance,
)

from ..readouts import (
    DCReadout,
    ACReadout,
    ACReadoutCLG,
)

from ..readouts.homodyne_AC import (
    HomodyneACReadout,
)

from ..base import (
    SystemElementSled,
    OOA_ASSIGN,
    Frequency,
)

from ..optics.modulators import (
    PM, AM
)

from ..optics.EZSqz import (
    EZSqz,
)

from ..optics.hidden_variable_homodyne import (
    HiddenVariableHomodynePD,
)

from ..optics.vacuum import (
    VacuumTerminator,
)

from ..signals import (
    SignalGenerator,
    Mixer,
    DistributionAmplifier,
    SummingAmplifier,
)
#from YALL.utilities.np import logspaced

class BalancedHomodyneDetector(SystemElementSled):
    def __init__(
            self,
            P_link_intermediate = None,
            phase_deg = 0,
            **kwargs
    ):
        super(BalancedHomodyneDetector, self).__init__(**kwargs)
        self.PD_P = PD()
        self.PD_N = PD()

        OOA_ASSIGN(self).QE_CMN_percent = 100
        OOA_ASSIGN(self).QE_P_percent   = 100
        OOA_ASSIGN(self).QE_N_percent   = 100
        OOA_ASSIGN(self).phase_deg      = phase_deg

        self.CMN_loss_M = Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.QE_CMN_percent * 1e-2,
        )

        self.PD_P_loss_M = Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.QE_P_percent * 1e-2,
        )

        self.PD_N_loss_M = Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.QE_N_percent * 1e-2,
        )

        self.BHD_BS = Mirror(
            T_hr    = 0.50,
            L_hr    = 0,
            AOI_deg = 45,
        )

        self.LO_phase = Space(
            L_m = 0,
            L_detune_m = self.phase_deg / 360 * 1.064e-6,
        )
        self.PD_IQ = HiddenVariableHomodynePD(
            source_port     = self.LO_phase.Bk.o,
            phase_deg       = 00,
        )
        self.PD_IQ_P = HiddenVariableHomodynePD(
            source_port     = self.LO_phase.Bk.o,
            phase_deg       = 00,
        )
        self.PD_IQ_N = HiddenVariableHomodynePD(
            source_port     = self.LO_phase.Bk.o,
            phase_deg       = 00,
        )
        if True or P_link_intermediate is None:
            self.system.link(
                self.CMN_loss_M.Bk,
                self.PD_IQ.Fr,
            )
        else:
            self.system.link(
                self.CMN_loss_M.Bk,
                P_link_intermediate[0],
            )
            self.system.link(
                P_link_intermediate[1],
                self.PD_IQ.Fr,
            )
        self.system.link(
            self.PD_IQ.Bk,
            self.BHD_BS.FrA,
        )
        self.system.link(
            self.LO_phase.Bk,
            self.BHD_BS.BkB,
        )
        if P_link_intermediate is None:
            self.system.link(
                self.BHD_BS.FrB,
                self.PD_P_loss_M.Fr,
            )
        else:
            self.system.link(
                self.BHD_BS.FrB,
                P_link_intermediate[0],
            )
            self.system.link(
                P_link_intermediate[1],
                self.PD_P_loss_M.Fr,
            )
        self.system.link(
            self.PD_P_loss_M.Bk,
            self.PD_IQ_P.Fr,
        )
        self.system.link(
            self.PD_IQ_P.Bk,
            self.PD_P.Fr,
        )
        self.system.link(
            self.BHD_BS.BkA,
            self.PD_N_loss_M.Fr,
        )
        self.system.link(
            self.PD_N_loss_M.Bk,
            self.PD_IQ_N.Fr,
        )
        self.system.link(
            self.PD_IQ_N.Bk,
            self.PD_N.Fr,
        )

        self.port_LO     = self.LO_phase.Fr
        self.port_signal = self.CMN_loss_M.Fr

        self.amp_Wpd_diff = SummingAmplifier(
            port_gains = dict(
                P = +1,
                N = -1,
            )
        )
        self.system.link(self.PD_P.Wpd, self.amp_Wpd_diff.P)
        self.system.link(self.PD_N.Wpd, self.amp_Wpd_diff.N)

        self.amp_Wpd_cmn = SummingAmplifier(
            port_gains = dict(
                P = +1,
                N = +1,
            )
        )
        self.system.link(self.PD_P.Wpd, self.amp_Wpd_cmn.P)
        self.system.link(self.PD_N.Wpd, self.amp_Wpd_cmn.N)

        self.Wpd_diff = self.amp_Wpd_diff.O
        self.Wpd_cmn  = self.amp_Wpd_cmn.O
        return

    def orient_optical_portsEW(self):
        return (self.signal_port,)

    def orient_optical_portsNS(self):
        return (self.signal_port,)


