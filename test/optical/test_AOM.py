# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import numpy.testing as np_test
import numpy as np
import declarative

#import numpy as np

from phasor import base
from phasor import system
from phasor import readouts
from phasor import optics
from phasor import signals
from phasor.optics.nonlinear_crystal import NonlinearCrystal
from phasor.utilities.print import pprint
from phasor.optics.models import AOMTestStand

#from phasor.utilities.np import logspaced



def test_AOM():
    db = declarative.DeepBunch()
    db.test.LO.phase.val = 0
    db.test.LO.phase.units = 'deg'
    db.test.LO.amplitude = np.linspace(0, 1, 100)
    db.test.aom.N_ode = 100
    db.test.aom.solution_order = 0
    sys = system.BGSystem(
        ctree = db,
    )
    sys.own.test = AOMTestStand.AOMTestStand()
    db = sys.ctree_shadow()

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
        ctree = db,
    )
    sys.own.test = AOMTestStand.AOM2VCOTestStand(
        VCO2_use = True,
    )
    db = sys.ctree_shadow()

    X = sys.test.aoms.VCO_AOM1.generate.amplitude
    Y = sys.test.aoms.VCO_AOM2.generate.amplitude
    np_test.assert_almost_equal(sys.test.DC_R.DC_readout, np.sin(X * np.pi/2)**2, 1)
    np_test.assert_almost_equal(sys.test.DC_RR.DC_readout / X / Y**2, np.pi/4 * np.sin(X * np.pi), 1)
    np_test.assert_almost_equal(sys.test.AC_R.AC_sensitivity / X, sys.test.DC_RR.DC_readout / X / Y**2, 2)

    np_test.assert_almost_equal(sys.test.AC_R_I_phase.AC_sensitivity, 0)
    np_test.assert_almost_equal(sys.test.AC_R_Q_amp.AC_sensitivity, 0)
    np_test.assert_almost_equal((sys.test.AC_R_I_amp.AC_sensitivity),  (X * np.sin(X * np.pi) / np.sin(X * np.pi/2)**2 / 4 * np.pi), 1)


    #can't (and shouldn't!) be able to directly detect phase noise
    np_test.assert_almost_equal(sys.test.AC_R_Q_phase.AC_sensitivity, 0, 4)

    #TODO: add homodyne detector to check that phase noise passes correctly
    return sys

def test_AOMBasic():
    db = declarative.DeepBunch()
    db.test.LO.phase.val = 0
    db.test.LO.phase.units = 'deg'
    db.test.LO.amplitude = np.linspace(.1, 1, 100)
    sys = system.BGSystem(
        ctree = db,
    )
    sys.own.test = AOMTestStand.AOMTestStandBasic()

    sys.own.F_LO2 = base.Frequency(
        F_Hz  = 250e6,
        order = 1,
    )
    sys.own.LO2 = signals.SignalGenerator(
        F         = sys.F_LO2,
        amplitude = 1,
    )
    sys.test.aom.Drv.bond(sys.LO2.ps_Out)

    db = sys.ctree_shadow()

    np_test.assert_almost_equal(sys.test.DC_Drv.DC_readout, (sys.LO2.amplitude**2 + sys.test.LO.amplitude**2)/2, 2)
    np_test.assert_almost_equal(sys.test.DC_R1.DC_readout, 1, 2)

    return sys


def test_AOMBasic_PWR2():
    db = declarative.DeepBunch()
    db.test.LO.phase.val = 0
    db.test.LO.phase.units = 'deg'
    db.test.LO.amplitude = np.linspace(.1, 1, 100)
    sys = system.BGSystem(
        ctree = db,
    )
    sys.own.test = AOMTestStand.AOMTestStandBasic()
    db = sys.ctree_shadow()

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
        ctree = db,
    )
    sys.own.test = AOMTestStand.AOM2VCOTestStandBasic(
        VCO2_use = True,
    )
    db = sys.ctree_shadow()

    X = sys.test.aoms.VCO_AOM1.generate.amplitude
    Y = sys.test.aoms.VCO_AOM2.generate.amplitude
    #np_test.assert_almost_equal(sys.test.DC_R.DC_readout, np.sin(X * np.pi/2)**2, 1)
    #np_test.assert_almost_equal(sys.test.DC_RR.DC_readout / X / Y**2, np.pi/4 * np.sin(X * np.pi), 1)
    #np_test.assert_almost_equal(sys.test.AC_R.AC_sensitivity / X, sys.test.DC_RR.DC_readout / X / Y**2, 2)

    np_test.assert_almost_equal(sys.test.AC_R_I_phase.AC_sensitivity, 0)
    np_test.assert_almost_equal(sys.test.AC_R_Q_amp.AC_sensitivity, 0)

    #the AM sensitivity is direct in AOMbasic, so it has derivative of 1
    np_test.assert_almost_equal((sys.test.AC_R_I_amp.AC_sensitivity), 1, 5)

    #can't directly detect phase noise!
    np_test.assert_almost_equal(sys.test.AC_R_Q_phase.AC_sensitivity, 0, 4)

    #TODO add homodyne detector to test the proper phase noise
    return sys

if __name__ == '__main__':
    test_AOM()
