# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from builtins import range
#from phasor.utilities.print import print

import numpy as np
import declarative

from ..math.key_matrix import (
    KeyMatrix,
    #KeyVector,
    KVSpace,
)

from .. import base
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


class MultiACReadout(base.SystemElementBase):
    def __init__(
        self,
        system,
        port_map,
        portD,
        portDrv = None,
        port_set = 'AC',
        **kwargs
    ):
        super(MultiACReadout, self).__init__(system = system, **kwargs)
        if portDrv is None:
            portDrv = portD

        self.portD = portD
        self.port_map = port_map
        self.portDrv = portDrv

        base.PTREE_ASSIGN(self).port_set = 'AC'

        #TODO: make this adjustable
        self.F_sep = system.F_AC

        self.keyP = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.F_sep : 1})})
        self.keyN = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.F_sep : -1})})

        self.noise = MultiNoiseReadout(
            port_map = self.port_map,
        )
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'AC_sensitivities', 'readouts']
        for pname, port in list(self.port_map.items()):
            system.readout_port_needed(port, self.keyP, portsets)
            system.readout_port_needed(port, self.keyN, portsets)
        system.readout_port_needed(self.portD, self.keyP, portsets)
        system.readout_port_needed(self.portD, self.keyN, portsets)
        system.drive_port_needed(self.portDrv, self.keyP, portsets)
        system.drive_port_needed(self.portDrv, self.keyN, portsets)
        return

    def system_associated_readout_view(self, solver):
        noise_view = self.noise.system_associated_readout_view(solver)
        return MultiACReadoutView(
            readout    = self,
            system     = self.system,
            solver     = solver,
            noise_view = noise_view,
            phase_deg  = 0,
        )


class MultiACReadoutView(ReadoutViewBase):
    def __init__(
            self,
            noise_view,
            phase_deg,
            **kwargs
    ):
        super(MultiACReadoutView, self).__init__(**kwargs)
        self.noise     = noise_view
        self.phase_deg = phase_deg

        return

    def select_sources(self, nobj_filter_func):
        noise_view = self.noise.select_sources(nobj_filter_func)
        return self.__class__(
            system     = self.system,
            solver     = self.solver,
            readout    = self.readout,
            noise_view = noise_view,
            phase_deg  = self.phase_deg,
        )

    @declarative.mproperty
    def F_Hz(self):
        return self.readout.F_sep.F_Hz

    @declarative.mproperty
    def AC_sensitivity(self):
        return self.AC_sensitivity_vec[0]

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
        return self.AC_CSD_vec[0, 0]

    @declarative.mproperty
    def AC_PSD_by_source(self):
        raise NotImplementedError()

    @declarative.mproperty
    def vspace(self):
        kv = KVSpace(dtype = np.complex128)
        kv.keys_add(list(self.port_map.keys()))
        kv.freeze()
        return kv

    @declarative.mproperty
    def AC_CSD_KV(self):
        km = KeyMatrix(
            vspace_from = self.vspace,
            vspace_to   = self.vspace,
        )
        for (portA, portB), cplg in list(self.noise.CSD.items()):
            km[portA, portB] = cplg
        return km

    @declarative.mproperty
    def AC_CSD_re_KV(self):
        km = KeyMatrix(
            vspace_from = self.vspace,
            vspace_to   = self.vspace,
        )
        for (portA, portB), cplg in list(self.noise.CSD.items()):
            km[portA, portB] = np.real(cplg)
        return km

    @declarative.mproperty
    def AC_CSD_vec(self):
        return np_roll_2D_mat_front(
            self.AC_CSD_vec_back
        )

    @declarative.mproperty
    def AC_CSD_vec_re_inv_back(self):
        return np.linalg.inv(np.real(self.AC_CSD_vec_back))

    @declarative.mproperty
    def AC_CSD_vec_re_inv(self):
        return np_roll_2D_mat_front(self.AC_CSD_vec_re_inv_back)

    @declarative.mproperty
    def AC_noise_limited_sensitivity_optimal(self):
        arr = self.AC_CSD_vec_re_inv_back
        vec  = self.AC_sensitivity_vec_back
        #Normal dot product doesn't work here
        arr = np.einsum('...j,...jk->...k', vec, arr)
        #this builds the transpose into the sum
        arr = np.einsum('...i,...i->...', arr, vec.conjugate())
        return 1/(arr)**.5

    @declarative.mproperty
    def AC_CSD_vec_inv_back(self):
        return np.linalg.inv(self.AC_CSD_vec_back)

    @declarative.mproperty
    def AC_CSD_vec_inv(self):
        return np_roll_2D_mat_front(self.AC_CSD_vec_inv_back)

    @declarative.mproperty
    def AC_signal_matrix(self):
        Svec = np.einsum('i...,j...->ji...', self.AC_sensitivity_vec, self.AC_sensitivity_vec.conjugate())
        return Svec

    @declarative.mproperty
    def AC_signal_matrix_norm(self):
        Svec = self.AC_signal_matrix
        Svec = Svec / (Svec[0, 0] + Svec[1, 1])
        return Svec

    @declarative.mproperty
    def AC_CSD_vec_norm(self):
        vec_mat = np.copy(self.AC_CSD_vec)
        sqrtIvecQ = np.sqrt(vec_mat[0, 0] * vec_mat[1, 1])
        vec_mat  /= sqrtIvecQ
        return vec_mat

    @declarative.mproperty
    def AC_sensitivity_vec(self):
        phase_rad = self.phase_deg * np.pi / 180
        ps_In = self._AC_sensitivity(self.readout.portNI)
        Q = self._AC_sensitivity(self.readout.portNQ)
        return np.array([
            np.cos(phase_rad) * ps_In + np.sin(phase_rad) * Q,
            -np.sin(phase_rad) * ps_In + np.cos(phase_rad) * Q,
        ])

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


class MultiNoiseReadout(base.SystemElementBase):
    def __init__(
            self,
            system,
            port_map,
            port_set = None,
            AC_sidebands_use = True,
            **kwargs
    ):
        super(MultiNoiseReadout, self).__init__(
            system = system,
            **kwargs
        )

        self.port_map = port_map

        if port_set is None:
            if AC_sidebands_use:
                base.PTREE_ASSIGN(self).port_set = 'AC noise'
            else:
                base.PTREE_ASSIGN(self).port_set = 'DC noise'
        else:
            self.port_set = port_set

        if AC_sidebands_use:
            self.keyP = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({system.F_AC : 1})})
            self.keyN = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({system.F_AC : -1})})
        else:
            self.keyP = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({})})
            self.keyN = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({})})
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'noise']
        for port_name, port in list(self.port_map.items()):
            system.readout_port_needed(port, self.keyP, portsets)
            system.readout_port_needed(port, self.keyN, portsets)
        return

    def system_associated_readout_view(self, solver):
        return NoiseMatrixView(
            system   = self.system,
            solver   = solver,
            readout  = self,
            port_set = self.port_set,
            port_map = self.port_map,
            keyP = self.keyP,
            keyN = self.keyN,
        )
