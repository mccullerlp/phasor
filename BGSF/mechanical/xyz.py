"""
"""
from __future__ import division
import numpy as np

import declarative

from . import ports
from . import passive


class XYZMass(object):
    @declarative.dproperty
    def A(self):
        return ports.MechanicalXYZPort(
            X = self.X.A,
            Y = self.Y.A,
            Z = self.Z.A,
        )

    @declarative.dproperty
    def mass_kg(self, val):
        return val

    @declarative.dproperty
    def X(self):
        return passive.Mass(
            mass_kg = self.mass_kg,
        )

    @declarative.dproperty
    def Y(self):
        return passive.Mass(
            mass_kg = self.mass_kg,
        )

    @declarative.dproperty
    def Z(self):
        return passive.Mass(
            mass_kg = self.mass_kg,
        )


class XYZTerminatorSpring(object):

    @declarative.dproperty
    def A(self):
        return ports.MechanicalXYZPort(
            X = self.X.A,
            Y = self.Y.A,
            Z = self.Z.A,
        )

    @declarative.dproperty
    def elasticityX_N_m(self, val):
        return val

    @declarative.dproperty
    def elasticityY_N_m(self, val):
        return val

    @declarative.dproperty
    def elasticityZ_N_m(self, val):
        return val

    @declarative.dproperty
    def X(self):
        return passive.TerminatorSpring(
            elasticity_N_m = self.elasticityX_N_m,
        )

    @declarative.dproperty
    def Y(self):
        return passive.TerminatorSpring(
            elasticity_N_m = self.elasticityY_N_m,
        )

    @declarative.dproperty
    def Z(self):
        return passive.TerminatorSpring(
            elasticity_N_m = self.elasticityZ_N_m,
        )


class XYZTerminatorDamper(object):

    @declarative.dproperty
    def A(self):
        return ports.MechanicalXYZPort(
            X = self.X.A,
            Y = self.Y.A,
            Z = self.Z.A,
        )

    @declarative.dproperty
    def resistanceX_Ns_m(self, val):
        return val

    @declarative.dproperty
    def resistanceY_Ns_m(self, val):
        return val

    @declarative.dproperty
    def resistanceZ_Ns_m(self, val):
        return val

    @declarative.dproperty
    def X(self):
        return passive.TerminatorDamper(
            resistance_Ns_m = self.resistanceX_Ns_m,
        )

    @declarative.dproperty
    def Y(self):
        return passive.TerminatorDamper(
            resistance_Ns_m = self.resistanceY_Ns_m,
        )

    @declarative.dproperty
    def Z(self):
        return passive.TerminatorDamper(
            resistance_Ns_m = self.resistanceZ_Ns_m,
        )


class XYZMoment(object):
    @declarative.dproperty
    def L(self):
        return ports.MechanicalXYZPort(
            X = self.X.A,
            Y = self.Y.A,
            Z = self.Z.A,
        )

    @declarative.dproperty
    def momentX_kgmsq(self, val):
        return val

    @declarative.dproperty
    def momentY_kgmsq(self, val):
        return val

    @declarative.dproperty
    def momentZ_kgmsq(self, val):
        return val

    @declarative.dproperty
    def X(self):
        return passive.Mass(
            mass_kg = self.momentX_kgmsq,
        )

    @declarative.dproperty
    def Y(self):
        return passive.Mass(
            mass_kg = self.momentY_kgmsq,
        )

    @declarative.dproperty
    def Z(self):
        return passive.Mass(
            mass_kg = self.momentZ_kgmsq,
        )


class XYZMomentDriver(object):
    @declarative.dproperty
    def L(self):
        return ports.MechanicalXYZPort()

    @declarative.dproperty
    def A(self):
        return ports.MechanicalXYZPort()

    @declarative.dproperty
    def displacementXYZ(self, XYZ):
        return XYZ

    def system_setup_ports(self, ports_algorithm):
        all_ports = [self.A.X, self.A.Y, self.A.Z] + [self.L.X, self.L.Y, self.L.Z]
        for port1 in all_ports:
            for port2 in all_ports:
                for kfrom in ports_algorithm.port_update_get(port1.i):
                    ports_algorithm.port_coupling_needed(port2.o, kfrom)
                for kto in ports_algorithm.port_update_get(port2.o):
                    ports_algorithm.port_coupling_needed(port1.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        A_ports = [self.A.X, self.A.Y, self.A.Z]
        L_ports = [self.L.X, self.L.Y, self.L.Z]
        d_vec = np.array(self.displacementXYZ)

        dLsq = np.dot(d_vec, d_vec)
        P_d = np.outer(d_vec, d_vec) / dLsq

        P_torque = np.array([
            [0,         -d_vec[2], +d_vec[1]],
            [+d_vec[2], 0,         -d_vec[0]],
            [-d_vec[1], +d_vec[0], 0]
        ])

        P_force = -P_torque / dLsq

        def matrix_inject(ports1, ports2, matrix):
            for idx1, port1 in enumerate(ports1):
                for idx2, port2 in enumerate(ports2):
                    for kfrom in matrix_algorithm.port_set_get(port1.i):
                        matrix_algorithm.port_coupling_insert(
                            port1.i,
                            kfrom,
                            port2.o,
                            kfrom,
                            matrix[idx1, idx2],
                        )
        matrix_inject(A_ports, A_ports, P_d)
        matrix_inject(L_ports, L_ports, P_d)
        matrix_inject(A_ports, L_ports, P_torque)
        matrix_inject(L_ports, A_ports, P_force)
        return


class MomentDriver(object):
    @declarative.dproperty
    def L(self):
        return ports.MechanicalXYZPort()

    @declarative.dproperty
    def A(self):
        return ports.MechanicalPort()

    @declarative.dproperty
    def displacementXYZ(self, XYZ):
        return XYZ

    @declarative.dproperty
    def driveXYZ(self, XYZ):
        return XYZ

    def system_setup_ports(self, ports_algorithm):
        all_ports = [self.A] + [self.L.X, self.L.Y, self.L.Z]
        for port1 in all_ports:
            for port2 in all_ports:
                for kfrom in ports_algorithm.port_update_get(port1.i):
                    ports_algorithm.port_coupling_needed(port2.o, kfrom)
                for kto in ports_algorithm.port_update_get(port2.o):
                    ports_algorithm.port_coupling_needed(port1.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        A_ports = [self.A]
        L_ports = [self.L.X, self.L.Y, self.L.Z]
        d_vec = np.array(self.displacementXYZ)
        v_vec = np.array(self.driveXYZ)

        dLsq = np.dot(d_vec, d_vec)
        vLsq = np.dot(v_vec, v_vec)

        P_d = np.outer(d_vec, d_vec) / dLsq
        vp_vec = v_vec - np.dot(P_d, v_vec)
        vpLsq = np.dot(vp_vec, vp_vec)
        P_vp = np.outer(vp_vec, vp_vec) / vpLsq

        P_torque = 1/vLsq**.5 * np.array([
            [-d_vec[2] * v_vec[1] + d_vec[1] * v_vec[2]],
            [+d_vec[2] * v_vec[0] - d_vec[0] * v_vec[2]],
            [-d_vec[1] * v_vec[0] + d_vec[0] * v_vec[1]]
        ])

        P_force = P_torque.T / dLsq

        P_X = P_d + P_vp

        def matrix_inject(ports1, ports2, matrix):
            for idx1, port1 in enumerate(ports1):
                for idx2, port2 in enumerate(ports2):
                    for kfrom in matrix_algorithm.port_set_get(port1.i):
                        matrix_algorithm.port_coupling_insert(
                            port1.i,
                            kfrom,
                            port2.o,
                            kfrom,
                            matrix[idx1, idx2],
                        )
        matrix_inject(A_ports, A_ports, [[0]])
        matrix_inject(L_ports, L_ports, P_X)
        matrix_inject(A_ports, L_ports, P_torque)
        matrix_inject(L_ports, A_ports, P_force)
        return
