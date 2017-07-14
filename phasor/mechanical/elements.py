# -*- coding: utf-8 -*-
"""
The zM_termination uses mechanical mobility in its calculations, folling the electrical/mechanical impedance analogy. ps_In this case using mobility/admittance rather than impedance to preserve the mechanical topology.

https://en.wikipedia.org/wiki/Impedance_analogy
https://en.wikipedia.org/wiki/Mobility_analogy

This implementation is more interested in measuring displacements rather than velocities so that the DC term may be
calculated. ps_In the standard mobility analogy, current becomes force and voltage becomes velocity and admittance [ps_In/V] is [kg/s]. This allows wave parameters to carry W as in the electrical case and the ports may be easily converted to vel and force. Displacement can be calculated as charge is, which requires knowing the DC force on all spring (capacitive) elements.

Instead this implementation uses a different convention, where voltage->displacement current->force. This means all of the wave parameters carry J and mobility is in units of [kg/s^2].

This does complicate johnson_noise, but the correspondance shouldn't be too bad

For convenience, multiple kinds of mobility are used, and formulas are modified. This is to prevent division by zero

mobility  [kg/s^2]
Vmobility [kg/s]
Amobility [kg]

and their inverses for reactance
"""
from __future__ import division, print_function, unicode_literals

from ..base.bases import (
    SystemElementBase,
    NoiseBase,
    CouplerBase,
)

import declarative as decl

from . import ports


class MechanicalElementBase(CouplerBase, SystemElementBase):
    zM_termination = 1

    @decl.mproperty
    def symbols(self):
        return self.system.symbols


class MechanicalNoiseBase(NoiseBase, MechanicalElementBase):
    pass


class Mechanical1PortBase(MechanicalElementBase):
    @decl.dproperty
    def pm_A(self):
        return ports.MechanicalPort(sname = 'pm_A')

    @decl.mproperty
    def pm_Fr(self):
        return self.pm_A

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.pm_A.i):
            ports_algorithm.port_coupling_needed(self.pm_A.o, kfrom)
        for kto in ports_algorithm.port_update_get(self.pm_A.o):
            ports_algorithm.port_coupling_needed(self.pm_A.i, kto)
        return


class Mechanical2PortBase(MechanicalElementBase):
    @decl.dproperty
    def pm_A(self):
        return ports.MechanicalPort(pchain = 'pm_B')

    @decl.dproperty
    def pm_B(self):
        return ports.MechanicalPort(pchain = 'pm_A')

    @decl.mproperty
    def pm_Fr(self):
        return self.pm_A

    @decl.mproperty
    def pm_Bk(self):
        return self.pm_B

    def bond_series(self, other):
        """
        Takes two 2-port objects and bonds them to form a series connection. With multibonding,
        this can be done and the original can still be connected.
        """
        self.pm_A.bond(other.pm_A)
        self.pm_B.bond(other.pm_B)

class Mechanical4PortBase(MechanicalElementBase):
    @decl.dproperty
    def pm_A(self):
        return ports.MechanicalPort()

    @decl.dproperty
    def pm_B(self):
        return ports.MechanicalPort()

    @decl.dproperty
    def pm_C(self):
        return ports.MechanicalPort()

    @decl.dproperty
    def pm_D(self):
        return ports.MechanicalPort()

    @decl.mproperty
    def pm_FrA(self):
        return self.pm_A

    @decl.mproperty
    def pm_FrB(self):
        return self.pm_B

    @decl.mproperty
    def pm_BkA(self):
        return self.pm_C

    @decl.mproperty
    def pm_BkB(self):
        return self.pm_D


class Connection(MechanicalElementBase):
    @decl.dproperty
    def N_ports(self, val = 0):
        return val

    @decl.dproperty
    def connect(self, val = ()):
        return val

    def __build__(self):
        super(Connection, self).__build__()

        total_ports = self.N_ports + len(self.connect)
        ports_mechanical = []
        for idx in range(total_ports):
            name = 'pm_{0}'.format(idx)
            pobj = ports.MechanicalPort(sname = name)
            pobj = self.insert(pobj, name)
            ports_mechanical.append(pobj)
        self.ports_mechanical = ports_mechanical
        for idx in range(len(self.connect)):
            name = 'pm_{0}'.format(idx + self.N_ports)
            port = getattr(self, name)
            self.system.bond(self.connect[idx], port)
        return

    def system_setup_ports(self, ports_algorithm):
        for port1 in self.ports_mechanical:
            for port2 in self.ports_mechanical:
                for kfrom in ports_algorithm.port_update_get(port1.i):
                    ports_algorithm.port_coupling_needed(port2.o, kfrom)
                for kto in ports_algorithm.port_update_get(port2.o):
                    ports_algorithm.port_coupling_needed(port1.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        _2 = self.symbols.number(2)
        total_ports = len(self.ports_mechanical)
        for port1 in self.ports_mechanical:
            for kfrom in matrix_algorithm.port_set_get(port1.i):
                for port2 in self.ports_mechanical:
                    if port1 is port2:
                        pgain = (_2 - total_ports) / total_ports
                    else:
                        pgain = (_2 / total_ports)
                    matrix_algorithm.port_coupling_insert(
                        port1.i,
                        kfrom,
                        port2.o,
                        kfrom,
                        pgain,
                    )


class Cable(Mechanical2PortBase):
    """
    Basically a longitudinal wave string with. This should be designed to have certain characteristic mobility
    """
    @decl.dproperty
    def delay_s(self, val = 0):
        return val

    @decl.dproperty
    def Loss(self, val = 0):
        return val

    def phase_advance(self, F):
        return self.symbols.math.exp(-2 * self.symbols.i * self.symbols.pi * F * self.delay_s)

    def system_setup_ports(self, ports_algorithm):
        #TODO could reduce these with more information about used S-matrix elements
        for port1, port2 in [
            (self.pm_A, self.pm_B),
            (self.pm_B, self.pm_A),
        ]:
            for kfrom in ports_algorithm.port_update_get(port1.i):
                ports_algorithm.port_coupling_needed(port2.o, kfrom)
            for kto in ports_algorithm.port_update_get(port2.o):
                ports_algorithm.port_coupling_needed(port1.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        if self.Loss != 0:
            loss_coeff = (1 - self.Loss)**.5
        else:
            loss_coeff = 1

        for port1, port2 in [
            (self.pm_A, self.pm_B),
            (self.pm_B, self.pm_A),
        ]:
            for kfrom in matrix_algorithm.port_set_get(port1.i):
                #if self.system.classical_frequency_test_max(kfrom, self.max_freq):
                #    continue
                freq = self.system.classical_frequency_extract(kfrom)
                pgain = self.phase_advance(freq) * loss_coeff
                matrix_algorithm.port_coupling_insert(
                    port1.i,
                    kfrom,
                    port2.o,
                    kfrom,
                    pgain,
                )
