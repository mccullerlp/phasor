# -*- coding: utf-8 -*-
"""
TODO:
add method for inserting nonlinear triplets, so they can be indexed for 2nd order noise analysis

have measurement objects inject objects into the solver, so that the solver state is totally separate

have coherent measurement systems able to run the solver independently to generate system-altering measurements
"""
from __future__ import division
from __future__ import print_function
from YALL.utilities.print import print
from collections import defaultdict

import numpy as np
import warnings

from declarative.bunch import (
    DeepBunchSingleAssign,
)

from ..base import (
    Frequency,
    SystemElementSled,
    SystemElementBase,
    ClassicalFreqKey,
    OOA_ASSIGN,
)

from .matrix_algorithm import (
    MatrixBuildAlgorithm,
)

from .ports_algorithm import (
    PortUpdatesAlgorithm,
)

from .solver_algorithm import (
    SystemSolver
)


class LinearSystem(object):

    field_space_proto      = None
    freq_order_max_default = 2
    _frozen = False

    def __init__(
        self,
        world_builder          = None,
        field_space            = None,
        freq_order_max_default = None,
        override_params        = None,
    ):
        if field_space is not None:
            self.field_space_proto = field_space
        if freq_order_max_default is not None:
            self.freq_order_max_default = freq_order_max_default

        #TODO, add argument to fill this
        self.ooa_params = DeepBunchSingleAssign()
        self.system     = self
        if override_params is not None:
            self.ooa_params.update_recursive(override_params)

        OOA_ASSIGN(self).c_m_s    = 299792458
        OOA_ASSIGN(self).kB_J_K   = 1.380658e-23
        OOA_ASSIGN(self).h_Js     = 6.6260700408e-34
        OOA_ASSIGN(self).hbar_Js  = 1.0545718001e-34
        OOA_ASSIGN(self).pi       = np.pi
        OOA_ASSIGN(self).i        = 1j
        OOA_ASSIGN(self).i2pi     = np.pi * 2j
        OOA_ASSIGN(self).math     = np
        OOA_ASSIGN(self).temp_K   = 299

        #debugging assignments
        OOA_ASSIGN(self).unique_selections_check = True

        OOA_ASSIGN(self).sided_spectra = 1
        if self.sided_spectra == 2:
            OOA_ASSIGN(self).adjust_PSD = 1
        elif self.sided_spectra == 1:
            OOA_ASSIGN(self).adjust_PSD = 2
        #this is a tag for the method calls whether to record the elements.
        #any methods or state applied to the system outside of the world_builder
        #can be replayed during N'th constructions. The world builder is a more
        #versatile way to replay constructions, since it is aware of the ooa_params
        self._record_build = False

        self.elements_named   = {}
        self.elements         = set()

        self.port_owners = dict()
        self.owners_ports = dict()
        self.owners_ports_virtual = dict()
        self.port_autoterminate = dict()

        #TODO: enforce single linkage if possible
        self.link_pairs = defaultdict(set)
        self.port_owners_virtual = defaultdict(set)

        self.frequencies         = set()
        self.elements_by_type = {
            Frequency : self.frequencies,
        }

        self.sled = SystemElementSled(
            parent     = None,
            name       = None,
            vparent    = self,
            _sled_root = True,
        )
        self.sled.environment = SystemElementSled()
        self.environment = self.sled.environment

        self.sled.environment.F_AC = Frequency(
            F_Hz  = 0,
            name  = 'AC',
            order = 1,
        )
        self.F_AC = self.sled.environment.F_AC

        #now run the world builder from the mostly constructed system
        if world_builder is None:
            pass
        elif issubclass(world_builder, SystemElementBase):
            self.sled.world = world_builder()
        else:
            world_builder(self.ooa_params, self.sled)

        #now that the system is done constructing, switch to recording mode so that any further
        #construction can be replayed
        self._record_build = True
        self._record_build_sequence = []
        return

    def number(self, num):
        return num

    def variant(self, params = None):
        raise NotImplementedError("TODO")

    def reject_classical_frequency_order(self, fkey):
        #TODO put this logic in a subobject
        group_N = defaultdict(lambda: 0)
        for F, N in fkey.F_dict.items():
            N_limit = F.order
            if N_limit is None:
                N_limit = self.freq_order_max_default
            Na = abs(N)
            if Na > N_limit:
                return True
            for group in F.groups:
                group_N[group] += Na

        for group, N in group_N.items():
            Nmax = self.groups_max_N.get(group, None)
            if Nmax is not None and N > Nmax:
                return True
        return False

    def classical_frequency_extract(self, key):
        #TODO put this logic in a subobject
        freq_Hz = 0
        for F, n in key[ClassicalFreqKey].F_dict.items():
            freq_Hz += n * F.F_Hz
        return freq_Hz

    def classical_frequency_test_max(self, key, max_freq):
        if max_freq is None:
            return False
        #TODO put this logic in a subobject
        freq_Hz = 0
        for F, n in key[ClassicalFreqKey].F_dict.items():
            freq_Hz += n * F.F_Hz
        if np.any(freq_Hz < max_freq):
            return False
        return True

    def _setup_sequence(self):
        self._autoterminate()
        self._frozen = True

        self.port_algo = PortUpdatesAlgorithm(
            system = self,
        )
        self.matrix_algorithm = MatrixBuildAlgorithm(
            system = self,
            ports_algorithm = self.port_algo,
        )
        self.solver = SystemSolver(
            system = self,
            ports_algorithm = self.port_algo,
            matrix_algorithm = self.matrix_algorithm,
        )
        return

    def solve(self):
        self._setup_sequence()
        self.solver.solve()
        return self.solver

    def include(self, element):
        if self._frozen:
            raise RuntimeError("Cannot include elements or link after solution requested")
        if element in self.elements:
            return
        self.elements.add(element)
        try:
            op = element.owned_ports
        except AttributeError:
            pass
        else:
            for port, pobj in op.items():
                self.port_owners[port] = element
                self.owners_ports.setdefault(element, []).append(port)
                self.owners_ports_virtual.setdefault(element, [])
                #have the port objects autoterminate
                pobj.autoterminations(self.port_autoterminate)
        if element.fully_resolved_name in self.elements_named:
            warnings.warn((
                "Multiple elements added with name {0}"
                ", may be confusing and prevent system rebuilding from functioning"
            ).format(element.fully_resolved_name))
            #break the elements named so that there isn't confusion later
            self.elements_named[element.fully_resolved_name] = None
        else:
            self.elements_named[element.fully_resolved_name] = element
        for t, s in self.elements_by_type.items():
            if isinstance(element, t):
                s.add(element)
        #TODO not sure linked_elements is relevant anymore with the sled system
        for sub_element in element.linked_elements():
            self.include(sub_element)

    def _autoterminate(self):
        terminated_ports = set()
        for k, v in self.link_pairs.items():
            if v:
                terminated_ports.add(k)
                terminated_ports.update(v)
        registered_ports = set(self.port_owners.keys())
        unterminated_ports = registered_ports - terminated_ports
        if unterminated_ports:
            self.sled.autoterminate = SystemElementSled()
        for port in unterminated_ports:
            aterm = self.port_autoterminate.get(port, None)
            if aterm is None:
                #print("unterminated port", port)
                pass
            else:
                #print("Autoterminating port:", port)
                pobj, tclass = aterm
                #have to build within include to get the sled connection
                #TODO: make this a sane naming scheme
                name = '{0}({2}-<{1}>)'.format(tclass.__name__, port, pobj.element.fully_resolved_name)
                tinst = self.sled.autoterminate.include(name, tclass())
                self.link(pobj, tinst.Fr)

    def _link_record(self, enameA, pkeyA, enameB, pkeyB):
        eA = self.elements_named[enameA]
        pA = eA.owned_port_keys[pkeyA]
        eB = self.elements_named[enameB]
        pB = eB.owned_port_keys[pkeyB]
        return self.link(pA, pB)

    def link(self, port_A, port_B):
        if self._record_build:
            self._record_build_sequence.append((
                '_link_record',
                port_A.element.fully_resolved_name,
                port_A.key,
                port_B.element.fully_resolved_name,
                port_B.key,
            ))
        #print("Linking: ", port_A, port_B)
        self.include(port_A.element)
        self.include(port_B.element)

        #print(port_A)
        #print(port_B)
        either_included = False
        try:
            port_A.o
            port_B.i
        except AttributeError:
            pass
        else:
            either_included = True
            if (not port_B.multiple_attach):
                assert(port_B.i not in self.link_pairs)
            if not (port_A.multiple_attach):
                assert(port_A.o not in self.link_pairs)

            self.link_pairs[port_A.o].add(port_B.i)

        #also attach the duals
        try:
            port_B.o
            port_A.i
        except AttributeError:
            pass
        else:
            either_included = True
            if (not port_A.multiple_attach):
                assert(port_A.i not in self.link_pairs)
            if (not port_B.multiple_attach):
                assert(port_B.o not in self.link_pairs)
            self.link_pairs[port_B.o].add(port_A.i)

        if not either_included:
            raise RuntimeError("Trying to link, but the pair is not in-out compatible")
        return

    def own_port_virtual(self, element, port):
        if self._record_build:
            #TODO
            pass

        self.port_owners_virtual[port].add(element)
        self.owners_ports_virtual.setdefault(element, []).append(port)
        return

    def _subsled_construct_record(self, sled_fqn, name, constructor):
        sled = self.elements_named[sled_fqn]
        return self._subsled_construct(sled, name, constructor)

    def _subsled_construct(
            self,
            element,
            name,
            constructor,
    ):
        #store the constructor so that it may be replayed
        if self._record_build:
            self._record_build_sequence.append((
                '_subsled_construct_record',
                element.fully_resolved_name,
                name,
                constructor,
            ))
        #TODO there may be a cleaner way to construct these dictionaries
        #ooa_params = element.ooa_params[name]
        constructed_item = constructor.construct(
            parent = element,
            name   = name,
        )
        if name == 'PD_P':
            print("BOO!", constructed_item, element)
            print(constructed_item.fully_resolved_name_tuple)
        self.include(constructed_item)
        return constructed_item

