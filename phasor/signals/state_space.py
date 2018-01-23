# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from phasor.utilities.print import print
import declarative

from . import ports
from . import bases


class StateSpaceModel(
    bases.SignalElementBase,
    bases.CouplerBase,
):
    @declarative.dproperty
    def names_in(self, val):
        return val

    @declarative.dproperty
    def names_out(self, val):
        return val

    @declarative.dproperty
    def A(self, val):
        return val

    @declarative.dproperty
    def B(self, val):
        return val

    @declarative.dproperty
    def C(self, val):
        return val

    @declarative.dproperty
    def D(self, val):
        return val

    @declarative.dproperty
    def pS_in(self):
        return bases.SignalElementBase()

    @declarative.dproperty
    def pS_out(self):
        return bases.SignalElementBase()

    @declarative.dproperty
    def pS_states(self):
        return bases.SignalElementBase()

    @declarative.dproperty
    def ports_in(self):
        plist = []
        for idx, name in enumerate(self.names_in):
            self.pS_in.insert(ports.SignalInPort(), name)
            port = self.pS_in[name]
            self.system.own_port_virtual(self, port.i)
            plist.append(port)

        return plist

    @declarative.dproperty
    def ports_out(self):
        plist = []
        for idx, name in enumerate(self.names_out):
            self.pS_out.insert(ports.SignalOutPort(), name)
            port = self.pS_out[name]
            self.system.own_port_virtual(self, port.o)
            plist.append(port)
        return plist

    @declarative.dproperty
    def ports_states(self):
        plist = []
        for idx in range(self.A.shape[0]):
            name = 'node_{0}'.format(idx)
            self.pS_states.insert(ports.SignalNode(), name)
            port = self.pS_states[name]
            self.system.own_port_virtual(self, port.node)
            plist.append(port)
        return plist

    @declarative.dproperty
    def max_freq(self, val = None):
        return val

    def system_setup_ports(self, ports_algorithm):
        #TODO! Fix using port_full_get required from using virtual port ownership
        N_in = self.B.shape[1]
        N_out = self.C.shape[0]
        N_states = self.A.shape[0]
        for idx_in in range(N_in):
            p_in = self.ports_in[idx_in]
            for kfrom in ports_algorithm.port_full_get(p_in.i):
                if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                    continue
                #in 2 states (B)
                for idx_state in range(N_states):
                    p_state = self.ports_states[idx_state]
                    cplg = self.B[idx_state, idx_in]
                    if cplg != 0:
                        #multiply by s
                        ports_algorithm.port_coupling_needed(p_state.node, kfrom)
                #in 2 out (D)
                for idx_out in range(N_out):
                    p_out = self.ports_states[idx_out]
                    cplg = self.D[idx_out, idx_in]
                    if cplg != 0:
                        ports_algorithm.port_coupling_needed(p_out.o, kfrom)

        for idx_state in range(N_states):
            p_state = self.ports_states[idx_state]
            for kfrom in ports_algorithm.port_full_get(p_state.node):
                if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                    continue
                for idx_in in range(N_in):
                    p_in = self.ports_in[idx_in]
                    cplg = self.B[idx_state, idx_in]
                    if cplg != 0:
                        ports_algorithm.port_coupling_needed(p_in.i, kfrom)
                #states 2 states (A)
                for idx_state_o in range(N_states):
                    p_state_o = self.ports_states[idx_state_o]
                    cplg = self.A[idx_state_o, idx_state]
                    if cplg != 0:
                        ports_algorithm.port_coupling_needed(p_state_o.node, kfrom)
                    #also check the reverse!
                    cplg = self.A[idx_state, idx_state_o]
                    if cplg != 0:
                        ports_algorithm.port_coupling_needed(p_state_o.node, kfrom)
                #states 2 out (C)
                for idx_out in range(N_out):
                    p_out = self.ports_out[idx_out]
                    cplg = self.C[idx_out, idx_state]
                    if cplg != 0:
                        ports_algorithm.port_coupling_needed(p_out.o, kfrom)

        for idx_out in range(N_out):
            p_out = self.ports_out[idx_out]
            for kfrom in ports_algorithm.port_full_get(p_out.o):
                #print(kfrom, p_out)
                if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                    continue
                for idx_in in range(N_in):
                    p_in = self.ports_in[idx_in]
                    cplg = self.D[idx_out, idx_in]
                    if cplg != 0:
                        #print("---", kfrom, p_in)
                        ports_algorithm.port_coupling_needed(p_in.i, kfrom)
                #states 2 states (A)
                for idx_state in range(N_states):
                    p_state = self.ports_states[idx_state]
                    cplg = self.C[idx_out, idx_state]
                    if cplg != 0:
                        #print("---", kfrom, p_state)
                        ports_algorithm.port_coupling_needed(p_state.node, kfrom)
        return

    def system_setup_coupling(self, matrix_algorithm):
        N_in = self.B.shape[1]
        N_out = self.C.shape[0]
        N_states = self.A.shape[0]
        for idx_in in range(N_in):
            p_in = self.ports_in[idx_in]
            #print(p_in)
            for kfrom in matrix_algorithm.port_set_get(p_in.i):
                if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                    continue
                #in 2 states (B)
                freq = self.system.classical_frequency_extract(kfrom)
                for idx_state in range(N_states):
                    p_state = self.ports_states[idx_state]
                    cplg = self.B[idx_state, idx_in]
                    if cplg != 0:
                        #multiply by 1/s
                        D_cplg = cplg / (freq * self.symbols.i2pi)
                        #print("    ", p_state)
                        matrix_algorithm.port_coupling_insert(p_in.i, kfrom, p_state.node, kfrom, D_cplg)
                #in 2 out (D)
                for idx_out in range(N_out):
                    p_out = self.ports_states[idx_out]
                    cplg = self.D[idx_out, idx_in]
                    if cplg != 0:
                        #print("    ", p_out)
                        matrix_algorithm.port_coupling_insert(p_in.i, kfrom, p_out.o, kfrom, cplg)

        for idx_state in range(N_states):
            p_state = self.ports_states[idx_state]
            #print(p_state)
            for kfrom in matrix_algorithm.port_set_get(p_state.node):
                if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                    continue
                freq = self.system.classical_frequency_extract(kfrom)
                #states 2 states (A)
                for idx_state_o in range(N_states):
                    p_state_o = self.ports_states[idx_state_o]
                    cplg = self.A[idx_state_o, idx_state]
                    if cplg != 0:
                        #multiply by 1/s
                        D_cplg = cplg / (freq * self.symbols.i2pi)
                        #print("    ", p_state_o)
                        matrix_algorithm.port_coupling_insert(p_state.node, kfrom, p_state_o.node, kfrom, D_cplg)
                #states 2 out (C)
                for idx_out in range(N_out):
                    p_out = self.ports_out[idx_out]
                    cplg = self.C[idx_out, idx_state]
                    if cplg != 0:
                        #print("    ", p_out)
                        matrix_algorithm.port_coupling_insert(p_state.node, kfrom, p_out.o, kfrom, cplg)
        return
