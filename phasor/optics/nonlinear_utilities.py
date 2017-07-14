# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from phasor.utilities.print import print
#import numpy as np

from . import ports


def ports_fill_2optical_2classical(
        system,
        ports_algorithm,
        ports_in_optical,
        ports_out_optical,
        pmap,
        in_port_classical,
        out_port_classical,
):
    #there are 4**2/2 matches amongst opt_in, out_out, cls_in, cls_out

    for port in ports_in_optical:
        pfrom = port.i
        for ptoOpt in pmap[pfrom]:
            for kfrom in ports_algorithm.port_update_get(pfrom):
                ports_algorithm.port_coupling_needed(ptoOpt, kfrom)
        if in_port_classical is not None:
            for kfrom, lkfrom in ports_algorithm.symmetric_update(pfrom, in_port_classical):
                if kfrom.contains(ports.LOWER):
                    ftoOptP = kfrom[ports.ClassicalFreqKey] + lkfrom[ports.ClassicalFreqKey]
                else:
                    ftoOptP = kfrom[ports.ClassicalFreqKey] - lkfrom[ports.ClassicalFreqKey]
                if system.reject_classical_frequency_order(ftoOptP):
                    continue
                ktoOptP = kfrom.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey: ftoOptP})

                ports_algorithm.prev_solution_needed(pfrom, kfrom)
                ports_algorithm.prev_solution_needed(in_port_classical, lkfrom)

                for ptoOpt in pmap[pfrom]:
                    ports_algorithm.port_coupling_needed(ptoOpt, ktoOptP)
                    ports_algorithm.port_coupling_needed(ptoOpt, kfrom)
                ports_algorithm.coherent_sources_perturb_needed(ptoOpt, ktoOptP)

        if out_port_classical is not None:
            for kfrom, lkto in ports_algorithm.symmetric_update(pfrom, out_port_classical):
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
                pass

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
            if out_port_classical is not None:
                ports_algorithm.port_coupling_needed(
                    out_port_classical,
                    ports.DictKey({ports.ClassicalFreqKey: fdiff})
                )

        ptoOpt = pmap[pfrom]
        def subset_second(pool2):
            setdict = dict()
            for kfrom2 in pool2:
                kfrom1_sm = kfrom2.without_keys(ports.ClassicalFreqKey, ports.QuantumKey)
                if kfrom2.contains(ports.RAISE):
                    kfrom1_sm = kfrom1_sm | ports.RAISE
                elif kfrom2.contains(ports.LOWER):
                    kfrom1_sm = kfrom1_sm | ports.LOWER
                group = setdict.setdefault(kfrom1_sm, [])
                group.append(kfrom2)
            def subset_func(kfrom1):
                kfrom1_sm = kfrom1.without_keys(ports.ClassicalFreqKey)
                return setdict.get(kfrom1_sm, [])
            return subset_func
        for kfrom1, kfrom2 in ports_algorithm.symmetric_update(
                pfrom,
                ptoOpt,
                subset_second = subset_second
        ):
            if kfrom1.contains(ports.LOWER):
                if not kfrom2.contains(ports.LOWER):
                    continue
                fdiff = kfrom2[ports.ClassicalFreqKey] - kfrom1[ports.ClassicalFreqKey]
            elif kfrom1.contains(ports.RAISE):
                if not kfrom2.contains(ports.RAISE):
                    continue
                fdiff = kfrom1[ports.ClassicalFreqKey] - kfrom2[ports.ClassicalFreqKey]
            if system.reject_classical_frequency_order(fdiff):
                continue
            if in_port_classical is not None:
                ports_algorithm.port_coupling_needed(
                    in_port_classical,
                    ports.DictKey({ports.ClassicalFreqKey: fdiff})
                )

    for port in ports_out_optical:
        pto = port.o
        if out_port_classical is not None:
            for kto, lkfrom in ports_algorithm.symmetric_update(pto, out_port_classical):
                if kto.contains(ports.LOWER):
                    ffromOptP = kto[ports.ClassicalFreqKey] - lkfrom[ports.ClassicalFreqKey]
                else:
                    ffromOptP = kto[ports.ClassicalFreqKey] + lkfrom[ports.ClassicalFreqKey]
                if system.reject_classical_frequency_order(ffromOptP):
                    continue
                for pfromOpt in pmap[pto]:
                    ports_algorithm.port_coupling_needed(
                        pfromOpt,
                        kto.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey: ffromOptP})
                    )
                    ports_algorithm.port_coupling_needed(
                        pfromOpt,
                        kto.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey: ffromOptP})
                    )


def modulations_fill_2optical_2classical(
    system,
    matrix_algorithm,
    pfrom, kfrom,
    ptoOpt,
    in_port_classical,
    out_port_classical,
    Stdcplg,
    StdcplgC,
    CLcplg,
    CLcplgC,
    BAcplg,
    BAcplgC,
    include_through_coupling = True,
):
    if ptoOpt is not None and in_port_classical is not None:
        lkfroms = matrix_algorithm.port_set_get(in_port_classical)
    else:
        lkfroms = []
    lkfrom_completed = set()
    for lkfrom in lkfroms:
        #must check and reject already completed ones as the inject generates more lkfroms
        if lkfrom in lkfrom_completed:
            continue
        lk_freq = lkfrom[ports.ClassicalFreqKey]
        assert(not lkfrom - ports.DictKey({ports.ClassicalFreqKey: lk_freq}))
        lk_freqN = -lk_freq
        if lk_freqN == lk_freq:
            #TODO: make the nonlinear system properly handle the DC cases
            continue
        lkfromN = ports.DictKey({ports.ClassicalFreqKey: lk_freqN})
        #print(pfrom.i, ptoOpt.o)
        #print(lkfromN, lkfroms)
        assert(lkfromN in lkfroms)
        lkfrom_completed.add(lkfrom)
        lkfrom_completed.add(lkfromN)

        if kfrom.contains(ports.LOWER):
            kfrom_conj = (kfrom - ports.LOWER) | ports.RAISE
        else:
            kfrom_conj = (kfrom - ports.RAISE) | ports.LOWER

        optCplg  = (pfrom.i, kfrom)
        optCplgC = (pfrom.i, kfrom_conj)

        posCplgP = (in_port_classical, lkfrom)
        posCplgN = (in_port_classical, lkfromN)

        ftoOptP = kfrom[ports.ClassicalFreqKey] + lkfrom[ports.ClassicalFreqKey]
        ftoOptN = kfrom[ports.ClassicalFreqKey] + lkfromN[ports.ClassicalFreqKey]

        if not system.reject_classical_frequency_order(ftoOptP):
            ktoOptP = kfrom.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey: ftoOptP})
        else:
            ktoOptP = None

        if not system.reject_classical_frequency_order(ftoOptN):
            ktoOptN = kfrom.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey: ftoOptN})
        else:
            ktoOptN = None

        if kfrom.contains(ports.LOWER):
            if ktoOptP is not None:
                matrix_algorithm.nonlinear_triplet_insert(
                    optCplg,
                    posCplgP,
                    (ptoOpt.o, ktoOptP),
                    Stdcplg * CLcplg
                )
            if ktoOptN is not None:
                matrix_algorithm.nonlinear_triplet_insert(
                    optCplg,
                    posCplgN,
                    (ptoOpt.o, ktoOptN),
                    Stdcplg * CLcplg
                )
        else:
            #TODO check
            if ktoOptP is not None:
                matrix_algorithm.nonlinear_triplet_insert(
                    optCplg,
                    posCplgN,
                    (ptoOpt.o, ktoOptP),
                    StdcplgC * CLcplgC
                )
            if ktoOptN is not None:
                matrix_algorithm.nonlinear_triplet_insert(
                    optCplg,
                    posCplgP,
                    (ptoOpt.o, ktoOptN),
                    StdcplgC * CLcplgC
                )
    if ptoOpt is not None and include_through_coupling:
        if kfrom.contains(ports.LOWER):
            matrix_algorithm.port_coupling_insert(
                pfrom.i, kfrom, ptoOpt.o, kfrom,
                Stdcplg,
            )
        else:
            matrix_algorithm.port_coupling_insert(
                pfrom.i, kfrom, ptoOpt.o, kfrom,
                StdcplgC,
            )

    if out_port_classical is not None:
        lktos = matrix_algorithm.port_set_get(out_port_classical)
    else:
        lktos = []
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

        optCplg  = (pfrom.i, kfrom)
        optCplgC = (pfrom.i, kfrom_conj)

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
            if lktoN != lkto:
                if ktoOptP is not None:
                    matrix_algorithm.port_coupling_insert(
                        pfrom.i, ktoOptP, out_port_classical, lkto,
                        Stdcplg * BAcplg, optCplgC,
                    )
                if ktoOptN is not None:
                    matrix_algorithm.port_coupling_insert(
                        pfrom.i, ktoOptN, out_port_classical, lktoN,
                        Stdcplg * BAcplg, optCplgC,
                    )
            else:
                if ktoOptP is not None:
                    matrix_algorithm.port_coupling_insert(
                        pfrom.i, ktoOptP, out_port_classical, lkto,
                        Stdcplg * BAcplg / 2, optCplgC,
                    )
        elif kfrom.contains(ports.RAISE):
            #TODO Check factor of 2 overcounting here between raising and lowering
            # because of conjugation issues, the frequencies are reversed in the lktos for the optical ports.RAISE operators
            if lktoN != lkto:
                if ktoOptP is not None:
                    matrix_algorithm.port_coupling_insert(
                        pfrom.i, ktoOptP, out_port_classical, lktoN,
                        StdcplgC * BAcplgC, optCplgC,
                    )
                if ktoOptN is not None:
                    matrix_algorithm.port_coupling_insert(
                        pfrom.i, ktoOptN, out_port_classical, lkto,
                        StdcplgC * BAcplgC, optCplgC,
                    )
            else:
                if ktoOptP is not None:
                    matrix_algorithm.port_coupling_insert(
                        pfrom.i, ktoOptP, out_port_classical, lktoN,
                        StdcplgC * BAcplgC / 2, optCplgC,
                    )
        else:
            raise RuntimeError("Boo")
