# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from phasor.utilities.print import print
import declarative

import numpy as np

from . import bases
from . import ports
from . import standard_attrs


class Mixer(bases.SignalElementBase):

    @declarative.dproperty
    def LO(self):
        return ports.SignalInPort()

    @declarative.dproperty
    def ps_In(self):
        return ports.SignalInPort()

    @declarative.dproperty
    def ps_R_I(self):
        return ports.SignalOutPort()

    @declarative.dproperty
    def ps_R_Q(self):
        return ports.SignalOutPort()

    def system_setup_ports(self, ports_algorithm):
        for kfrom1, kfrom2 in ports_algorithm.symmetric_update(self.LO.i, self.ps_In.i):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kfrom2[ports.ClassicalFreqKey]
            f_new = f1 + f2
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.ps_R_I.o, ports.DictKey({ports.ClassicalFreqKey: f_new}))
            ports_algorithm.port_coupling_needed(self.ps_R_Q.o, ports.DictKey({ports.ClassicalFreqKey: f_new}))
        for kfrom1, kto2 in ports_algorithm.symmetric_update(self.LO.i, [self.ps_R_I.o, self.ps_R_Q.o]):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kto2[ports.ClassicalFreqKey]
            f_new = f2 - f1
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.ps_In.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))
        for kfrom1, kto2 in ports_algorithm.symmetric_update(self.ps_In.i, [self.ps_R_I.o, self.ps_R_Q.o]):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kto2[ports.ClassicalFreqKey]
            f_new = f2 - f1
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.LO.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom1 in matrix_algorithm.port_set_get(self.LO.i):
            for kfrom2 in matrix_algorithm.port_set_get(self.ps_In.i):
                f1 = kfrom1[ports.ClassicalFreqKey]
                f2 = kfrom2[ports.ClassicalFreqKey]
                f_new = f1 + f2
                if self.system.reject_classical_frequency_order(f_new):
                    continue

                freq_LO = self.system.classical_frequency_extract(kfrom1)
                kto = ports.DictKey({ports.ClassicalFreqKey: f_new})

                if not f_new.DC_is():
                    #TODO add inhomogenous term
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.LO.i,  kfrom1),
                        (self.ps_In.i,   kfrom2),
                        (self.ps_R_I.o, kto),
                        1 / 2,
                    )
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.LO.i,  kfrom1),
                        (self.ps_In.i,   kfrom2),
                        (self.ps_R_Q.o, kto),
                        self.symbols.i * np.sign(freq_LO) / 2,
                    )
                else:
                    #TODO add inhomogenous term
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.LO.i,  kfrom1),
                        (self.ps_In.i,   kfrom2),
                        (self.ps_R_I.o, kto),
                        1 / 4,
                    )
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.LO.i,  kfrom1),
                        (self.ps_In.i,   kfrom2),
                        (self.ps_R_Q.o, kto),
                        self.symbols.i * np.sign(freq_LO) / 4,
                    )
        return


class Modulator(bases.SignalElementBase):

    @declarative.dproperty
    def ps_In(self):
        return ports.SignalInPort()

    @declarative.dproperty
    def Mod_amp(self):
        return ports.SignalInPort()

    @declarative.dproperty
    def Mod_phase(self):
        return ports.SignalInPort()

    @declarative.dproperty
    def Mod_freq(self):
        return self.FM2PM.ps_In

    @declarative.dproperty
    def FM2PM(self):
        from .. import signals
        return signals.Integrator()

    @declarative.dproperty
    def FM2PM_setup(self):
        self.FM2PM.ps_Out.bond(self.Mod_phase)
        return

    @declarative.dproperty
    def ps_Out(self):
        return ports.SignalOutPort()

    phase = standard_attrs.generate_rotate(name = 'phase')
    _phase_default = ('phase_rad', 0)

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.ps_In.i):
            ports_algorithm.port_coupling_needed(self.ps_Out.o, kfrom)

        for kto in ports_algorithm.port_update_get(self.ps_Out.o):
            ports_algorithm.port_coupling_needed(self.ps_In.i, kto)

        for kfrom1, kfrom2 in ports_algorithm.symmetric_update(self.ps_In.i, [self.Mod_amp.i, self.Mod_phase.i]):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kfrom2[ports.ClassicalFreqKey]
            f_new = f1 + f2
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.ps_Out.o, ports.DictKey({ports.ClassicalFreqKey: f_new}))

        for kto2, kfrom1 in ports_algorithm.symmetric_update(self.ps_Out.o, self.ps_In.i):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kto2[ports.ClassicalFreqKey]
            f_new = f2 - f1
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.Mod_amp.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))
            ports_algorithm.port_coupling_needed(self.Mod_phase.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))

        for kto2, kfrom1 in ports_algorithm.symmetric_update(self.ps_Out.o, [self.Mod_amp.i, self.Mod_phase.i]):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kto2[ports.ClassicalFreqKey]
            f_new = f2 - f1
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.ps_In.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom1 in matrix_algorithm.port_set_get(self.ps_In.i):
            freq_In = self.system.classical_frequency_extract(kfrom1)
            freq_center_in = self.system.classical_frequency_extract_center(kfrom1[ports.ClassicalFreqKey])
            if freq_center_in > 0:
                cplg = self.symbols.math.exp(self.symbols.i * self.phase_rad.val)
            elif freq_center_in < 0:
                cplg = self.symbols.math.exp(-self.symbols.i * self.phase_rad.val)
            else:
                cplg = 1
            matrix_algorithm.port_coupling_insert(
                self.ps_In.i,  kfrom1,
                self.ps_Out.o, kfrom1,
                cplg
            )
            for kfrom2 in matrix_algorithm.port_set_get(self.Mod_amp.i):
                f1 = kfrom1[ports.ClassicalFreqKey]
                f2 = kfrom2[ports.ClassicalFreqKey]
                f_new = f1 + f2
                if self.system.reject_classical_frequency_order(f_new):
                    continue

                kto = ports.DictKey({ports.ClassicalFreqKey: f_new})

                if not f_new.DC_is():
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.ps_In.i,  kfrom1),
                        (self.Mod_amp.i,   kfrom2),
                        (self.ps_Out.o, kto),
                        cplg / 2,
                    )
                else:
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.ps_In.i,  kfrom1),
                        (self.Mod_amp.i,   kfrom2),
                        (self.ps_Out.o, kto),
                        cplg / 4,
                    )
            for kfrom2 in matrix_algorithm.port_set_get(self.Mod_phase.i):
                f1 = kfrom1[ports.ClassicalFreqKey]
                f2 = kfrom2[ports.ClassicalFreqKey]
                f_new = f1 + f2
                if self.system.reject_classical_frequency_order(f_new):
                    continue

                kto = ports.DictKey({ports.ClassicalFreqKey: f_new})

                if not f_new.DC_is():
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.ps_In.i,  kfrom1),
                        (self.Mod_phase.i,   kfrom2),
                        (self.ps_Out.o, kto),
                        cplg * self.symbols.i * np.sign(freq_In) / 2,
                    )
                else:
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.ps_In.i,  kfrom1),
                        (self.Mod_phase.i,   kfrom2),
                        (self.ps_Out.o, kto),
                        cplg * self.symbols.i * np.sign(freq_In) / 4,
                    )
        return


class Harmonic2Generator(bases.SignalElementBase):

    @declarative.dproperty
    def ps_In(self):
        return ports.SignalInPort()

    @declarative.dproperty
    def ps_Out(self):
        return ports.SignalOutPort()

    def system_setup_ports(self, ports_algorithm):
        for kfrom1 in ports_algorithm.port_update_get(self.ps_In.i):
            for kfrom2 in ports_algorithm.port_full_get(self.ps_In.i):
                f1 = kfrom1[ports.ClassicalFreqKey]
                f2 = kfrom2[ports.ClassicalFreqKey]
                freq_center_f1 = self.system.classical_frequency_extract_center(f1)
                freq_center_f2 = self.system.classical_frequency_extract_center(f2)
                #make sure the frequencies have the same sign
                if freq_center_f1 > 0:
                    if freq_center_f2 < 0:
                        continue
                else:
                    if freq_center_f2 > 0:
                        continue
                f_new = f1 + f2

                if self.system.reject_classical_frequency_order(f_new):
                    continue
                ports_algorithm.port_coupling_needed(self.ps_Out.o, ports.DictKey({ports.ClassicalFreqKey: f_new}))

            for kto in ports_algorithm.port_full_get(self.ps_Out.o):
                f1 = kfrom1[ports.ClassicalFreqKey]
                f2 = kto[ports.ClassicalFreqKey]
                #make sure the frequencies have the same sign
                f_new = f2 - f1

                freq_center_f1 = self.system.classical_frequency_extract_center(f1)
                freq_center_f2 = self.system.classical_frequency_extract_center(f_new)

                if freq_center_f1 > 0:
                    if freq_center_f2 < 0:
                        continue
                else:
                    if freq_center_f2 > 0:
                        continue

                if self.system.reject_classical_frequency_order(f_new):
                    continue

                ports_algorithm.port_coupling_needed(self.ps_In.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))
        for kto in ports_algorithm.port_update_get(self.ps_Out.o):
            for kfrom1 in ports_algorithm.port_full_get(self.ps_In.i):
                f1 = kfrom1[ports.ClassicalFreqKey]
                f2 = kto[ports.ClassicalFreqKey]
                #make sure the frequencies have the same sign
                f_new = f2 - f1

                freq_center_f1 = self.system.classical_frequency_extract_center(f1)
                freq_center_f2 = self.system.classical_frequency_extract_center(f_new)

                if freq_center_f1 > 0:
                    if freq_center_f2 <= 0:
                        continue
                elif freq_center_f1 == 0:
                    continue
                else:
                    if freq_center_f2 >= 0:
                        continue
                if self.system.reject_classical_frequency_order(f_new):
                    continue

                ports_algorithm.port_coupling_needed(self.ps_In.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))
        return

    def system_setup_coupling(self, matrix_algorithm):
        #beware of combinatoric factors for high harmonics

        #so far copied from Mixer
        for kfrom1 in matrix_algorithm.port_set_get(self.ps_In.i):
            for kfrom2 in matrix_algorithm.port_set_get(self.ps_In.i):
                f1 = kfrom1[ports.ClassicalFreqKey]
                f2 = kfrom2[ports.ClassicalFreqKey]
                freq_center_f1 = self.system.classical_frequency_extract_center(f1)
                freq_center_f2 = self.system.classical_frequency_extract_center(f2)
                #make sure the frequencies have the same sign
                if freq_center_f1 > 0:
                    if freq_center_f2 <= 0:
                        continue
                elif freq_center_f1 == 0:
                    continue
                else:
                    if freq_center_f2 >= 0:
                        continue
                f_new = f1 + f2

                if self.system.reject_classical_frequency_order(f_new):
                    continue

                kto = ports.DictKey({ports.ClassicalFreqKey: f_new})

                #TODO add inhomogenous term
                matrix_algorithm.nonlinear_triplet_insert(
                    (self.ps_In.i,  kfrom1),
                    (self.ps_In.i,  kfrom2),
                    (self.ps_Out.o, kto),
                    1,
                )
        return

