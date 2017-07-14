# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np
#from phasor.utilities.print import print
import declarative

from . import ports
from . import bases
from ..system.matrix_injections import TripletNormCoupling
#from ..utilities.print import pprint



class AOMBasic(
    bases.OpticalCouplerBase,
    bases.SystemElementBase,
):
    @declarative.dproperty
    def po_Fr(self):
        return ports.OpticalPort(pchain = lambda : self.po_Bk)

    @declarative.dproperty
    def po_Bk(self):
        return ports.OpticalPort(pchain = lambda : self.po_Fr)

    @declarative.dproperty
    def Drv(self):
        return ports.SignalInPort()

    @declarative.dproperty
    def Drv_Pwr(self):
        from .. import signals
        return signals.MeanSquareMixer(
            ps_In = self.Drv,
        )

    @declarative.mproperty
    def ports_optical(self):
        return set([
            self.po_Fr,
            self.po_Bk,
        ])

    def system_setup_ports(self, ports_algorithm):
        tmap = {
            self.po_Fr.i: self.po_Bk.o,
            self.po_Fr.o: self.po_Bk.i,
            self.po_Bk.i: self.po_Fr.o,
            self.po_Bk.o: self.po_Fr.i,
        }

        for port, direction in [
            (self.po_Fr.i, 1),
            (self.po_Bk.i, -1),
            (self.po_Fr.o, 1),
            (self.po_Bk.o, -1),
        ]:
            for kfrom in ports_algorithm.port_update_get(self.Drv.i):
                drv_ckey = kfrom[ports.ClassicalFreqKey]
                for kfrom2 in ports_algorithm.port_full_get(port):
                    barekey = kfrom2.without_keys(ports.OpticalFreqKey, ports.ClassicalFreqKey, ports.QuantumKey)
                    okey = kfrom2[ports.OpticalFreqKey]
                    ckey = kfrom2[ports.ClassicalFreqKey]
                    qkey = kfrom2[ports.QuantumKey]

                    if qkey == ports.LOWER[ports.QuantumKey]:
                        neg = 1
                        ckeyO = ckey + drv_ckey
                    else:
                        neg = -1
                        ckeyO = ckey - drv_ckey

                    if not self.system.reject_classical_frequency_order(ckeyO):
                        nkey = self.system.classical_frequency_extract_center(drv_ckey)
                        if neg * nkey * direction <= 0:
                            continue

                        ports_algorithm.port_coupling_needed(
                            tmap[port],
                            barekey | ports.DictKey({
                                ports.OpticalFreqKey   : okey,
                                ports.ClassicalFreqKey : ckeyO,
                                ports.QuantumKey       : qkey
                            })
                        )

            for kfrom in ports_algorithm.port_update_get(port):
                okey = kfrom[ports.OpticalFreqKey]
                ckey = kfrom[ports.ClassicalFreqKey]
                qkey = kfrom[ports.QuantumKey]
                barekey = kfrom.without_keys(ports.OpticalFreqKey, ports.ClassicalFreqKey, ports.QuantumKey)

                for kfrom in ports_algorithm.port_full_get(self.Drv.i):
                    drv_ckey = kfrom[ports.ClassicalFreqKey]
                    if qkey == ports.LOWER[ports.QuantumKey]:
                        neg = 1
                        ckeyO = ckey + drv_ckey
                    else:
                        neg = -1
                        ckeyO = ckey - drv_ckey

                    if not self.system.reject_classical_frequency_order(ckeyO):
                        nkey = self.system.classical_frequency_extract_center(drv_ckey)
                        if neg * nkey * direction <= 0:
                            continue

                        ports_algorithm.port_coupling_needed(
                            tmap[port],
                            barekey | ports.DictKey({
                                ports.OpticalFreqKey   : okey,
                                ports.ClassicalFreqKey : ckeyO,
                                ports.QuantumKey       : qkey
                            })
                        )
                for kfrom2 in ports_algorithm.port_full_get(tmap[port]):
                    okey2 = kfrom2[ports.OpticalFreqKey]
                    ckey2 = kfrom2[ports.ClassicalFreqKey]
                    qkey2 = kfrom2[ports.QuantumKey]
                    barekey2 = kfrom2.without_keys(ports.OpticalFreqKey, ports.ClassicalFreqKey, ports.QuantumKey)
                    if barekey2 != barekey:
                        continue
                    elif okey2 != okey:
                        continue
                    elif qkey2 != qkey:
                        continue
                    if qkey == ports.LOWER[ports.QuantumKey]:
                        neg = 1
                        drv_ckey = ckey2 - ckey
                    else:
                        neg = -1
                        drv_ckey = ckey2 + ckey

                    if not self.system.reject_classical_frequency_order(drv_ckey):
                        nkey = self.system.classical_frequency_extract_center(drv_ckey)
                        if neg * nkey * direction <= 0:
                            continue

                        ports_algorithm.port_coupling_needed(
                            self.Drv.i,
                            ports.DictKey({ports.ClassicalFreqKey : drv_ckey})
                        )
        return

    def system_setup_coupling(self, matrix_algorithm):
        tmap = {
            self.po_Fr: self.po_Bk,
            self.po_Bk: self.po_Fr,
        }

        fdkey  = ports.DictKey({ports.ClassicalFreqKey: ports.FrequencyKey({})})
        pknorm = (self.Drv_Pwr.MS.o, fdkey)
        for port, direction in [
            (self.po_Fr, 1),
            (self.po_Bk, -1),
        ]:
            for kfrom in matrix_algorithm.port_set_get(port.i):
                okey = kfrom[ports.OpticalFreqKey]
                ckey = kfrom[ports.ClassicalFreqKey]
                qkey = kfrom[ports.QuantumKey]
                barekey = kfrom.without_keys(ports.OpticalFreqKey, ports.ClassicalFreqKey, ports.QuantumKey)

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
                        if neg * nkey * direction <= 0:
                            continue

                        kto = barekey | ports.DictKey({
                            ports.OpticalFreqKey   : okey,
                            ports.ClassicalFreqKey : ckeyO,
                            ports.QuantumKey       : qkey,
                        })

                        matrix_algorithm.injection_insert(
                            TripletNormCoupling(
                                pkfrom1 = (port.i, kfrom),
                                pkfrom2 = (self.Drv.i, kfrom2),
                                pkto    = (tmap[port].o, kto),
                                pknorm  = pknorm,
                                cplg    = 1,
                                pknorm_func = lambda val : (2 * val)**.5 if np.any(val != 0) else 1e8,
                            )
                        )
        return
