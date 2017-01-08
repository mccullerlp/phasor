# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print
import numpy as np

from declarative import (
    mproperty,
)

from .bases import (
    OpticalCouplerBase,
    SystemElementBase,
    OOA_ASSIGN,
)

from .ports import (
    OpticalPortHolderInOut,
    OpticalSymmetric2PortMixin,
    ClassicalFreqKey,
    OpticalFreqKey,
    RAISE, LOWER,
)


class EZSqz(OpticalSymmetric2PortMixin, OpticalCouplerBase, SystemElementBase):
    """
    Defaults to squeezing amplitude quadrature, the two_photon matrix is chosen to be
    [nonlinear_field_gain_1 -nonlinear_field_gain_2]
    [-nonlinear_field_gain_2 nonlinear_field_gain_1]
    which squeezes the _1 (usually amplitude) quadrature
    """
    def __init__(
            self,
            Fkey_QC_center,
            loss                            = None,
            nonlinear_power_gain            = None,
            nonlinear_field_gain            = None,
            normalized_nonlinear_field_gain = None,
            rel_variance_1                  = None,
            rel_variance_2                  = None,
            sqzDB                           = None,
            antisqzDB                       = None,
            phi_sqz_deg                     = 0,
            **kwargs
    ):
        super(EZSqz, self).__init__(**kwargs)

        check_all = set([
            nonlinear_power_gain           ,
            nonlinear_field_gain           ,
            normalized_nonlinear_field_gain,
            rel_variance_1                 ,
            rel_variance_2                 ,
            sqzDB                          ,
            antisqzDB                      ,
        ])
        if nonlinear_power_gain is not None:
            assert all(x is None for x in (check_all - set([nonlinear_power_gain, loss])))
            use_parameter = 'nonlinear_power_gain'
        elif nonlinear_field_gain is not None:
            assert all(x is None for x in (check_all - set([nonlinear_field_gain, loss])))
            use_parameter = 'nonlinear_field_gain'
        elif normalized_nonlinear_field_gain is not None:
            assert all(x is None for x in (check_all - set([normalized_nonlinear_field_gain, loss])))
            use_parameter = 'normalized_nonlinear_field_gain'
        elif rel_variance_1 is not None:
            assert all(x is None for x in (check_all - set([rel_variance_1, rel_variance_2])))
            use_parameter = 'rel_variance'
        elif sqzDB is not None:
            assert all(x is None for x in (check_all - set([sqzDB, antisqzDB])))
            use_parameter = 'sqzDB'
        else:
            raise RuntimeError("Must specify some squeezing parameter")

        #TODO, actually respect this variable
        OOA_ASSIGN(self).phi_sqz_deg = phi_sqz_deg

        OOA_ASSIGN(self).use_parameter = use_parameter

        if self.use_parameter == 'nonlinear_power_gain':
            subtype = 'gain'
            OOA_ASSIGN(self).nonlinear_power_gain = nonlinear_power_gain
            if loss is None:
                loss = 0
            OOA_ASSIGN(self).loss                 = loss
            nonlinear_field_gain_1 = np.sqrt(self.nonlinear_power_gain)
            nonlinear_field_gain_2 = np.sqrt(self.nonlinear_power_gain - 1)
            normalized_nonlinear_field_gain = 1 - 1/nonlinear_field_gain_1
        elif self.use_parameter == 'nonlinear_field_gain':
            subtype = 'gain'
            OOA_ASSIGN(self).nonlinear_field_gain = nonlinear_field_gain
            if loss is None:
                loss = 0
            OOA_ASSIGN(self).loss                 = loss
            nonlinear_field_gain_1 = self.nonlinear_field_gain
            nonlinear_power_gain   = nonlinear_field_gain_1**2
            nonlinear_field_gain_2 = np.sqrt(nonlinear_power_gain - 1)
            normalized_nonlinear_field_gain = 1 - 1/nonlinear_field_gain_1
        elif self.use_parameter == 'normalized_nonlinear_field_gain':
            subtype = 'gain'
            OOA_ASSIGN(self).normalized_nonlinear_field_gain = normalized_nonlinear_field_gain
            if loss is None:
                loss = 0
            OOA_ASSIGN(self).loss                 = loss
            nonlinear_field_gain = 1/(1 - normalized_nonlinear_field_gain)
            nonlinear_field_gain_1 = nonlinear_field_gain
            nonlinear_power_gain = nonlinear_field_gain_1**2
            nonlinear_field_gain_2 = np.sqrt(nonlinear_power_gain - 1)
        elif self.use_parameter == 'rel_variance':
            subtype = 'variance'
            if rel_variance_2 is None:
                rel_variance_2 = 1/rel_variance_1
                loss = 0
            else:
                loss = (1 - rel_variance_1 * rel_variance_2) / (2 - rel_variance_1 - rel_variance_2)

            sqzDB     = -10 * np.log(rel_variance_1) / np.log(10)
            antisqzDB = +10 * np.log(rel_variance_2) / np.log(10)
        elif self.use_parameter == 'sqzDB':
            subtype = 'variance'
            OOA_ASSIGN(self).sqzDB = sqzDB
            if antisqzDB is None:
                antisqzDB = self.sqzDB
            OOA_ASSIGN(self).antisqzDB = antisqzDB
            rel_variance_1 = 10**(-self.sqzDB    / 10)
            rel_variance_2 = 10**(self.antisqzDB / 10)
        else:
            raise RuntimeError("Must specify some squeezing parameter")

        if subtype == 'gain':
            print("ASDASD", self.loss)
            rel_variance_1 = (1 - self.loss) * (nonlinear_field_gain_1 - nonlinear_field_gain_2)**2 + self.loss
            rel_variance_2 = (1 - self.loss) * (nonlinear_field_gain_1 + nonlinear_field_gain_2)**2 + self.loss
            sqzDB     = -10 * np.log(rel_variance_1) / np.log(10)
            antisqzDB = +10 * np.log(rel_variance_2) / np.log(10)
            #Xloss = (1 - rel_variance_1 * rel_variance_2) / (2 - rel_variance_1 - rel_variance_2)
            #print('loss check', loss, Xloss)
            #V_d = (rel_variance_1 - 1) / (rel_variance_2 - 1) - (rel_variance_2 - 1) / (rel_variance_1 - 1)
            #Xnonlinear_power_gain = (2 + np.sqrt(4 + V_d**2))/4
            #print('Power Check', self.nonlinear_power_gain, Xnonlinear_power_gain)
        elif subtype == 'variance':
            V_d = (rel_variance_1 - 1) / (rel_variance_2 - 1) - (rel_variance_2 - 1) / (rel_variance_1 - 1)
            nonlinear_power_gain = (2 + np.sqrt(4 + V_d**2))/4
            nonlinear_field_gain_1 = np.sqrt(nonlinear_power_gain)
            nonlinear_field_gain_2 = np.sqrt(nonlinear_power_gain - 1)
            normalized_nonlinear_field_gain = 1 - 1/nonlinear_field_gain_1
            loss = (1 - rel_variance_1 * rel_variance_2) / (2 - rel_variance_1 - rel_variance_2)
            #Xrel_variance_1 = (1 - loss) * (nonlinear_field_gain_1 - nonlinear_field_gain_2)**2 + loss
            #Xrel_variance_2 = (1 - loss) * (nonlinear_field_gain_1 + nonlinear_field_gain_2)**2 + loss
            #print(rel_variance_1 , Xrel_variance_1)
            #print(rel_variance_2 , Xrel_variance_2)

        OOA_ASSIGN(self).nonlinear_power_gain            = nonlinear_power_gain
        OOA_ASSIGN(self).nonlinear_field_gain            = nonlinear_field_gain_1
        OOA_ASSIGN(self).normalized_nonlinear_field_gain = normalized_nonlinear_field_gain
        OOA_ASSIGN(self).loss                            = loss
        OOA_ASSIGN(self).rel_variance_1                  = rel_variance_1
        OOA_ASSIGN(self).rel_variance_2                  = rel_variance_2
        OOA_ASSIGN(self).sqzDB                           = sqzDB
        OOA_ASSIGN(self).antisqzDB                       = antisqzDB

        self.used_nonlinear_power_gain            = nonlinear_power_gain
        self.used_nonlinear_field_gain_1          = nonlinear_field_gain_1
        self.used_nonlinear_field_gain_2          = nonlinear_field_gain_2
        self.used_normalized_nonlinear_field_gain = normalized_nonlinear_field_gain
        self.used_loss                            = loss
        self.used_rel_variance_1                  = rel_variance_1
        self.used_rel_variance_2                  = rel_variance_2
        self.used_sqzDB                           = sqzDB
        self.used_antisqzDB                       = antisqzDB

        self.Fkey_QC_center = Fkey_QC_center

        self.Fr   = OpticalPortHolderInOut(self, x = 'Fr' )
        self.Bk   = OpticalPortHolderInOut(self, x = 'Bk' )
        self._LFr = OpticalPortHolderInOut(self, x = 'LFr')
        self._LBk = OpticalPortHolderInOut(self, x = 'LBk')
        return

    @mproperty
    def ports_optical(self):
        return (
            self.Fr,
            self.Bk,
        )

    @mproperty
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
        okey = self.Fkey_QC_center[OpticalFreqKey]
        ckey = self.Fkey_QC_center[ClassicalFreqKey]

        for port in self.ports_optical:
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(tmap[port].o, kfrom)
                ports_algorithm.port_coupling_needed(lmap[port].o, kfrom)

                if kfrom[OpticalFreqKey] != okey:
                    continue
                kckey = kfrom[ClassicalFreqKey]
                reflected_SB = 2*ckey - kckey
                if kfrom.contains(LOWER):
                    ktoR = kfrom.replace_keys({ClassicalFreqKey: reflected_SB}, RAISE)
                elif kfrom.contains(RAISE):
                    ktoR = kfrom.replace_keys({ClassicalFreqKey: reflected_SB}, LOWER)

                ports_algorithm.port_coupling_needed(tmap[port].o, ktoR)
            for kto in ports_algorithm.port_update_get(port.o):
                ports_algorithm.port_coupling_needed(tmap[port].i, kto)
                ports_algorithm.port_coupling_needed(lmap[port].i, kto)

                if kto[OpticalFreqKey] != okey:
                    continue
                kckey = kto[ClassicalFreqKey]
                reflected_SB = 2*ckey - kckey
                if kto.contains(LOWER):
                    kfromR = kto.replace_keys({ClassicalFreqKey: reflected_SB}, RAISE)
                elif kto.contains(RAISE):
                    kfromR = kto.replace_keys({ClassicalFreqKey: reflected_SB}, LOWER)
                ports_algorithm.port_coupling_needed(tmap[port].i, kfromR)
        return

    def system_setup_coupling(self, matrix_algorithm):
        lR = self.system.math.sqrt(self.used_loss)
        lT = self.system.math.sqrt(1 - self.used_loss)
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

        okey = self.Fkey_QC_center[OpticalFreqKey]
        ckey = self.Fkey_QC_center[ClassicalFreqKey]

        for port in self.ports_optical:
            for kfrom in matrix_algorithm.port_set_get(port.i):
                if kfrom[OpticalFreqKey] != okey:
                    continue
                kckey = kfrom[ClassicalFreqKey]
                reflected_SB = 2*ckey - kckey
                #if self.system.reject_classical_frequency_order(reflected_SB):
                #    continue
                if kfrom.contains(LOWER):
                    ktoR = kfrom.replace_keys({ClassicalFreqKey: reflected_SB}, RAISE)
                    phi_cplC = self.system.math.exp(2 * -self.system.i2pi * self.phi_sqz_deg / 360)
                elif kfrom.contains(RAISE):
                    ktoR = kfrom.replace_keys({ClassicalFreqKey: reflected_SB}, LOWER)
                    phi_cplC = self.system.math.exp(2 * self.system.i2pi * self.phi_sqz_deg / 360)

                pto = tmap[port]
                cplg1 = self.used_nonlinear_field_gain_1 * self.system.math.sqrt(1 - self.used_loss)
                cplg2 = phi_cplC * self.used_nonlinear_field_gain_2 * self.system.math.sqrt(1 - self.used_loss)
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


