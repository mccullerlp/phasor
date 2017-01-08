# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

#import numpy as np

from declarative import (
    mproperty,
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
from .noise import NoiseReadout


class ACReadout(SystemElementBase):

    def __init__(
        self,
        portN,
        portD,
        portDrv = None,
        port_set = 'AC',
        include_noise = True,
        **kwargs
    ):
        super(ACReadout, self).__init__(**kwargs)
        if portDrv is None:
            portDrv = portD

        self.portD = portD
        self.portN = portN
        self.portDrv = portDrv

        OOA_ASSIGN(self).port_set = 'AC'

        #TODO: make this adjustable
        self.F_sep = self.system.F_AC

        self.keyP = DictKey({ClassicalFreqKey: FrequencyKey({self.F_sep : 1})})
        self.keyN = DictKey({ClassicalFreqKey: FrequencyKey({self.F_sep : -1})})

        if include_noise:
            self.noise = NoiseReadout(
                portN = self.portN,
            )
        else:
            self.noise = None
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'AC_sensitivitys', 'readouts']
        system.readout_port_needed(self.portN, self.keyP, portsets)
        system.readout_port_needed(self.portN, self.keyN, portsets)
        system.readout_port_needed(self.portD, self.keyP, portsets)
        system.readout_port_needed(self.portD, self.keyN, portsets)
        system.drive_port_needed(self.portDrv, self.keyP, portsets)
        system.drive_port_needed(self.portDrv, self.keyN, portsets)
        return

    def system_associated_readout_view(self, solver):
        if self.noise is not None:
            noise_view = self.noise.system_associated_readout_view(solver)
        else:
            noise_view = None
        return ACReadoutView(
            readout = self,
            system = self.system,
            solver = solver,
            noise_view = noise_view,
        )


class ACReadoutView(ReadoutViewBase):
    def __init__(
            self,
            noise_view = None,
            **kwargs
    ):
        super(ACReadoutView, self).__init__(**kwargs)
        self.noise = noise_view
        return

    @mproperty
    def F_Hz(self):
        return self.readout.F_sep.F_Hz

    @mproperty
    def AC_sensitivity(self):

        pk_DP = (self.readout.portD, self.readout.keyP)
        #pk_DN = (self.readout.portD, self.readout.keyN)

        pk_NP = (self.readout.portN, self.readout.keyP)
        #pk_NN = (self.readout.portD, self.readout.keyN)

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
        #print("NTOT: ", N_tot)
        #print("DOT: ", D_tot)
        #The factor of 2 captures the missing readout power from the negative frequencies
        return 2 * N_tot / D_tot

    @mproperty
    def AC_noise_limited_sensitivity(self):
        return self.AC_ASD / abs(self.AC_sensitivity)

    @mproperty
    def AC_ASD(self):
        return self.AC_PSD**.5

    @mproperty
    def AC_PSD(self):
        return self.noise.CSD['R', 'R']

    @mproperty
    def AC_PSD_by_source(self):
        eachCSD = dict()
        for nobj, subCSD in self.noise.CSD_by_source.items():
            nsum = subCSD['R', 'R']
            eachCSD[nobj] = nsum
        return eachCSD


class ACReadoutCLG(SystemElementBase):

    def __init__(
        self,
        system,
        portN,
        portD,
        port_set = 'AC',
        include_noise = True,
        **kwargs
    ):
        super(ACReadoutCLG, self).__init__(system = system, **kwargs)
        self.portD = portD
        self.portN = portN

        OOA_ASSIGN(self).port_set = 'AC'

        #TODO: make this adjustable
        self.F_sep = system.F_AC

        self.keyP = DictKey({ClassicalFreqKey: FrequencyKey({self.F_sep : 1})})
        self.keyN = DictKey({ClassicalFreqKey: FrequencyKey({self.F_sep : -1})})

        if include_noise:
            self.noise = NoiseReadout(
                portN = self.portN,
            )
        else:
            self.noise = None
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'AC_sensitivitys', 'readouts']
        system.readout_port_needed(self.portN, self.keyP, portsets)
        system.readout_port_needed(self.portN, self.keyN, portsets)
        system.drive_port_needed(self.portD, self.keyP, portsets)
        system.drive_port_needed(self.portD, self.keyN, portsets)
        return

    def system_associated_readout_view(self, solver):
        if self.noise is not None:
            noise_view = self.noise.system_associated_readout_view(solver)
        else:
            noise_view = None
        return ACReadoutCLGView(
            readout = self,
            system = self.system,
            solver = solver,
            noise_view = noise_view,
        )


class ACReadoutCLGView(ReadoutViewBase):
    def __init__(
            self,
            noise_view = None,
            **kwargs
    ):
        super(ACReadoutCLGView, self).__init__(**kwargs)
        self.noise = noise_view
        return

    @mproperty
    def F_Hz(self):
        return self.readout.F_sep.F_Hz

    @mproperty
    def AC_sensitivity(self):

        pk_NP = (self.readout.portN, self.readout.keyP)
        #pk_NN = (self.readout.portD, self.readout.keyN)

        pk_DrP = (self.readout.portD, self.readout.keyP)
        pk_DrN = (self.readout.portD, self.readout.keyN)

        cbunch = self.solver.coupling_solution_get(
            drive_set = self.readout.port_set,
            readout_set = self.readout.port_set,
        )

        coupling_matrix_inv = cbunch.coupling_matrix_inv
        N_tot = (
            + coupling_matrix_inv.get((pk_DrP, pk_NP), 0)
            + coupling_matrix_inv.get((pk_DrN, pk_NP), 0)
        )
        #print("NTOT: ", N_tot)
        #print("DOT: ", D_tot)
        #The factor of 2 captures the missing readout power from the negative frequencies
        return 2 * N_tot

    @mproperty
    def AC_noise_limited_sensitivity(self):
        return self.AC_ASD / abs(self.AC_sensitivity)

    @mproperty
    def AC_ASD(self):
        return self.AC_PSD**.5

    @mproperty
    def AC_PSD(self):
        return self.noise.CSD['R', 'R']

    @mproperty
    def AC_PSD_by_source(self):
        eachCSD = dict()
        for nobj, subCSD in self.noise.CSD_by_source.items():
            nsum = subCSD['R', 'R']
            eachCSD[nobj] = nsum
        return eachCSD

