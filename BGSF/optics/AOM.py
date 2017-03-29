# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
#from BGSF.utilities.print import print
import declarative
import collections

from . import bases
from . import ports
from . import nonlinear_utilities
from . import nonlinear_crystal
from ..utilities.print import pprint

class Optical2PortModulator(
    bases.OpticalCouplerBase,
    bases.SystemElementBase,
):
    @declarative.dproperty
    def Fr(self):
        return ports.OpticalPort(sname = 'Fr', pchain = 'Bk')

    @declarative.dproperty
    def Bk(self):
        return ports.OpticalPort(sname = 'Bk', pchain = 'Fr')

    @declarative.dproperty
    def Drv(self):
        return ports.SignalInPort(sname = 'Drv')

    @declarative.dproperty
    def BA(self):
        return ports.SignalOutPort(sname = 'BA')

    @declarative.mproperty
    def ports_optical(self):
        return set([
            self.Fr,
            self.Bk,
        ])

    def system_setup_ports(self, ports_algorithm):
        pmap = {
            self.Fr.i : [self.Bk.o],
            self.Bk.i : [self.Fr.o],
            self.Fr.o : [self.Bk.i],
            self.Bk.o : [self.Fr.i],
        }

        #direct couplings
        for port in self.ports_optical:
            for kfrom in ports_algorithm.port_update_get(port.i):
                for pto in pmap[port.i]:
                    ports_algorithm.port_coupling_needed(pto, kfrom)
            for kto in ports_algorithm.port_update_get(port.o):
                for pfrom in pmap[port.o]:
                    ports_algorithm.port_coupling_needed(pfrom, kto)

        nonlinear_utilities.ports_fill_2optical_2classical(
            self.system,
            ports_algorithm,
            self.ports_optical,
            self.ports_optical,
            pmap,
            self.Drv,
            self.BA,
        )
        return

class AOM(
    bases.OpticalCouplerBase,
    bases.SystemElementBase,
):
    @declarative.dproperty
    def FrA(self):
        return ports.OpticalPort()

    @declarative.dproperty
    def BkA(self):
        return ports.OpticalPort()

    @declarative.dproperty
    def BkB(self):
        return ports.OpticalPort()

    @declarative.dproperty
    def FrB(self):
        return ports.OpticalPort()

    @declarative.dproperty
    def Drv(self):
        return ports.SignalInPort()

    @declarative.dproperty
    def N_ode(self, val = 10):
        """
        Number of iterations to use in the ODE solution
        """
        val = self.ooa_params.setdefault('N_ode', val)
        return val

    @declarative.dproperty
    def solution_order(self, val = 3):
        """
        Taylor expansion order used for the expM in the ODE solution
        """
        val = self.ooa_params.setdefault('solution_order', val)
        return val

    @declarative.dproperty
    def shift_direction(self, val = 'up'):
        assert(val in ['up', 'dn'])
        return val

    @declarative.dproperty
    def freq_split_Hz(self, val = 40e6):
        val = self.ooa_params.setdefault('freq_split_Hz', val)
        return val

    @declarative.dproperty
    def drive_PWR_nominal(self, val = 1):
        return val

    @declarative.mproperty
    def ports_optical(self):
        return set([
            self.FrA,
            self.BkA,
            self.FrB,
            self.BkB,
        ])

    def system_setup_ports(self, ports_algorithm):
        tmap = {
            self.FrA: self.BkA,
            self.BkA: self.FrA,
            self.FrB: self.BkB,
            self.BkB: self.FrB,
        }
        smap = {
            self.FrA: self.BkB,
            self.BkA: self.FrB,
            self.FrB: self.BkA,
            self.BkB: self.FrA,
        }

        for kfrom in ports_algorithm.port_update_get(self.Drv.i):
            drv_ckey = kfrom[ports.ClassicalFreqKey]
            for port in self.ports_optical:
                for kfrom2 in ports_algorithm.port_full_get(port.i):
                    barekey = kfrom2.without_keys(ports.OpticalFreqKey, ports.ClassicalFreqKey, ports.QuantumKey)
                    okey = kfrom2[ports.OpticalFreqKey]
                    ckey = kfrom2[ports.ClassicalFreqKey]
                    qkey = kfrom2[ports.QuantumKey]

                    ckeyO = ckey + drv_ckey
                    if qkey == ports.LOWER[ports.QuantumKey]:
                        neg = 1
                    else:
                        neg = -1

                    if not self.system.reject_classical_frequency_order(ckeyO):
                        nkey = self.system.classical_frequency_extract_center(drv_ckey)
                        if neg * nkey > self.freq_split_Hz:
                            portO = smap[port]
                        if neg * nkey > 0:
                            portO = tmap[port]
                        else:
                            continue

                        ports_algorithm.port_coupling_needed(
                            tmap[port].o,
                            barekey | ports.DictKey({
                                ports.OpticalFreqKey   : okey,
                                ports.ClassicalFreqKey : ckeyO,
                                ports.QuantumKey       : qkey
                            })
                        )
                        ports_algorithm.port_coupling_needed(
                            smap[port].o,
                            barekey | ports.DictKey({
                                ports.OpticalFreqKey   : okey,
                                ports.ClassicalFreqKey : ckeyO,
                                ports.QuantumKey       : qkey
                            })
                        )

        for port in self.ports_optical:
            for kfrom in ports_algorithm.port_update_get(port.i):
                #gets a passthrough always
                ports_algorithm.port_coupling_needed(tmap[port].o, kfrom)

                okey = kfrom[ports.OpticalFreqKey]
                ckey = kfrom[ports.ClassicalFreqKey]
                qkey = kfrom[ports.QuantumKey]
                barekey = kfrom.without_keys(ports.OpticalFreqKey, ports.ClassicalFreqKey, ports.QuantumKey)

                for kfrom2 in ports_algorithm.port_full_get(self.Drv.i):
                    drv_ckey = kfrom2[ports.ClassicalFreqKey]
                    ckeyO = ckey + drv_ckey
                    if qkey == ports.LOWER[ports.QuantumKey]:
                        neg = 1
                    else:
                        neg = -1

                    if not self.system.reject_classical_frequency_order(ckeyO):
                        nkey = self.system.classical_frequency_extract_center(drv_ckey)
                        if neg * nkey > self.freq_split_Hz:
                            portO = smap[port]
                        if neg * nkey > 0:
                            portO = tmap[port]
                        else:
                            continue

                        ports_algorithm.port_coupling_needed(
                            tmap[port].o,
                            barekey | ports.DictKey({
                                ports.OpticalFreqKey   : okey,
                                ports.ClassicalFreqKey : ckeyO,
                                ports.QuantumKey       : qkey
                            })
                        )
                        ports_algorithm.port_coupling_needed(
                            smap[port].o,
                            barekey | ports.DictKey({
                                ports.OpticalFreqKey   : okey,
                                ports.ClassicalFreqKey : ckeyO,
                                ports.QuantumKey       : qkey
                            })
                        )

            for kto in ports_algorithm.port_update_get(port.o):
                #just pass these to the inputs and they will deal with them
                #TODO be smarter!
                ports_algorithm.port_coupling_needed(tmap[port].i, kto)
                ports_algorithm.port_coupling_needed(smap[port].i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        tmap = {
            self.FrA: self.FrA,
            #self.BkA: self.FrA,
            self.FrB: self.FrB,
            #self.BkB: self.FrB,
        }
        smap = {
            self.FrA: self.FrB,
            #self.BkA: self.FrB,
            self.FrB: self.FrA,
            #self.BkB: self.FrA,
        }
        omap = {
            self.FrA: self.BkA,
            #self.BkA: self.FrB,
            self.FrB: self.BkB,
            #self.BkB: self.FrA,
        }

        ddlt = collections.defaultdict(lambda : collections.defaultdict(list))
        out_map = dict()
        in_map = dict()
        for port, direction in {self.FrA : 1, self.FrB : -1}.items():
            for kfrom in matrix_algorithm.port_set_get(port.i):
                #print("KFR: ", kfrom)
                okey = kfrom[ports.OpticalFreqKey]
                ckey = kfrom[ports.ClassicalFreqKey]
                qkey = kfrom[ports.QuantumKey]
                barekey = kfrom.without_keys(ports.OpticalFreqKey, ports.ClassicalFreqKey, ports.QuantumKey)

                #TODO probably need a pi in here
                if qkey == ports.LOWER[ports.QuantumKey]:
                    G = -self.symbols.i / self.drive_PWR_nominal**.5 * self.symbols.pi / 4
                else:
                    G = +self.symbols.i / self.drive_PWR_nominal**.5 * self.symbols.pi / 4

                for kfrom2 in matrix_algorithm.port_set_get(self.Drv.i):
                    drv_ckey = kfrom2[ports.ClassicalFreqKey]
                    if qkey == ports.LOWER[ports.QuantumKey]:
                        neg = 1
                        ckeyO = ckey + drv_ckey
                    else:
                        #to keep the conjugates correct
                        neg = -1
                        ckeyO = ckey - drv_ckey

                    if not self.system.reject_classical_frequency_order(ckeyO):
                        nkey = self.system.classical_frequency_extract_center(drv_ckey)
                        if neg * nkey * direction > self.freq_split_Hz:
                            portO = smap[port]
                        elif neg * nkey * direction > 0:
                            portO = tmap[port]
                        else:
                            continue

                        kto = barekey | ports.DictKey({
                            ports.OpticalFreqKey   : okey,
                            ports.ClassicalFreqKey : ckeyO,
                            ports.QuantumKey       : qkey,
                        })

                        #if neg > 0:
                        #    print("NKEY: ", nkey, neg)
                        #    print("KFR: ", port.i, kfrom)
                        #    print("KFR2: ", self.Drv.i, kfrom2)
                        #    print("KTO: ", portO.i, kto)
                        #    print("G: ", G)
                        ddlt[(portO.i, kto)][(port.i, kfrom)].append(
                            (G, (self.Drv.i, kfrom2))
                        )
                        ddlt[(portO.i, kto)][(self.Drv.i, kfrom2)].append(
                            (G, (port.i, kfrom))
                        )
                        in_map[(port.i, kto)] = (port.i, kto)
                        in_map[(port.i, kfrom)] = (port.i, kfrom)
                        in_map[(portO.i, kto)] = (portO.i, kto)
                        in_map[(portO.i, kfrom)] = (portO.i, kfrom)
                        in_map[(self.Drv.i, kfrom2)] = (self.Drv.i, kfrom2)
                        out_map[(port.i, kto)] = (omap[port].o, kto)
                        out_map[(port.i, kfrom)] = (omap[port].o, kfrom)
                        out_map[(portO.i, kto)] = (omap[portO].o, kto)
                        out_map[(portO.i, kfrom)] = (omap[portO].o, kfrom)
                        out_map[(self.Drv.i, kfrom2)] = None
                        #print("JOIN: ", kfrom, kfrom2, kto)

        matrix_algorithm.injection_insert(
            nonlinear_crystal.ExpMatCoupling(
                ddlt    = ddlt,
                in_map  = in_map,
                out_map = out_map,
                N_ode   = self.N_ode,
                order   = self.solution_order,
            )
        )
        return
