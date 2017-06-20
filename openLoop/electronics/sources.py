"""
"""
from __future__ import division

import declarative as decl

from . import ports
from . import smatrix


class VoltageSource(smatrix.SMatrix1PortBase):
    def S11_by_freq(self, F):
        return -1

    @decl.mproperty
    def V_DC(self, val = 0):
        return val

    @decl.dproperty
    def V(self):
        return ports.SignalInPort(sname = 'V')

    @decl.mproperty
    def fkey(self):
        return ports.DictKey({
            ports.ClassicalFreqKey: ports.FrequencyKey({}),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        if self.V_DC != 0:
            ports_algorithm.coherent_sources_needed(self.pe_A.o, self.fkey)
        return

    def system_setup_ports(self, ports_algorithm):
        super(VoltageSource, self).system_setup_ports(ports_algorithm)
        for kfrom in ports_algorithm.port_update_get(self.V.i):
            ports_algorithm.port_coupling_needed(self.pe_A.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.pe_A.o):
            ports_algorithm.port_coupling_needed(self.V.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(VoltageSource, self).system_setup_coupling(matrix_algorithm)

        if self.V_DC != 0:
            matrix_algorithm.coherent_sources_insert(
                self.pe_A.o,
                self.fkey,
                self.V_DC
            )

        for kfrom in matrix_algorithm.port_set_get(self.V.i):
            matrix_algorithm.port_coupling_insert(
                self.V.i,
                kfrom,
                self.pe_A.o,
                kfrom,
                1,
            )
        return


class CurrentSource(smatrix.SMatrix1PortBase):
    def S11_by_freq(self, F):
        return 1

    @decl.mproperty
    def I_DC(self, val = 0):
        #TODO set I_DC
        return val

    @decl.dproperty
    def ps_In(self):
        return ports.SignalInPort(sname = 'ps_In')

    @decl.mproperty
    def fkey(self):
        return ports.DictKey({
            ports.ClassicalFreqKey: ports.FrequencyKey({}),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        if self.I_DC != 0:
            ports_algorithm.coherent_sources_needed(self.pe_A.o, self.fkey)
        return

    def system_setup_ports(self, ports_algorithm):
        super(CurrentSource, self).system_setup_ports(ports_algorithm)
        for kfrom in ports_algorithm.port_update_get(self.ps_In.i):
            ports_algorithm.port_coupling_needed(self.pe_A.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.pe_A.o):
            ports_algorithm.port_coupling_needed(self.ps_In.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(CurrentSource, self).system_setup_coupling(matrix_algorithm)

        if self.I_DC != 0:
            matrix_algorithm.coherent_sources_insert(
                self.pe_A.o,
                self.fkey,
                self.I_DC * self.Z_termination
            )

        for kfrom in matrix_algorithm.port_set_get(self.ps_In.i):
            matrix_algorithm.port_coupling_insert(
                self.ps_In.i,
                kfrom,
                self.pe_A.o,
                kfrom,
                self.Z_termination,
            )
        return


class VoltageSourceBalanced(smatrix.SMatrix2PortBase):
    """
    TODO consider making this the VoltageSource but with the "pe_B" port autoterminate with a short
    """
    def S11_by_freq(self, F):
        return 0

    def S12_by_freq(self, F):
        return 1

    def S21_by_freq(self, F):
        return 1

    def S22_by_freq(self, F):
        return 0

    @decl.mproperty
    def V_DC(self, val = 0):
        return val

    @decl.dproperty
    def V(self):
        return ports.SignalInPort(sname = 'V')

    @decl.mproperty
    def I_DC(self, val = 0):
        return val

    @decl.dproperty
    def ps_In(self):
        return ports.SignalInPort(sname = 'ps_In')

    @decl.mproperty
    def fkey(self):
        return ports.DictKey({
            ports.ClassicalFreqKey: ports.FrequencyKey({}),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        if self.I_DC != 0 or self.V_DC != 0:
            ports_algorithm.coherent_sources_needed(self.pe_A.o, self.fkey)
            ports_algorithm.coherent_sources_needed(self.pe_B.o, self.fkey)
        return

    def system_setup_ports(self, ports_algorithm):
        super(VoltageSourceBalanced, self).system_setup_ports(ports_algorithm)
        for port2 in [self.pe_A, self.pe_B]:
            for kfrom in ports_algorithm.port_update_get(self.V.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(self.V.i, kto)
            for kfrom in ports_algorithm.port_update_get(self.ps_In.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(self.ps_In.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(VoltageSourceBalanced, self).system_setup_coupling(matrix_algorithm)
        #TODO, not sure about the 1/2 everywhere
        _2 = self.symbols.number(2)

        if self.V_DC != 0:
            matrix_algorithm.coherent_sources_insert(
                self.pe_A.o,
                self.fkey,
                self.V_DC / _2,
            )

            matrix_algorithm.coherent_sources_insert(
                self.pe_B.o,
                self.fkey,
                -self.V_DC / _2,
            )

        if self.I_DC != 0:
            matrix_algorithm.coherent_sources_insert(
                self.pe_A.o,
                self.fkey,
                self.Z_termination * self.I_DC / _2,
            )

            matrix_algorithm.coherent_sources_insert(
                self.pe_B.o,
                self.fkey,
                self.Z_termination * self.I_DC / _2,
            )

        for kfrom in matrix_algorithm.port_set_get(self.V.i):
            matrix_algorithm.port_coupling_insert(
                self.V.i,
                kfrom,
                self.pe_A.o,
                kfrom,
                1 / _2,
            )
            matrix_algorithm.port_coupling_insert(
                self.V.i,
                kfrom,
                self.pe_B.o,
                kfrom,
                -1 / _2,
            )
        for kfrom in matrix_algorithm.port_set_get(self.ps_In.i):
            matrix_algorithm.port_coupling_insert(
                self.ps_In.i,
                kfrom,
                self.pe_A.o,
                kfrom,
                self.Z_termination / _2,
            )
            matrix_algorithm.port_coupling_insert(
                self.ps_In.i,
                kfrom,
                self.pe_B.o,
                kfrom,
                self.Z_termination / _2,
            )


class CurrentSourceBalanced(smatrix.SMatrix2PortBase):
    def S11_by_freq(self, F):
        return 1

    def S12_by_freq(self, F):
        return 0

    def S21_by_freq(self, F):
        return 0

    def S22_by_freq(self, F):
        return 1

    @decl.mproperty
    def I_DC(self, val = 0):
        return val

    @decl.dproperty
    def ps_In(self):
        return ports.SignalInPort(sname = 'ps_In')

    @decl.mproperty
    def fkey(self):
        return ports.DictKey({
            ports.ClassicalFreqKey: ports.FrequencyKey({}),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        ports_algorithm.coherent_sources_needed(self.pe_A.o, self.fkey)
        ports_algorithm.coherent_sources_needed(self.pe_B.o, self.fkey)
        return

    def system_setup_ports(self, ports_algorithm):
        super(CurrentSourceBalanced, self).system_setup_ports(ports_algorithm)
        for port2 in [self.pe_A, self.pe_B]:
            for kfrom in ports_algorithm.port_update_get(self.ps_In.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(self.ps_In.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(CurrentSourceBalanced, self).system_setup_coupling(matrix_algorithm)

        matrix_algorithm.coherent_sources_insert(
            self.pe_A.o,
            self.fkey,
            self.Z_termination * self.I_DC,
        )

        matrix_algorithm.coherent_sources_insert(
            self.pe_B.o,
            self.fkey,
            self.Z_termination * self.I_DC,
        )

        for kfrom in matrix_algorithm.port_set_get(self.ps_In.i):
            matrix_algorithm.port_coupling_insert(
                self.ps_In.i,
                kfrom,
                self.pe_A.o,
                kfrom,
                self.Z_termination,
            )
            matrix_algorithm.port_coupling_insert(
                self.ps_In.i,
                kfrom,
                self.pe_B.o,
                kfrom,
                self.Z_termination,
            )


