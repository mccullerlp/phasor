# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

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
            pksrc,
            pknorm,
            cplg,
    ):
        self.pkfrom = pkfrom
        self.pkto   = pkto
        self.pksrc  = pksrc
        self.pknorm = pknorm
        self.cplg   = cplg

        self.edges_pkpk_dict = {
            (self.pkfrom, self.pkto) : self.edge_func,
        }
        self.edges_NZ_pkset_dict = {
            (self.pkfrom, self.pkto) : frozenset(),
        }
        self.edges_req_pkset_dict = {
            (self.pkfrom, self.pkto) : frozenset([self.pksrc, self.pknorm]),
        }

    def edge_func(self, sol_vector, sB):
        normalization_PWR = sol_vector.get(self.pknorm, 1)
        source            = sol_vector.get(self.pksrc, 0)
        normalized_gain = source * self.cplg / np.sqrt(normalization_PWR)
        return normalized_gain


class HiddenVariableHomodynePD(
        #OpticalNonOriented1PortMixin,
        OpticalOriented2PortMixin,
        OpticalCouplerBase,
        SystemElementBase,
):
    def __init__(
        self,
        source_port      = None,
        phase_deg        = 0,
        include_readouts = False,
        **kwargs
    ):
        #TODO make optional, requires adjusting the OpticalNonOriented1PortMixin base to be adjustable
        super(HiddenVariableHomodynePD, self).__init__(**kwargs)

        self.Fr    = OpticalPortHolderInOut(self, x = 'Fr')
        OOA_ASSIGN(self).phase_deg = phase_deg

        self.Bk = OpticalPortHolderInOut(self, x = 'Bk')
        ##Only required if Bk isn't used (not a MagicPD)
        #self._fluct = OpticalVacuumFluctuation(port = self.Fr)

        self.rtWpdI = SignalPortHolderOut(self, x = 'rtWpdI')
        self.rtWpdQ = SignalPortHolderOut(self, x = 'rtWpdQ')
        self.rtWpdCmn = SignalPortHolderOut(self, x = 'rtWpdCmn')

        if source_port is None:
            self.source_port = self.Fr.i
        else:
            self.source_port = source_port
            self.system.own_port_virtual(self, self.source_port)

        self.PWR_tot = TotalDCPowerPD(
            port = self.source_port,
        )

        OOA_ASSIGN(self).include_readouts = include_readouts
        if self.include_readouts:
            self.I_DC    = DCReadout(port = self.rtWpdI.o)
            self.Q_DC    = DCReadout(port = self.rtWpdQ.o)
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

        ports_fill_2optical_2classical_hdyne(
            system = self.system,
            ports_algorithm = ports_algorithm,
            ports_in_optical = [self.Fr.i, self.source_port],
            out_port_classical = self.rtWpdCmn,
        )

        pmap = {
            self.Fr.i : self.Bk.o,
            self.Fr.o : self.Bk.i,
            self.Bk.i : self.Fr.o,
            self.Bk.o : self.Fr.i,
        }
        for kfrom in ports_algorithm.port_update_get(self.Fr.i):
            ports_algorithm.port_coupling_needed(pmap[self.Fr.i], kfrom)
        for kto in ports_algorithm.port_update_get(self.Fr.o):
            ports_algorithm.port_coupling_needed(pmap[self.Fr.o], kto)
        for kfrom in ports_algorithm.port_update_get(self.Bk.i):
            ports_algorithm.port_coupling_needed(pmap[self.Bk.i], kfrom)
        for kto in ports_algorithm.port_update_get(self.Bk.o):
            ports_algorithm.port_coupling_needed(pmap[self.Bk.o], kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.source_port):
            #TODO put this into the system
            if self.phase_deg == 0:
                Stdcplg            = 1
                StdcplgC           = 1
            elif self.phase_deg in (90, -270):
                Stdcplg            = self.system.i
                StdcplgC           = -self.system.i
            elif self.phase_deg in (-180,180):
                Stdcplg            = 1
                StdcplgC           = 1
            elif self.phase_deg in (-90, 270):
                Stdcplg            = -self.system.i
                StdcplgC           = self.system.i
            else:
                Stdcplg            = self.system.math.exp(self.phase_deg / 360 * self.system.i2pi)
                StdcplgC           = self.system.math.exp(-self.phase_deg / 360 * self.system.i2pi)

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

                    #optCplg  = (self.source_port, kfrom)
                    optCplgC = (self.source_port, kfrom_conj)

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
                                pksrc       = optCplgC,
                                pknorm      = self.PWR_tot.pk_WpdDC,
                                cplg        = Stdcplg / 2,
                            )
                            matrix_algorithm.injection_insert(inj)
                        if lktoN != lkto and ktoOptN is not None:
                            inj = HomodyneCoupling(
                                pkfrom      = (self.Fr.i, ktoOptN),
                                pkto        = (out_port_classical.o, lktoN),
                                pksrc       = optCplgC,
                                pknorm      = self.PWR_tot.pk_WpdDC,
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
                                pksrc       = optCplgC,
                                pknorm      = self.PWR_tot.pk_WpdDC,
                                cplg        = StdcplgC / 2,
                            )
                            matrix_algorithm.injection_insert(inj)
                        if lktoN != lkto and ktoOptN is not None:
                            inj = HomodyneCoupling(
                                pkfrom      = (self.Fr.i, ktoOptN),
                                pkto        = (out_port_classical.o, lkto),
                                pksrc       = optCplgC,
                                pknorm      = self.PWR_tot.pk_WpdDC,
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

        for kfrom in matrix_algorithm.port_set_get(self.Bk.i):
            matrix_algorithm.port_coupling_insert(self.Bk.i, kfrom, self.Fr.o, kfrom, 1)

        for kfrom in matrix_algorithm.port_set_get(self.Fr.i):
            matrix_algorithm.port_coupling_insert(self.Fr.i, kfrom, self.Bk.o, kfrom, 1)

            modulations_fill_2optical_2classical_hdyne(
                system             = self.system,
                matrix_algorithm   = matrix_algorithm,
                pfrom             = self.Fr.i,
                kfrom              = kfrom,
                out_port_classical = self.rtWpdCmn,
                Stdcplg            = 1,
                StdcplgC           = 1,
                BAcplg             = 1,
                BAcplgC            = 1,
                pknorm             = self.PWR_tot.pk_WpdDC,
            )
        for kfrom in matrix_algorithm.port_set_get(self.source_port):
            modulations_fill_2optical_2classical_hdyne(
                system             = self.system,
                matrix_algorithm   = matrix_algorithm,
                pfrom             = self.source_port,
                kfrom              = kfrom,
                out_port_classical = self.rtWpdCmn,
                Stdcplg            = 1,
                StdcplgC           = 1,
                BAcplg             = 1,
                BAcplgC            = 1,
                pknorm             = self.PWR_tot.pk_WpdDC,
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
        self.fdkey  = DictKey({ClassicalFreqKey: FrequencyKey({})})
        self.pk_WpdDC = (self.WpdDC.o, self.fdkey)
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
            self.fdkey,
        )
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.port):
            if kfrom.contains(LOWER):
                kfrom_conj = (kfrom - LOWER) | RAISE
            else:
                kfrom_conj = (kfrom - RAISE) | LOWER

            matrix_algorithm.port_coupling_insert(
                self.port, kfrom,
                self.WpdDC.o, self.fdkey,
                1 / 2,
                (self.port, kfrom_conj),
            )
        return


def ports_fill_2optical_2classical_hdyne(
        system,
        ports_algorithm,
        ports_in_optical,
        out_port_classical,
):
    for pfrom in ports_in_optical:
        if out_port_classical is not None:
            for kfrom, lkto in ports_algorithm.symmetric_update(pfrom, out_port_classical.o):
                if kfrom.contains(LOWER):
                    fnew = kfrom[ClassicalFreqKey] - lkto[ClassicalFreqKey]
                    qKey = RAISE
                elif kfrom.contains(RAISE):
                    fnew = kfrom[ClassicalFreqKey] + lkto[ClassicalFreqKey]
                    qKey = LOWER
                if system.reject_classical_frequency_order(fnew):
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
                pfrom,
                pfrom,
                subset_second = subset_second
        ):
            if kfrom1.contains(LOWER):
                fdiff = kfrom1[ClassicalFreqKey] - kfrom2[ClassicalFreqKey]
            elif kfrom1.contains(RAISE):
                fdiff = kfrom2[ClassicalFreqKey] - kfrom1[ClassicalFreqKey]
            if system.reject_classical_frequency_order(fdiff):
                continue
            ports_algorithm.port_coupling_needed(
                out_port_classical.o,
                DictKey({ClassicalFreqKey: fdiff})
            )


def modulations_fill_2optical_2classical_hdyne(
    system,
    matrix_algorithm,
    pfrom, kfrom,
    out_port_classical,
    Stdcplg,
    StdcplgC,
    BAcplg,
    BAcplgC,
    pknorm,
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

        #optCplg  = (pfrom, kfrom)
        optCplgC = (pfrom, kfrom_conj)

        ftoOptP = kfrom[ClassicalFreqKey] + lkto[ClassicalFreqKey]
        ftoOptN = kfrom[ClassicalFreqKey] + lktoN[ClassicalFreqKey]

        if not system.reject_classical_frequency_order(ftoOptP):
            ktoOptP = kfrom.without_keys(ClassicalFreqKey) | DictKey({ClassicalFreqKey: ftoOptP})
        else:
            ktoOptP = None

        if not system.reject_classical_frequency_order(ftoOptN):
            ktoOptN = kfrom.without_keys(ClassicalFreqKey) | DictKey({ClassicalFreqKey: ftoOptN})
        else:
            ktoOptN = None
        #Both raising and lowering use optCplgC because it is always the conjugate to the other, so it always matches LOWER with the classical field of RAISE
        #and vice-versa
        if kfrom.contains(LOWER):
            #TODO Check factor of 2 overcounting here between raising and lowering
            if ktoOptP is not None:
                inj = HomodyneCoupling(
                    pkfrom      = (pfrom, ktoOptP),
                    pkto        = (out_port_classical.o, lkto),
                    pksrc       = optCplgC,
                    pknorm      = pknorm,
                    cplg        = Stdcplg / 2,
                )
                matrix_algorithm.injection_insert(inj)
            if lktoN != lkto and ktoOptN is not None:
                inj = HomodyneCoupling(
                    pkfrom      = (pfrom, ktoOptN),
                    pkto        = (out_port_classical.o, lktoN),
                    pksrc       = optCplgC,
                    pknorm      = pknorm,
                    cplg        = Stdcplg / 2,
                )
                matrix_algorithm.injection_insert(inj)
        elif kfrom.contains(RAISE):
            #TODO Check factor of 2 overcounting here between raising and lowering
            # because of conjugation issues, the frequencies are reversed in the lktos for the optical RAISE operators
            if ktoOptP is not None:
                inj = HomodyneCoupling(
                    pkfrom      = (pfrom, ktoOptP),
                    pkto        = (out_port_classical.o, lktoN),
                    pksrc       = optCplgC,
                    pknorm      = pknorm,
                    cplg        = StdcplgC / 2,
                )
                matrix_algorithm.injection_insert(inj)
            if lktoN != lkto and ktoOptN is not None:
                inj = HomodyneCoupling(
                    pkfrom      = (pfrom, ktoOptN),
                    pkto        = (out_port_classical.o, lkto),
                    pksrc       = optCplgC,
                    pknorm      = pknorm,
                    cplg        = StdcplgC / 2,
                )
                matrix_algorithm.injection_insert(inj)
        else:
            raise RuntimeError("Boo")
