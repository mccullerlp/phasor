# -*- coding: utf-8 -*-
"""
TODO:
add method for inserting nonlinear triplets, so they can be indexed for 2nd order noise analysis

have measurement objects inject objects into the solver, so that the solver state is totally separate

have coherent measurement systems able to run the solver independently to generate system-altering measurements
"""
from __future__ import division, print_function, unicode_literals
from phasor.utilities.print import print
from collections import defaultdict
from declarative import bunch

import numpy as np
import warnings

import declarative as declarative

from ..base import (
    DictKey,
    Frequency,
    SystemElementBase,
    ClassicalFreqKey,
    PTREE_ASSIGN,
)

from .matrix_algorithm import (
    MatrixBuildAlgorithm,
)

from . import ports_algorithm
from . import solver_algorithm

from ..base import Element, RootElement
from ..base.ports import PostBondKey
from ..base import ports
from ..base import visitors as VISIT

from ..optics import (
    OpticalFrequency,
    OpticalFreqKey,
)


class SystemSymbols(Element):
    """
    Separate Class for constants to allow replacing them with symbols or more math appropriate ones
    """

    def __build__(self):
        PTREE_ASSIGN(self).c_m_s                 = 299792458
        PTREE_ASSIGN(self).kB_J_K                = 1.380658e-23
        PTREE_ASSIGN(self).h_Js                  = 6.6260700408e-34
        PTREE_ASSIGN(self).hbar_Js               = 1.0545718001e-34
        PTREE_ASSIGN(self).pi                    = np.pi
        PTREE_ASSIGN(self).i                     = 1j
        PTREE_ASSIGN(self).i2pi                  = np.pi * 2j
        PTREE_ASSIGN(self).math                  = np
        PTREE_ASSIGN(self).temp_K                = 299
        PTREE_ASSIGN(self).Z_termination         = 50
        super(SystemSymbols, self).__build__()

    def number(self, num):
        return num


class BGSystem(RootElement):
    exact_order = None
    max_N = 100
    warning_N = 20
    solver_Q_conditioning = True

    _frozen = False

    solver_name_default = 'loop_LUQ'
    #solver_name_default = 'scisparse'
    @declarative.dproperty
    def solver_name(self, val = None):
        if val is None:
            val = self.solver_name_default
        return val

    solver_symbolic_name_default = 'loop_LUQ'
    @declarative.dproperty
    def solver_symbolic_name(self, val = None):
        if val is None:
            val = self.solver_symbolic_name_default
        return val

    @declarative.dproperty
    def symbolic(self, val = False):
        return val

    @declarative.dproperty
    def include_johnson_noise(self, val = True):
        val = self.ctree.setdefault('include_johnson_noise', val)
        return val

    @declarative.dproperty
    def symbols(self):
        return SystemSymbols()

    @declarative.mproperty
    def field_space(self, FS = None):
        return FS

    @declarative.mproperty
    def freq_order_max_default(self, val = 2):
        return val

    @declarative.dproperty
    def adjust_PSD(self):
        if self.sided_spectra == 1:
            val = 2
        elif self.sided_spectra == 2:
            val = 1
        val = self.ctree.setdefault('adjust_PSD', val)
        return val

    @declarative.dproperty
    def sided_spectra(self, val = 1):
        val = self.ctree.setdefault('sided_spectra', val)
        return val

    @declarative.dproperty
    def system(self):
        #should use environment_query instead
        return self

    @declarative.mproperty
    def elements_named(self):
        return dict()

    @declarative.mproperty
    def elements(self):
        return set()

    @declarative.mproperty
    def port_owners(self):
        return dict()

    @declarative.mproperty
    def owners_ports(self):
        return dict()

    @declarative.mproperty
    def owners_ports_virtual(self):
        return dict()

    @declarative.mproperty
    def port_autoterminate(self):
        return dict()

    @declarative.mproperty
    def bond_pairs(self):
        return defaultdict(dict)

    @declarative.mproperty
    def ports_post(self):
        return dict()

    def ports_post_get(self, port):
        val = port.get(PostBondKey, 0)
        nport = port | DictKey({PostBondKey : val + 1})
        self.ports_post[port] = nport
        return nport

    @declarative.mproperty
    def ports_pre(self):
        return dict()

    def ports_pre_get(self, port):
        val = port.get(PostBondKey, 0)
        nport = port | DictKey({PostBondKey : val - 1})
        self.ports_pre[port] = nport
        return nport

    @declarative.mproperty
    def bonded_set(self):
        return set()

    @declarative.mproperty
    def port_owners_virtual(self):
        return defaultdict(set)

    @declarative.dproperty
    def F_AC(self, val = 1e-4):
        #TODO make this detect a PropertyTransforming or injected frequency object
        self.environment.own.F_AC = Frequency(
            F_Hz  = val,
            name  = 'AC',
            order = 2,
            F_center_Hz = 1e3,
        )
        return self.environment.own.F_AC

    @declarative.dproperty
    def F_carrier_1064(self):
        self.environment.own.F_carrier_1064 = OpticalFrequency(
            wavelen_m = 1064e-9,
            name = u'λIR',
        )
        return self.environment.own.F_carrier_1064

    @declarative.dproperty
    def FD_carrier_1064(self):
        return ports.FrequencyKey({self.F_carrier_1064 : 1})

    @declarative.dproperty
    def environment(self):
        return SystemElementBase()

    def optical_frequency_extract(self, key):
        iwavelen_m = 0
        freq_Hz = 0
        for F, n in list(key[ClassicalFreqKey].F_dict.items()):
            freq_Hz += n * F.F_Hz.val
        for F, n in list(key[OpticalFreqKey].F_dict.items()):
            iwavelen_m += n * F.iwavelen_m
        return iwavelen_m, freq_Hz

    @declarative.mproperty
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
            #TODO revisit max frequency groups
            #for group in F.groups:
            #    group_N[group] += Na

        for group, N in list(group_N.items()):
            Nmax = self.groups_max_N.get(group, None)
            if Nmax is not None and N > Nmax:
                return True
        return False

    def reject_optical_frequency_order(self, fkey):
        #TODO put this logic in a subobject
        group_N = defaultdict(lambda: 0)
        if len(fkey.F_dict) == 0:
            #if it is truely DC then reject
            #TODO optical rectification
            return True
        for F, N in list(fkey.F_dict.items()):
            N_limit = F.order
            if N_limit is None:
                N_limit = 2
            if N > N_limit:
                return True
            if N < 1:
                return True
            #TODO revisit max frequency groups
            #for group in F.groups:
            #    group_N[group] += Na

        for group, N in list(group_N.items()):
            Nmax = self.groups_max_N.get(group, None)
            if Nmax is not None and N > Nmax:
                return True
        return False

    def classical_frequency_extract(self, key):
        #TODO put this logic in a subobject
        freq_Hz = 0
        for F, n in list(key[ClassicalFreqKey].F_dict.items()):
            freq_Hz += n * F.F_Hz.val
        return freq_Hz

    def classical_frequency_extract_center(self, ekey):
        #TODO put this logic in a subobject
        freq_Hz = 0
        for F, n in list(ekey.F_dict.items()):
            if len(np.array(F.F_center_Hz).shape) > 0:
                print("Weird F_center_Hz shape: ", F, n, F.F_center_Hz)
            freq_Hz += n * F.F_center_Hz
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
        self._complete()
        assert(not self._frozen)

        with self.building:
            #must do delegate calls before autotermination
            has_delegated = set()
            while True:
                no_delegates = True
                for element, delegate_call in self.targets_recurse(VISIT.bond_delegate):
                    if element not in has_delegated:
                        has_delegated.add(element)
                        delegate_call()
                        no_delegates = False
                    #print("Bond delegate", element)
                if no_delegates:
                    break

        while self._include_lst:
            self.do_includes()
            #print("INCLUDE LST: ", self._include_lst)
            self._autoterminate()

        for element in self.targets_recurse(VISIT.bond_completion):
            #print("Bond Completion", element)
            pass

        bad_completions = dict()
        while self._bond_completions_raw:
            (pe_1, pe_2), raw_port1 = self._bond_completions_raw.popitem()
            raw_port2 = self._bond_completions_raw.pop((pe_2, pe_1), None)
            if raw_port2 is None:
                bad_completions[(pe_1, pe_2)] = raw_port1
            else:
                self.bond_old(raw_port1, raw_port2)
        if bad_completions:
            raise RuntimeError("Incomplete port pairings: {0}".format(bad_completions))

        assert(not self._frozen)
        self._frozen = True

        self.port_algo = ports_algorithm.PortUpdatesAlgorithm(
            system           = self,
        )
        self.matrix_algorithm = MatrixBuildAlgorithm(
            system           = self,
            ports_algorithm  = self.port_algo,
        )
        self.solver = solver_algorithm.SystemSolver(
            system           = self,
            ports_algorithm  = self.port_algo,
            matrix_algorithm = self.matrix_algorithm,
        )
        return

    def bond_completion_raw_pair(self, pe_1, pe_2, raw_port1, raw_port2):
        self.bond_completion_raw(pe_1, pe_2, raw_port1)
        self.bond_completion_raw(pe_2, pe_1, raw_port2)

    @declarative.mproperty
    def _bond_completions_raw(self):
        return dict()

    def bond_completion_raw(self, pe_1, pe_2, raw_port):
        self._bond_completions_raw[(pe_1, pe_2)] = raw_port
        return

    def _solve(self):
        self._setup_sequence()
        self.solver.solve()
        return self.solver

    @declarative.mproperty
    def solution(self):
        return self._solve()

    @declarative.mproperty
    def _include_lst(self):
        return []

    def include(self, element):
        #TODO get rid of this deferred include business
        self._include_lst.append(element)
        #self._include(element)

    def do_includes(self):
        while self._include_lst:
            el = self._include_lst.pop()
            self._include(el)

    def port_add(self, owner, pkey):
        #TODO phase out
        self.port_owners[pkey] = owner
        self.owners_ports.setdefault(owner, []).append(pkey)
        self.owners_ports_virtual.setdefault(owner, [])
        return

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
                self.port_add(element, port)
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
        #TODO purge this code since now bonds handle autotermination
        terminated_ports = set(self.bonded_set)
        registered_ports = set(self.port_owners.keys())
        unterminated_ports = registered_ports - terminated_ports
        if unterminated_ports and not hasattr(self, 'autoterminate'):
            self.own.autoterminate = SystemElementBase()
        for port in unterminated_ports:
            #print("UNTERMINATED: ", port)
            aterm = self.port_autoterminate.get(port, None)
            if aterm is None:
                #print("unterminated port", port)
                pass
            else:
                pobj, tclass = aterm
                #have to build within include to get the sled connection
                #TODO: make this a sane naming scheme
                #TODO GOTTA GOTTA FIX
                name = '{0}({2}-<{1}>)'.format(tclass.__name__, port, pobj.element.name_system).replace('.', '_')
                tinst = self.autoterminate.insert(tclass(), name)
                #print("Autoterminating port:", port)
                #print("with ", tinst)
                self.bond(pobj, tinst.po_Fr)

        with self.building:
            for port, obj in self.targets_recurse(VISIT.auto_terminate):
                #print("Autoterminating port:", port)
                #print("with ", obj)
                pass
        return

    def bond(self, port_A, port_B):
        #TODO ptypes testing is only for the transition to local bond scheme
        return port_A.bond(port_B)

    def bond_old(self, port_A, port_B):
        #TODO, phase this out
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
            if (port_B.i in self.bonded_set):
                assert(port_B.multiple_attach)
            if (port_A.o in self.bonded_set):
                assert(port_A.multiple_attach)
            self.bonded_set.add(port_A.o)
            self.bonded_set.add(port_B.i)
            self.bond_pairs[port_A.o][port_B.i] = 1

        #also attach the duals
        try:
            port_B.o
            port_A.i
        except AttributeError:
            pass
        else:
            either_included = True
            if (port_A.i in self.bonded_set):
                assert(port_A.multiple_attach)
            if (port_B.o in self.bonded_set):
                assert(port_B.multiple_attach)
            self.bonded_set.add(port_B.o)
            self.bonded_set.add(port_A.i)
            self.bond_pairs[port_B.o][port_A.i] = 1

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
        #TODO rename bond port virtual
        #assert(self.root is port.element.root)
        #assert(self.element.root is self.root)
        self.port_owners_virtual[port].add(element)
        self.owners_ports_virtual.setdefault(element, []).append(port)
        return

#add an additional name for the system
LinearSystem = BGSystem



