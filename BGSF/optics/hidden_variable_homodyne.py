# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
import numpy as np

from ..system.matrix_injections import (
    FactorCouplingBase,
)

from .. import readouts

from . import ports
from . import bases
#from . import vacuum


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
        bases.OpticalCouplerBase,
        bases.SystemElementBase,
):
    def __init__(
        self,
        source_port      = None,
        phase_deg        = 0,
        include_readouts = False,
        **kwargs
    ):
        #TODO make optional, requires adjusting the ports.OpticalNonOriented1PortMixin base to be adjustable
        super(HiddenVariableHomodynePD, self).__init__(**kwargs)

        self.my.Fr    = ports.OpticalPort(sname = 'Fr', pchain = 'Bk')
        bases.OOA_ASSIGN(self).phase_deg = phase_deg

        self.my.Bk = ports.OpticalPort(sname = 'Bk', pchain = 'Fr')
        ##Only required if Bk isn't used (not a MagicPD)
        #self._fluct = vacuum.OpticalVacuumFluctuation(port = self.Fr)

        self.my.rtWpdI = ports.SignalOutPort(sname = 'rtWpdI')
        self.my.rtWpdQ = ports.SignalOutPort(sname = 'rtWpdQ')
        self.my.rtWpdCmn = ports.SignalOutPort(sname = 'rtWpdCmn')

        if source_port is None:
            self.source_port = self.Fr.i
        else:
            self.source_port = source_port
            self.system.own_port_virtual(self, self.source_port)

        self.my.PWR_tot = TotalDCPowerPD(
            port = self.source_port,
        )

        bases.OOA_ASSIGN(self).include_readouts = include_readouts
        if self.include_readouts:
            self.my.I_DC    = readouts.DCReadout(port = self.rtWpdI.o)
            self.my.Q_DC    = readouts.DCReadout(port = self.rtWpdQ.o)
        return

    def system_setup_ports(self, ports_algorithm):
        def referred_ports_fill(
            out_port_classical,
        ):
            pfrom = self.Fr.i
            for kfrom, lkto in ports_algorithm.symmetric_update(self.source_port, out_port_classical.o):
                if kfrom.contains(ports.LOWER):
                    fnew = kfrom[ports.ClassicalFreqKey] - lkto[ports.ClassicalFreqKey]
                    qKey = ports.RAISE
                elif kfrom.contains(ports.RAISE):
                    fnew = kfrom[ports.ClassicalFreqKey] + lkto[ports.ClassicalFreqKey]
                    qKey = ports.LOWER
                if self.system.reject_classical_frequency_order(fnew):
                    continue
                kfrom2 = kfrom.without_keys(ports.QuantumKey, ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey: fnew}) | qKey
                ports_algorithm.port_coupling_needed(pfrom, kfrom2)

            def subset_second(pool2):
                setdict = dict()
                for kfrom2 in pool2:
                    kfrom1_sm = kfrom2.without_keys(ports.ClassicalFreqKey, ports.QuantumKey)
                    if kfrom2.contains(ports.RAISE):
                        kfrom1_sm = kfrom1_sm | ports.LOWER
                    elif kfrom2.contains(ports.LOWER):
                        kfrom1_sm = kfrom1_sm | ports.RAISE
                    group = setdict.setdefault(kfrom1_sm, [])
                    group.append(kfrom2)

                def subset_func(kfrom1):
                    kfrom1_sm = kfrom1.without_keys(ports.ClassicalFreqKey)
                    return setdict.get(kfrom1_sm, [])

                return subset_func
            for kfrom1, kfrom2 in ports_algorithm.symmetric_update(
                    self.source_port,
                    pfrom,
                    subset_second = subset_second
            ):
                if kfrom1.contains(ports.LOWER):
                    fdiff = kfrom1[ports.ClassicalFreqKey] - kfrom2[ports.ClassicalFreqKey]
                elif kfrom1.contains(ports.RAISE):
                    fdiff = kfrom2[ports.ClassicalFreqKey] - kfrom1[ports.ClassicalFreqKey]
                if self.system.reject_classical_frequency_order(fdiff):
                    continue
                ports_algorithm.port_coupling_needed(
                    out_port_classical.o,
                    ports.DictKey({ports.ClassicalFreqKey: fdiff})
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
                Stdcplg            = self.symbols.i
                StdcplgC           = -self.symbols.i
            elif self.phase_deg in (-180,180):
                Stdcplg            = 1
                StdcplgC           = 1
            elif self.phase_deg in (-90, 270):
                Stdcplg            = -self.symbols.i
                StdcplgC           = self.symbols.i
            else:
                Stdcplg            = self.symbols.math.exp(self.phase_deg / 360 * self.symbols.i2pi)
                StdcplgC           = self.symbols.math.exp(-self.phase_deg / 360 * self.symbols.i2pi)

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
                    lk_freq = lkto[ports.ClassicalFreqKey]
                    assert(not lkto - ports.DictKey({ports.ClassicalFreqKey: lk_freq}))
                    lk_freqN = -lk_freq
                    lktoN = ports.DictKey({ports.ClassicalFreqKey: lk_freqN})
                    assert(lktoN in lktos)
                    lkto_completed.add(lkto)
                    lkto_completed.add(lktoN)

                    if kfrom.contains(ports.LOWER):
                        kfrom_conj = (kfrom - ports.LOWER) | ports.RAISE
                    else:
                        kfrom_conj = (kfrom - ports.RAISE) | ports.LOWER

                    #optCplg  = (self.source_port, kfrom)
                    optCplgC = (self.source_port, kfrom_conj)

                    ftoOptP = kfrom[ports.ClassicalFreqKey] + lkto[ports.ClassicalFreqKey]
                    ftoOptN = kfrom[ports.ClassicalFreqKey] + lktoN[ports.ClassicalFreqKey]

                    if not self.system.reject_classical_frequency_order(ftoOptP):
                        ktoOptP = kfrom.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey: ftoOptP})
                    else:
                        ktoOptP = None

                    if not self.system.reject_classical_frequency_order(ftoOptN):
                        ktoOptN = kfrom.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey: ftoOptN})
                    else:
                        ktoOptN = None
                    #Both raising and lowering use optCplgC because it is always the conjugate to the other, so it always matches ports.LOWER with the classical field of ports.RAISE
                    #and vice-versa
                    if kfrom.contains(ports.LOWER):
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
                    elif kfrom.contains(ports.RAISE):
                        #TODO Check factor of 2 overcounting here between raising and lowering
                        # because of conjugation issues, the frequencies are reversed in the lktos for the optical ports.RAISE operators
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
                self.symbols.i * Stdcplg,
                -self.symbols.i * StdcplgC,
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
        bases.OpticalCouplerBase,
        bases.SystemElementBase
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
        self.my.WpdDC = ports.SignalOutPort(sname = 'WpdDC')
        self.fdkey  = ports.DictKey({ports.ClassicalFreqKey: ports.FrequencyKey({})})
        self.pk_WpdDC = (self.WpdDC.o, self.fdkey)
        return

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.port):
            if kfrom.contains(ports.LOWER):
                qKey = ports.RAISE
            elif kfrom.contains(ports.RAISE):
                qKey = ports.LOWER
            kfrom2 = kfrom.without_keys(ports.QuantumKey) | qKey
            ports_algorithm.port_coupling_needed(self.port, kfrom2)
        ports_algorithm.port_coupling_needed(
            self.WpdDC.o,
            self.fdkey,
        )
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.port):
            if kfrom.contains(ports.LOWER):
                kfrom_conj = (kfrom - ports.LOWER) | ports.RAISE
            else:
                kfrom_conj = (kfrom - ports.RAISE) | ports.LOWER

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
                if kfrom.contains(ports.LOWER):
                    fnew = kfrom[ports.ClassicalFreqKey] - lkto[ports.ClassicalFreqKey]
                    qKey = ports.RAISE
                elif kfrom.contains(ports.RAISE):
                    fnew = kfrom[ports.ClassicalFreqKey] + lkto[ports.ClassicalFreqKey]
                    qKey = ports.LOWER
                if system.reject_classical_frequency_order(fnew):
                    continue
                kfrom2 = kfrom.without_keys(ports.QuantumKey, ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey: fnew}) | qKey
                ports_algorithm.port_coupling_needed(pfrom, kfrom2)

        def subset_second(pool2):
            setdict = dict()
            for kfrom2 in pool2:
                kfrom1_sm = kfrom2.without_keys(ports.ClassicalFreqKey, ports.QuantumKey)
                if kfrom2.contains(ports.RAISE):
                    kfrom1_sm = kfrom1_sm | ports.LOWER
                elif kfrom2.contains(ports.LOWER):
                    kfrom1_sm = kfrom1_sm | ports.RAISE
                group = setdict.setdefault(kfrom1_sm, [])
                group.append(kfrom2)

            def subset_func(kfrom1):
                kfrom1_sm = kfrom1.without_keys(ports.ClassicalFreqKey)
                return setdict.get(kfrom1_sm, [])

            return subset_func
        for kfrom1, kfrom2 in ports_algorithm.symmetric_update(
                pfrom,
                pfrom,
                subset_second = subset_second
        ):
            if kfrom1.contains(ports.LOWER):
                fdiff = kfrom1[ports.ClassicalFreqKey] - kfrom2[ports.ClassicalFreqKey]
            elif kfrom1.contains(ports.RAISE):
                fdiff = kfrom2[ports.ClassicalFreqKey] - kfrom1[ports.ClassicalFreqKey]
            if system.reject_classical_frequency_order(fdiff):
                continue
            ports_algorithm.port_coupling_needed(
                out_port_classical.o,
                ports.DictKey({ports.ClassicalFreqKey: fdiff})
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
        lk_freq = lkto[ports.ClassicalFreqKey]
        assert(not lkto - ports.DictKey({ports.ClassicalFreqKey: lk_freq}))
        lk_freqN = -lk_freq
        lktoN = ports.DictKey({ports.ClassicalFreqKey: lk_freqN})
        assert(lktoN in lktos)
        lkto_completed.add(lkto)
        lkto_completed.add(lktoN)

        if kfrom.contains(ports.LOWER):
            kfrom_conj = (kfrom - ports.LOWER) | ports.RAISE
        else:
            kfrom_conj = (kfrom - ports.RAISE) | ports.LOWER

        #optCplg  = (pfrom, kfrom)
        optCplgC = (pfrom, kfrom_conj)

        ftoOptP = kfrom[ports.ClassicalFreqKey] + lkto[ports.ClassicalFreqKey]
        ftoOptN = kfrom[ports.ClassicalFreqKey] + lktoN[ports.ClassicalFreqKey]

        if not system.reject_classical_frequency_order(ftoOptP):
            ktoOptP = kfrom.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey: ftoOptP})
        else:
            ktoOptP = None

        if not system.reject_classical_frequency_order(ftoOptN):
            ktoOptN = kfrom.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey: ftoOptN})
        else:
            ktoOptN = None
        #Both raising and lowering use optCplgC because it is always the conjugate to the other, so it always matches ports.LOWER with the classical field of ports.RAISE
        #and vice-versa
        if kfrom.contains(ports.LOWER):
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
        elif kfrom.contains(ports.RAISE):
            #TODO Check factor of 2 overcounting here between raising and lowering
            # because of conjugation issues, the frequencies are reversed in the lktos for the optical ports.RAISE operators
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
