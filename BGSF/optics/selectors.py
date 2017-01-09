# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

from declarative import (
    mproperty,
)

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
    OOA_ASSIGN,
)

from . import ports
from .ports import (
    OpticalPortHolderInOut,
    OpticalPortHolderIn,
    #QuantumKey,
    RAISE, LOWER,
    PolKEY, PolS, PolP,
    #OpticalSymmetric2PortMixin,
)

from collections import defaultdict


class PolSelector(OpticalCouplerBase, SystemElementBase):
    def __init__(
        self,
        **kwargs
    ):
        super(PolSelector, self).__init__(**kwargs)
        self.Fr   = OpticalPortHolderInOut(self, x = 'Fr')
        self.Bk_P = OpticalPortHolderInOut(self, x = 'Bk_P')
        self.Bk_S = OpticalPortHolderInOut(self, x = 'Bk_S')
        return

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.Fr.i):
            if PolP & kfrom:
                ports_algorithm.port_coupling_needed(self.Bk_P.o, kfrom)
            elif PolS & kfrom:
                ports_algorithm.port_coupling_needed(self.Bk_S.o, kfrom)
            else:
                assert(False)
        for kfrom in ports_algorithm.port_update_get(self.Bk_P.i):
            ports_algorithm.port_coupling_needed(self.Fr.o, kfrom)
        for kfrom in ports_algorithm.port_update_get(self.Bk_S.i):
            ports_algorithm.port_coupling_needed(self.Fr.o, kfrom)

        for kto in ports_algorithm.port_update_get(self.Fr.o):
            if PolP & kto:
                ports_algorithm.port_coupling_needed(self.Bk_P.i, kto)
            elif PolS & kto:
                ports_algorithm.port_coupling_needed(self.Bk_S.i, kto)
            else:
                assert(False)
        for kto in ports_algorithm.port_update_get(self.Bk_P.o):
            ports_algorithm.port_coupling_needed(self.Fr.i, kto)
        for kto in ports_algorithm.port_update_get(self.Bk_S.o):
            ports_algorithm.port_coupling_needed(self.Fr.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.Fr.i):
            if PolP & kfrom:
                matrix_algorithm.port_coupling_insert(self.Fr.i, kfrom, self.Bk_P.o, kfrom, 1)
            elif PolS & kfrom:
                matrix_algorithm.port_coupling_insert(self.Fr.i, kfrom, self.Bk_S.o, kfrom, 1)
            else:
                assert(False)
        for kfrom in matrix_algorithm.port_set_get(self.Bk_P.i):
            matrix_algorithm.port_coupling_insert(self.Bk_P.i, kfrom, self.Fr.o, kfrom, 1)
        for kfrom in matrix_algorithm.port_set_get(self.Bk_S.i):
            matrix_algorithm.port_coupling_insert(self.Bk_P.i, kfrom, self.Fr.o, kfrom, 1)
        return


class GenericSelector(OpticalCouplerBase, SystemElementBase):
    def __init__(
        self,
        select_map,
        **kwargs
    ):
        super(GenericSelector, self).__init__(**kwargs)
        self.check      = self.system.unique_selections_check
        self.select_map = select_map
        self.port_map   = {}
        self.Fr         = OpticalPortHolderInOut(self, x = 'Fr')

        for name, key in list(self.select_map.items()):
            pname = 'Bk_{0}'.format(name)
            port = OpticalPortHolderInOut(self, x = pname)
            setattr(self, pname, port)
            self.port_map[name] = (port, key)
        return

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.Fr.i):
            N_selections = 0
            for pname, (port, key) in list(self.port_map.items()):
                if key & kfrom:
                    N_selections += 1
                    ports_algorithm.port_coupling_needed(port.o, kfrom)
                    if not self.check:
                        break
            assert(N_selections == 1)
        for pname, (port, key) in list(self.port_map.items()):
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(self.Fr.o, kfrom)

        for kto in ports_algorithm.port_update_get(self.Fr.o):
            N_selections = 0
            for pname, (port, key) in list(self.port_map.items()):
                if key & kto:
                    N_selections += 1
                    ports_algorithm.port_coupling_needed(port.i, kto)
                    if not self.check:
                        break
        for pname, (port, key) in list(self.port_map.items()):
            for kto in ports_algorithm.port_update_get(port.o):
                ports_algorithm.port_coupling_needed(self.Fr.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.Fr.i):
            N_selections = 0
            for pname, (port, key) in list(self.port_map.items()):
                if key & kfrom:
                    N_selections += 1
                    matrix_algorithm.port_coupling_insert(self.Fr.i, kfrom, port.o, kfrom, 1)
                    if not self.check:
                        break
            assert(N_selections == 1)
        for pname, (port, key) in list(self.port_map.items()):
            for kfrom in matrix_algorithm.port_set_get(port.i):
                matrix_algorithm.port_coupling_insert(port.i, kfrom, self.Fr.o, kfrom, 1)
        return


class OpticalSelectionStack(OpticalCouplerBase, SystemElementBase):
    def __init__(
        self,
        sub_element_map,
        select_map,
        port_set = None,
        **kwargs
    ):
        super(OpticalSelectionStack, self).__init__(**kwargs)
        if port_set is None:
            optical_ports = defaultdict(lambda : 0)
        else:
            optical_ports = None

        for ename, element in list(sub_element_map.items()):
            setattr(self, ename, element)
            #separate these as the setattr "constructs" the element through the sled mechanism
            celement = getattr(self, ename)
            if optical_ports is not None:
                for pname, port in list(celement.owned_port_keys.items()):
                    if isinstance(port, (
                            OpticalPortHolderInOut,
                            OpticalPortHolderIn,
                            ports.OpticalPortHolderOut
                    )):
                        optical_ports[pname] += 1

        if optical_ports is not None:
            pnum_cmn = None
            for pname, pnum in list(optical_ports.items()):
                if pnum != pnum_cmn:
                    if pnum_cmn is None:
                        pnum_cmn == pnum
                    else:
                        assert(False)
            port_set = set(optical_ports.keys())

        self.split_ports = {}
        for pname in port_set:
            sname = "psel_{0}".format(pname)
            setattr(self, sname, GenericSelector(
                select_map = select_map,
            ))
            psel = getattr(self, sname)
            self.split_ports[pname] = psel
            setattr(self, pname, psel.Fr)

            for ename, element in list(sub_element_map.items()):
                celement = getattr(self, ename)
                port = getattr(celement, pname)
                self.system.link(psel.port_map[ename][0], port)
        return


