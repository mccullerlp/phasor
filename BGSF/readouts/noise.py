# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
from ..utilities.print import pprint
from builtins import object

import numpy as np
from collections import defaultdict

from declarative import (
    mproperty,
    Bunch
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


class NoiseReadout(SystemElementBase):
    def __init__(
            self,
            portN,
            port_set = None,
            AC_sidebands_use = True,
            port_map = None,
            **kwargs
    ):
        super(NoiseReadout, self).__init__(
            **kwargs
        )

        self.portN = portN

        if port_set is None:
            if AC_sidebands_use:
                OOA_ASSIGN(self).port_set = 'AC noise'
            else:
                OOA_ASSIGN(self).port_set = 'DC noise'
        else:
            self.port_set = port_set

        if AC_sidebands_use:
            self.keyP = DictKey({ClassicalFreqKey: FrequencyKey({self.system.F_AC : 1})})
            self.keyN = DictKey({ClassicalFreqKey: FrequencyKey({self.system.F_AC : -1})})
        else:
            self.keyP = DictKey({ClassicalFreqKey: FrequencyKey({})})
            self.keyN = DictKey({ClassicalFreqKey: FrequencyKey({})})

        if port_map is None:
            self.port_map = dict(
                R = self.portN,
            )
        else:
            self.port_map = port_map
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'noise']
        system.readout_port_needed(self.portN, self.keyP, portsets)
        system.readout_port_needed(self.portN, self.keyN, portsets)
        return

    @mproperty
    def CSD(self):
        return self.CSD_builds.nsums

    @mproperty
    def CSD_by_source(self):
        return self.CSD_builds.ncollect

    @mproperty
    def external_collect(self):
        return None
        #TODO
        external_collect = dict()
        for nobj, sumdict in list(self.CSD_by_source.items()):
            if nobj_filter_func(nobj):
                external_collect[nobj] = sumdict
        return external_collect

    @mproperty
    def CSD_builds(self):
        if self.external_collect is not None:
            nsums    = dict()
            for nobj, sumdict in list(self.external_collect.items()):
                for dkey, nsum in list(sumdict.items()):
                    if dkey not in nsums:
                        nsums[dkey] = np.copy(nsum)
                    else:
                        nsums[dkey] += nsum
            return Bunch(
                nsums = nsums,
                ncollect = self.external_collect
            )

        #TODO, can definitely condense this
        cbunch = self.system.solution.coupling_solution_get(
            drive_set = 'noise',
            readout_set = self.port_set,
        )
        coupling_matrix_inv = cbunch.coupling_matrix_inv
        #pprint(coupling_matrix_inv)
        nmap = self.system.solution.noise_map()
        #pprint(("NMAP: ", nmap))

        pkviewsP = dict()
        pkviewsN = dict()
        for pname, port in list(self.port_map.items()):
            pkviewsP[pname] = (port, self.keyP)
            pkviewsN[pname] = (port, self.keyN)

        kvecsP = defaultdict(dict)
        kvecsN = defaultdict(dict)
        for (pkfrom, pkto), cplg in list(coupling_matrix_inv.items()):
            for pname, pkview in list(pkviewsP.items()):
                if pkto == pkview:
                    kvecsP[pname][pkfrom] = cplg
            for pname, pkview in list(pkviewsN.items()):
                if pkto == pkview:
                    kvecsN[pname][pkfrom] = cplg

        ncollect = defaultdict(lambda: defaultdict(lambda: 0))
        nsums    = dict()
        for pnameP, kvecP in list(kvecsP.items()):
            for pnameN, kvecN in list(kvecsN.items()):
                nsum = 0
                for pk1, cplg1 in list(kvecP.items()):
                    nmap_inner = nmap.get(pk1, None)
                    if nmap_inner is None:
                        continue
                    for pk2, cplg2 in list(kvecN.items()):
                        vals = nmap_inner.get(pk2, None)
                        if vals is None:
                            continue
                        for p1, k1, p2, k2, nobj in vals:
                            pspec_2sided = nobj.noise_2pt_expectation(p1, k1, p2, k2)
                            #print("PSPEC: ", p1, k1, p2, k2, pspec_2sided, cplg1 * cplg2)
                            pspec_tot = self.system.adjust_PSD * pspec_2sided * cplg1 * cplg2
                            if pnameP == pnameN:
                                pspec_tot = np.real(pspec_tot)

                            if not np.all(np.isfinite(pspec_tot)):
                                print("BADNESS: ", nobj.name_system, pspec_tot)
                            else:
                                nsum += pspec_tot
                                ncollect[nobj][pnameP, pnameN] = ncollect[nobj][pnameP, pnameN] + pspec_tot
                nsums[pnameP, pnameN] = nsum
        return Bunch(
            ncollect = ncollect,
            nsums    = nsums,
        )

    def select_sources(self, nobj_filter_func):
        external_collect = dict()
        for nobj, sumdict in list(self.CSD_by_source.items()):
            if nobj_filter_func(nobj):
                external_collect[nobj] = sumdict
        return self.__class__(
            system           = self.system,
            solver           = self.system.solution,
            port_set         = self.port_set,
            port_map         = self.port_map,
            keyP             = self.keyP,
            keyN             = self.keyN,
            external_collect = external_collect,
        )

