# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
from builtins import range
#from YALL.utilities.print import print

import numpy as np
from collections import defaultdict

from declarative import (
    mproperty,
)

from declarative.bunch import (
    Bunch,
)

from ..math.key_matrix import (
    DictKey,
    FrequencyKey,
)

from ..base import (
    SystemElementBase,
    OOA_ASSIGN,
    ClassicalFreqKey,
)

from .base import ReadoutViewBase
from .noise import NoiseMatrixView


def np_roll_2D_mat_back(arr_mat, N = 2):
    for idx in range(len(arr_mat.shape) - N):
        arr_mat = np.rollaxis(arr_mat, -1, 0)
    return arr_mat


def np_roll_2D_mat_front(arr_mat, N = 2):
    for idx in range(len(arr_mat.shape) - N):
        arr_mat = np.rollaxis(arr_mat, 0, len(arr_mat.shape))
    return arr_mat


class HomodyneACReadout(SystemElementBase):
    def __init__(
        self,
        system,
        portNI,
        portNQ,
        portD,
        portDrv = None,
        port_set = 'AC',
        **kwargs
    ):
        super(HomodyneACReadout, self).__init__(system = system, **kwargs)
        if portDrv is None:
            portDrv = portD

        self.portD = portD
        self.portNI = portNI
        self.portNQ = portNQ
        self.portDrv = portDrv

        OOA_ASSIGN(self).port_set = 'AC'

        #TODO: make this adjustable
        self.F_sep = system.F_AC

        self.keyP = DictKey({ClassicalFreqKey: FrequencyKey({self.F_sep : 1})})
        self.keyN = DictKey({ClassicalFreqKey: FrequencyKey({self.F_sep : -1})})

        self.noise = HomodyneNoiseReadout(
            portNI = self.portNI,
            portNQ = self.portNQ,
        )
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'AC_sensitivitys', 'readouts']
        system.readout_port_needed(self.portNI, self.keyP, portsets)
        system.readout_port_needed(self.portNI, self.keyN, portsets)
        system.readout_port_needed(self.portNQ, self.keyP, portsets)
        system.readout_port_needed(self.portNQ, self.keyN, portsets)
        system.readout_port_needed(self.portD, self.keyP, portsets)
        system.readout_port_needed(self.portD, self.keyN, portsets)
        system.drive_port_needed(self.portDrv, self.keyP, portsets)
        system.drive_port_needed(self.portDrv, self.keyN, portsets)
        return

    def system_associated_readout_view(self, solver):
        noise_view = self.noise.system_associated_readout_view(solver)
        return HomodyneACReadoutView(
            readout    = self,
            system     = self.system,
            solver     = solver,
            noise_view = noise_view,
            phase_deg  = 0,
        )


class HomodyneACReadoutView(ReadoutViewBase):
    def __init__(
            self,
            noise_view,
            phase_deg,
            **kwargs
    ):
        super(HomodyneACReadoutView, self).__init__(**kwargs)
        self.noise     = noise_view
        self.phase_deg = phase_deg

        return

    def rotate_deg(self, phase_deg):
        return self.__class__(
            system     = self.system,
            solver     = self.solver,
            readout    = self.readout,
            noise_view = self.noise,
            phase_deg  = self.phase_deg + phase_deg
        )

    def select_sources(self, nobj_filter_func):
        noise_view = self.noise.select_sources(nobj_filter_func)
        return self.__class__(
            system     = self.system,
            solver     = self.solver,
            readout    = self.readout,
            noise_view = noise_view,
            phase_deg  = self.phase_deg,
        )

    @mproperty
    def F_Hz(self):
        return self.readout.F_sep.F_Hz

    @mproperty
    def AC_sensitivity(self):
        return self.AC_sensitivity_IQ[0]

    def homodyne_SNR(self):
        return self.noise.noise / abs(self.AC_sensitivity)

    @mproperty
    def AC_noise_limited_sensitivity(self):
        return self.AC_ASD / abs(self.AC_sensitivity)

    @mproperty
    def AC_ASD(self):
        return self.AC_PSD**.5

    @mproperty
    def AC_PSD(self):
        return self.AC_CSD_IQ[0, 0]

    @mproperty
    def AC_PSD_by_source(self):
        eachCSD = dict()
        for nobj, subCSD in list(self.noise.CSD_by_source.items()):
            II = subCSD['I', 'I']
            IQ = subCSD['I', 'Q']
            QI = subCSD['Q', 'I']
            QQ = subCSD['Q', 'Q']
            arr = np_roll_2D_mat_back(
                np.array(
                    [[II, IQ], [QI, QQ]]
                )
            )
            print(arr)
            print(arr.dtype)
            arr = np.einsum('...ij,...jk->...ik', self.rotation_matrix_back, arr)
            #this builds the transpose into the sum
            arr = np.einsum('...ij,...kj->...ik', arr, self.rotation_matrix_back)
            eachCSD[nobj] = arr[..., 0, 0]
        return eachCSD

    @mproperty
    def rotation_matrix_back(self):
        phase_rad = self.phase_deg * np.pi / 180
        S = np.sin(phase_rad)
        C = np.cos(phase_rad)
        ROT = np_roll_2D_mat_back(
            np.array(
                [[C, S], [-S, C]]
            )
        )
        return ROT

    @mproperty
    def AC_CSD_IQ_back(self):
        II = self.noise.CSD['I', 'I']
        IQ = self.noise.CSD['I', 'Q']
        QI = self.noise.CSD['Q', 'I']
        QQ = self.noise.CSD['Q', 'Q']
        arr = np_roll_2D_mat_back(
            np.array(
                [[II, IQ], [QI, QQ]]
            )
        )
        #Normal dot product doesn't work here
        arr = np.einsum('...ij,...jk->...ik', self.rotation_matrix_back, arr)
        #this builds the transpose into the sum
        arr = np.einsum('...ij,...kj->...ik', arr, self.rotation_matrix_back)
        return arr

    @mproperty
    def AC_CSD_IQ(self):
        return np_roll_2D_mat_front(
            self.AC_CSD_IQ_back
        )

    @mproperty
    def AC_CSD_IQ_re_inv_back(self):
        return np.linalg.inv(np.real(self.AC_CSD_IQ_back))

    @mproperty
    def AC_CSD_IQ_re_inv(self):
        return np_roll_2D_mat_front(self.AC_CSD_IQ_re_inv_back)

    @mproperty
    def AC_noise_limited_sensitivity_optimal(self):
        arr = self.AC_CSD_IQ_re_inv_back
        IQ  = self.AC_sensitivity_IQ_back
        #Normal dot product doesn't work here
        arr = np.einsum('...j,...jk->...k', IQ, arr)
        #this builds the transpose into the sum
        arr = np.einsum('...i,...i->...', arr, IQ.conjugate())
        return 1/(arr)**.5

    @mproperty
    def AC_CSD_IQ_inv_back(self):
        return np.linalg.inv(self.AC_CSD_IQ_back)

    @mproperty
    def AC_CSD_IQ_inv(self):
        return np_roll_2D_mat_front(self.AC_CSD_IQ_inv_back)

    @mproperty
    def AC_CSD_ellipse(self):
        NIQ = np.real(self.AC_CSD_IQ)
        rtDisc = np.sqrt((NIQ[0, 0] - NIQ[1, 1])**2 + 4*(NIQ[0, 1]*NIQ[1, 0]))
        min_eig = (NIQ[0, 0] + NIQ[1, 1] - rtDisc)/2
        max_eig = (NIQ[0, 0] + NIQ[1, 1] + rtDisc)/2
        disc = NIQ[0, 0] - min_eig
        disc[disc < 0] = 0
        ratio = ((NIQ[1, 0] > 0)*2 - 1) * np.sqrt(disc / (max_eig - min_eig))
        ang_rad = np.pi - np.arccos(ratio)
        return Bunch(
            min = min_eig,
            max = max_eig,
            rad = ang_rad,
            deg = 180 * ang_rad / np.pi,
        )

    @mproperty
    def AC_CSD_ellipse_norm(self):
        ellipse = self.AC_CSD_ellipse
        #TODO, get appropriate wavelength rather than assuming 1064nm
        R = np.sqrt(ellipse.min / ellipse.max)
        return Bunch(
            min = R,
            max = 1 / R,
            rad = ellipse.rad,
            deg = ellipse.deg,
        )

    @mproperty
    def AC_CSD_ellipse_normSN(self):
        ellipse = self.AC_CSD_ellipse
        #TODO, get appropriate wavelength rather than assuming 1064nm
        qmag = self.system.adjust_PSD * self.system.h_Js * self.system.c_m_s / 1064e-9  # * iwavelen_m
        return Bunch(
            min = ellipse.min / qmag,
            max = ellipse.max / qmag,
            rad = ellipse.rad,
            deg = ellipse.deg,
        )

    @mproperty
    def AC_signal_matrix(self):
        SIQ = np.einsum('i...,j...->ji...', self.AC_sensitivity_IQ, self.AC_sensitivity_IQ.conjugate())
        return SIQ

    @mproperty
    def AC_signal_matrix_norm(self):
        SIQ = self.AC_signal_matrix
        SIQ = SIQ / (SIQ[0, 0] + SIQ[1, 1])
        return SIQ

    @mproperty
    def AC_signal_ellipse(self):
        SIQ = np.real(self.AC_signal_matrix)
        rtDisc = np.sqrt((SIQ[0, 0] - SIQ[1, 1])**2 + 4*(SIQ[0, 1]*SIQ[1, 0]))
        min_eig = (SIQ[0, 0] + SIQ[1, 1] - rtDisc)/2
        max_eig = (SIQ[0, 0] + SIQ[1, 1] + rtDisc)/2
        ratio = ((SIQ[1, 0] > 0)*2 - 1) * np.sqrt((SIQ[0, 0] - min_eig) / (max_eig - min_eig))
        ang_rad = np.pi - np.arccos(ratio)
        return Bunch(
            min = min_eig,
            max = max_eig,
            rad = ang_rad,
            deg = 180 * ang_rad / np.pi,
        )

    @mproperty
    def AC_signal_ellipse_norm(self):
        SIQ = np.real(self.AC_signal_matrix_norm)
        rtDisc = np.sqrt((SIQ[0, 0] - SIQ[1, 1])**2 + 4*(SIQ[0, 1]*SIQ[1, 0]))
        min_eig = (SIQ[0, 0] + SIQ[1, 1] - rtDisc)/2
        max_eig = (SIQ[0, 0] + SIQ[1, 1] + rtDisc)/2
        ratio = ((SIQ[1, 0] > 0)*2 - 1) * np.sqrt((SIQ[0, 0] - min_eig) / (max_eig - min_eig))
        ang_rad = np.pi - np.arccos(ratio)
        return Bunch(
            min = min_eig,
            max = max_eig,
            rad = ang_rad,
            deg = 180 * ang_rad / np.pi,
        )

    @mproperty
    def AC_optimal_readout_deg(self):
        NIQ = self.AC_CSD_IQ
        SIQ = self.AC_signal_matrix
        N_0 = np.real(NIQ[0, 0])
        N_1 = np.real(NIQ[1, 1])
        N_c = 2 * np.real(NIQ[0, 1])
        S_0 = np.real(SIQ[0, 0])
        S_1 = np.real(SIQ[1, 1])
        S_c = 2 * np.real(SIQ[0, 1])

        A = (-N_1*S_c + N_c*S_1)
        B = (2*N_0*S_1 - 2*N_1*S_0)
        C = (N_0*S_c - N_c*S_0)
        SGN = (N_0*S_c + N_1*S_c*(N_0*S_1 - N_1*S_0)**2/(N_1*S_c - N_c*S_1)**2 - N_c*S_0 - N_c*S_1*(N_0*S_1 - N_1*S_0)**2/(N_1*S_c - N_c*S_1)**2)
        where_quad = (abs(A) > 1e-7)
        SGN = (N_0**3*S_c*(S_0 - S_1)**2/(N_0*S_c - N_c*S_1)**2 - N_0**2*N_c*S_1*(S_0 - S_1)**2/(N_0*S_c - N_c*S_1)**2 + N_0*S_c - N_c*S_0)
        SOL_quad = ((-B + np.sqrt(-4*A*C + B**2)*np.sign(SGN))[where_quad] / (2*A)[where_quad])
        ang_quad = np.arctan2(np.real(SOL_quad), 1)
        SOL_lin  = -(C/B)[~where_quad]
        ang_lin = np.arctan2(np.real(SOL_lin), 1)
        ans = np.empty(N_0.shape)
        ans[where_quad] = ang_quad
        ans[~where_quad] = ang_lin
        return ans * 180 / np.pi

    @mproperty
    def AC_CSD_IQ_norm(self):
        IQ_mat = np.copy(self.AC_CSD_IQ)
        sqrtIIQQ = np.sqrt(IQ_mat[0, 0] * IQ_mat[1, 1])
        IQ_mat  /= sqrtIIQQ
        return IQ_mat

    @mproperty
    def AC_sensitivity_IQ(self):
        phase_rad = self.phase_deg * np.pi / 180
        I = self._AC_sensitivity(self.readout.portNI)
        Q = self._AC_sensitivity(self.readout.portNQ)
        return np.array([
            np.cos(phase_rad) * I + np.sin(phase_rad) * Q,
            -np.sin(phase_rad) * I + np.cos(phase_rad) * Q,
        ])

    @mproperty
    def AC_sensitivity_IQ_back(self):
        return np_roll_2D_mat_back(
            self.AC_sensitivity_IQ, N = 1,
        )

    def _AC_sensitivity(self, portN):

        pk_DP = (self.readout.portD, self.readout.keyP)
        pk_NP = (portN, self.readout.keyP)

        pk_DrP = (self.readout.portDrv, self.readout.keyP)
        pk_DrN = (self.readout.portDrv, self.readout.keyN)

        cbunch = self.solver.coupling_solution_get(
            drive_set = self.readout.port_set,
            readout_set = self.readout.port_set,
        )

        coupling_matrix_inv = cbunch.coupling_matrix_inv
        N_tot = (
            + coupling_matrix_inv.get((pk_DrP, pk_NP), 0)
            + coupling_matrix_inv.get((pk_DrN, pk_NP), 0)
        )
        D_tot = (
            + coupling_matrix_inv.get((pk_DrP, pk_DP), 0)
            + coupling_matrix_inv.get((pk_DrN, pk_DP), 0)
        )
        return 2 * N_tot / D_tot


class HomodyneNoiseReadout(SystemElementBase):
    def __init__(
            self,
            system,
            portNI,
            portNQ,
            port_set = None,
            AC_sidebands_use = True,
            **kwargs
    ):
        super(HomodyneNoiseReadout, self).__init__(
            system = system,
            **kwargs
        )

        self.portNI = portNI
        self.portNQ = portNQ

        if port_set is None:
            if AC_sidebands_use:
                OOA_ASSIGN(self).port_set = 'AC noise'
            else:
                OOA_ASSIGN(self).port_set = 'DC noise'
        else:
            self.port_set = port_set

        if AC_sidebands_use:
            self.keyP = DictKey({ClassicalFreqKey: FrequencyKey({system.F_AC : 1})})
            self.keyN = DictKey({ClassicalFreqKey: FrequencyKey({system.F_AC : -1})})
        else:
            self.keyP = DictKey({ClassicalFreqKey: FrequencyKey({})})
            self.keyN = DictKey({ClassicalFreqKey: FrequencyKey({})})
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'noise']
        system.readout_port_needed(self.portNI, self.keyP, portsets)
        system.readout_port_needed(self.portNI, self.keyN, portsets)
        system.readout_port_needed(self.portNQ, self.keyP, portsets)
        system.readout_port_needed(self.portNQ, self.keyN, portsets)
        return

    def system_associated_readout_view(self, solver):
        return NoiseMatrixView(
            system   = self.system,
            solver   = solver,
            readout  = self,
            port_set = self.port_set,
            port_map = dict(
                I = self.portNI,
                Q = self.portNQ,
            ),
            keyP = self.keyP,
            keyN = self.keyN,
        )
