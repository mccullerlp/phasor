"""
"""
from __future__ import division, print_function
import numpy as np
import declarative

from ... import optics
from ... import base
from ... import signals
from ... import readouts
from ... import mechanical
from ...utilities.mpl.autoniceplot import mplfigB
#from ... import selftem

from .. import elements


class HTTS_Flag(mechanical.XYZMomentDriver):
    def __build__(self):
        super(HTTS_Flag, self).__build__()
        self.my.FZ = mechanical.ForceSource()
        self.my.FZ.A.bond(self.A.Z)

        self.my.M_teeny = mechanical.XYZMass(mass_kg = 1e-9)
        self.my.M_teeny.A.bond(self.A)

        self.my.dZ = mechanical.DisplacementReadout(
            terminal = self.A.Z,
        )


class HTTS(elements.MechanicalElementBase):

    @declarative.dproperty
    def d_pitch(self, val = .0014 * 1.5):
        return val

    @declarative.dproperty
    def dd_pitch(self, val = .0014):
        return val

    @declarative.dproperty
    def dz_spring(self, val = 0):
        return val

    @declarative.dproperty
    def d_yaw(self, val = .038 * 2):
        return val

    @declarative.dproperty
    def d_yaw_top(self, val = .015 * 2):
        return val

    @declarative.dproperty
    def dd_yaw(self, val = -.0000):
        return val

    @declarative.dproperty
    def COM_kg(self, val = .0885):
        return val

    @declarative.dproperty
    def L_pend_m(self, val = .14):
        return val

    @declarative.dproperty
    def Ld_pend_m(self, val = .001):
        return val

    def __build__(self):
        super(HTTS, self).__build__()
        #tip-tilt displacement test
        self.my.M_com = mechanical.XYZMass(
            mass_kg = self.COM_kg,
        )
        self.my.L1 = mechanical.XYZMoment(
            moment_kgmsq = 1 * np.array([
                30677 / 1e9,
                37696 / 1e9,
                64087 / 1e9,
            ]),
        )

        #halve the effective mass since there are two pendula for the single mass
        k_pendL = (self.COM_kg/2) * 9.81 / (self.L_pend_m - self.Ld_pend_m/2) + 0
        k_pendR = (self.COM_kg/2) * 9.81 / (self.L_pend_m + self.Ld_pend_m/2) + 0
        k_pend_AS = (1 - self.d_yaw_top/self.d_yaw) * (k_pendL + k_pendR) / 4

        #bounce mode is k_y, set here to be the pendulum k, which is wrong
        self.my.S_left = mechanical.XYZTerminatorSpring(
            elasticity_N_m = [k_pendL, 65.8, k_pendL + self.dz_spring],
        )
        self.my.S_right = mechanical.XYZTerminatorSpring(
            elasticity_N_m = [k_pendR, 65.8, k_pendR - self.dz_spring],
        )
        self.my.S_YAS = mechanical.SeriesSpring(
            elasticity_N_m = -k_pend_AS,
        )
        self.S_YAS.A.bond(self.S_left.A.Z)
        self.S_YAS.B.bond(self.S_right.A.Z)
        self.my.D_left = mechanical.XYZTerminatorDamper(
            resistance_Ns_m = [.01, .01, .004],
        )
        self.D_left.A.bond(self.S_left.A)
        self.my.D_right = mechanical.XYZTerminatorDamper(
            resistance_Ns_m = [.01, .01, .004],
        )
        self.D_right.A.bond(self.S_right.A)
        self.my.Ld_left = mechanical.XYZMomentDriver(
            displacementXYZ = [-self.d_yaw/2 + self.dd_yaw/2, self.d_pitch + self.dd_pitch/2, 0],
        )
        self.my.Ld_left2 = mechanical.XYZMomentDriver(
            displacementXYZ = [-self.d_yaw/2 + self.dd_yaw/2, +self.dd_pitch/2, 0],
        )
        self.Ld_left.A.bond(self.S_left.A)
        self.Ld_left2.A.bond(self.S_left.A)
        self.Ld_left.L.bond(self.L1.L)
        self.my.M_com.A.bond(self.Ld_left.B)

        self.my.Ld_right = mechanical.XYZMomentDriver(
            displacementXYZ = [+self.d_yaw/2 + self.dd_yaw/2, self.d_pitch - self.dd_pitch/2, 0],
        )
        self.Ld_right.A.bond(self.S_right.A)
        self.Ld_right.L.bond(self.L1.L)
        self.my.M_com.A.bond(self.Ld_right.B)
        self.my.Ld_right2 = mechanical.XYZMomentDriver(
            displacementXYZ = [+self.d_yaw/2 + self.dd_yaw/2, -self.dd_pitch/2, 0],
        )
        self.Ld_right2.A.bond(self.S_right.A)

        self.Ld_left2.B.bond(self.Ld_right2.B)
        self.Ld_left2.L.bond(self.Ld_right2.L)
        self.my.L_teeny = mechanical.XYZMoment(moment_kgmsq = 1e-9)
        self.my.L_teeny.L.bond(self.Ld_left2.L)

        self.my.S_p = mechanical.SeriesSpring(
            elasticity_N_m = 9.81 * self.COM_kg / self.d_pitch,
        )
        self.my.S_p.A.bond(self.M_com.Z.A)
        self.my.S_p.B.bond(self.Ld_left2.B.Z)
        self.my.M_teeny = mechanical.XYZMass(mass_kg = 1e-9)
        self.my.M_teeny.A.bond(self.Ld_left2.B)

        self.my.Ld_UL = HTTS_Flag(
            displacementXYZ = [-.0241, .0251, -.0382],
        )
        self.my.Ld_UR = HTTS_Flag(
            displacementXYZ = [+.0241, .0251, -.0382],
        )
        self.my.Ld_LL = HTTS_Flag(
            displacementXYZ = [-.0241, -.0251, -.0382],
        )
        self.my.Ld_LR = HTTS_Flag(
            displacementXYZ = [+.0241, -.0251, -.0382],
        )
        self.Ld_UL.L.bond(self.L1.L)
        self.Ld_UL.B.bond(self.M_com.A)
        self.Ld_UR.L.bond(self.L1.L)
        self.Ld_UR.B.bond(self.M_com.A)
        self.Ld_LL.L.bond(self.L1.L)
        self.Ld_LL.B.bond(self.M_com.A)
        self.Ld_LR.L.bond(self.L1.L)
        self.Ld_LR.B.bond(self.M_com.A)

        self.my.F_L = mechanical.ForceSource()
        self.my.F_L.A.bond(self.M_com.Z.A)

        self.my.F_P = mechanical.ForceSource()
        self.my.F_P.A.bond(self.L1.X.A)

        self.my.F_Y = mechanical.ForceSource()
        self.my.F_Y.A.bond(self.L1.Y.A)

        self.my.R_L = mechanical.DisplacementReadout(
            terminal = self.M_com.A.Z,
        )
        self.my.R_P = mechanical.DisplacementReadout(
            terminal = self.L1.L.X,
        )
        self.my.R_Y = mechanical.DisplacementReadout(
            terminal = self.L1.L.Y,
        )
        self.my.RAC = base.SystemElementBase()

        ins = dict(
            L = self.F_L.F.i,
            P = self.F_P.F.i,
            Y = self.F_Y.F.i,
            UL = self.Ld_UL.FZ.F.i,
            UR = self.Ld_UR.FZ.F.i,
            LL = self.Ld_LL.FZ.F.i,
            LR = self.Ld_LR.FZ.F.i,
        )
        outs = dict(
            L = self.R_L.d.o,
            P = self.R_P.d.o,
            Y = self.R_Y.d.o,
            UL = self.Ld_UL.dZ.d.o,
            UR = self.Ld_UR.dZ.d.o,
            LL = self.Ld_LL.dZ.d.o,
            LR = self.Ld_LR.dZ.d.o,
        )
        for Iname, Iobj in ins.items():
            for Oname, Oobj in outs.items():
                obj = readouts.ACReadout(
                    portD = Iobj,
                    portN = Oobj,
                )
                self.RAC.insert(obj, '{0}_{1}'.format(Iname, Oname))
