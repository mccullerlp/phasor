# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
import collections
import copy
import numpy as np
from ..utilities.print import pprint

import declarative

from . import ports
from . import bases
from . import standard_attrs
from . import ODE_solver


class NonlinearCrystal(
    bases.OpticalCouplerBase,
    bases.SystemElementBase,
):
    """
    """
    @declarative.dproperty
    def N_ode(self, val = 10):
        """
        Number of iterations to use in the ODE solution
        """
        val = self.ctree.setdefault('N_ode', val)
        return val

    @declarative.dproperty
    def nlg(self, val):
        """
        This is in rtW/(W * mm)

        Should al
        """
        val = self.ctree.setdefault('nlg', val)
        return val

    #@declarative.dproperty
    #def length_mm(self, val = 10):
    #    """
    #    in [mm]
    #    """
    #    val = self.ctree.setdefault('length_mm', val)
    #    return val

    _length_default = '10mm'
    length = standard_attrs.generate_length()

    @declarative.dproperty
    def loss(self, val = 0):
        """
        in W/(W * mm)
        """
        #not yet implemented
        assert(val == 0)
        return val

    def __build__(self):
        super(NonlinearCrystal, self).__build__()
        self.own.po_Fr   = ports.OpticalPort(sname = 'po_Fr', pchain = lambda : self.po_Bk)
        self.own.po_Bk   = ports.OpticalPort(sname = 'po_Bk', pchain = lambda : self.po_Fr)
        return

    @declarative.mproperty
    def ports_optical(self):
        return (
            self.po_Fr,
            self.po_Bk,
        )

    def system_setup_ports(self, ports_algorithm):
        tmap = {
            self.po_Fr: self.po_Bk,
            self.po_Bk: self.po_Fr,
        }

        for port in self.ports_optical:
            for kfrom in ports_algorithm.port_update_get(port.i):
                #gets a passthrough always
                ports_algorithm.port_coupling_needed(tmap[port].o, kfrom)

                okey = kfrom[ports.OpticalFreqKey]
                ckey = kfrom[ports.ClassicalFreqKey]
                qkey = kfrom[ports.QuantumKey]
                barekey = kfrom.without_keys(ports.OpticalFreqKey, ports.ClassicalFreqKey, ports.QuantumKey)

                for kfrom2 in ports_algorithm.port_full_get(port.i):
                    barekey2 = kfrom2.without_keys(ports.OpticalFreqKey, ports.ClassicalFreqKey, ports.QuantumKey)
                    if barekey != barekey2:
                        continue

                    okey2 = kfrom2[ports.OpticalFreqKey]
                    ckey2 = kfrom2[ports.ClassicalFreqKey]
                    qkey2 = kfrom2[ports.QuantumKey]

                    if qkey2 == qkey:
                        #similar quantum keys means sum generation
                        okeyO = okey + okey2
                        ckeyO = ckey + ckey2
                    else:
                        #different keys implies difference generation
                        okeyO = okey - okey2
                        ckeyO = ckey - ckey2

                    if (
                        not self.system.reject_optical_frequency_order(okeyO)
                        and
                        not self.system.reject_classical_frequency_order(ckeyO)
                    ):
                        ports_algorithm.port_coupling_needed(
                            tmap[port].o,
                            barekey | ports.DictKey({
                                ports.OpticalFreqKey   : okeyO,
                                ports.ClassicalFreqKey : ckeyO,
                                ports.QuantumKey       : qkey
                            })
                        )

                    #in the difference case there can also be conjugate generation, so try the other difference as well
                    if qkey2 != qkey:
                        #different keys implies difference generation
                        okeyO = okey2 - okey
                        ckeyO = ckey2 - ckey
                        if (
                            not self.system.reject_optical_frequency_order(okeyO)
                            and
                            not self.system.reject_classical_frequency_order(ckeyO)
                        ):
                            #note using qkey2
                            ports_algorithm.port_coupling_needed(
                                tmap[port].o,
                                barekey | ports.DictKey({
                                    ports.OpticalFreqKey   : okeyO,
                                    ports.ClassicalFreqKey : ckeyO,
                                    ports.QuantumKey       : qkey2
                                })
                            )

            for kto in ports_algorithm.port_update_get(port.o):
                #just pass these to the input and it will deal with them
                ports_algorithm.port_coupling_needed(tmap[port].i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        tmap = {
            self.po_Fr: self.po_Bk,
            self.po_Bk: self.po_Fr,
        }

        for port in self.ports_optical:
            dLt = collections.defaultdict(list)
            out_map = dict()
            in_map = dict()
            portO = tmap[port]
            for kfrom in matrix_algorithm.port_set_get(port.i):
                #print("KFR: ", kfrom)
                okey = kfrom[ports.OpticalFreqKey]
                ckey = kfrom[ports.ClassicalFreqKey]
                qkey = kfrom[ports.QuantumKey]
                barekey = kfrom.without_keys(ports.OpticalFreqKey, ports.ClassicalFreqKey, ports.QuantumKey)

                if qkey == ports.LOWER[ports.QuantumKey]:
                    G = +self.symbols.i * self.nlg * self.length_mm.val
                else:
                    G = -self.symbols.i * self.nlg * self.length_mm.val

                for kfrom2 in matrix_algorithm.port_set_get(port.i):
                    #TODO could halve the number of ops here between these loops
                    barekey2 = kfrom2.without_keys(ports.OpticalFreqKey, ports.ClassicalFreqKey, ports.QuantumKey)
                    if barekey != barekey2:
                        continue

                    okey2 = kfrom2[ports.OpticalFreqKey]
                    ckey2 = kfrom2[ports.ClassicalFreqKey]
                    qkey2 = kfrom2[ports.QuantumKey]

                    if qkey2 == qkey:
                        #similar quantum keys means sum generation
                        okeyO = okey + okey2
                        ckeyO = ckey + ckey2
                    else:
                        #different keys implies difference generation
                        okeyO = okey - okey2
                        ckeyO = ckey - ckey2

                    kto = barekey | ports.DictKey({
                        ports.OpticalFreqKey   : okeyO,
                        ports.ClassicalFreqKey : ckeyO,
                        ports.QuantumKey       : qkey,
                    })

                    #print("KFR2: ", kfrom2)
                    #print("KTO: ", kto)
                    if kto in matrix_algorithm.port_set_get(portO.o):
                        F_list = list(okeyO.F_dict.items())
                        if len(F_list) > 1:
                            raise RuntimeError("Can't Currently do nonlinear optics on multiply composite wavelengths")
                        F, n = F_list[0]
                        #factor of two since this injects twice
                        if kfrom == kfrom2:
                            dLt[(port.i, kto)].append(
                                (n * G / 2, (port.i, kfrom2), (port.i, kfrom))
                            )
                        else:
                            dLt[(port.i, kto)].append(
                                (n * G, (port.i, kfrom2), (port.i, kfrom))
                            )
                        in_map[(port.i, kfrom)] = (port.i, kfrom)
                        out_map[(port.i, kto)] = (portO.o, kto)
                        #print("JOIN: ", kfrom, kfrom2, kto)

                    #in the difference case there can also be conjugate generation, so try the other difference as well
                    #if qkey2 != qkey:
                    #    #note the reversal from above
                    #    okeyO = okey2 - okey
                    #    ckeyO = ckey2 - ckey
                    #    #note using qkey2 and negating the gain for the alternate out conjugation
                    #    kto = barekey | ports.DictKey({
                    #        ports.OpticalFreqKey   : okeyO,
                    #        ports.ClassicalFreqKey : ckeyO,
                    #        ports.QuantumKey       : qkey2,
                    #    })

                    #    if kto in matrix_algorithm.port_set_get(portO.o):
                    #        F_list = list(okeyO.F_dict.items())
                    #        if len(F_list) > 1:
                    #            raise RuntimeError("Can't Currently do nonlinear optics on multiply composite wavelengths")
                    #        F, n = F_list[0]

                    #        dLt[(port.i, kto)].append(
                    #            (-n * G / 2, (port.i, kfrom2), (port.i, kfrom))
                    #        )
                    #        in_map[(port.i, kfrom)] = (port.i, kfrom)
                    #        out_map[(port.i, kto)] = (portO.o, kto)
                    #        #print("JOIN2: ", kfrom, kfrom2, kto)

            #pprint(dLt)
            matrix_algorithm.injection_insert(
                ODE_solver.ExpMatCoupling(
                    dLt         = dLt,
                    in_map      = in_map,
                    out_map     = out_map,
                    N_ode       = self.N_ode,
                )
            )
        return


