# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from phasor.utilities.print import print

import numpy as np
import declarative

from .. import base

from . import noise


def np_roll_2D_mat_back(arr_mat, N = 2):
    for idx in range(len(arr_mat.shape) - N):
        arr_mat = np.rollaxis(arr_mat, -1, 0)
    return arr_mat


def np_roll_2D_mat_front(arr_mat, N = 2):
    for idx in range(len(arr_mat.shape) - N):
        arr_mat = np.rollaxis(arr_mat, 0, len(arr_mat.shape))
    return arr_mat


class HomodyneACReadoutBase(base.SystemElementBase):
    def rotate_deg(self, phase_deg):
        #TODO: FIX THESE SEMANTICS

        name = "ROTATOR{0}".format(int(np.random.uniform(0, 1000000)))
        obj = self.insert(
            self.__class__(
                portNI     = self.portNI,
                portNQ     = self.portNQ,
                portD      = self.portD,
                portDrv    = self.portDrv,
                port_set   = self.port_set,
                phase_deg  = self.phase_deg + phase_deg,
            ),
            name
        )
        return obj

    @declarative.mproperty
    def F_Hz(self):
        return self.F_sep.F_Hz

    @declarative.mproperty
    def AC_sensitivity(self):
        return self.AC_sensitivity_IQ[0]

    def homodyne_SNR(self):
        return self.noise.noise / abs(self.AC_sensitivity)

    @declarative.mproperty
    def AC_noise_limited_sensitivity(self):
        return self.AC_ASD / abs(self.AC_sensitivity)

    @declarative.mproperty
    def AC_ASD(self):
        return self.AC_PSD**.5

    @declarative.mproperty
    def AC_PSD(self):
        return self.AC_CSD_IQ[0, 0]

    @declarative.mproperty
    def AC_PSD_by_source(self):
        eachCSD = dict()
        for nobj, subCSD in list(self.noise.CSD_by_source.items()):
            II = subCSD['ps_In', 'ps_In']
            IQ = subCSD['ps_In', 'Q']
            QI = subCSD['Q', 'ps_In']
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

    @declarative.mproperty
    def rotation_matrix_back(self):
        phase_rad = self.phase_deg * np.pi / 180
        S = np.sin(phase_rad)
        pe_C = np.cos(phase_rad)
        ROT = np_roll_2D_mat_back(
            np.array(
                [[pe_C, S], [-S, pe_C]]
            )
        )
        return ROT

    @declarative.mproperty
    def AC_CSD_IQ_back(self):
        II = self.noise.CSD['ps_In', 'ps_In']
        IQ = self.noise.CSD['ps_In', 'Q']
        QI = self.noise.CSD['Q', 'ps_In']
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

    @declarative.mproperty
    def AC_CSD_IQ(self):
        return np_roll_2D_mat_front(
            self.AC_CSD_IQ_back
        )

    @declarative.mproperty
    def AC_CSD_IQ_re_inv_back(self):
        return np.linalg.inv(np.real(self.AC_CSD_IQ_back))

    @declarative.mproperty
    def AC_CSD_IQ_re_inv(self):
        return np_roll_2D_mat_front(self.AC_CSD_IQ_re_inv_back)

    @declarative.mproperty
    def AC_noise_limited_sensitivity_optimal(self):
        arr = self.AC_CSD_IQ_re_inv_back
        IQ  = self.AC_sensitivity_IQ_back
        #Normal dot product doesn't work here
        arr = np.einsum('...j,...jk->...k', IQ, arr)
        #this builds the transpose into the sum
        arr = np.einsum('...i,...i->...', arr, IQ.conjugate())
        return 1/(arr)**.5

    @declarative.mproperty
    def AC_CSD_IQ_inv_back(self):
        return np.linalg.inv(self.AC_CSD_IQ_back)

    @declarative.mproperty
    def AC_CSD_IQ_inv(self):
        return np_roll_2D_mat_front(self.AC_CSD_IQ_inv_back)

    @declarative.mproperty
    def AC_CSD_ellipse(self):
        NIQ            = np.real(self.AC_CSD_IQ)
        rtDisc         = np.sqrt((NIQ[0, 0] - NIQ[1, 1])**2 + 4*(NIQ[0, 1]*NIQ[1, 0]))
        min_eig        = (NIQ[0, 0] + NIQ[1, 1] - rtDisc)/2
        max_eig        = (NIQ[0, 0] + NIQ[1, 1] + rtDisc)/2
        disc           = np.asarray(NIQ[0, 0] - min_eig)
        disc[disc < 0] = 0
        ratio          = ((NIQ[1, 0] > 0)*2 - 1) * np.sqrt(disc / (max_eig - min_eig))
        ang_rad        = np.pi - np.arccos(ratio)
        Imin           = NIQ[0, 0] - abs(NIQ[1, 0])**2 / NIQ[1, 1]
        Qmin           = NIQ[1, 1] - abs(NIQ[1, 0])**2 / NIQ[0, 0]
        return declarative.Bunch(
            ps_In    = self.AC_CSD_IQ[0, 0],
            Q    = self.AC_CSD_IQ[1, 1],
            IQ   = self.AC_CSD_IQ[0, 1],
            min  = min_eig,
            max  = max_eig,
            Imin = Imin,
            Qmin = Qmin,
            rad  = ang_rad,
            deg  = 180 * ang_rad / np.pi,
        )

    @declarative.mproperty
    def AC_CSD_ellipse_norm(self):
        ellipse = self.AC_CSD_ellipse
        #TODO, get appropriate wavelength rather than assuming 1064nm
        R = np.sqrt(ellipse.min / ellipse.max)
        return declarative.Bunch(
            min = R,
            max = 1 / R,
            rad = ellipse.rad,
            deg = ellipse.deg,
        )

    @declarative.mproperty
    def AC_CSD_ellipse_normSN(self):
        ellipse = self.AC_CSD_ellipse
        #TODO, get appropriate wavelength rather than assuming 1064nm
        qmag = self.system.adjust_PSD * self.symbols.h_Js * self.symbols.c_m_s / 1064e-9  # * iwavelen_m
        return declarative.Bunch(
            min = ellipse.min / qmag,
            max = ellipse.max / qmag,
            rad = ellipse.rad,
            deg = ellipse.deg,
        )

    @declarative.mproperty
    def AC_signal_matrix(self):
        SIQ = np.einsum('i...,j...->ji...', self.AC_sensitivity_IQ, self.AC_sensitivity_IQ.conjugate())
        return SIQ

    @declarative.mproperty
    def AC_signal_matrix_norm(self):
        SIQ = self.AC_signal_matrix
        SIQ = SIQ / (SIQ[0, 0] + SIQ[1, 1])
        return SIQ

    @declarative.mproperty
    def AC_signal_ellipse(self):
        SIQ = np.real(self.AC_signal_matrix)
        rtDisc = np.sqrt((SIQ[0, 0] - SIQ[1, 1])**2 + 4*(SIQ[0, 1]*SIQ[1, 0]))
        min_eig = (SIQ[0, 0] + SIQ[1, 1] - rtDisc)/2
        max_eig = (SIQ[0, 0] + SIQ[1, 1] + rtDisc)/2
        ratio = ((SIQ[1, 0] > 0)*2 - 1) * np.sqrt((SIQ[0, 0] - min_eig) / (max_eig - min_eig))
        ang_rad = np.pi - np.arccos(ratio)
        return declarative.Bunch(
            min = min_eig,
            max = max_eig,
            rad = ang_rad,
            deg = 180 * ang_rad / np.pi,
        )

    @declarative.mproperty
    def AC_signal_ellipse_norm(self):
        SIQ = np.real(self.AC_signal_matrix_norm)
        rtDisc = np.sqrt((SIQ[0, 0] - SIQ[1, 1])**2 + 4*(SIQ[0, 1]*SIQ[1, 0]))
        min_eig = (SIQ[0, 0] + SIQ[1, 1] - rtDisc)/2
        max_eig = (SIQ[0, 0] + SIQ[1, 1] + rtDisc)/2
        ratio = ((SIQ[1, 0] > 0)*2 - 1) * np.sqrt((SIQ[0, 0] - min_eig) / (max_eig - min_eig))
        ang_rad = np.pi - np.arccos(ratio)
        return declarative.Bunch(
            min = min_eig,
            max = max_eig,
            rad = ang_rad,
            deg = 180 * ang_rad / np.pi,
        )

    @declarative.mproperty
    def AC_optimal_readout_deg(self):
        NIQ = self.AC_CSD_IQ
        SIQ = self.AC_signal_matrix
        N_0 = np.real(NIQ[0, 0])
        N_1 = np.real(NIQ[1, 1])
        N_c = 2 * np.real(NIQ[0, 1])
        S_0 = np.real(SIQ[0, 0])
        S_1 = np.real(SIQ[1, 1])
        S_c = 2 * np.real(SIQ[0, 1])

        pe_A = (-N_1*S_c + N_c*S_1)
        pe_B = (2*N_0*S_1 - 2*N_1*S_0)
        pe_C = (N_0*S_c - N_c*S_0)
        SGN = (N_0*S_c + N_1*S_c*(N_0*S_1 - N_1*S_0)**2/(N_1*S_c - N_c*S_1)**2 - N_c*S_0 - N_c*S_1*(N_0*S_1 - N_1*S_0)**2/(N_1*S_c - N_c*S_1)**2)
        where_quad = (abs(pe_A) > 1e-7)
        SGN = (N_0**3*S_c*(S_0 - S_1)**2/(N_0*S_c - N_c*S_1)**2 - N_0**2*N_c*S_1*(S_0 - S_1)**2/(N_0*S_c - N_c*S_1)**2 + N_0*S_c - N_c*S_0)
        SOL_quad = ((-pe_B + np.sqrt(-4*pe_A*pe_C + pe_B**2)*np.sign(SGN))[where_quad] / (2*pe_A)[where_quad])
        ang_quad = np.arctan2(np.real(SOL_quad), 1)
        SOL_lin  = -(pe_C/pe_B)[~where_quad]
        ang_lin = np.arctan2(np.real(SOL_lin), 1)
        ans = np.empty(N_0.shape)
        ans[where_quad] = ang_quad
        ans[~where_quad] = ang_lin
        return ans * 180 / np.pi

    @declarative.mproperty
    def AC_CSD_IQ_norm(self):
        IQ_mat = np.copy(self.AC_CSD_IQ)
        sqrtIIQQ = np.sqrt(IQ_mat[0, 0] * IQ_mat[1, 1])
        IQ_mat  /= sqrtIIQQ
        return IQ_mat

    @declarative.mproperty
    def AC_sensitivity_IQ(self):
        phase_rad = self.phase_deg * np.pi / 180
        ps_In = self._AC_sensitivity(self.portNI)
        Q = self._AC_sensitivity(self.portNQ)
        return np.array([
            np.cos(phase_rad) * ps_In + np.sin(phase_rad) * Q,
            -np.sin(phase_rad) * ps_In + np.cos(phase_rad) * Q,
        ])

    @declarative.mproperty
    def AC_sensitivity_IQ_back(self):
        return np_roll_2D_mat_back(
            self.AC_sensitivity_IQ, N = 1,
        )

    def _AC_sensitivity(self, portN):

        pk_DP = (self.portD, self.keyP)
        pk_NP = (portN, self.keyP)

        pk_DrP = (self.portDrv, self.keyP)
        pk_DrN = (self.portDrv, self.keyN)

        cbunch = self.system.solution.coupling_solution_get(
            drive_set = self.port_set,
            readout_set = self.port_set,
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
        return N_tot / D_tot


class HomodyneNoiseReadout(noise.NoiseReadout):
    def __init__(
            self,
            portNI,
            portNQ,
            **kwargs
    ):
        self.portNI = portNI
        self.portNQ = portNQ

        super(HomodyneNoiseReadout, self).__init__(
            port_map = dict(
                ps_In = self.portNI,
                Q = self.portNQ,
            ),
            **kwargs
        )
        return


class HomodyneACReadout(HomodyneACReadoutBase, base.SystemElementBase):
    def __init__(
        self,
        portNI,
        portNQ,
        portD,
        portDrv = None,
        port_set = 'AC',
        phase_deg = 0,
        **kwargs
    ):
        super(HomodyneACReadout, self).__init__(**kwargs)
        if portDrv is None:
            portDrv = portD

        self.portD = portD
        self.portNI = portNI
        self.portNQ = portNQ
        self.portDrv = portDrv

        base.PTREE_ASSIGN(self).port_set = 'AC'

        #TODO: make this adjustable
        self.F_sep = self.system.F_AC

        self.keyP = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.F_sep : 1})})
        self.keyN = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.F_sep : -1})})

        self.own.noise = HomodyneNoiseReadout(
            portNI = self.portNI,
            portNQ = self.portNQ,
        )

        self.phase_deg = phase_deg
        return

    def system_setup_ports_initial(self, ports_algorithm):
        portsets = [self.port_set, 'AC_sensitivities', 'readouts']
        ports_algorithm.readout_port_needed(self.portNI, self.keyP, portsets)
        ports_algorithm.readout_port_needed(self.portNI, self.keyN, portsets)
        ports_algorithm.readout_port_needed(self.portNQ, self.keyP, portsets)
        ports_algorithm.readout_port_needed(self.portNQ, self.keyN, portsets)
        ports_algorithm.readout_port_needed(self.portD, self.keyP, portsets)
        ports_algorithm.readout_port_needed(self.portD, self.keyN, portsets)
        ports_algorithm.drive_port_needed(self.portDrv, self.keyP, portsets)
        ports_algorithm.drive_port_needed(self.portDrv, self.keyN, portsets)
        return

class HomodyneACReadoutSub(base.SystemElementBase):
    pass
