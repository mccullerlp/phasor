# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import declarative as decl

from . import bases
from . import ports

from .mirror import Mirror
from .selective_mirrors import PolarizingMirror
from . import standard_attrs


class BaseRotator(
        bases.OpticalCouplerBase,
        bases.SystemElementBase
):
    @decl.dproperty
    def po_Fr(self):
        return ports.OpticalPort(sname = 'po_Fr' , pchain = 'po_Bk')

    @decl.dproperty
    def po_Bk(self):
        return ports.OpticalPort(sname = 'po_Bk' , pchain = 'po_Fr')

    _rotate_default = ('rotate_deg', 0)
    rotate = standard_attrs.generate_rotate()

    @decl.mproperty
    def ports_optical(self):
        return [
            self.po_Fr,
            self.po_Bk,
        ]

    @decl.mproperty
    def pmap(self):
        return {
            self.po_Fr : self.po_Bk,
            self.po_Bk : self.po_Fr,
        }

    def system_setup_ports(self, ports_algorithm):
        if self.rotate_deg.val in (0, 180, -180):
            for port in self.ports_optical:
                for kfrom in ports_algorithm.port_update_get(port.i):
                    ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom)
                for kto in ports_algorithm.port_update_get(port.o):
                    ports_algorithm.port_coupling_needed(self.pmap[port].i, kto)
        elif self.rotate_deg.val in (90, -90, 270, -270):
            for port in self.ports_optical:
                for kfrom in ports_algorithm.port_update_get(port.i):
                    if kfrom & ports.PolS:
                        ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom.replace_keys(ports.PolP))
                    elif kfrom & ports.PolP:
                        ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom.replace_keys(ports.PolS))
                for kto in ports_algorithm.port_update_get(port.o):
                    if kto & ports.PolS:
                        ports_algorithm.port_coupling_needed(self.pmap[port].i, kto.replace_keys(ports.PolP))
                    elif kto & ports.PolP:
                        ports_algorithm.port_coupling_needed(self.pmap[port].i, kto.replace_keys(ports.PolS))
        else:
            for port in self.ports_optical:
                for kfrom in ports_algorithm.port_update_get(port.i):
                    ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom.replace_keys(ports.PolS))
                    ports_algorithm.port_coupling_needed(self.pmap[port].o, kfrom.replace_keys(ports.PolP))
                for kto in ports_algorithm.port_update_get(port.o):
                    ports_algorithm.port_coupling_needed(self.pmap[port].i, kto.replace_keys(ports.PolS))
                    ports_algorithm.port_coupling_needed(self.pmap[port].i, kto.replace_keys(ports.PolP))
        return

    def system_setup_coupling(self, matrix_algorithm):
        if self.rotate_deg.val in (0, 180, -180):
            if self.rotate_deg.val == 0:
                cplg = 1
            elif self.rotate_deg.val in (180, -180):
                cplg = -1
            for port in self.ports_optical:
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    matrix_algorithm.port_coupling_insert(port.i, kfrom, self.pmap[port].o, kfrom, cplg)
        elif self.rotate_deg.val in (90, -90, 270, -270):
            if self.rotate_deg.val in (90, -270):
                cplg_O = 1
            elif self.rotate_deg.val in (-90, 270):
                cplg_O = -1
            for port in self.ports_optical:
                if port is self.po_Fr:
                    cplg = cplg_O
                else:
                    cplg = -cplg_O
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & ports.PolS:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(ports.PolP),
                            cplg,
                        )
                    elif kfrom & ports.PolP:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(ports.PolS),
                            -cplg,
                        )
        else:
            cplgC = self.symbols.math.cos(self.rotate_deg.val / 180 * self.symbols.pi)
            cplgS_O = self.symbols.math.sin(self.rotate_deg.val / 180 * self.symbols.pi)
            for port in self.ports_optical:
                if port is self.po_Fr:
                    cplgS = cplgS_O
                else:
                    cplgS = -cplgS_O
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & ports.PolS:
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
                            kfrom.replace_keys(ports.PolP),
                            cplgS,
                        )
                    elif kfrom & ports.PolP:
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
                            kfrom.replace_keys(ports.PolS),
                            -cplgS,
                        )
        return


class PolarizationRotator(
        BaseRotator
):
    def system_setup_coupling(self, matrix_algorithm):
        if self.rotate_deg.val in (0, 180, -180):
            if self.rotate_deg.val == 0:
                cplg = 1
            elif self.rotate_deg.val in (180, -180):
                cplg = -1
            for port in self.ports_optical:
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    matrix_algorithm.port_coupling_insert(port.i, kfrom, self.pmap[port].o, kfrom, cplg)
        elif self.rotate_deg.val in (90, -90, 270, -270):
            if self.rotate_deg.val in (90, -270):
                cplg_O = 1
            elif self.rotate_deg.val in (-90, 270):
                cplg_O = -1
            for port in self.ports_optical:
                if port is self.po_Fr:
                    cplg = cplg_O
                else:
                    cplg = -cplg_O
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & ports.PolS:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(ports.PolP),
                            cplg,
                        )
                    elif kfrom & ports.PolP:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(ports.PolS),
                            -cplg,
                        )
        else:
            cplgC = self.symbols.math.cos(self.rotate_deg.val / 180 * self.symbols.pi)
            cplgS_O = self.symbols.math.sin(self.rotate_deg.val / 180 * self.symbols.pi)
            for port in self.ports_optical:
                if port is self.po_Fr:
                    cplgS = cplgS_O
                else:
                    cplgS = -cplgS_O
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & ports.PolS:
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
                            kfrom.replace_keys(ports.PolP),
                            cplgS,
                        )
                    elif kfrom & ports.PolP:
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
                            kfrom.replace_keys(ports.PolS),
                            -cplgS,
                        )
        return


class FaradayRotator(
        BaseRotator
):
    def system_setup_coupling(self, matrix_algorithm):
        if self.rotate_deg.val in (0, 180, -180):
            if self.rotate_deg.val == 0:
                cplg = 1
            elif self.rotate_deg.val in (180, -180):
                cplg = -1
            for port in self.ports_optical:
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    matrix_algorithm.port_coupling_insert(port.i, kfrom, self.pmap[port].o, kfrom, cplg)
        elif self.rotate_deg.val in (90, -90, 270, -270):
            if self.rotate_deg.val in (90, -270):
                cplg = 1
            elif self.rotate_deg.val in (-90, 270):
                cplg = -1
            for port in self.ports_optical:
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & ports.PolS:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(ports.PolP),
                            cplg,
                        )
                    elif kfrom & ports.PolP:
                        matrix_algorithm.port_coupling_insert(
                            port.i,
                            kfrom,
                            self.pmap[port].o,
                            kfrom.replace_keys(ports.PolS),
                            -cplg,
                        )
        else:
            cplgC = self.symbols.math.cos(self.rotate_deg.val / 180 * self.symbols.pi)
            cplgS = self.symbols.math.sin(self.rotate_deg.val / 180 * self.symbols.pi)
            for port in self.ports_optical:
                for kfrom in matrix_algorithm.port_set_get(port.i):
                    if kfrom & ports.PolS:
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
                            kfrom.replace_keys(ports.PolP),
                            cplgS,
                        )
                    elif kfrom & ports.PolP:
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
                            kfrom.replace_keys(ports.PolS),
                            -cplgS,
                        )
        return

class WavePlate(
        bases.OpticalCouplerBase,
        bases.SystemElementBase
):
    def __init__(
            self,
            cplgP  = 1,
            cplgPC = None,
            cplgS  = 1,
            cplgSC = None,
            **kwargs
    ):
        #TODO Make these generic properties
        super(WavePlate, self).__init__(**kwargs)

        bases.PTREE_ASSIGN(self).cplgP  = cplgP
        if cplgPC is None:
            cplgPC = self.cplgP.conjugate()
        bases.PTREE_ASSIGN(self).cplgPC = cplgPC
        bases.PTREE_ASSIGN(self).cplgS  = cplgS
        if cplgSC is None:
            cplgSC = self.cplgS.conjugate()
        bases.PTREE_ASSIGN(self).cplgSC = cplgSC

    @decl.dproperty
    def po_Fr(self):
        return ports.OpticalPort(sname = 'po_Fr')

    @decl.dproperty
    def po_Bk(self):
        return ports.OpticalPort(sname = 'po_Bk')

    @decl.mproperty
    def ports_optical(self):
        return [
            self.po_Fr,
            self.po_Bk,
        ]

    @decl.mproperty
    def pmap(self):
        return {
            self.po_Fr : self.po_Bk,
            self.po_Bk : self.po_Fr,
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
                if kfrom & ports.PolS:
                    if ports.LOWER & kfrom:
                        cplgS = self.cplgS
                    elif ports.RAISE & kfrom:
                        cplgS = self.cplgSC
                    matrix_algorithm.port_coupling_insert(
                        port.i,
                        kfrom,
                        self.pmap[port].o,
                        kfrom,
                        cplgS,
                    )
                elif kfrom & ports.PolP:
                    if ports.LOWER & kfrom:
                        cplgP = self.cplgP
                    elif ports.RAISE & kfrom:
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
            cplgP  = 1j,  # #TODO, use global/system ps_In
            **kwargs
        )


class UnmountedHalfWavePlate(WavePlate):
    def __init__(self, **kwargs):
        super(UnmountedHalfWavePlate, self).__init__(
            cplgS  = 1,
            cplgP  = -1,
            **kwargs
        )

class WavePlateMount(
        bases.OpticalCouplerBase,
        bases.SystemElementBase,
):
    _rotate_default = ('rotate_deg', 0)
    rotate = standard_attrs.generate_rotate()

    @decl.dproperty
    def plate(self, sled):
        return sled

    def __init__(
        self,
        **kwargs
    ):
        super(WavePlateMount, self).__init__(**kwargs)

        self.own.coord_Fr = PolarizationRotator(rotate =  self.rotate)
        self.own.coord_Bk = PolarizationRotator(rotate = -self.rotate)

        self.system.bond(self.coord_Fr.po_Bk, self.plate.po_Fr)
        self.system.bond(self.plate.po_Bk, self.coord_Bk.po_Fr)

        self.own.po_Fr = ports.PortIndirect(inner_port = self.coord_Fr.po_Fr, pchain = lambda : self.po_Bk)
        self.own.po_Bk = ports.PortIndirect(inner_port = self.coord_Bk.po_Bk, pchain = lambda : self.po_Fr)


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
        self.__init_ctree__(**kwargs)
        bases.PTREE_ASSIGN(self).pass_polarization = pass_polarization
        bases.PTREE_ASSIGN(self).selection_defect  = selection_defect
        bases.PTREE_ASSIGN(self).rejection_defect  = rejection_defect
        bases.PTREE_ASSIGN(self).select_loss       = select_loss
        bases.PTREE_ASSIGN(self).reject_loss       = reject_loss

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
