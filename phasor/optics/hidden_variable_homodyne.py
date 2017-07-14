# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np

from .. import readouts
from ..system.matrix_injections import TripletNormCoupling

from . import ports
from . import bases

#from . import vacuum


class HiddenVariableHomodynePD(
        bases.OpticalCouplerBase,
        bases.SystemElementBase,
):
    def __init__(
        self,
        source_port      = None,
        phase_deg        = 0,
        include_readouts = False,
        include_quanta   = False,
        include_relative = False,
        **kwargs
    ):
        #TODO make optional, requires adjusting the ports.OpticalNonOriented1PortMixin base to be adjustable
        super(HiddenVariableHomodynePD, self).__init__(**kwargs)
        self.include_quanta = include_quanta
        self.include_relative = include_relative

        self.own.po_Fr    = ports.OpticalPort(sname = 'po_Fr', pchain = 'po_Bk')
        bases.PTREE_ASSIGN(self).phase_deg = phase_deg

        self.own.po_Bk = ports.OpticalPort(sname = 'po_Bk', pchain = 'po_Fr')
        ##Only required if po_Bk isn't used (not a MagicPD)
        #self._fluct = vacuum.OpticalVacuumFluctuation(port = self.po_Fr)

        self.own.rtWpdI   = ports.SignalOutPort()
        self.own.rtWpdQ   = ports.SignalOutPort()
        self.own.rtWpdCmn = ports.SignalOutPort()

        if self.include_quanta:
            self.own.rtQuantumI   = ports.SignalOutPort()
            self.own.rtQuantumQ   = ports.SignalOutPort()

        if self.include_relative:
            self.own.RinI   = ports.SignalOutPort()
            self.own.RadQ   = ports.SignalOutPort()

        if source_port is None:
            self.source_port = self.po_Fr.i
        else:
            self.source_port = source_port
            self.system.own_port_virtual(self, self.source_port)

        self.own.PWR_tot = TotalDCPowerPD(
            port           = self.source_port,
            #include_quanta = self.include_quanta,
        )

        bases.PTREE_ASSIGN(self).include_readouts = include_readouts
        if self.include_readouts:
            self.own.I_DC    = readouts.DCReadout(port = self.rtWpdI.o)
            self.own.Q_DC    = readouts.DCReadout(port = self.rtWpdQ.o)
            if self.include_quanta:
                self.own.qI_DC    = readouts.DCReadout(port = self.rtQuantumI.o)
                self.own.qQ_DC    = readouts.DCReadout(port = self.rtQuantumQ.o)
            if self.include_relative:
                self.own.rI_DC    = readouts.DCReadout(port = self.RinI.o)
                self.own.rQ_DC    = readouts.DCReadout(port = self.RadQ.o)
        return

    def system_setup_ports(self, ports_algorithm):
        def referred_ports_fill(
            out_port_classical,
        ):
            pfrom = self.po_Fr.i
            for kfrom, lkto in ports_algorithm.symmetric_update(self.source_port, out_port_classical.o):
                if kfrom.contains(ports.LOWER):
                    fnew = kfrom[ports.ClassicalFreqKey] - lkto[ports.ClassicalFreqKey]
                    qKey = ports.RAISE
                elif kfrom.contains(ports.RAISE):
                    fnew = kfrom[ports.ClassicalFreqKey] + lkto[ports.ClassicalFreqKey]
                    qKey = ports.LOWER
                if self.system.reject_classical_frequency_order(fnew):
                    continue
                kfrom2 = (
                    kfrom.without_keys(ports.QuantumKey, ports.ClassicalFreqKey)
                    | ports.DictKey({ports.ClassicalFreqKey: fnew})
                    | qKey
                )
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
        if self.include_quanta:
            referred_ports_fill(
                out_port_classical = self.rtQuantumI,
            )
            referred_ports_fill(
                out_port_classical = self.rtQuantumQ,
            )
        if self.include_relative:
            referred_ports_fill(
                out_port_classical = self.RinI,
            )
            referred_ports_fill(
                out_port_classical = self.RadQ,
            )

        ports_fill_2optical_2classical_hdyne(
            system = self.system,
            ports_algorithm = ports_algorithm,
            ports_in_optical = [self.po_Fr.i, self.source_port],
            out_port_classical = self.rtWpdCmn,
        )

        pmap = {
            self.po_Fr.i : self.po_Bk.o,
            self.po_Fr.o : self.po_Bk.i,
            self.po_Bk.i : self.po_Fr.o,
            self.po_Bk.o : self.po_Fr.i,
        }
        for kfrom in ports_algorithm.port_update_get(self.po_Fr.i):
            ports_algorithm.port_coupling_needed(pmap[self.po_Fr.i], kfrom)
        for kto in ports_algorithm.port_update_get(self.po_Fr.o):
            ports_algorithm.port_coupling_needed(pmap[self.po_Fr.o], kto)
        for kfrom in ports_algorithm.port_update_get(self.po_Bk.i):
            ports_algorithm.port_coupling_needed(pmap[self.po_Bk.i], kfrom)
        for kto in ports_algorithm.port_update_get(self.po_Bk.o):
            ports_algorithm.port_coupling_needed(pmap[self.po_Bk.o], kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.source_port):
            #TODO put this into the system
            if np.all(self.phase_deg == 0):
                Stdcplg            = 1
                StdcplgC           = 1
            elif np.all(abs(self.phase_deg + 90) == 180):
                Stdcplg            = self.symbols.i
                StdcplgC           = -self.symbols.i
            elif np.all(abs(self.phase_deg) == 180):
                Stdcplg            = -1
                StdcplgC           = -1
            elif np.all(abs(self.phase_deg - 90) == 180):
                Stdcplg            = -self.symbols.i
                StdcplgC           = self.symbols.i
            else:
                Stdcplg            = self.symbols.math.exp(self.phase_deg / 360 * self.symbols.i2pi)
                StdcplgC           = self.symbols.math.exp(-self.phase_deg / 360 * self.symbols.i2pi)

            def insert_coupling(
                    out_port_classical,
                    Stdcplg, StdcplgC,
                    norm_port,
                    as_quanta,
                    norm_func = lambda v : v**.5,
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

                    if not as_quanta:
                        cplg_adjust = 1
                    else:
                        iwavelen_m, freq_Hz = self.system.optical_frequency_extract(kfrom)
                        cplg_adjust = 1/(self.symbols.h_Js * self.symbols.c_m_s * iwavelen_m / 2)**.5

                    #Both raising and lowering use optCplgC because it is always the conjugate to the other, so it always matches ports.LOWER with the classical field of ports.RAISE
                    #and vice-versa
                    if kfrom.contains(ports.LOWER):
                        #TODO Check factor of 2 overcounting here between raising and lowering
                        if ktoOptP is not None:
                            inj = TripletNormCoupling(
                                pkfrom1     = (self.po_Fr.i,            ktoOptP),
                                pkfrom2     = optCplgC,
                                pkto        = (out_port_classical.o, lkto),
                                pknorm      = norm_port,
                                cplg        = Stdcplg / 2 * cplg_adjust,
                                pknorm_func = norm_func,
                            )
                            matrix_algorithm.injection_insert(inj)
                        if lktoN != lkto and ktoOptN is not None:
                            inj = TripletNormCoupling(
                                pkfrom1     = (self.po_Fr.i, ktoOptN),
                                pkfrom2     = optCplgC,
                                pkto        = (out_port_classical.o, lktoN),
                                pknorm      = norm_port,
                                cplg        = Stdcplg / 2 * cplg_adjust,
                                pknorm_func = norm_func,
                            )
                            matrix_algorithm.injection_insert(inj)
                    elif kfrom.contains(ports.RAISE):
                        #TODO Check factor of 2 overcounting here between raising and lowering
                        # because of conjugation issues, the frequencies are reversed in the lktos for the optical ports.RAISE operators
                        if ktoOptP is not None:
                            inj = TripletNormCoupling(
                                pkfrom1      = (self.po_Fr.i, ktoOptP),
                                pkfrom2     = optCplgC,
                                pkto        = (out_port_classical.o, lktoN),
                                pknorm      = norm_port,
                                cplg        = StdcplgC / 2 * cplg_adjust,
                                pknorm_func = norm_func,
                            )
                            matrix_algorithm.injection_insert(inj)
                        if lktoN != lkto and ktoOptN is not None:
                            inj = TripletNormCoupling(
                                pkfrom1     = (self.po_Fr.i, ktoOptN),
                                pkfrom2     = optCplgC,
                                pkto        = (out_port_classical.o, lkto),
                                pknorm      = norm_port,
                                cplg        = StdcplgC / 2 * cplg_adjust,
                                pknorm_func = norm_func,
                            )
                            matrix_algorithm.injection_insert(inj)
                    else:
                        raise RuntimeError("Boo")

            insert_coupling(
                self.rtWpdI,
                Stdcplg,
                StdcplgC,
                norm_port = self.PWR_tot.pk_WpdDC,
                as_quanta = False,
            )
            insert_coupling(
                self.rtWpdQ,
                self.symbols.i * Stdcplg,
                -self.symbols.i * StdcplgC,
                norm_port = self.PWR_tot.pk_WpdDC,
                as_quanta = False,
            )
            if self.include_quanta:
                insert_coupling(
                    self.rtQuantumI,
                    Stdcplg,
                    StdcplgC,
                    norm_port = self.PWR_tot.pk_WpdDC,
                    as_quanta = True,
                )
                insert_coupling(
                    self.rtQuantumQ,
                    self.symbols.i * Stdcplg,
                    -self.symbols.i * StdcplgC,
                    norm_port = self.PWR_tot.pk_WpdDC,
                    as_quanta = True,
                )
            if self.include_relative:
                insert_coupling(
                    self.RinI,
                    Stdcplg,
                    StdcplgC,
                    norm_port = self.PWR_tot.pk_WpdDC,
                    as_quanta = False,
                    norm_func = lambda v : v,
                )
                insert_coupling(
                    self.RadQ,
                    self.symbols.i * Stdcplg,
                    -self.symbols.i * StdcplgC,
                    norm_port = self.PWR_tot.pk_WpdDC,
                    as_quanta = False,
                    norm_func = lambda v : v,
                )

        for kfrom in matrix_algorithm.port_set_get(self.po_Bk.i):
            matrix_algorithm.port_coupling_insert(self.po_Bk.i, kfrom, self.po_Fr.o, kfrom, 1)

        if self.source_port != self.po_Fr.i:
            for kfrom in matrix_algorithm.port_set_get(self.po_Fr.i):
                matrix_algorithm.port_coupling_insert(self.po_Fr.i, kfrom, self.po_Bk.o, kfrom, 1)

                modulations_fill_2optical_2classical_hdyne(
                    system             = self.system,
                    matrix_algorithm   = matrix_algorithm,
                    pfrom             = self.po_Fr.i,
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
        else:
            #TODO: double check the constants for this case, may (probably) need factor of 2
            for kfrom in matrix_algorithm.port_set_get(self.po_Fr.i):
                matrix_algorithm.port_coupling_insert(self.po_Fr.i, kfrom, self.po_Bk.o, kfrom, 1)

                modulations_fill_2optical_2classical_hdyne(
                    system             = self.system,
                    matrix_algorithm   = matrix_algorithm,
                    pfrom             = self.po_Fr.i,
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
            include_quanta = False,
            **kwargs
    ):
        #TODO make magic optional
        super(TotalDCPowerPD, self).__init__(**kwargs)
        self.include_quanta = include_quanta
        self.port           = port

        self.system.own_port_virtual(self, self.port)

        self.own.WpdDC       = ports.SignalOutPort(sname = 'WpdDC')
        self.fdkey          = ports.DictKey({ports.ClassicalFreqKey: ports.FrequencyKey({})})
        self.pk_WpdDC       = (self.WpdDC.o, self.fdkey)

        if self.include_quanta:
            self.own.QuantaDC       = ports.SignalOutPort(sname = 'QuantaDC')
            self.fdkey          = ports.DictKey({ports.ClassicalFreqKey: ports.FrequencyKey({})})
            self.pk_QuantaDC       = (self.QuantaDC.o, self.fdkey)
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
        if self.include_quanta:
            ports_algorithm.port_coupling_needed(
                self.QuantaDC.o,
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
            if self.include_quanta:
                iwavelen_m, freq_Hz = self.system.optical_frequency_extract(kfrom)
                pwr = self.symbols.h_Js * self.symbols.c_m_s * iwavelen_m / 2
                matrix_algorithm.port_coupling_insert(
                    self.port, kfrom,
                    self.QuantaDC.o, self.fdkey,
                    1 / 2 / pwr,
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
            #needs a list here to decouple port_coupling_needed from using the same port
            for kfrom, lkto in list(ports_algorithm.symmetric_update(pfrom, out_port_classical.o)):
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
                inj = TripletNormCoupling(
                    pkfrom1     = (pfrom, ktoOptP),
                    pkfrom2     = optCplgC,
                    pkto        = (out_port_classical.o, lkto),
                    pknorm      = pknorm,
                    cplg        = Stdcplg / 2,
                    pknorm_func = lambda v : v**.5,
                )
                matrix_algorithm.injection_insert(inj)
            if lktoN != lkto and ktoOptN is not None:
                inj = TripletNormCoupling(
                    pkfrom1     = (pfrom, ktoOptN),
                    pkfrom2     = optCplgC,
                    pkto        = (out_port_classical.o, lktoN),
                    pknorm      = pknorm,
                    cplg        = Stdcplg / 2,
                    pknorm_func = lambda v : v**.5,
                )
                matrix_algorithm.injection_insert(inj)
        elif kfrom.contains(ports.RAISE):
            #TODO Check factor of 2 overcounting here between raising and lowering
            # because of conjugation issues, the frequencies are reversed in the lktos for the optical ports.RAISE operators
            if ktoOptP is not None:
                inj = TripletNormCoupling(
                    pkfrom1     = (pfrom, ktoOptP),
                    pkfrom2     = optCplgC,
                    pkto        = (out_port_classical.o, lktoN),
                    pknorm      = pknorm,
                    cplg        = StdcplgC / 2,
                    pknorm_func = lambda v : v**.5,
                )
                matrix_algorithm.injection_insert(inj)
            if lktoN != lkto and ktoOptN is not None:
                inj = TripletNormCoupling(
                    pkfrom1     = (pfrom, ktoOptN),
                    pkfrom2     = optCplgC,
                    pkto        = (out_port_classical.o, lkto),
                    pknorm      = pknorm,
                    cplg        = StdcplgC / 2,
                    pknorm_func = lambda v : v**.5,
                )
                matrix_algorithm.injection_insert(inj)
        else:
            raise RuntimeError("Boo")
