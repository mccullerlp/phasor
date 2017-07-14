# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from ..utilities.print import pprint

import numpy as np
from collections import defaultdict

import declarative

from .. import base


class NoiseReadout(base.SystemElementBase):
    def __init__(
            self,
            portN = None,
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
                base.PTREE_ASSIGN(self).port_set = 'AC noise'
            else:
                base.PTREE_ASSIGN(self).port_set = 'DC noise'
        else:
            self.port_set = port_set

        if AC_sidebands_use:
            self.keyP = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.system.F_AC : 1})})
            self.keyN = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({self.system.F_AC : -1})})
        else:
            self.keyP = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({})})
            self.keyN = base.DictKey({base.ClassicalFreqKey: base.FrequencyKey({})})

        if port_map is None:
            self.port_map = dict(
                R = self.portN,
            )
        else:
            self.port_map = port_map
        return

    def system_setup_ports_initial(self, system):
        portsets = [self.port_set, 'noise']
        for pname, port in self.port_map.items():
            system.readout_port_needed(port, self.keyP, portsets)
            system.readout_port_needed(port, self.keyN, portsets)
        return

    @declarative.mproperty
    def CSD(self):
        return self.CSD_builds.nsums

    @declarative.mproperty
    def CSD_by_source(self):
        return self.CSD_builds.ncollect

    @declarative.mproperty
    def external_collect(self):
        return None
        #TODO
        external_collect = dict()
        for nobj, sumdict in list(self.CSD_by_source.items()):
            if nobj_filter_func(nobj):
                external_collect[nobj] = sumdict
        return external_collect

    @declarative.mproperty
    def CSD_builds(self):
        if self.external_collect is not None:
            nsums    = dict()
            for nobj, sumdict in list(self.external_collect.items()):
                for dkey, nsum in list(sumdict.items()):
                    if dkey not in nsums:
                        nsums[dkey] = np.copy(nsum)
                    else:
                        nsums[dkey] += nsum
            return declarative.Bunch(
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

        ncollect = defaultdict(lambda: defaultdict(lambda: 0))
        nsums    = dict()

        pkviewsP = dict()
        pkviewsN = dict()
        for pname, port in list(self.port_map.items()):
            pkviewsP[pname] = (port, self.keyP)
            pkviewsN[pname] = (port, self.keyN)
            for pname2, port2 in list(self.port_map.items()):
                nsums[pname, pname2] = 0

        kvecsP = defaultdict(dict)
        kvecsN = defaultdict(dict)
        for (pkfrom, pkto), cplg in list(coupling_matrix_inv.items()):
            for pname, pkview in list(pkviewsP.items()):
                if pkto == pkview:
                    kvecsP[pname][pkfrom] = cplg
            for pname, pkview in list(pkviewsN.items()):
                if pkto == pkview:
                    kvecsN[pname][pkfrom] = cplg

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
                        for pe_1, k1, pe_2, k2, nobj in vals:
                            pspec_2sided = nobj.noise_2pt_expectation(pe_1, k1, pe_2, k2)
                            #print("PSPEC: ", pe_1, k1, pe_2, k2, pspec_2sided, cplg1 * cplg2)
                            pspec_tot = self.system.adjust_PSD * pspec_2sided * cplg1 * cplg2
                            if pnameP == pnameN:
                                pspec_tot = np.real(pspec_tot)

                            if not np.all(np.isfinite(pspec_tot)):
                                print("BADNESS: ", nobj.name_system, pspec_tot)
                            else:
                                nsum += pspec_tot
                                ncollect[nobj][pnameP, pnameN] = ncollect[nobj][pnameP, pnameN] + pspec_tot
                nsums[pnameP, pnameN] = nsum
        return declarative.Bunch(
            ncollect = ncollect,
            nsums    = nsums,
        )

    def select_sources(self, nobj_filter_func):
        external_collect = dict()
        for nobj, sumdict in list(self.CSD_by_source.items()):
            if nobj_filter_func(nobj):
                external_collect[nobj] = sumdict
        return self.__class__(
            port_set         = self.port_set,
            port_map         = self.port_map,
            keyP             = self.keyP,
            keyN             = self.keyN,
            external_collect = external_collect,
        )

