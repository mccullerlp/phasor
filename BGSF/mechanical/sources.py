"""
"""
from __future__ import division

import declarative as decl

from . import ports
from . import smatrix


class ForceSource(smatrix.SMatrix1PortBase):
    def S11_by_freq(self, F):
        return -1

    @decl.mproperty
    def F_DC(self, val = 0):
        return val

    @decl.dproperty
    def F(self):
        return ports.SignalInPort(sname = 'F')

    @decl.mproperty
    def fkey(self):
        return ports.DictKey({
            ports.ClassicalFreqKey: ports.FrequencyKey({}),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        if self.F_DC != 0:
            ports_algorithm.coherent_sources_needed(self.A.o, self.fkey)
        return

    def system_setup_ports(self, ports_algorithm):
        super(ForceSource, self).system_setup_ports(ports_algorithm)
        for kfrom in ports_algorithm.port_update_get(self.F.i):
            ports_algorithm.port_coupling_needed(self.A.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.A.o):
            ports_algorithm.port_coupling_needed(self.F.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(ForceSource, self).system_setup_coupling(matrix_algorithm)

        if self.F_DC != 0:
            matrix_algorithm.coherent_sources_insert(
                self.A.o,
                self.fkey,
                self.F_DC
            )

        for kfrom in matrix_algorithm.port_set_get(self.F.i):
            matrix_algorithm.port_coupling_insert(
                self.F.i,
                kfrom,
                self.A.o,
                kfrom,
                1,
            )
        return


class DisplacementSource(smatrix.SMatrix1PortBase):
    def S11_by_freq(self, F):
        return 1

    @decl.mproperty
    def d_DC(self, val = 0):
        #TODO set d_DC
        return val

    @decl.dproperty
    def d(self):
        return ports.SignalInPort(sname = 'd')

    @decl.mproperty
    def fkey(self):
        return ports.DictKey({
            ports.ClassicalFreqKey: ports.FrequencyKey({}),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        if self.d_DC != 0:
            ports_algorithm.coherent_sources_needed(self.A.o, self.fkey)
        return

    def system_setup_ports(self, ports_algorithm):
        super(DisplacementSource, self).system_setup_ports(ports_algorithm)
        for kfrom in ports_algorithm.port_update_get(self.d.i):
            ports_algorithm.port_coupling_needed(self.A.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.A.o):
            ports_algorithm.port_coupling_needed(self.d.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(DisplacementSource, self).system_setup_coupling(matrix_algorithm)

        if self.d_DC != 0:
            matrix_algorithm.coherent_sources_insert(
                self.A.o,
                self.fkey,
                self.d_DC * self.zM_termination
            )

        for kfrom in matrix_algorithm.port_set_get(self.d.i):
            matrix_algorithm.port_coupling_insert(
                self.d.i,
                kfrom,
                self.A.o,
                kfrom,
                self.zM_termination,
            )
        return


class ForceSourceBalanced(smatrix.SMatrix2PortBase):
    """
    TODO consider making this the ForceSource but with the "B" port autoterminate with a short
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
    def F_DC(self, val = 0):
        return val

    @decl.dproperty
    def F(self):
        return ports.SignalInPort(sname = 'F')

    @decl.mproperty
    def d_DC(self, val = 0):
        return val

    @decl.dproperty
    def d(self):
        return ports.SignalInPort(sname = 'd')

    @decl.mproperty
    def fkey(self):
        return ports.DictKey({
            ports.ClassicalFreqKey: ports.FrequencyKey({}),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        if self.d_DC != 0 or self.F_DC != 0:
            ports_algorithm.coherent_sources_needed(self.A.o, self.fkey)
            ports_algorithm.coherent_sources_needed(self.B.o, self.fkey)
        return

    def system_setup_ports(self, ports_algorithm):
        super(ForceSourceBalanced, self).system_setup_ports(ports_algorithm)
        for port2 in [self.A, self.B]:
            for kfrom in ports_algorithm.port_update_get(self.F.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(self.F.i, kto)
            for kfrom in ports_algorithm.port_update_get(self.d.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(self.d.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(ForceSourceBalanced, self).system_setup_coupling(matrix_algorithm)
        #TODO, not sure about the 1/2 everywhere
        _2 = self.symbols.number(2)

        if self.F_DC != 0:
            matrix_algorithm.coherent_sources_insert(
                self.A.o,
                self.fkey,
                self.F_DC / _2,
            )

            matrix_algorithm.coherent_sources_insert(
                self.B.o,
                self.fkey,
                -self.F_DC / _2,
            )

        if self.d_DC != 0:
            matrix_algorithm.coherent_sources_insert(
                self.A.o,
                self.fkey,
                self.zM_termination * self.d_DC / _2,
            )

            matrix_algorithm.coherent_sources_insert(
                self.B.o,
                self.fkey,
                self.zM_termination * self.d_DC / _2,
            )

        for kfrom in matrix_algorithm.port_set_get(self.F.i):
            matrix_algorithm.port_coupling_insert(
                self.F.i,
                kfrom,
                self.A.o,
                kfrom,
                1 / _2,
            )
            matrix_algorithm.port_coupling_insert(
                self.F.i,
                kfrom,
                self.B.o,
                kfrom,
                -1 / _2,
            )
        for kfrom in matrix_algorithm.port_set_get(self.d.i):
            matrix_algorithm.port_coupling_insert(
                self.d.i,
                kfrom,
                self.A.o,
                kfrom,
                self.zM_termination / _2,
            )
            matrix_algorithm.port_coupling_insert(
                self.d.i,
                kfrom,
                self.B.o,
                kfrom,
                self.zM_termination / _2,
            )


class DisplacementSourceBalanced(smatrix.SMatrix2PortBase):
    def S11_by_freq(self, F):
        return 1

    def S12_by_freq(self, F):
        return 0

    def S21_by_freq(self, F):
        return 0

    def S22_by_freq(self, F):
        return 1

    @decl.mproperty
    def d_DC(self, val = 0):
        return val

    @decl.dproperty
    def d(self):
        return ports.SignalInPort(sname = 'd')

    @decl.mproperty
    def fkey(self):
        return ports.DictKey({
            ports.ClassicalFreqKey: ports.FrequencyKey({}),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        ports_algorithm.coherent_sources_needed(self.A.o, self.fkey)
        ports_algorithm.coherent_sources_needed(self.B.o, self.fkey)
        return

    def system_setup_ports(self, ports_algorithm):
        super(DisplacementSourceBalanced, self).system_setup_ports(ports_algorithm)
        for port2 in [self.A, self.B]:
            for kfrom in ports_algorithm.port_update_get(self.d.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(self.d.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(DisplacementSourceBalanced, self).system_setup_coupling(matrix_algorithm)

        matrix_algorithm.coherent_sources_insert(
            self.A.o,
            self.fkey,
            self.zM_termination * self.d_DC,
        )

        matrix_algorithm.coherent_sources_insert(
            self.B.o,
            self.fkey,
            self.zM_termination * self.d_DC,
        )

        for kfrom in matrix_algorithm.port_set_get(self.d.i):
            matrix_algorithm.port_coupling_insert(
                self.d.i,
                kfrom,
                self.A.o,
                kfrom,
                self.zM_termination,
            )
            matrix_algorithm.port_coupling_insert(
                self.d.i,
                kfrom,
                self.B.o,
                kfrom,
                self.zM_termination,
            )


