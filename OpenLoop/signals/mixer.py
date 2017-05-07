# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

import numpy as np

from . import bases
from . import ports


class Mixer(bases.SignalElementBase):
    def __build__(self):
        super(Mixer, self).__build__()
        self.my.LO  = ports.SignalInPort(sname = 'LO')
        self.my.I   = ports.SignalInPort(sname = 'I')
        self.my.R_I = ports.SignalOutPort(sname = 'R_I')
        self.my.R_Q = ports.SignalOutPort(sname = 'R_Q')
        return

    def system_setup_ports(self, ports_algorithm):
        for kfrom1, kfrom2 in ports_algorithm.symmetric_update(self.LO.i, self.I.i):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kfrom2[ports.ClassicalFreqKey]
            f_new = f1 + f2
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.R_I.o, ports.DictKey({ports.ClassicalFreqKey: f_new}))
            ports_algorithm.port_coupling_needed(self.R_Q.o, ports.DictKey({ports.ClassicalFreqKey: f_new}))
        for kfrom1, kto2 in ports_algorithm.symmetric_update(self.LO.i, [self.R_I.o, self.R_Q.o]):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kto2[ports.ClassicalFreqKey]
            f_new = f2 - f1
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.I.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))
        for kfrom1, kto2 in ports_algorithm.symmetric_update(self.I.i, [self.R_I.o, self.R_Q.o]):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kto2[ports.ClassicalFreqKey]
            f_new = f2 - f1
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.LO.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom1 in matrix_algorithm.port_set_get(self.LO.i):
            for kfrom2 in matrix_algorithm.port_set_get(self.I.i):
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
                        (self.I.i,   kfrom2),
                        (self.R_I.o, kto),
                        1 / 2,
                    )
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.LO.i,  kfrom1),
                        (self.I.i,   kfrom2),
                        (self.R_Q.o, kto),
                        self.symbols.i * np.sign(freq_LO) / 2,
                    )
                else:
                    #TODO add inhomogenous term
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.LO.i,  kfrom1),
                        (self.I.i,   kfrom2),
                        (self.R_I.o, kto),
                        1 / 4,
                    )
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.LO.i,  kfrom1),
                        (self.I.i,   kfrom2),
                        (self.R_Q.o, kto),
                        self.symbols.i * np.sign(freq_LO) / 4,
                    )
        return


class Modulator(bases.SignalElementBase):
    def __build__(self):
        super(Modulator, self).__build__()
        self.my.In = ports.SignalInPort()
        self.my.Mod_amp   = ports.SignalInPort()
        self.my.Mod_phase = ports.SignalInPort()
        self.my.Out = ports.SignalOutPort()
        return

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.In.i):
            ports_algorithm.port_coupling_needed(self.Out.o, kfrom)

        for kfrom1, kfrom2 in ports_algorithm.symmetric_update(self.In.i, [self.Mod_amp.i, self.Mod_phase.i]):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kfrom2[ports.ClassicalFreqKey]
            f_new = f1 + f2
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.Out.o, ports.DictKey({ports.ClassicalFreqKey: f_new}))

        for kto2, kfrom1 in ports_algorithm.symmetric_update(self.Out.o, self.In.i):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kto2[ports.ClassicalFreqKey]
            f_new = f2 - f1
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.Mod_amp.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))
            ports_algorithm.port_coupling_needed(self.Mod_phase.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))

        for kto2, kfrom1 in ports_algorithm.symmetric_update(self.Out.o, [self.Mod_amp.i, self.Mod_phase.i]):
            f1 = kfrom1[ports.ClassicalFreqKey]
            f2 = kto2[ports.ClassicalFreqKey]
            f_new = f2 - f1
            if self.system.reject_classical_frequency_order(f_new):
                continue
            ports_algorithm.port_coupling_needed(self.In.i, ports.DictKey({ports.ClassicalFreqKey: f_new}))
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom1 in matrix_algorithm.port_set_get(self.In.i):
            freq_In = self.system.classical_frequency_extract(kfrom1)
            matrix_algorithm.port_coupling_insert(
                self.In.i,  kfrom1,
                self.Out.o, kfrom1,
                1
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
                        (self.In.i,  kfrom1),
                        (self.Mod_amp.i,   kfrom2),
                        (self.Out.o, kto),
                        1 / 2,
                    )
                else:
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.In.i,  kfrom1),
                        (self.Mod_amp.i,   kfrom2),
                        (self.Out.o, kto),
                        1 / 4,
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
                        (self.In.i,  kfrom1),
                        (self.Mod_phase.i,   kfrom2),
                        (self.Out.o, kto),
                        self.symbols.i * np.sign(freq_In) / 2,
                    )
                else:
                    matrix_algorithm.nonlinear_triplet_insert(
                        (self.In.i,  kfrom1),
                        (self.Mod_phase.i,   kfrom2),
                        (self.Out.o, kto),
                        self.symbols.i * np.sign(freq_In) / 4,
                    )
        return
