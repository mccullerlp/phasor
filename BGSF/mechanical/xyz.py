"""
"""
from __future__ import division
import numpy as np

import declarative

from . import ports
from . import passive
from . import elements


class XYZMass(elements.Mechanical1PortBase):
    @declarative.dproperty
    def A(self):
        return ports.MechanicalXYZPort(
            X = self.X.A,
            Y = self.Y.A,
            Z = self.Z.A,
        )

    @declarative.dproperty
    def mass_kg(self, val):
        val = np.asarray(val)
        if val.shape == ():
            val = np.ones(3) * val
        return val

    @declarative.dproperty
    def X(self):
        return passive.Mass(
            mass_kg = self.mass_kg[0],
        )

    @declarative.dproperty
    def Y(self):
        return passive.Mass(
            mass_kg = self.mass_kg[1],
        )

    @declarative.dproperty
    def Z(self):
        return passive.Mass(
            mass_kg = self.mass_kg[2],
        )


class XYZTerminatorSpring(elements.Mechanical1PortBase):

    @declarative.dproperty
    def A(self):
        return ports.MechanicalXYZPort(
            X = self.X.A,
            Y = self.Y.A,
            Z = self.Z.A,
        )

    @declarative.dproperty
    def elasticity_N_m(self, val):
        val = np.asarray(val)
        if val.shape == ():
            val = np.ones(3) * val
        return val

    @declarative.dproperty
    def X(self):
        return passive.TerminatorSpring(
            elasticity_N_m = self.elasticity_N_m[0],
        )

    @declarative.dproperty
    def Y(self):
        return passive.TerminatorSpring(
            elasticity_N_m = self.elasticity_N_m[1],
        )

    @declarative.dproperty
    def Z(self):
        return passive.TerminatorSpring(
            elasticity_N_m = self.elasticity_N_m[2],
        )


class XYZTerminatorOpen(elements.Mechanical1PortBase):
    @declarative.dproperty
    def A(self):
        return ports.MechanicalXYZPort(
            X = self.X.A,
            Y = self.Y.A,
            Z = self.Z.A,
        )

    @declarative.dproperty
    def X(self):
        return passive.TerminatorOpen()

    @declarative.dproperty
    def Y(self):
        return passive.TerminatorOpen()

    @declarative.dproperty
    def Z(self):
        return passive.TerminatorOpen()


class XYZTerminatorShorted(elements.Mechanical1PortBase):
    @declarative.dproperty
    def A(self):
        return ports.MechanicalXYZPort(
            X = self.X.A,
            Y = self.Y.A,
            Z = self.Z.A,
        )

    @declarative.dproperty
    def X(self):
        return passive.TerminatorShorted()

    @declarative.dproperty
    def Y(self):
        return passive.TerminatorShorted()

    @declarative.dproperty
    def Z(self):
        return passive.TerminatorShorted()


class XYZTerminatorDamper(elements.Mechanical1PortBase):

    @declarative.dproperty
    def A(self):
        return ports.MechanicalXYZPort(
            X = self.X.A,
            Y = self.Y.A,
            Z = self.Z.A,
        )

    @declarative.dproperty
    def resistance_Ns_m(self, val):
        val = np.asarray(val)
        if val.shape == ():
            val = np.ones(3) * val
        return val

    @declarative.dproperty
    def X(self):
        return passive.TerminatorDamper(
            resistance_Ns_m = self.resistance_Ns_m[0],
        )

    @declarative.dproperty
    def Y(self):
        return passive.TerminatorDamper(
            resistance_Ns_m = self.resistance_Ns_m[1],
        )

    @declarative.dproperty
    def Z(self):
        return passive.TerminatorDamper(
            resistance_Ns_m = self.resistance_Ns_m[2],
        )


class XYZMoment(elements.Mechanical1PortBase):
    @declarative.dproperty
    def L(self):
        return ports.MechanicalXYZPort(
            X = self.X.A,
            Y = self.Y.A,
            Z = self.Z.A,
        )

    @declarative.dproperty
    def moment_kgmsq(self, val):
        val = np.asarray(val)
        if val.shape == ():
            val = np.ones(3) * val
        return val

    @declarative.dproperty
    def X(self):
        return passive.Mass(
            mass_kg = self.moment_kgmsq[0],
        )

    @declarative.dproperty
    def Y(self):
        return passive.Mass(
            mass_kg = self.moment_kgmsq[1],
        )

    @declarative.dproperty
    def Z(self):
        return passive.Mass(
            mass_kg = self.moment_kgmsq[2],
        )


class XYZMomentDriver(elements.Mechanical1PortBase):
    @declarative.dproperty
    def L(self):
        return ports.MechanicalXYZPort(
            X = self.Lx,
            Y = self.Ly,
            Z = self.Lz,
        )

    @declarative.dproperty
    def A(self):
        return ports.MechanicalXYZPort(
            X = self.Ax,
            Y = self.Ay,
            Z = self.Az,
        )

    @declarative.dproperty
    def B(self):
        return ports.MechanicalXYZPort(
            X = self.Bx,
            Y = self.By,
            Z = self.Bz,
        )

    #TODO temporary fix, remove
    @declarative.dproperty
    def Lx(self):
        return ports.MechanicalPort()

    #TODO temporary fix, remove
    @declarative.dproperty
    def Ly(self):
        return ports.MechanicalPort()

    #TODO temporary fix, remove
    @declarative.dproperty
    def Lz(self):
        return ports.MechanicalPort()

    #TODO temporary fix, remove
    @declarative.dproperty
    def Ax(self):
        return ports.MechanicalPort()

    #TODO temporary fix, remove
    @declarative.dproperty
    def Ay(self):
        return ports.MechanicalPort()

    #TODO temporary fix, remove
    @declarative.dproperty
    def Az(self):
        return ports.MechanicalPort()

    #TODO temporary fix, remove
    @declarative.dproperty
    def Bx(self):
        return ports.MechanicalPort()

    #TODO temporary fix, remove
    @declarative.dproperty
    def By(self):
        return ports.MechanicalPort()

    #TODO temporary fix, remove
    @declarative.dproperty
    def Bz(self):
        return ports.MechanicalPort()

    @declarative.dproperty
    def displacementXYZ(self, XYZ):
        return XYZ

    def system_setup_ports(self, ports_algorithm):
        all_ports = [self.A.X, self.A.Y, self.A.Z] + [self.B.X, self.B.Y, self.B.Z] + [self.L.X, self.L.Y, self.L.Z]
        for port1 in all_ports:
            for port2 in all_ports:
                for kfrom in ports_algorithm.port_update_get(port1.i):
                    ports_algorithm.port_coupling_needed(port2.o, kfrom)
                for kto in ports_algorithm.port_update_get(port2.o):
                    ports_algorithm.port_coupling_needed(port1.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        A_ports = [self.A.X, self.A.Y, self.A.Z]
        B_ports = [self.B.X, self.B.Y, self.B.Z]
        L_ports = [self.L.X, self.L.Y, self.L.Z]
        d_vec = np.asarray(self.displacementXYZ)

        I = np.eye(3)
        dLsq = np.dot(d_vec, d_vec)
        d = dLsq**.5
        P_d = np.outer(d_vec, d_vec) / dLsq

        P_force = np.array([
            [0,         +d_vec[2], -d_vec[1]],
            [-d_vec[2], 0,         +d_vec[0]],
            [+d_vec[1], -d_vec[0], 0]
        ]) / d

        P_torque = -P_force
        I_sub = I - P_d

        #print("d_vec: ")
        #print(d_vec)
        #print("P_d: ")
        #print(P_d)
        #print("P_torque: ")
        #print(P_torque)
        #print("P_force: ")
        #print(P_force)

        def matrix_inject(ports1, ports2, matrix):
            for idx1, port1 in enumerate(ports1):
                for idx2, port2 in enumerate(ports2):
                    for idx, kfrom in enumerate(matrix_algorithm.port_set_get(port1.i)):
                        cplg = matrix[idx1, idx2]
                        if np.any(cplg != 0):
                            #if idx == 0:
                            #    print(port1.i, port2.o, cplg)
                            matrix_algorithm.port_coupling_insert(
                                port1.i,
                                kfrom,
                                port2.o,
                                kfrom,
                                cplg,
                            )
        #    [d**2, 2   , +2*d],
        #    [2   , d**2, -2*d],
        #    [2*d , -2*d, -d**2 + 2],
        den = d**2 + 2

        matrix_inject(A_ports, A_ports, d**2/den * I_sub)
        matrix_inject(B_ports, B_ports, d**2/den * I_sub)
        matrix_inject(L_ports, L_ports, (2-d**2)/den * I_sub + P_d)

        matrix_inject(A_ports, L_ports, 2*d/den * P_torque)
        matrix_inject(L_ports, A_ports, 2*d/den * P_force)

        matrix_inject(B_ports, L_ports, -2*d/den * P_torque)
        matrix_inject(L_ports, B_ports, -2*d/den * P_force)

        matrix_inject(A_ports, B_ports, 2/den * I_sub + P_d)
        matrix_inject(B_ports, A_ports, 2/den * I_sub + P_d)
        print("NEW! 2")
        return


class Moment1D(elements.Mechanical1PortBase):
    @declarative.dproperty
    def L(self):
        return ports.MechanicalPort()

    @declarative.dproperty
    def A(self):
        return ports.MechanicalPort()

    @declarative.dproperty
    def B(self):
        return ports.MechanicalPort()

    @declarative.dproperty
    def displacement(self, X):
        return X

    def system_setup_ports(self, ports_algorithm):
        all_ports = [self.A, self.B, self.L]
        for port1 in all_ports:
            for port2 in all_ports:
                for kfrom in ports_algorithm.port_update_get(port1.i):
                    ports_algorithm.port_coupling_needed(port2.o, kfrom)
                for kto in ports_algorithm.port_update_get(port2.o):
                    ports_algorithm.port_coupling_needed(port1.i, kto)
        return

    @declarative.dproperty
    def type(self, val = 0):
        return val

    def system_setup_coupling(self, matrix_algorithm):
        d = self.displacement
        ports = [self.A, self.B, self.L]
        den = d**2 + 2
        matrix = 1/den * np.array([
            [d**2, 2   , +2*d],
            [2   , d**2, -2*d],
            [2*d , -2*d, -d**2 + 2],
        ])

        def matrix_inject(ports1, ports2, matrix):
            for idx1, port1 in enumerate(ports1):
                for idx2, port2 in enumerate(ports2):
                    for kfrom in matrix_algorithm.port_set_get(port1.i):
                        cplg = matrix[idx1, idx2]
                        if np.any(cplg != 0):
                            matrix_algorithm.port_coupling_insert(
                                port1.i,
                                kfrom,
                                port2.o,
                                kfrom,
                                cplg,
                            )
        matrix_inject(ports, ports, matrix)
        return

class MomentDriver(elements.Mechanical1PortBase):
    @declarative.dproperty
    def L(self):
        return ports.MechanicalXYZPort(
            X = self.Lx,
            Y = self.Ly,
            Z = self.Lz,
        )

    #TODO temporary fix, remove
    @declarative.dproperty
    def Lx(self):
        return ports.MechanicalPort()

    #TODO temporary fix, remove
    @declarative.dproperty
    def Ly(self):
        return ports.MechanicalPort()

    #TODO temporary fix, remove
    @declarative.dproperty
    def Lz(self):
        return ports.MechanicalPort()

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

        P_force = -1/vLsq**.5 * np.array([
            [-d_vec[2] * v_vec[1] + d_vec[1] * v_vec[2]],
            [+d_vec[2] * v_vec[0] - d_vec[0] * v_vec[2]],
            [-d_vec[1] * v_vec[0] + d_vec[0] * v_vec[1]]
        ])

        P_torque = P_force.T / dLsq

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
        matrix_inject(A_ports, A_ports, np.array([[0]]))
        matrix_inject(L_ports, L_ports, P_X)
        matrix_inject(A_ports, L_ports, P_torque)
        matrix_inject(L_ports, A_ports, P_force)
        return
