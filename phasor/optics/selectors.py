# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from collections import defaultdict

import declarative

from . import bases
from . import ports


class PolSelector(
        bases.OpticalCouplerBase,
        bases.SystemElementBase
):

    def __build__(self):
        self.own.po_Fr   = ports.OpticalPort(sname = 'po_Fr')
        self.own.Bk_P = ports.OpticalPort(sname = 'Bk_P')
        self.own.Bk_S = ports.OpticalPort(sname = 'Bk_S')
        return

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.po_Fr.i):
            if ports.PolP & kfrom:
                ports_algorithm.port_coupling_needed(self.Bk_P.o, kfrom)
            elif ports.PolS & kfrom:
                ports_algorithm.port_coupling_needed(self.Bk_S.o, kfrom)
            else:
                assert(False)
        for kfrom in ports_algorithm.port_update_get(self.Bk_P.i):
            ports_algorithm.port_coupling_needed(self.po_Fr.o, kfrom)
        for kfrom in ports_algorithm.port_update_get(self.Bk_S.i):
            ports_algorithm.port_coupling_needed(self.po_Fr.o, kfrom)

        for kto in ports_algorithm.port_update_get(self.po_Fr.o):
            if ports.PolP & kto:
                ports_algorithm.port_coupling_needed(self.Bk_P.i, kto)
            elif ports.PolS & kto:
                ports_algorithm.port_coupling_needed(self.Bk_S.i, kto)
            else:
                assert(False)
        for kto in ports_algorithm.port_update_get(self.Bk_P.o):
            ports_algorithm.port_coupling_needed(self.po_Fr.i, kto)
        for kto in ports_algorithm.port_update_get(self.Bk_S.o):
            ports_algorithm.port_coupling_needed(self.po_Fr.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.po_Fr.i):
            if ports.PolP & kfrom:
                matrix_algorithm.port_coupling_insert(self.po_Fr.i, kfrom, self.Bk_P.o, kfrom, 1)
            elif ports.PolS & kfrom:
                matrix_algorithm.port_coupling_insert(self.po_Fr.i, kfrom, self.Bk_S.o, kfrom, 1)
            else:
                assert(False)
        for kfrom in matrix_algorithm.port_set_get(self.Bk_P.i):
            matrix_algorithm.port_coupling_insert(self.Bk_P.i, kfrom, self.po_Fr.o, kfrom, 1)
        for kfrom in matrix_algorithm.port_set_get(self.Bk_S.i):
            matrix_algorithm.port_coupling_insert(self.Bk_P.i, kfrom, self.po_Fr.o, kfrom, 1)
        return


class GenericSelector(bases.OpticalCouplerBase, bases.SystemElementBase):

    @declarative.dproperty
    def select_map(self, val):
        return val

    @declarative.dproperty
    def po_Fr(self):
        return ports.OpticalPort(sname = 'po_Fr')

    def __build__(self):
        self.check      = True
        self.port_map   = {}

        for name, key in list(self.select_map.items()):
            pname = 'Bk_{0}'.format(name)
            port = ports.OpticalPort(sname = pname)
            port = self.insert(port, pname)
            self.port_map[name] = (port, key)
        return

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.po_Fr.i):
            N_selections = 0
            #print("KFROM: ", kfrom)
            for pname, (port, key) in list(self.port_map.items()):
                #print("PORT: ", pname, port, key)
                #print(key & kfrom)
                if key & kfrom:
                    #print("SEL: ", key, kfrom)
                    N_selections += 1
                    ports_algorithm.port_coupling_needed(port.o, kfrom)
                    if not self.check:
                        break
            assert(N_selections == 1)
        for pname, (port, key) in list(self.port_map.items()):
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(self.po_Fr.o, kfrom)

        for kto in ports_algorithm.port_update_get(self.po_Fr.o):
            N_selections = 0
            for pname, (port, key) in list(self.port_map.items()):
                if key & kto:
                    N_selections += 1
                    ports_algorithm.port_coupling_needed(port.i, kto)
                    if not self.check:
                        break
        for pname, (port, key) in list(self.port_map.items()):
            for kto in ports_algorithm.port_update_get(port.o):
                ports_algorithm.port_coupling_needed(self.po_Fr.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.po_Fr.i):
            N_selections = 0
            for pname, (port, key) in list(self.port_map.items()):
                if key & kfrom:
                    N_selections += 1
                    matrix_algorithm.port_coupling_insert(self.po_Fr.i, kfrom, port.o, kfrom, 1)
                    if not self.check:
                        break
            assert(N_selections == 1)
        for pname, (port, key) in list(self.port_map.items()):
            for kfrom in matrix_algorithm.port_set_get(port.i):
                matrix_algorithm.port_coupling_insert(port.i, kfrom, self.po_Fr.o, kfrom, 1)
        return


class OpticalSelectionStack(
    bases.OpticalCouplerBase,
    bases.SystemElementBase,
):
    @declarative.dproperty
    def sub_element_map(self, val):
        return val

    @declarative.dproperty
    def select_map(self, val):
        return val

    @declarative.dproperty
    def port_set(self, val = None):
        return val

    def __build__(self):
        super(OpticalSelectionStack, self).__build__()

        if self.port_set is None:
            optical_ports = defaultdict(lambda : 0)
        else:
            optical_ports = None

        for ename, element in self.sub_element_map.items():
            celement = self.insert(element, ename)
            #used to check that ports are not redundant (due to aliasing)
            ports_already = set()
            if optical_ports is not None:
                for port in celement.ports_select:
                    if port in ports_already:
                        continue
                    ports_already.add(port)
                    if isinstance(port, (ports.OpticalPort,)):
                        optical_ports[port.name_child] += 1
                    else:
                        raise RuntimeError("HMMM")

        #check that all of the subobjects carry the same optical ports
        if optical_ports is not None:
            pnum_cmn = None
            for pname, pnum in list(optical_ports.items()):
                if pnum != pnum_cmn:
                    if pnum_cmn is None:
                        pnum_cmn == pnum
                    else:
                        assert(False)
            self.port_set = set(optical_ports.keys())

        self.split_ports = {}
        for pname in self.port_set:
            sname = "psel_{0}".format(pname)
            psel = self.insert(GenericSelector(select_map = self.select_map), sname)
            self.split_ports[pname] = psel
            setattr(self, pname, psel.po_Fr)

            for ename, element in self.sub_element_map.items():
                celement = getattr(self, ename)
                port = getattr(celement, pname)
                self.system.bond(psel.port_map[ename][0], port)
        return


