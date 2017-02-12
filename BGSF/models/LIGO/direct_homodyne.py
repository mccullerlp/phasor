# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from BGSF.utilities.np import logspaced

#import numpy as np
#import declarative

from ... import optics
from ... import signals
#from ... import readouts
from ... import base
#from ... import signals

class BalancedHomodyneDetector(base.SystemElementBase):
    def __init__(
            self,
            P_link_intermediate = None,
            phase_deg = 0,
            **kwargs
    ):
        super(BalancedHomodyneDetector, self).__init__(**kwargs)
        self.my.PD_P = optics.PD()
        self.my.PD_N = optics.PD()

        base.OOA_ASSIGN(self).QE_CMN_percent = 100
        base.OOA_ASSIGN(self).QE_P_percent   = 100
        base.OOA_ASSIGN(self).QE_N_percent   = 100
        base.OOA_ASSIGN(self).phase_deg      = phase_deg

        self.my.CMN_loss_M = optics.Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.QE_CMN_percent * 1e-2,
        )

        self.my.PD_P_loss_M = optics.Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.QE_P_percent * 1e-2,
        )

        self.my.PD_N_loss_M = optics.Mirror(
            T_hr = 1,
            L_hr = 0,
            L_t  = 1 - self.QE_N_percent * 1e-2,
        )

        self.my.BHD_BS = optics.Mirror(
            T_hr    = 0.50,
            L_hr    = 0,
            AOI_deg = 45,
        )

        self.my.LO_phase = optics.Space(
            L_m = 0,
            L_detune_m = self.phase_deg / 360 * 1.064e-6,
        )
        self.my.PD_IQ = optics.HiddenVariableHomodynePD(
            source_port     = self.LO_phase.Bk.o,
            phase_deg       = 00,
        )
        self.my.PD_IQ_P = optics.HiddenVariableHomodynePD(
            source_port     = self.LO_phase.Bk.o,
            phase_deg       = 00,
        )
        self.my.PD_IQ_N = optics.HiddenVariableHomodynePD(
            source_port     = self.LO_phase.Bk.o,
            phase_deg       = 00,
        )
        if True or P_link_intermediate is None:
            self.system.bond(
                self.CMN_loss_M.Bk,
                self.PD_IQ.Fr,
            )
        else:
            self.system.bond(
                self.CMN_loss_M.Bk,
                P_link_intermediate[0],
            )
            self.system.bond(
                P_link_intermediate[1],
                self.PD_IQ.Fr,
            )
        self.system.bond(
            self.PD_IQ.Bk,
            self.BHD_BS.FrA,
        )
        self.system.bond(
            self.LO_phase.Bk,
            self.BHD_BS.BkB,
        )
        if P_link_intermediate is None:
            self.system.bond(
                self.BHD_BS.FrB,
                self.PD_P_loss_M.Fr,
            )
        else:
            self.system.bond(
                self.BHD_BS.FrB,
                P_link_intermediate[0],
            )
            self.system.bond(
                P_link_intermediate[1],
                self.PD_P_loss_M.Fr,
            )
        self.system.bond(
            self.PD_P_loss_M.Bk,
            self.PD_IQ_P.Fr,
        )
        self.system.bond(
            self.PD_IQ_P.Bk,
            self.PD_P.Fr,
        )
        self.system.bond(
            self.BHD_BS.BkA,
            self.PD_N_loss_M.Fr,
        )
        self.system.bond(
            self.PD_N_loss_M.Bk,
            self.PD_IQ_N.Fr,
        )
        self.system.bond(
            self.PD_IQ_N.Bk,
            self.PD_N.Fr,
        )

        self.port_LO     = self.LO_phase.Fr
        self.port_signal = self.CMN_loss_M.Fr

        self.my.amp_Wpd_diff = signals.SummingAmplifier(
            port_gains = dict(
                P = +1,
                N = -1,
            )
        )
        self.system.bond(self.PD_P.Wpd, self.amp_Wpd_diff.P)
        self.system.bond(self.PD_N.Wpd, self.amp_Wpd_diff.N)

        self.my.amp_Wpd_cmn = signals.SummingAmplifier(
            port_gains = dict(
                P = +1,
                N = +1,
            )
        )
        self.system.bond(self.PD_P.Wpd, self.amp_Wpd_cmn.P)
        self.system.bond(self.PD_N.Wpd, self.amp_Wpd_cmn.N)

        self.Wpd_diff = self.amp_Wpd_diff.O
        self.Wpd_cmn  = self.amp_Wpd_cmn.O
        return
