"""
"""
from __future__ import (division, print_function)

import numpy.testing as np_test
import numpy as np
import declarative

#import numpy as np

from OpenLoop import base
from OpenLoop import system
from OpenLoop import readouts
from OpenLoop import optics
from OpenLoop import signals
from OpenLoop.optics.nonlinear_crystal import NonlinearCrystal
from OpenLoop.utilities.print import pprint
from OpenLoop.optics.models import AOMTestStand

#from OpenLoop.utilities.np import logspaced



def test_AOM():
    db = declarative.DeepBunch()
    db.test.LO.phase.val = 0
    db.test.LO.phase.units = 'deg'
    db.test.LO.amplitude = np.linspace(0, 1, 100)
    db.test.aom.N_ode = 100
    db.test.aom.solution_order = 0
    sys = system.BGSystem(
        ooa_params = db,
    )
    sys.my.test = AOMTestStand.AOMTestStand()
    db = sys.ooa_shadow()

    np_test.assert_almost_equal(sys.test.DC_R1.DC_readout, np.cos(sys.test.LO.amplitude * np.pi/2)**2, 2)
    np_test.assert_almost_equal(sys.test.DC_R2.DC_readout, np.sin(sys.test.LO.amplitude * np.pi/2)**2, 2)
    np_test.assert_almost_equal((sys.test.DC_R1.DC_readout + sys.test.DC_R2.DC_readout), 1, 2)

    return sys


def test_AOM_derivative():
    db = declarative.DeepBunch()
    db.test.aoms.AOM1.N_ode = 100
    db.test.aoms.VCO_AOM1.generate.amplitude = np.linspace(.01, 1.2, 14)
    db.test.aoms.VCO_AOM2.generate.amplitude = .01
    db.environment.F_AC.order = 1
    sys = system.BGSystem(
        ooa_params = db,
    )
    sys.my.test = AOMTestStand.AOM2VCOTestStand(
        VCO2_use = True,
    )
    db = sys.ooa_shadow()

    X = sys.test.aoms.VCO_AOM1.generate.amplitude
    Y = sys.test.aoms.VCO_AOM2.generate.amplitude
    np_test.assert_almost_equal(sys.test.DC_R.DC_readout, np.sin(X * np.pi/2)**2, 1)
    np_test.assert_almost_equal(sys.test.DC_RR.DC_readout / X / Y**2, np.pi/4 * np.sin(X * np.pi), 1)
    np_test.assert_almost_equal(sys.test.AC_R.AC_sensitivity / X, sys.test.DC_RR.DC_readout / X / Y**2, 2)

    np_test.assert_almost_equal(sys.test.AC_R_Q_phase.AC_sensitivity / (-.5), 1, 4)
    np_test.assert_almost_equal(sys.test.AC_R_I_phase.AC_sensitivity, 0)
    np_test.assert_almost_equal(sys.test.AC_R_Q_amp.AC_sensitivity, 0)
    np_test.assert_almost_equal((sys.test.AC_R_I_amp.AC_sensitivity),  (X * np.sin(X * np.pi) / np.sin(X * np.pi/2)**2 / 4 * np.pi/2), 1)
    return sys

def test_AOMBasic():
    db = declarative.DeepBunch()
    db.test.LO.phase.val = 0
    db.test.LO.phase.units = 'deg'
    db.test.LO.amplitude = np.linspace(.1, 1, 100)
    sys = system.BGSystem(
        ooa_params = db,
    )
    sys.my.test = AOMTestStand.AOMTestStandBasic()

    sys.my.F_LO2 = base.Frequency(
        F_Hz  = 250e6,
        order = 1,
    )
    sys.my.LO2 = signals.SignalGenerator(
        F         = sys.F_LO2,
        amplitude = 1,
    )
    sys.test.aom.Drv.bond(sys.LO2.Out)

    db = sys.ooa_shadow()

    np_test.assert_almost_equal(sys.test.DC_Drv.DC_readout, (sys.LO2.amplitude**2 + sys.test.LO.amplitude**2)/2, 2)
    np_test.assert_almost_equal(sys.test.DC_R1.DC_readout, 1, 2)

    return sys


def test_AOMBasic_PWR2():
    db = declarative.DeepBunch()
    db.test.LO.phase.val = 0
    db.test.LO.phase.units = 'deg'
    db.test.LO.amplitude = np.linspace(.1, 1, 100)
    sys = system.BGSystem(
        ooa_params = db,
    )
    sys.my.test = AOMTestStand.AOMTestStandBasic()
    db = sys.ooa_shadow()

    np_test.assert_almost_equal(sys.test.DC_Drv.DC_readout, db.test.LO.amplitude**2/2, 2)
    np_test.assert_almost_equal(sys.test.DC_R1.DC_readout, 1, 2)

    return sys


def test_AOMBasic_derivative():
    db = declarative.DeepBunch()
    db.test.aoms.AOM1.N_ode = 100
    db.test.aoms.VCO_AOM1.generate.amplitude = np.linspace(.01, 1.2, 14)
    db.test.aoms.VCO_AOM2.generate.amplitude = .00
    db.environment.F_AC.order = 1
    sys = system.BGSystem(
        ooa_params = db,
    )
    sys.my.test = AOMTestStand.AOM2VCOTestStandBasic(
        VCO2_use = True,
    )
    db = sys.ooa_shadow()

    X = sys.test.aoms.VCO_AOM1.generate.amplitude
    Y = sys.test.aoms.VCO_AOM2.generate.amplitude
    #np_test.assert_almost_equal(sys.test.DC_R.DC_readout, np.sin(X * np.pi/2)**2, 1)
    #np_test.assert_almost_equal(sys.test.DC_RR.DC_readout / X / Y**2, np.pi/4 * np.sin(X * np.pi), 1)
    #np_test.assert_almost_equal(sys.test.AC_R.AC_sensitivity / X, sys.test.DC_RR.DC_readout / X / Y**2, 2)

    np_test.assert_almost_equal(sys.test.AC_R_Q_phase.AC_sensitivity / (-.5), 1, 4)
    np_test.assert_almost_equal(sys.test.AC_R_I_phase.AC_sensitivity, 0)
    np_test.assert_almost_equal(sys.test.AC_R_Q_amp.AC_sensitivity, 0)
    np_test.assert_almost_equal((sys.test.AC_R_I_amp.AC_sensitivity) / (.5), 1, 5)
    return sys

if __name__ == '__main__':
    test_AOM()
