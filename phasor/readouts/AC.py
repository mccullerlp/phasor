# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from phasor.utilities.print import print

#import numpy as np

import declarative as decl

from .. import base

from .noise import NoiseReadout


class ACReadout(base.SystemElementBase):

    @decl.dproperty
    def port_set(self, val = 'AC'):
        val = self.ctree.setdefault('port_set', val)
        return val

    def __init__(
        self,
        portN,
        portD,
        portDrv = None,
        include_noise = True,
        **kwargs
    ):
        super(ACReadout, self).__init__(**kwargs)
        if portDrv is None:
            portDrv = portD

        self.portD = portD
        self.portN = portN
        self.portDrv = portDrv

        #TODO: make this adjustable
        self.F_sep = self.system.F_AC

        self.keyP = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.F_sep : 1})})
        self.keyN = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.F_sep : -1})})

        if include_noise:
            self.own.noise = NoiseReadout(
                portN = self.portN,
            )
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'AC_sensitivities', 'readouts']
        system.readout_port_needed(self.portN, self.keyP, portsets)
        system.readout_port_needed(self.portN, self.keyN, portsets)
        system.readout_port_needed(self.portD, self.keyP, portsets)
        system.readout_port_needed(self.portD, self.keyN, portsets)
        system.drive_port_needed(self.portDrv, self.keyP, portsets)
        system.drive_port_needed(self.portDrv, self.keyN, portsets)
        return

    @decl.mproperty
    def F_Hz(self):
        return self.F_sep.F_Hz

    @decl.mproperty
    def AC_sensitivityOL(self):

        pk_DP = (self.portD, self.keyP)
        pk_DN = (self.portD, self.keyN)

        pk_NP = (self.portN, self.keyP)
        pk_NN = (self.portN, self.keyN)

        pk_DrP = (self.portDrv, self.keyP)
        pk_DrN = (self.portDrv, self.keyN)

        cbunch = self.system.solution.coupling_solution_get(
            drive_set = self.port_set,
            readout_set = self.port_set,
        )

        coupling_matrix_inv = cbunch.coupling_matrix_inv

        #print("PP", coupling_matrix_inv.get((pk_DrP, pk_NP), 0))
        #print("NN", coupling_matrix_inv.get((pk_DrN, pk_NP), 0))
        #print("PN", coupling_matrix_inv.get((pk_DrP, pk_NN), 0))
        #print("NN", coupling_matrix_inv.get((pk_DrN, pk_NN), 0))
        N_tot = (
            + coupling_matrix_inv.get((pk_DrP, pk_NP), 0)
            + coupling_matrix_inv.get((pk_DrN, pk_NP), 0)
            #+ coupling_matrix_inv.get((pk_DrP, pk_NN), 0)
            #+ coupling_matrix_inv.get((pk_DrN, pk_NN), 0)
        )
        D_tot = (
            + coupling_matrix_inv.get((pk_DrP, pk_DP), 0)
            + coupling_matrix_inv.get((pk_DrN, pk_DP), 0)
            #+ coupling_matrix_inv.get((pk_DrP, pk_DN), 0)
            #+ coupling_matrix_inv.get((pk_DrN, pk_DN), 0)
        )
        #print("NTOT: ", N_tot)
        #print("DOT: ", D_tot)
        return N_tot / D_tot

    @decl.mproperty
    def AC_sensitivity(self):
        pk_NP = (self.portN, self.keyP)
        pk_NN = (self.portN, self.keyN)

        pk_DrP = (self.portDrv, self.keyP)
        pk_DrN = (self.portDrv, self.keyN)

        cbunch = self.system.solution.coupling_solution_get(
            drive_set = self.port_set,
            readout_set = self.port_set,
        )

        coupling_matrix_inv = cbunch.coupling_matrix_inv

        #print("PP", coupling_matrix_inv.get((pk_DrP, pk_NP), 0))
        #print("NN", coupling_matrix_inv.get((pk_DrN, pk_NP), 0))
        #print("PN", coupling_matrix_inv.get((pk_DrP, pk_NN), 0))
        #print("NN", coupling_matrix_inv.get((pk_DrN, pk_NN), 0))
        N_tot = (
            + coupling_matrix_inv.get((pk_DrP, pk_NP), 0)
            + coupling_matrix_inv.get((pk_DrN, pk_NP), 0)
            #+ coupling_matrix_inv.get((pk_DrP, pk_NN), 0)
            #+ coupling_matrix_inv.get((pk_DrN, pk_NN), 0)
        )
        return N_tot


    @decl.mproperty
    def AC_noise_limited_sensitivity(self):
        return self.AC_ASD / abs(self.AC_sensitivity)

    @decl.mproperty
    def AC_ASD(self):
        return self.AC_PSD**.5

    @decl.mproperty
    def AC_PSD(self):
        return self.noise.CSD['R', 'R']

    @decl.mproperty
    def AC_PSD_by_source(self):
        eachCSD = dict()
        for nobj, subCSD in list(self.noise.CSD_by_source.items()):
            nsum = subCSD['R', 'R']
            eachCSD[nobj] = nsum
        return eachCSD


class ACReadoutCLG(base.SystemElementBase):

    @decl.dproperty
    def port_set(self, val = 'AC'):
        val = self.ctree.setdefault('port_set', val)
        return val

    def __init__(
        self,
        portN,
        portD,
        include_noise = True,
        **kwargs
    ):
        super(ACReadoutCLG, self).__init__(**kwargs)
        self.portD = portD
        self.portN = portN

        #TODO: make this adjustable
        self.F_sep = self.system.F_AC

        self.keyP = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.F_sep : 1})})
        self.keyN = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.F_sep : -1})})

        if include_noise:
            self.own.noise = NoiseReadout(
                portN = self.portN,
            )
        else:
            self.noise = None
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'AC_sensitivities', 'readouts']
        system.readout_port_needed(self.portN, self.keyP, portsets)
        system.readout_port_needed(self.portN, self.keyN, portsets)
        system.drive_port_needed(self.portD, self.keyP, portsets)
        system.drive_port_needed(self.portD, self.keyN, portsets)
        return

    @decl.mproperty
    def F_Hz(self):
        return self.F_sep.F_Hz

    @decl.mproperty
    def AC_sensitivity(self):

        pk_NP = (self.portN, self.keyP)
        #pk_NN = (self.portD, self.keyN)

        pk_DrP = (self.portD, self.keyP)
        pk_DrN = (self.portD, self.keyN)

        cbunch = self.system.solution.coupling_solution_get(
            drive_set = self.port_set,
            readout_set = self.port_set,
        )

        coupling_matrix_inv = cbunch.coupling_matrix_inv
        N_tot = (
            + coupling_matrix_inv.get((pk_DrP, pk_NP), 0)
            + coupling_matrix_inv.get((pk_DrN, pk_NP), 0)
        )
        #print("NTOT: ", N_tot)
        #print("DOT: ", D_tot)
        #The factor of 2 captures the missing readout power from the negative frequencies
        return N_tot

    @decl.mproperty
    def AC_noise_limited_sensitivity(self):
        return self.AC_ASD / abs(self.AC_sensitivity)

    @decl.mproperty
    def AC_ASD(self):
        return self.AC_PSD**.5

    @decl.mproperty
    def AC_PSD(self):
        return self.noise.CSD['R', 'R']

    @decl.mproperty
    def AC_PSD_by_source(self):
        eachCSD = dict()
        for nobj, subCSD in list(self.noise.CSD_by_source.items()):
            nsum = subCSD['R', 'R']
            eachCSD[nobj] = nsum
        return eachCSD


class ACReadoutLG(base.SystemElementBase):
    @decl.dproperty
    def port_set(self, val = 'AC'):
        val = self.ctree.setdefault('port_set', val)
        return val

    def __init__(
        self,
        portAct   = None,
        portSense = None,
        portDrv   = None,
        include_noise = True,
        **kwargs
    ):
        super(ACReadoutLG, self).__init__(**kwargs)
        self.portAct   = portAct
        self.portSense = portSense
        if portDrv is not None:
            self.portDrv   = portDrv
        elif portAct is not None:
            self.portDrv   = portAct
        elif portSense is not None:
            self.portDrv   = portSense

        #TODO: make this adjustable
        self.F_sep = self.system.F_AC

        self.keyP = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.F_sep : 1})})
        self.keyN = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.F_sep : -1})})

        if include_noise:
            if self.portAct is not None:
                self.own.noiseAct = NoiseReadout(
                    portN = self.portAct,
                )
            if self.portSense is not None:
                self.own.noiseSense = NoiseReadout(
                    portN = self.portSense,
                )
        else:
            self.noise = None
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'AC_sensitivities', 'readouts']
        if self.portAct is not None:
            system.readout_port_needed(self.portAct, self.keyP, portsets)
            system.readout_port_needed(self.portAct, self.keyN, portsets)
            system.drive_port_needed(self.portAct, self.keyP, portsets)
            system.drive_port_needed(self.portAct, self.keyN, portsets)
        if self.portSense is not None:
            system.readout_port_needed(self.portSense, self.keyP, portsets)
            system.readout_port_needed(self.portSense, self.keyN, portsets)
            system.drive_port_needed(self.portSense, self.keyP, portsets)
            system.drive_port_needed(self.portSense, self.keyN, portsets)
        if self.portDrv is not None:
            system.drive_port_needed(self.portDrv, self.keyP, portsets)
            system.drive_port_needed(self.portDrv, self.keyN, portsets)
        return

    @decl.mproperty
    def F_Hz(self):
        return self.F_sep.F_Hz

    @decl.mproperty
    def CLG(self):
        if self.portSense is not None:
            port = self.portSense
        else:
            port = self.portAct

        pk_NP = (port, self.keyP)
        #pk_NN = (self.portD, self.keyN)

        pk_DrP = (port, self.keyP)
        pk_DrN = (port, self.keyN)

        cbunch = self.system.solution.coupling_solution_get(
            drive_set = self.port_set,
            readout_set = self.port_set,
        )

        coupling_matrix_inv = cbunch.coupling_matrix_inv
        N_tot = (
            + coupling_matrix_inv.get((pk_DrP, pk_NP), 0)
            + coupling_matrix_inv.get((pk_DrN, pk_NP), 0)
        )
        #print("NTOT: ", N_tot)
        #print("DOT: ", D_tot)
        #The factor of 2 captures the missing readout power from the negative frequencies
        return N_tot

    @decl.mproperty
    def OLG(self):
        return (1 - self.CLG) / self.CLG

    @decl.mproperty
    def GPlant(self):
        pk_NP = (self.portSense, self.keyP)
        #pk_NN = (self.portD, self.keyN)
        pk_DP = (self.portAct, self.keyP)
        #pk_DN = (self.portAct, self.keyN)

        pk_DrP = (self.portDrv, self.keyP)
        pk_DrN = (self.portDrv, self.keyN)

        cbunch = self.system.solution.coupling_solution_get(
            drive_set = self.port_set,
            readout_set = self.port_set,
        )

        coupling_matrix_inv = cbunch.coupling_matrix_inv
        N_tot = (
            + coupling_matrix_inv.get((pk_DrP, pk_NP), 0)
            #+ coupling_matrix_inv.get((pk_DrN, pk_NP), 0)
        )
        D_tot = (
            + coupling_matrix_inv.get((pk_DrP, pk_DP), 0)
            #+ coupling_matrix_inv.get((pk_DrN, pk_DP), 0)
            #+ coupling_matrix_inv.get((pk_DrP, pk_DN), 0)
            #+ coupling_matrix_inv.get((pk_DrN, pk_DN), 0)
        )
        #print("NTOT: ", N_tot)
        #print("DOT: ", D_tot)
        #The factor of 2 captures the missing readout power from the negative frequencies
        return N_tot / D_tot


