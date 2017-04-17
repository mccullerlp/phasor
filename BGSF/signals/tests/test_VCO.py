"""
"""
from __future__ import (division, print_function)
#import pytest
import declarative
#import numpy as np
import numpy.testing as test

import BGSF.signals as signals
import BGSF.readouts as readouts
import BGSF.system as system
from BGSF import base


class VCOTest(signals.SignalElementBase):
    f_dict = None

    @declarative.dproperty
    def F_AOM1(self):
        val = base.Frequency(
            F_Hz  = 200e6,
            order = 1,
        )
        return val

    @declarative.dproperty
    def generate(self):
        val = signals.SignalGenerator(
            F = self.F_AOM1,
            amplitude = 1,
        )
        return val

    @declarative.dproperty
    def modulate(self):
        val = signals.Modulator()
        return val

    @declarative.dproperty
    def mix(self):
        val = signals.Mixer()
        return val

    @declarative.dproperty
    def AC_I(self, val = None):
        val = readouts.ACReadout(
            portN = self.mix.R_I.o,
            portD  = self.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def AC_IQ(self, val = None):
        val = readouts.ACReadout(
            portN = self.mix.R_Q.o,
            portD  = self.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def AC_QI(self, val = None):
        val = readouts.ACReadout(
            portN = self.mix.R_Q.o,
            portD  = self.modulate.Mod_amp.i,
        )
        return val

    @declarative.dproperty
    def AC_Q(self, val = None):
        val = readouts.ACReadout(
            portN = self.mix.R_Q.o,
            portD  = self.modulate.Mod_phase.i,
        )
        return val

    def __build__(self):
        super(VCOTest, self).__build__()
        self.generate.Out.bond(
            self.modulate.In,
        )
        self.mix.LO.bond(self.generate.Out)
        self.modulate.Out.bond(
            self.mix.I,
        )


def test_VCO():
    db = declarative.DeepBunch()
    db.environment.F_AC.order = 1
    sys = system.BGSystem(
        ooa_params = db,
        F_AC = 1e3,
    )
    sys.my.test = VCOTest()
    db = sys.ooa_shadow()

    print(sys.test.AC_I.AC_sensitivity)
    print(sys.test.AC_Q.AC_sensitivity)
    print(sys.test.AC_IQ.AC_sensitivity)
    print(sys.test.AC_QI.AC_sensitivity)

    test.assert_almost_equal(sys.test.AC_I.AC_sensitivity / 0.5, 1)
    test.assert_almost_equal(sys.test.AC_Q.AC_sensitivity / 0.5, 1)
    test.assert_almost_equal(sys.test.AC_IQ.AC_sensitivity, 0)
    test.assert_almost_equal(sys.test.AC_QI.AC_sensitivity, 0)
    return


if __name__ == '__main__':
    test_VCO()
