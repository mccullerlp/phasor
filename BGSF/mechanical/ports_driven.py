# -*- coding: utf-8 -*-
from __future__ import division, print_function
import declarative

from . import elements
from . import ports


class ForceToDisplacementBase(elements.MechanicalElementBase):
    @declarative.dproperty
    def _port(self, port):
        self.system.own_port_virtual(self, port.i)
        self.system.own_port_virtual(self, port.o)

    @declarative.mproperty
    def F_DC(self, val = 0):
        #TODO set F_DC
        return val

    @declarative.dproperty
    def F(self):
        return ports.SignalInPort(sname = 'F')

    @declarative.dproperty
    def d(self):
        return ports.SignalOutPort(sname = 'd')

    @declarative.mproperty
    def fkey(self):
        return ports.DictKey({
            ports.ClassicalFreqKey: ports.FrequencyKey({}),
        })

    def system_setup_ports_initial(self, ports_algorithm):
        if self.F_DC != 0:
            ports_algorithm.coherent_sources_needed(self._port.o, self.fkey)
        return

    def system_setup_ports(self, ports_algorithm):
        super(ForceToDisplacementBase, self).system_setup_ports(ports_algorithm)
        for kfrom in ports_algorithm.port_update_get(self.F.i):
            ports_algorithm.port_coupling_needed(self._port.o, kfrom)
        for kto in ports_algorithm.port_update_get(self._port.o):
            ports_algorithm.port_coupling_needed(self.F.i, kto)

        #now displacement readout
        for port1 in [self._port.i, self._port.o]:
            for kfrom in ports_algorithm.port_update_get(port1):
                ports_algorithm.port_coupling_needed(self.d.o, kfrom)
            for kto in ports_algorithm.port_update_get(self.d.o):
                ports_algorithm.port_coupling_needed(port1, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO setup DC
        super(ForceToDisplacementBase, self).system_setup_coupling(matrix_algorithm)

        if self.F_DC != 0:
            matrix_algorithm.coherent_sources_insert(
                self._port.o,
                self.fkey,
                self.F_DC * self.zM_termination
            )

        for kfrom in matrix_algorithm.port_set_get(self.F.i):
            matrix_algorithm.port_coupling_insert(
                self.F.i,
                kfrom,
                self._port.o,
                kfrom,
                self.zM_termination,
            )

        #now do displacement
        pcplgs = {
            self.system.ports_pre_get(self._port.i) :  1,
            self.system.ports_post_get(self._port.o) : 1,
        }
        for port, pcplg in pcplgs.items():
            for kfrom in matrix_algorithm.port_set_get(port):
                matrix_algorithm.port_coupling_insert(
                    port,
                    kfrom,
                    self.d.o,
                    kfrom,
                    pcplg,
                )
        return


class MechanicalPortDriven(ForceToDisplacementBase, ports.MechanicalPort):
    @declarative.dproperty
    def _port(self):
        port = self
        self.system.own_port_virtual(self, port.i)
        self.system.own_port_virtual(self, port.o)
        return port


