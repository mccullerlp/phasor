# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
from ..utilities.future_from_2 import object

from collections import defaultdict
import declarative

from ..base import (
    DictKey,
)

from ..base import ports


class PortUpdatesAlgorithm(object):
    def __init__(
        self,
        system,
    ):
        #TODO split the forward and back filling of ports
        self.system             = system
        self.port_cplgs         = dict()
        self.port_cplgs_update  = dict()
        self.port_cplgs_updateX = dict()
        self.owners_update      = set()
        self._current_element   = None

        self.drive_pk_sets      = defaultdict(set)
        self.readout_pk_sets    = defaultdict(set)

        #holds the reverse of the bond pairs so that the backfilling of ports works
        self.bond_pairsR = defaultdict(set)
        for k, v_dict in self.system.bond_pairs.items():
            for v in v_dict:
                self.bond_pairsR[v].add(k)

        for port, owner in system.port_owners.items():
            self.port_cplgs[port]               = set()
            self.port_cplgs_update[owner, port] = set()
            self.port_cplgs_updateX[port]       = set()

        for port, owners in system.port_owners_virtual.items():
            for owner in owners:
                #print((owner, port))
                self.port_cplgs_update.setdefault((owner, port), set())

        self._setup_port_needs()

    def _setup_port_needs(self):
        for el in self.system.elements:
            try:
                sspi = el.system_setup_ports_initial
            except AttributeError:
                pass
            else:
                sspi(self)

        while self.owners_update:
            el = self.owners_update.pop()
            #print("Updating owner: ", el)
            try:
                ssp = el.system_setup_ports
            except AttributeError:
                pass
            else:
                self._current_element = el
                ssp(self)
                self.resolve_port_updates()

        return

    def resolve_port_updates(self):
        assert(self._current_element is not None)
        element = self._current_element
        self._current_element = None
        for port in self.system.owners_ports[element]:
            update = self.port_cplgs_update[element, port]
            updateX = self.port_cplgs_updateX[port]
            self.port_cplgs[port].update(update)
            update.clear()
            #swap in the new updates
            self.port_cplgs_update[element, port] = updateX
            self.port_cplgs_updateX[port] = update
        for port in self.system.owners_ports_virtual[element]:
            update = self.port_cplgs_update[element, port]
            updateX = self.port_cplgs_updateX[port]
            self.port_cplgs[port].update(update)
            update.clear()
            #swap in the new updates
            self.port_cplgs_update[element, port] = updateX
            self.port_cplgs_updateX[port] = update
        return

    def port_coupling_needed(self, pto, kto):
        self.coherent_sources_needed(pto, kto)

    def prev_solution_needed(self, pto, kto):
        self.coherent_sources_needed(pto, kto)

    def port_update_get(self, port):
        assert(self._current_element is not None)
        return self.port_cplgs_update[self._current_element, port]

    def port_set_get(self, port):
        port = self.port_cplgs[port]
        return port

    def port_full_get(self, port):
        assert(self._current_element is not None)
        update = self.port_cplgs_update[self._current_element, port]
        port   = self.port_cplgs[port]
        return update.union(port)

    def _coherent_sources_needed(self, pto, kto):
        ptofull = self.port_cplgs.get(pto, declarative.NOARG)
        ptoupdate = self.port_cplgs_update.get((self._current_element, pto), declarative.NOARG)
        if ptofull is declarative.NOARG:
            print("Missing Connection: ", kto, " for ", pto)
        else:
            if kto not in ptofull and kto not in ptoupdate:
                owner = self.system.port_owners[pto]
                if owner is self._current_element:
                    v = self.port_cplgs_updateX[pto]
                else:
                    v = self.port_cplgs_update[owner, pto]
                v.add(kto)

                self.owners_update.add(owner)
                for Vowner in self.system.port_owners_virtual[pto]:
                    v = self.port_cplgs_update[Vowner, pto]
                    v.add(kto)
                    self.owners_update.add(Vowner)
        return

    def coherent_sources_needed(self, pto, kto):
        #print('needed port: ', pto, kto)
        #assert(isinstance(pto, DictKey))
        assert(isinstance(kto, DictKey))
        self._coherent_sources_needed(pto, kto)
        #TODO: make this dispersal occur during resolve_port_updates

        to_extend = set([pto])
        already_extended = set()

        #performs a transitive completion keys at every port that is logically connected
        while to_extend:
            pto_next = to_extend.pop()
            if pto_next in already_extended:
                continue
            already_extended.add(pto_next)

            ptolink_dict = self.system.bond_pairs.get(pto_next, declarative.NOARG)
            if ptolink_dict is not declarative.NOARG:
                to_extend.update(ptolink_dict.keys())
            ptolink_set = self.bond_pairsR.get(pto_next, declarative.NOARG)
            if ptolink_set is not declarative.NOARG:
                to_extend.update(ptolink_set)

            self._coherent_sources_needed(pto_next, kto)
        return

    def coherent_sources_perturb_needed(self, pto, kto):
        self.coherent_sources_needed(pto, kto)

    def readout_port_needed(self, pto, kto, portsets = ()):
        self.coherent_sources_needed(pto, kto)
        for pset in portsets:
            self.readout_pk_sets[pset].add((pto, kto))

    def drive_port_needed(self, pto, kto, portsets = ()):
        self.coherent_sources_needed(pto, kto)
        for pset in portsets:
            self.drive_pk_sets[pset].add((pto, kto))

    def port_set_print(self, select_port = None):
        if select_port is None:
            for port, kset in self.port_cplgs.items():
                print("Portset: ", port)
                print(kset)
        else:
            print("Portset: ", select_port)
            kset = self.port_cplgs[select_port]
            print(kset)

    def symmetric_update(
            self,
            pfrom1,
            pfrom2,
            subset_second = None,
            subset_first  = None,
    ):
        if pfrom1 is None or pfrom2 is None:
            return

        if isinstance(pfrom1, list):
            pool1 = set([])
            for inst_pfrom1 in pfrom1:
                pool1.update(self.port_update_get(inst_pfrom1))
        else:
            pool1 = self.port_update_get(pfrom1)

        if isinstance(pfrom2, list):
            pool2 = set([])
            for inst_pfrom2 in pfrom2:
                pool2.update(self.port_full_get(inst_pfrom2))
        else:
            pool2 = self.port_full_get(pfrom2)

        if subset_second:
            subset_func = subset_second(pool2)
            for kfrom1 in self.port_update_get(pfrom1):
                for kfrom2 in subset_func(kfrom1):
                    yield kfrom1, kfrom2
        else:
            for kfrom1 in self.port_update_get(pfrom1):
                for kfrom2 in pool2:
                    yield kfrom1, kfrom2
        if pfrom1 != pfrom2:
            if isinstance(pfrom1, list):
                pool1 = set([])
                for inst_pfrom1 in pfrom1:
                    pool1.update(self.port_set_get(inst_pfrom1))
            else:
                pool1 = self.port_set_get(pfrom1)

            if isinstance(pfrom2, list):
                pool2 = set([])
                for inst_pfrom2 in pfrom2:
                    pool2.update(self.port_update_get(inst_pfrom2))
            else:
                pool2 = self.port_update_get(pfrom2)

            if subset_first:
                subset_func = subset_first(pool1)
                for kfrom2 in pool2:
                    for kfrom1 in subset_func(kfrom2):
                        yield kfrom1, kfrom2
            else:
                for kfrom2 in pool2:
                    for kfrom1 in pool1:
                        yield kfrom1, kfrom2
            return

