# -*- coding: utf-8 -*-
"""
NOT SURE IF COMPLETING THIS WILL BE NECESSARY

the standard hidden variable homodyne works OK, this one adds additional optical tespoints to automatically
determine the phasing for the homodyne
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

import numpy as np

from ..math.key_matrix import (
    DictKey,
    FrequencyKey,
)

from .ports import (
    QuantumKey,
    RAISE, LOWER,
    ClassicalFreqKey,
)


from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
    OOA_ASSIGN,
)

from .ports import (
    OpticalPortHolderIn,
    #OpticalPortHolderOut,
    OpticalPortHolderInOut,
    SignalPortHolderIn,
    SignalPortHolderOut,
    OpticalOriented2PortMixin,
    OpticalNonOriented1PortMixin,
)

from ..readouts import (
    DCReadout,
    #ACReadout,
    NoiseReadout,
)

from .vacuum import (
    OpticalVacuumFluctuation,
)

from ..system.matrix_injections import (
    FactorCouplingBase,
)


class HomodyneCoupling(FactorCouplingBase):
    #reset since the base is an @property
    edges_req_pkset_dict = None

    def __init__(
            self,
            pkfrom,
            pkto,
            pkref,
            pkprop_from,  # may be none
            pkprop_to,  # may be none
            cplg,
    ):
        self.pkfrom      = pkfrom
        self.pkto        = pkto
        self.pkref       = pkref
        self.pkprop_from = pkprop_from
        self.pkprop_to   = pkprop_to
        self.pkto        = pkto
        self.cplg        = cplg

        self.edges_pkpk_dict = {
            (self.pkfrom, self.pkto) : self.edge_func,
        }
        self.edges_NZ_pkset_dict = {
            (self.pkfrom, self.pkto) : frozenset(),
        }
        self.edges_req_pkset_dict = {
            (self.pkfrom, self.pkto) : frozenset([self.pkref]),
        }

        if self.pkprop_from is not None:
            self.AC_ins_pk  = ([self.pkprop_from])
            self.AC_outs_pk = ([self.pkprop_to])

    def edge_func(self, sol_vector, sB):
        if self.pkprop_from is not None:
            #print("AC: ", sB.AC_solution)
            if sB.AC_solution is None:
                phase_alter = 1
            else:
                #print("XXXX: ", sB.AC_solution)
                phase_alter = sB.AC_solution[self.pkprop_from, self.pkprop_to]
                #phase_alter = 1
                if np.all(phase_alter == 0):
                    print("WE GOT PROBLEMS OVER HERE WITH THE DARN HOMODYNE")
        else:
            phase_alter = 1
        phase_ref = sol_vector.get(self.pkref, 0)
        total_phased = phase_alter * phase_ref * self.cplg
        if np.all(total_phased != 0):
            phase_only = total_phased / abs(total_phased)
        else:
            phase_only = 1
        return phase_only


class HiddenVariableHomodynePD(
        OpticalNonOriented1PortMixin,
        OpticalCouplerBase,
        SystemElementBase,
):
    def __init__(
        self,
        source_port,
        phase_reference_port,
        phase_propagation_port = None,
        phase_deg              = 0,
        include_readouts       = False,
        **kwargs
    ):
        #TODO make optional, requires adjusting the OpticalNonOriented1PortMixin base to be adjustable
        magic = False
        super(HiddenVariableHomodynePD, self).__init__(**kwargs)

        self.PWR_tot = TotalDCPowerPD(
            port = self.source_port,
        )

        self.Fr    = OpticalPortHolderInOut(self, x = 'Fr')
        OOA_ASSIGN(self).phase_deg = phase_deg

        self.magic = magic
        if magic:
            self.Bk = OpticalPortHolderInOut(self, x = 'Bk')

        self.rtWpdI = SignalPortHolderOut(self, x = 'rtWpdI')
        self.rtWpdQ = SignalPortHolderOut(self, x = 'rtWpdQ')

        self.source_port            = source_port
        self.phase_reference_port   = phase_reference_port
        self.phase_propagation_port = phase_propagation_port

        self.system.own_port_virtual(self, self.source_port)
        self.system.own_port_virtual(self, self.phase_reference_port)
        if self.phase_propagation_port is not None:
            self.system.own_port_virtual(self, self.phase_propagation_port)

        self._fluct = OpticalVacuumFluctuation(port = self.Fr)

        OOA_ASSIGN(self).include_readouts = include_readouts
        if self.include_readouts:
            self.I_DC    = DCReadout(port = self.rtWpdI.o)
            self.Q_DC    = DCReadout(port = self.rtWpdQ.o)
            #TODO, make a correlation readout
            self.I_noise = NoiseReadout(portN = self.rtWpdI.o)
            self.Q_noise = NoiseReadout(portN = self.rtWpdQ.o)
        return

    def system_setup_ports(self, ports_algorithm):
        def referred_ports_fill(
            out_port_classical,
        ):
            pfrom = self.Fr.i
            for kfrom, lkto in ports_algorithm.symmetric_update(self.source_port, out_port_classical.o):
                if kfrom.contains(LOWER):
                    fnew = kfrom[ClassicalFreqKey] - lkto[ClassicalFreqKey]
                    qKey = RAISE
                elif kfrom.contains(RAISE):
                    fnew = kfrom[ClassicalFreqKey] + lkto[ClassicalFreqKey]
                    qKey = LOWER
                if self.system.reject_classical_frequency_order(fnew):
                    continue
                kfrom2 = kfrom.without_keys(QuantumKey, ClassicalFreqKey) | DictKey({ClassicalFreqKey: fnew}) | qKey
                ports_algorithm.port_coupling_needed(pfrom, kfrom2)

            def subset_second(pool2):
                setdict = dict()
                for kfrom2 in pool2:
                    kfrom1_sm = kfrom2.without_keys(ClassicalFreqKey, QuantumKey)
                    if kfrom2.contains(RAISE):
                        kfrom1_sm = kfrom1_sm | LOWER
                    elif kfrom2.contains(LOWER):
                        kfrom1_sm = kfrom1_sm | RAISE
                    group = setdict.setdefault(kfrom1_sm, [])
                    group.append(kfrom2)
                def subset_func(kfrom1):
                    kfrom1_sm = kfrom1.without_keys(ClassicalFreqKey)
                    return setdict.get(kfrom1_sm, [])
                return subset_func
            for kfrom1, kfrom2 in ports_algorithm.symmetric_update(
                    self.source_port,
                    pfrom,
                    subset_second = subset_second
            ):
                if kfrom1.contains(LOWER):
                    fdiff = kfrom1[ClassicalFreqKey] - kfrom2[ClassicalFreqKey]
                elif kfrom1.contains(RAISE):
                    fdiff = kfrom2[ClassicalFreqKey] - kfrom1[ClassicalFreqKey]
                if self.system.reject_classical_frequency_order(fdiff):
                    continue
                ports_algorithm.port_coupling_needed(
                    out_port_classical.o,
                    DictKey({ClassicalFreqKey: fdiff})
                )
        referred_ports_fill(
            out_port_classical = self.rtWpdI,
        )
        referred_ports_fill(
            out_port_classical = self.rtWpdQ,
        )
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.source_port):
            #TODO put this into the system
            if self.phase_deg == 0:
                Stdcplg            = 1
                StdcplgC           = 1
            elif self.phase_deg == 90:
                Stdcplg            = self.system.i
                StdcplgC           = -self.system.i
            elif self.phase_deg == 180:
                Stdcplg            = 1
                StdcplgC           = 1
            elif self.phase_deg == 270:
                Stdcplg            = -self.system.i
                StdcplgC           = self.system.i
            else:
                Stdcplg            = self.system.e**(self.phase_deg / 360 * self.system.i2pi)
                StdcplgC           = self.system.e**(-self.phase_deg / 360 * self.system.i2pi)

            def insert_coupling(
                    out_port_classical,
                    Stdcplg, StdcplgC,
            ):
                lktos = matrix_algorithm.port_set_get(out_port_classical.o)
                lkto_completed = set()
                for lkto in lktos:
                    #must check and reject already completed ones as the inject generates more lktos
                    if lkto in lkto_completed:
                        continue
                    lk_freq = lkto[ClassicalFreqKey]
                    assert(not lkto - DictKey({ClassicalFreqKey: lk_freq}))
                    lk_freqN = -lk_freq
                    lktoN = DictKey({ClassicalFreqKey: lk_freqN})
                    assert(lktoN in lktos)
                    lkto_completed.add(lkto)
                    lkto_completed.add(lktoN)

                    if kfrom.contains(LOWER):
                        kfrom_conj = (kfrom - LOWER) | RAISE
                    else:
                        kfrom_conj = (kfrom - RAISE) | LOWER

                    #optCplg  = (self.phase_reference_port, kfrom)
                    optCplgC = (self.phase_reference_port, kfrom_conj)
                    if self.phase_propagation_port is not None:
                        #optCplgPP  = (self.phase_propagation_port, kfrom)
                        optCplgPPC_from = (self.phase_propagation_port, kfrom_conj)
                        optCplgPPC_to   = (self.Fr.i,                   kfrom_conj)
                    else:
                        #optCplgPP  = None
                        optCplgPPC_from = None
                        optCplgPPC_to   = None

                    ftoOptP = kfrom[ClassicalFreqKey] + lkto[ClassicalFreqKey]
                    ftoOptN = kfrom[ClassicalFreqKey] + lktoN[ClassicalFreqKey]

                    if not self.system.reject_classical_frequency_order(ftoOptP):
                        ktoOptP = kfrom.without_keys(ClassicalFreqKey) | DictKey({ClassicalFreqKey: ftoOptP})
                    else:
                        ktoOptP = None

                    if not self.system.reject_classical_frequency_order(ftoOptN):
                        ktoOptN = kfrom.without_keys(ClassicalFreqKey) | DictKey({ClassicalFreqKey: ftoOptN})
                    else:
                        ktoOptN = None
                    #Both raising and lowering use optCplgC because it is always the conjugate to the other, so it always matches LOWER with the classical field of RAISE
                    #and vice-versa
                    if kfrom.contains(LOWER):
                        #TODO Check factor of 2 overcounting here between raising and lowering
                        if ktoOptP is not None:
                            inj = HomodyneCoupling(
                                pkfrom      = (self.Fr.i,            ktoOptP),
                                pkto        = (out_port_classical.o, lkto),
                                pkref       = optCplgC,
                                pkprop_from = optCplgPPC_from,
                                pkprop_to   = optCplgPPC_to,
                                cplg        = Stdcplg / 2,
                            )
                            matrix_algorithm.injection_insert(inj)
                        if lktoN != lkto and ktoOptN is not None:
                            inj = HomodyneCoupling(
                                pkfrom      = (self.Fr.i, ktoOptN),
                                pkto        = (out_port_classical.o, lktoN),
                                pkref       = optCplgC,
                                pkprop_from = optCplgPPC_from,
                                pkprop_to   = optCplgPPC_to,
                                cplg        = Stdcplg / 2,
                            )
                            matrix_algorithm.injection_insert(inj)
                    elif kfrom.contains(RAISE):
                        #TODO Check factor of 2 overcounting here between raising and lowering
                        # because of conjugation issues, the frequencies are reversed in the lktos for the optical RAISE operators
                        if ktoOptP is not None:
                            inj = HomodyneCoupling(
                                pkfrom      = (self.Fr.i, ktoOptP),
                                pkto        = (out_port_classical.o, lktoN),
                                pkref       = optCplgC,
                                pkprop_from = optCplgPPC_from,
                                pkprop_to   = optCplgPPC_to,
                                cplg        = StdcplgC / 2,
                            )
                            matrix_algorithm.injection_insert(inj)
                        if lktoN != lkto and ktoOptN is not None:
                            inj = HomodyneCoupling(
                                pkfrom      = (self.Fr.i, ktoOptN),
                                pkto        = (out_port_classical.o, lkto),
                                pkref       = optCplgC,
                                pkprop_from = optCplgPPC_from,
                                pkprop_to   = optCplgPPC_to,
                                cplg        = StdcplgC / 2,
                            )
                            matrix_algorithm.injection_insert(inj)
                    else:
                        raise RuntimeError("Boo")

            insert_coupling(
                self.rtWpdI,
                Stdcplg,
                StdcplgC,
            )
            insert_coupling(
                self.rtWpdQ,
                self.system.i * Stdcplg,
                -self.system.i * StdcplgC,
            )
        return


class TotalDCPowerPD(
        OpticalNonOriented1PortMixin,
        OpticalCouplerBase,
        SystemElementBase
):
    def __init__(
            self,
            port,
            **kwargs
    ):
        #TODO make magic optional
        super(TotalDCPowerPD, self).__init__(**kwargs)
        self.port  = port
        self.system.own_port_virtual(self, self.port)
        self.WpdDC = SignalPortHolderOut(self, x = 'WpdDC')
        return

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.port):
            if kfrom.contains(LOWER):
                qKey = RAISE
            elif kfrom.contains(RAISE):
                qKey = LOWER
            kfrom2 = kfrom.without_keys(QuantumKey) | qKey
            ports_algorithm.port_coupling_needed(self.port, kfrom2)
        ports_algorithm.port_coupling_needed(
            self.WpdDC.o,
            DictKey({ClassicalFreqKey: FrequencyKey({})})
        )
        return

    def system_setup_coupling(self, matrix_algorithm):
        lkto = DictKey({ClassicalFreqKey: FrequencyKey({})})
        for kfrom in matrix_algorithm.port_set_get(self.port):
            if kfrom.contains(LOWER):
                kfrom_conj = (kfrom - LOWER) | RAISE
            else:
                kfrom_conj = (kfrom - RAISE) | LOWER

            matrix_algorithm.port_coupling_insert(
                self.port, kfrom,
                self.WpdDC.o, lkto,
                1 / 2,
                (self.port, kfrom_conj),
            )
        return
