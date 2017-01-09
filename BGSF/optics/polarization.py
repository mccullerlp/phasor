# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

from declarative import (
    mproperty,
)

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
    OOA_ASSIGN,
)

from . import ports
from .ports import (
    OpticalPortHolderInOut,
    RAISE, LOWER,
    PolS, PolP,
    OpticalSymmetric2PortMixin,
    #OpticalOriented4PortMixin,
)

from .selective_mirrors import PolarizingMirror
from .mirror import Mirror


class BaseRotator(OpticalCouplerBase, SystemElementBase):
    def __init__(
        self,
        rotate_deg = 0,
        **kwargs
    ):
        super(BaseRotator, self).__init__(**kwargs)
        OOA_ASSIGN(self).rotate_deg = rotate_deg
        self.Fr = OpticalPortHolderInOut(self, x = 'Fr')
        self.Bk = OpticalPortHolderInOut(self, x = 'Bk')
        return

    @mproperty
    def ports_optical(self):
        return [
            self.Fr,
            self.Bk,
        ]

    @mproperty
    def pmap(self):
        return {
            self.Fr : self.Bk,
            self.Bk : self.Fr,
        }

    def system_setup_ports(self, ports_algorithm):
        if self.rotate_deg in (0, 180, -180):
            for port in self.ports_optical:
                for kfrom in ports_algorithm.port_update_get(port.i):
                    ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom)
                for kto in ports_algorithm.port_update_get(port.o):
                    ports_algorithm.port_coupling_needed(self.pmap[port].i, kto)
        elif self.rotate_deg in (90, -90, 270, -270):
            for port in self.ports_optical:
                for kfrom in ports_algorithm.port_update_get(port.i):
                    if kfrom & PolS:
                        ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom.replace_keys(PolP))
                    elif kfrom & PolP:
                        ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom.replace_keys(PolS))
                for kto in ports_algorithm.port_update_get(port.o):
                    if kto & PolS:
                        ports_algorithm.port_coupling_needed(self.pmap[port].i, kto.replace_keys(PolP))
                    elif kto & PolP:
                        ports_algorithm.port_coupling_needed(self.pmap[port].i, kto.replace_keys(PolS))
        else:
            for port in self.ports_optical:
                for kfrom in ports_algorithm.port_update_get(port.i):
                    ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom.replace_keys(PolS))
                    ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom.replace_keys(PolP))
                for kto in ports_algorithm.port_update_get(port.o):
                    ports_algorithm.port_coupling_needed(self.pmap[port].i, kto.replace_keys(PolS))
                    ports_algorithm.port_coupling_needed(self.pmap[port].i, kto.replace_keys(PolP))
        return

    def system_setup_coupling(self, matrix_algorithm):
        if self.rotate_deg in (0, 180, -180):
            if self.rotate_deg == 0:
                cplg = 1
            elif self.rotate_deg in (180, -180):
                cplg = -1
            for port in self.ports_optical:
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    matrix_algorithm.port_coupling_insert(port.i, kfrom, self.pmap[port].o, kfrom, cplg)
        elif self.rotate_deg in (90, -90, 270, -270):
            if self.rotate_deg in (90, -270):
                cplg_O = 1
            elif self.rotate_deg in (-90, 270):
                cplg_O = -1
            for port in self.ports_optical:
                if port is self.Fr:
                    cplg = cplg_O
                else:
                    cplg = -cplg_O
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & PolS:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolP),
                            cplg,
                        )
                    elif kfrom & PolP:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolS),
                            -cplg,
                        )
        else:
            cplgC = self.system.math.cos(self.rotate_deg / 180 * self.system.pi)
            cplgS_O = self.system.math.sin(self.rotate_deg / 180 * self.system.pi)
            for port in self.ports_optical:
                if port is self.Fr:
                    cplgS = cplgS_O
                else:
                    cplgS = -cplgS_O
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & PolS:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom,
                            cplgC,
                        )
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolP),
                            cplgS,
                        )
                    elif kfrom & PolP:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom,
                            cplgC,
                        )
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolS),
                            -cplgS,
                        )
        return


class PolarizationRotator(ports.OpticalOriented2PortMixin, BaseRotator):
    def system_setup_coupling(self, matrix_algorithm):
        if self.rotate_deg in (0, 180, -180):
            if self.rotate_deg == 0:
                cplg = 1
            elif self.rotate_deg in (180, -180):
                cplg = -1
            for port in self.ports_optical:
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    matrix_algorithm.port_coupling_insert(port.i, kfrom, self.pmap[port].o, kfrom, cplg)
        elif self.rotate_deg in (90, -90, 270, -270):
            if self.rotate_deg in (90, -270):
                cplg_O = 1
            elif self.rotate_deg in (-90, 270):
                cplg_O = -1
            for port in self.ports_optical:
                if port is self.Fr:
                    cplg = cplg_O
                else:
                    cplg = -cplg_O
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & PolS:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolP),
                            cplg,
                        )
                    elif kfrom & PolP:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolS),
                            -cplg,
                        )
        else:
            cplgC = self.system.math.cos(self.rotate_deg / 180 * self.system.pi)
            cplgS_O = self.system.math.sin(self.rotate_deg / 180 * self.system.pi)
            for port in self.ports_optical:
                if port is self.Fr:
                    cplgS = cplgS_O
                else:
                    cplgS = -cplgS_O
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & PolS:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom,
                            cplgC,
                        )
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolP),
                            cplgS,
                        )
                    elif kfrom & PolP:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom,
                            cplgC,
                        )
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolS),
                            -cplgS,
                        )
        return


class FaradayRotator(OpticalSymmetric2PortMixin, BaseRotator):
    def system_setup_coupling(self, matrix_algorithm):
        if self.rotate_deg in (0, 180, -180):
            if self.rotate_deg == 0:
                cplg = 1
            elif self.rotate_deg in (180, -180):
                cplg = -1
            for port in self.ports_optical:
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    matrix_algorithm.port_coupling_insert(port.i, kfrom, self.pmap[port].o, kfrom, cplg)
        elif self.rotate_deg in (90, -90, 270, -270):
            if self.rotate_deg in (90, -270):
                cplg = 1
            elif self.rotate_deg in (-90, 270):
                cplg = -1
            for port in self.ports_optical:
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & PolS:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolP),
                            cplg,
                        )
                    elif kfrom & PolP:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolS),
                            -cplg,
                        )
        else:
            cplgC = self.system.math.cos(self.rotate_deg / 180 * self.system.pi)
            cplgS = self.system.math.sin(self.rotate_deg / 180 * self.system.pi)
            for port in self.ports_optical:
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & PolS:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom,
                            cplgC,
                        )
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolP),
                            cplgS,
                        )
                    elif kfrom & PolP:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom,
                            cplgC,
                        )
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(PolS),
                            -cplgS,
                        )
        return

class WavePlate(OpticalSymmetric2PortMixin, OpticalCouplerBase, SystemElementBase):
    def __init__(
            self,
            cplgP  = 1,
            cplgPC = None,
            cplgS  = 1,
            cplgSC = None,
            **kwargs
    ):
        super(WavePlate, self).__init__(**kwargs)

        OOA_ASSIGN(self).cplgP  = cplgP
        if cplgPC is None:
            cplgPC = self.cplgP.conjugate()
        OOA_ASSIGN(self).cplgPC = cplgPC
        OOA_ASSIGN(self).cplgS  = cplgS
        if cplgSC is None:
            cplgSC = self.cplgS.conjugate()
        OOA_ASSIGN(self).cplgSC = cplgSC

        self.Fr = OpticalPortHolderInOut(self, x = 'Fr')
        self.Bk = OpticalPortHolderInOut(self, x = 'Bk')
        return

    @mproperty
    def ports_optical(self):
        return [
            self.Fr,
            self.Bk,
        ]

    @mproperty
    def pmap(self):
        return {
            self.Fr : self.Bk,
            self.Bk : self.Fr,
        }

    def system_setup_ports(self, ports_algorithm):
        for port in self.ports_optical:
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom)
            for kto in ports_algorithm.port_update_get(port.o):
                ports_algorithm.port_coupling_needed(self.pmap[port].i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for port in self.ports_optical:
            for kfrom in matrix_algorithm.port_set_get(port.i):
                if kfrom & PolS:
                    if LOWER & kfrom:
                        cplgS = self.cplgS
                    elif RAISE & kfrom:
                        cplgS = self.cplgSC
                    matrix_algorithm.port_coupling_insert(
                        port.i,
                        kfrom,
                        self.pmap[port].o,
                        kfrom,
                        cplgS,
                    )
                elif kfrom & PolP:
                    if LOWER & kfrom:
                        cplgP = self.cplgP
                    elif RAISE & kfrom:
                        cplgP = self.cplgPC
                    matrix_algorithm.port_coupling_insert(
                        port.i,
                        kfrom,
                        self.pmap[port].o,
                        kfrom,
                        cplgP,
                    )
        return


class UnmountedQuarterWavePlate(WavePlate):
    def __init__(self, **kwargs):
        super(UnmountedQuarterWavePlate, self).__init__(
            cplgS  = 1,
            cplgP  = 1j,  # #TODO, use global/system I
            **kwargs
        )


class UnmountedHalfWavePlate(WavePlate):
    def __init__(self, **kwargs):
        super(UnmountedHalfWavePlate, self).__init__(
            cplgS  = 1,
            cplgP  = -1,
            **kwargs
        )

class WavePlateMount(ports.OpticalOriented2PortMixin, OpticalCouplerBase, SystemElementBase):
    def __init__(
        self,
        plate,
        rotate_deg = 0,
        **kwargs
    ):
        super(WavePlateMount, self).__init__(**kwargs)

        self.plate = plate
        OOA_ASSIGN(self).rotate_deg = rotate_deg
        self.coord_Fr = PolarizationRotator(rotate_deg = self.rotate_deg)
        self.coord_Bk = PolarizationRotator(rotate_deg = -self.rotate_deg)

        self.system.link(self.coord_Fr.Bk, self.plate.Fr)
        self.system.link(self.plate.Bk, self.coord_Bk.Fr)

        self.Fr = self.coord_Fr.Fr
        self.Bk = self.coord_Bk.Bk


class HalfWavePlate(WavePlateMount):
    def __init__(
        self,
        **kwargs
    ):
        super(HalfWavePlate, self).__init__(
            plate = UnmountedHalfWavePlate(),
            **kwargs
        )


class QuarterWavePlate(WavePlateMount):
    def __init__(
        self,
        **kwargs
    ):
        super(QuarterWavePlate, self).__init__(
            plate = UnmountedQuarterWavePlate(),
            **kwargs
        )


class PolarizingBeamsplitter(PolarizingMirror):
    #TODO allow loss
    def __init__(
        self,
        pass_polarization = 'P',
        selection_defect  = 0,
        rejection_defect  = 0,
        select_loss       = 0,
        reject_loss       = 0,
        AOI_deg           = 45,
        **kwargs
    ):
        self.__init_ooa__(**kwargs)
        OOA_ASSIGN(self).pass_polarization = pass_polarization
        OOA_ASSIGN(self).selection_defect  = selection_defect
        OOA_ASSIGN(self).rejection_defect  = rejection_defect
        OOA_ASSIGN(self).select_loss       = select_loss
        OOA_ASSIGN(self).reject_loss       = reject_loss

        select_mirror = Mirror(
            T_hr = 1 - self.selection_defect,
            L_hr = self.reject_loss,
            L_t  = self.select_loss,
        )

        reject_mirror = Mirror(
            T_hr = self.rejection_defect,
            L_hr = self.reject_loss,
            L_t  = self.select_loss,
        )

        if self.pass_polarization.upper() == 'P':
            super(PolarizingBeamsplitter, self).__init__(
                mirror_P = select_mirror,
                mirror_S = reject_mirror,
                AOI_deg  = AOI_deg,
                **kwargs
            )
        elif self.pass_polarization.upper() == 'S':
            super(PolarizingBeamsplitter, self).__init__(
                mirror_S = select_mirror,
                mirror_P = reject_mirror,
                AOI_deg  = AOI_deg,
                **kwargs
            )


def polarization_opposite(pol_str):
    if pol_str.upper() == 'S':
        return 'P'
    elif pol_str.upper() == 'P':
        return 'S'
    return None
