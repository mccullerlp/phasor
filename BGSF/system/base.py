# -*- coding: utf-8 -*-
"""
TODO:
add method for inserting nonlinear triplets, so they can be indexed for 2nd order noise analysis

have measurement objects inject objects into the solver, so that the solver state is totally separate

have coherent measurement systems able to run the solver independently to generate system-altering measurements
"""
from __future__ import (division, print_function)
from BGSF.utilities.print import print
from collections import defaultdict

import numpy as np
import warnings

import declarative as decl

from ..base import (
    Frequency,
    SystemElementSled,
    ClassicalFreqKey,
    OOA_ASSIGN,
)

from .matrix_algorithm import (
    MatrixBuildAlgorithm,
)

from . import ports_algorithm
from . import solver_algorithm

from ..base import Element, RootElement


class Constants(Element):

    def __build__(self):
        OOA_ASSIGN(self).c_m_s    = 299792458
        OOA_ASSIGN(self).kB_J_K   = 1.380658e-23
        OOA_ASSIGN(self).h_Js     = 6.6260700408e-34
        OOA_ASSIGN(self).hbar_Js  = 1.0545718001e-34
        OOA_ASSIGN(self).pi       = np.pi
        OOA_ASSIGN(self).i        = 1j
        OOA_ASSIGN(self).i2pi     = np.pi * 2j
        OOA_ASSIGN(self).math     = np
        OOA_ASSIGN(self).temp_K   = 299
        OOA_ASSIGN(self).Z_termination = 50
        super(Constants, self).__build__()


class LinearSystem(RootElement, Constants):

    _frozen = False

    @decl.mproperty
    def field_space(self, FS = None):
        return FS

    @decl.mproperty
    def freq_order_max_default(self, val = 2):
        return val

    def __init__(
        self,
        **kwargs
    ):
        super(LinearSystem, self).__init__(**kwargs)

    @decl.dproperty
    def adjust_PSD(self):
        if self.sided_spectra == 1:
            val = 2
        elif self.sided_spectra == 2:
            val = 1
        val = self.ooa_params.setdefault('adjust_PSD', val)
        return val

    @decl.dproperty
    def sided_spectra(self, val = 1):
        val = self.ooa_params.setdefault('sided_spectra', val)
        return val

    @decl.dproperty
    def system(self):
        #should use environment_query instead
        return self

    @decl.mproperty
    def elements_named(self):
        return dict()

    @decl.mproperty
    def elements(self):
        return set()

    @decl.mproperty
    def port_owners(self):
        return dict()

    @decl.mproperty
    def owners_ports(self):
        return dict()

    @decl.mproperty
    def owners_ports_virtual(self):
        return dict()
    @decl.mproperty
    def port_autoterminate(self):
        return dict()

    @decl.mproperty
    def bond_pairs(self):
        #TODO: enforce single linkage if possible
        return defaultdict(set)

    @decl.mproperty
    def bonded_set(self):
        return set()

    @decl.mproperty
    def port_owners_virtual(self):
        return defaultdict(set)

    def __build__(self):
        self.my.sled = SystemElementSled(
            ooa_params = self.ooa_params,
        )
        self.sled.my.environment = SystemElementSled()
        self.environment = self.sled.environment

        self.sled.environment.my.F_AC = Frequency(
            F_Hz  = 0,
            name  = 'AC',
            order = 1,
        )
        self.F_AC = self.sled.environment.F_AC

        #now that the system is done constructing, switch to recording mode so that any further
        #construction can be replayed
        super(LinearSystem, self).__build__()
        return

    def number(self, num):
        return num

    @decl.mproperty
    def fully_resolved_name_tuple(self):
        return ()

    def reject_classical_frequency_order(self, fkey):
        #TODO put this logic in a subobject
        group_N = defaultdict(lambda: 0)
        for F, N in list(fkey.F_dict.items()):
            N_limit = F.order
            if N_limit is None:
                N_limit = self.freq_order_max_default
            Na = abs(N)
            if Na > N_limit:
                return True
            for group in F.groups:
                group_N[group] += Na

        for group, N in list(group_N.items()):
            Nmax = self.groups_max_N.get(group, None)
            if Nmax is not None and N > Nmax:
                return True
        return False

    def classical_frequency_extract(self, key):
        #TODO put this logic in a subobject
        freq_Hz = 0
        for F, n in list(key[ClassicalFreqKey].F_dict.items()):
            freq_Hz += n * F.F_Hz
        return freq_Hz

    def classical_frequency_test_max(self, key, max_freq):
        if max_freq is None:
            return False
        #TODO put this logic in a subobject
        freq_Hz = 0
        for F, n in list(key[ClassicalFreqKey].F_dict.items()):
            freq_Hz += n * F.F_Hz
        if np.any(freq_Hz < max_freq):
            return False
        return True

    def _setup_sequence(self):
        while self._include_lst:
            self.do_includes()
            #print("INCLUDE LST: ", self._include_lst)
            self._autoterminate()
        self._frozen = True

        self.port_algo = ports_algorithm.PortUpdatesAlgorithm(
            system = self,
        )
        self.matrix_algorithm = MatrixBuildAlgorithm(
            system = self,
            ports_algorithm = self.port_algo,
        )
        self.solver = solver_algorithm.SystemSolver(
            system = self,
            ports_algorithm = self.port_algo,
            matrix_algorithm = self.matrix_algorithm,
        )
        return

    def solve(self):
        self._setup_sequence()
        self.solver.solve()
        return self.solver

    @decl.mproperty
    def solution(self):
        return self.solve()

    @decl.mproperty
    def _include_lst(self):
        return []

    def include(self, element):
        #TODO get rid of this deferred include business
        self._include_lst.append(element)

    def do_includes(self):
        while self._include_lst:
            el = self._include_lst.pop()
            self._include(el)

    def _include(self, element):
        if self._frozen:
            raise RuntimeError("Cannot include elements or bond after solution requested")
        if element in self.elements:
            return
        #print("INCLUDE: ", element, element.name_system)
        self.elements.add(element)
        try:
            op = element.owned_ports
        except AttributeError:
            pass
        else:
            for port, pobj in list(op.items()):
                self.port_owners[port] = element
                self.owners_ports.setdefault(element, []).append(port)
                self.owners_ports_virtual.setdefault(element, [])
                #have the port objects autoterminate
                pobj.autoterminations(self.port_autoterminate)
        if element.name_system in self.elements_named:
            warnings.warn((
                "Multiple elements added with name {0}"
                ", may be confusing and prevent system rebuilding from functioning"
            ).format(element.name_system))
            #break the elements named so that there isn't confusion later
            self.elements_named[element.name_system] = None
        else:
            self.elements_named[element.name_system] = element

    def _autoterminate(self):
        terminated_ports = set(self.bonded_set)
        registered_ports = set(self.port_owners.keys())
        unterminated_ports = registered_ports - terminated_ports
        if unterminated_ports and not hasattr(self.sled, 'autoterminate'):
            self.sled.my.autoterminate = SystemElementSled()
        for port in unterminated_ports:
            print("UNTERMINATED: ", port)
            aterm = self.port_autoterminate.get(port, None)
            if aterm is None:
                #print("unterminated port", port)
                pass
            else:
                #print("Autoterminating port:", port)
                pobj, tclass = aterm
                #have to build within include to get the sled connection
                #TODO: make this a sane naming scheme
                #TODO GOTTA GOTTA FIX
                name = '{0}({2}-<{1}>)'.format(tclass.__name__, port, pobj.element.name_system).replace('.', '_')
                tinst = self.sled.autoterminate.insert(tclass(), name)
                self.bond(pobj, tinst.Fr)

    def bond(self, port_A, port_B):
        self.include(port_A.element)
        self.include(port_B.element)

        either_included = False
        try:
            port_A.o
            port_B.i
        except AttributeError:
            pass
        else:
            either_included = True
            if (not port_B.multiple_attach):
                assert(port_B.i not in self.bonded_set)
            if not (port_A.multiple_attach):
                assert(port_A.o not in self.bonded_set)
            self.bonded_set.add(port_A.o)
            self.bonded_set.add(port_B.i)
            self.bond_pairs[port_A.o].add(port_B.i)

        #also attach the duals
        try:
            port_B.o
            port_A.i
        except AttributeError:
            pass
        else:
            either_included = True
            if (not port_A.multiple_attach):
                assert(port_A.i not in self.bonded_set)
            if (not port_B.multiple_attach):
                assert(port_B.o not in self.bonded_set)
            self.bonded_set.add(port_B.o)
            self.bonded_set.add(port_A.i)
            self.bond_pairs[port_B.o].add(port_A.i)

        if not either_included:
            raise RuntimeError("Trying to bond, but the pair is not in-out compatible")
        return

    def bond_sequence(self, first, *args):
        next = first
        for bond_arg in args[:-1]:
            self.bond(next, bond_arg)
            next = bond_arg.chain_next
            if next is None:
                raise RuntimeError("Bond in sequence doesn't indicate a natural 'next' element: ".format(bond_arg))
        self.bond(next, args[-1])
        pass

    def own_port_virtual(self, element, port):
        self.port_owners_virtual[port].add(element)
        self.owners_ports_virtual.setdefault(element, []).append(port)
        return

