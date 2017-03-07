# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
import numpy as np

import declarative as decl

from . import ports
from . import bases


class EZSqz(
        bases.OpticalCouplerBase,
        bases.SystemElementBase,
):
    """
    Defaults to squeezing amplitude quadrature, the two_photon matrix is chosen to be
    [nonlinear_field_gain_1 -nonlinear_field_gain_2]
    [-nonlinear_field_gain_2 nonlinear_field_gain_1]
    which squeezes the _1 (usually amplitude) quadrature
    """
    def __init__(
            self,
            Fkey_QC_center,
            nonlinear_power_gain            = None,
            nonlinear_field_gain            = None,
            phi_sqz_deg                     = 0,
            **kwargs
    ):
        super(EZSqz, self).__init__(**kwargs)

        #TODO, actually respect this variable
        bases.OOA_ASSIGN(self).phi_sqz_deg = phi_sqz_deg

        if self.use_parameter == 'nonlinear_power_gain':
            bases.OOA_ASSIGN(self).nonlinear_power_gain = nonlinear_power_gain
            if loss is None:
                loss = 0
            bases.OOA_ASSIGN(self).loss                 = loss
            nonlinear_field_gain_1 = np.sqrt(self.nonlinear_power_gain)
            nonlinear_field_gain_2 = np.sqrt(self.nonlinear_power_gain - 1)
        elif self.use_parameter == 'nonlinear_field_gain':
            bases.OOA_ASSIGN(self).nonlinear_field_gain = nonlinear_field_gain
            if loss is None:
                loss = 0
            bases.OOA_ASSIGN(self).loss                 = loss
            nonlinear_field_gain_1 = self.nonlinear_field_gain
            nonlinear_power_gain   = nonlinear_field_gain_1**2
            nonlinear_field_gain_2 = np.sqrt(nonlinear_power_gain - 1)

        self.used_nonlinear_field_gain_1          = nonlinear_field_gain_1
        self.used_nonlinear_field_gain_2          = nonlinear_field_gain_2

        self.Fkey_QC_center = Fkey_QC_center

        self.Fr   = ports.OpticalPort(sname = 'Fr' )
        self.Bk   = ports.OpticalPort(sname = 'Bk' )
        self._LFr = ports.OpticalPort(sname = 'LFr')
        self._LBk = ports.OpticalPort(sname = 'LBk')
        return

    @decl.mproperty
    def ports_optical(self):
        return (
            self.Fr,
            self.Bk,
        )

    @decl.mproperty
    def ports_optical_loss(self):
        return (
            self._LFr,
            self._LBk,
        )

    def system_setup_ports(self, ports_algorithm):
        tmap = {
            self.Fr: self.Bk,
            self.Bk: self.Fr,
        }

        lmap = {
            self.Fr: self._LFr,
            self.Bk: self._LBk,
            self._LFr: self.Fr,
            self._LBk: self.Bk,
        }
        #direct couplings
        okey = self.Fkey_QC_center[ports.OpticalFreqKey]
        ckey = self.Fkey_QC_center[ports.ClassicalFreqKey]

        for port in self.ports_optical:
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(tmap[port].o, kfrom)
                ports_algorithm.port_coupling_needed(lmap[port].o, kfrom)

                if kfrom[ports.OpticalFreqKey] != okey:
                    continue
                kckey = kfrom[ports.ClassicalFreqKey]
                reflected_SB = 2*ckey - kckey
                if kfrom.contains(ports.LOWER):
                    ktoR = kfrom.replace_keys({ports.ClassicalFreqKey: reflected_SB}, ports.RAISE)
                elif kfrom.contains(ports.RAISE):
                    ktoR = kfrom.replace_keys({ports.ClassicalFreqKey: reflected_SB}, ports.LOWER)

                ports_algorithm.port_coupling_needed(tmap[port].o, ktoR)
            for kto in ports_algorithm.port_update_get(port.o):
                ports_algorithm.port_coupling_needed(tmap[port].i, kto)
                ports_algorithm.port_coupling_needed(lmap[port].i, kto)

                if kto[ports.OpticalFreqKey] != okey:
                    continue
                kckey = kto[ports.ClassicalFreqKey]
                reflected_SB = 2*ckey - kckey
                if kto.contains(ports.LOWER):
                    kfromR = kto.replace_keys({ports.ClassicalFreqKey: reflected_SB}, ports.RAISE)
                elif kto.contains(ports.RAISE):
                    kfromR = kto.replace_keys({ports.ClassicalFreqKey: reflected_SB}, ports.LOWER)
                ports_algorithm.port_coupling_needed(tmap[port].i, kfromR)
        return

    def system_setup_coupling(self, matrix_algorithm):
        lR = self.symbols.math.sqrt(self.used_loss)
        lT = self.symbols.math.sqrt(1 - self.used_loss)
        tmap = {
            self.Fr: self.Bk,
            self.Bk: self.Fr,
        }

        lmap = {
            self.Fr  : self._LFr,
            self.Bk  : self._LBk,
            self._LFr: self.Fr  ,
            self._LBk: self.Bk  ,
        }

        okey = self.Fkey_QC_center[ports.OpticalFreqKey]
        ckey = self.Fkey_QC_center[ports.ClassicalFreqKey]

        for port in self.ports_optical:
            for kfrom in matrix_algorithm.port_set_get(port.i):
                if kfrom[ports.OpticalFreqKey] != okey:
                    continue
                kckey = kfrom[ports.ClassicalFreqKey]
                reflected_SB = 2*ckey - kckey
                #if self.system.reject_classical_frequency_order(reflected_SB):
                #    continue
                if kfrom.contains(ports.LOWER):
                    ktoR = kfrom.replace_keys({ports.ClassicalFreqKey: reflected_SB}, ports.RAISE)
                    phi_cplC = self.symbols.math.exp(2 * -self.symbols.i2pi * self.phi_sqz_deg / 360)
                elif kfrom.contains(ports.RAISE):
                    ktoR = kfrom.replace_keys({ports.ClassicalFreqKey: reflected_SB}, ports.LOWER)
                    phi_cplC = self.symbols.math.exp(2 * self.symbols.i2pi * self.phi_sqz_deg / 360)

                pto = tmap[port]
                cplg1 = self.used_nonlinear_field_gain_1 * self.symbols.math.sqrt(1 - self.used_loss)
                cplg2 = phi_cplC * self.used_nonlinear_field_gain_2 * self.symbols.math.sqrt(1 - self.used_loss)
                matrix_algorithm.port_coupling_insert(
                    port.i,
                    kfrom,
                    pto.o,
                    kfrom,
                    cplg1,
                )
                matrix_algorithm.port_coupling_insert(
                    port.i,
                    kfrom,
                    pto.o,
                    ktoR,
                    cplg2,
                )

                #dual loss coupling
                pto = lmap[port]
                matrix_algorithm.port_coupling_insert(
                    port.i,
                    kfrom,
                    pto.o,
                    kfrom,
                    lR,
                )
                matrix_algorithm.port_coupling_insert(
                    pto.i,
                    kfrom,
                    port.o,
                    kfrom,
                    lR,
                )

        #to keep the matrix with loss ports unitary
        for port in self.ports_optical_loss:
            for kfrom in matrix_algorithm.port_set_get(port.i):
                matrix_algorithm.port_coupling_insert(
                    port.i,
                    kfrom,
                    port.o,
                    kfrom,
                    lT,
                )
        return


