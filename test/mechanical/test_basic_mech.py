# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#import pytest
import numpy.testing as test

import phasor.mechanical as mechanical
import phasor.readouts as readouts
import phasor.system as system


def test_F():
    #with explicit terminator
    sys = system.BGSystem()
    sys.own.F1 = mechanical.ForceSource(F_DC = 1)
    sys.own.T1 = mechanical.TerminatorShorted()
    sys.bond(sys.F1.pm_A, sys.T1.pm_A)
    sys.own.R1 = mechanical.ForceReadout(
        terminal =sys.F1.pm_A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)

    #measure across terminator
    sys = system.BGSystem()
    sys.own.F1 = mechanical.ForceSource(F_DC = 1)
    sys.own.T1 = mechanical.TerminatorShorted()
    sys.bond(sys.F1.pm_A, sys.T1.pm_A)
    sys.own.R1 = mechanical.ForceReadout(
        terminal =sys.T1.pm_A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, -1)


def test_d():
    sys = system.BGSystem()
    sys.own.d1 = mechanical.DisplacementSource(d_DC = 1)
    sys.own.T1 = mechanical.TerminatorOpen()
    sys.bond(sys.d1.pm_A, sys.T1.pm_A)
    sys.own.R1 = mechanical.DisplacementReadout(
        terminal = sys.d1.pm_A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)

    #measure across terminator
    sys = system.BGSystem()
    sys.own.d1 = mechanical.DisplacementSource(d_DC = 1)
    sys.own.T1 = mechanical.TerminatorOpen()
    sys.bond(sys.d1.pm_A, sys.T1.pm_A)
    sys.own.R1 = mechanical.DisplacementReadout(
        terminal = sys.T1.pm_A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)

def test_displacement_damper():
    sys = system.BGSystem()
    sys.own.d1 = mechanical.DisplacementSource(d_DC = 1)
    sys.own.T1 = mechanical.TerminatorDamper(
        resistance_Ns_m = 10,
    )
    sys.bond(sys.d1.pm_A, sys.T1.pm_A)
    sys.own.R1 = mechanical.DisplacementReadout(
        terminal = sys.d1.pm_A,
    )
    sys.own.R2 = mechanical.ForceReadout(
        terminal = sys.d1.pm_A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)
    test.assert_almost_equal(sys.R2.DC_readout, 0)

    #2
    sys = system.BGSystem()
    sys.own.d1 = mechanical.DisplacementSource(d_DC = 1)
    sys.own.T1 = mechanical.TerminatorDamper(
        resistance_Ns_m = 50,
    )
    sys.bond(sys.d1.pm_A, sys.T1.pm_A)
    sys.own.R1 = mechanical.DisplacementReadout(
        terminal = sys.d1.pm_A,
    )
    sys.own.R2 = mechanical.ForceReadout(
        terminal = sys.d1.pm_A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)
    test.assert_almost_equal(sys.R2.DC_readout, 0)

def test_force_spring():
    sys = system.BGSystem()
    sys.own.d1 = mechanical.ForceSource(F_DC = 1)
    sys.own.T1 = mechanical.TerminatorSpring(
        elasticity_N_m = 10,
    )
    sys.bond(sys.d1.pm_A, sys.T1.pm_A)
    sys.own.R1 = mechanical.DisplacementReadout(
        terminal = sys.T1.pm_A,
    )
    #measures force to the ground
    sys.own.R2 = mechanical.ForceReadout(
        terminal = sys.T1.pm_A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, .1)
    test.assert_almost_equal(sys.R2.DC_readout, -1)

    #2
    sys = system.BGSystem()
    sys.own.d1 = mechanical.ForceSource(F_DC = 1)
    sys.own.T1 = mechanical.TerminatorSpring(
        elasticity_N_m = 1,
    )
    sys.bond(sys.d1.pm_A, sys.T1.pm_A)
    sys.own.R1 = mechanical.DisplacementReadout(
        terminal = sys.d1.pm_A,
    )
    sys.own.R2 = mechanical.ForceReadout(
        terminal = sys.d1.pm_A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)
    test.assert_almost_equal(sys.R2.DC_readout, 1)

def test_displacement_spring():
    sys = system.BGSystem()
    sys.own.d1 = mechanical.DisplacementSource(d_DC = 1)
    sys.own.T1 = mechanical.TerminatorSpring(
        elasticity_N_m = 10,
    )
    sys.bond(sys.d1.pm_A, sys.T1.pm_A)
    sys.own.R1 = mechanical.DisplacementReadout(
        terminal = sys.d1.pm_A,
    )
    #measures force to the ground
    sys.own.R2 = mechanical.ForceReadout(
        terminal = sys.d1.pm_A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)
    test.assert_almost_equal(sys.R2.DC_readout, 10)

    #2
    sys = system.BGSystem()
    sys.own.d1 = mechanical.DisplacementSource(d_DC = 1)
    sys.own.T1 = mechanical.TerminatorSpring(
        elasticity_N_m = 1,
    )
    sys.bond(sys.d1.pm_A, sys.T1.pm_A)
    sys.own.R1 = mechanical.DisplacementReadout(
        terminal = sys.d1.pm_A,
    )
    sys.own.R2 = mechanical.ForceReadout(
        terminal = sys.d1.pm_A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)
    test.assert_almost_equal(sys.R2.DC_readout, 1)

#def test_bdFdR_AC():
#    sys = system.BGSystem()
#    sys.own.F1 = mechanical.ForceSourceBalanced()
#    sys.own.T1 = mechanical.TerminatorDamper(
#        resistance_Ns_m = 10,
#    )
#    sys.bond(sys.F1.pm_A, sys.T1.pm_A)
#    sys.own.T2 = mechanical.TerminatorDamper(
#        resistance_Ns_m = 20,
#    )
#    sys.bond(sys.F1.pm_B, sys.T2.pm_A)
#    sys.own.R1 = mechanical.DisplacementReadout(
#        terminal = sys.T1.pm_A,
#    )
#    sys.own.RAC1 = readouts.ACReadout(
#        portD = sys.F1.F.i,
#        portN = sys.R1.d.o,
#    )
#    test.assert_almost_equal(sys.RAC1.AC_sensitivity, 1 / 30)

def test_F_AC():
    sys = system.system.BGSystem(
        F_AC = 100.,
    )
    sys.own.F1 = mechanical.ForceSource()
    sys.own.T1 = mechanical.TerminatorShorted()
    sys.bond(sys.F1.pm_A, sys.T1.pm_A)
    sys.own.R1 = mechanical.ForceReadout(
        terminal = sys.F1.pm_A,
    )
    sys.own.RAC1 = readouts.ACReadout(
        portD = sys.F1.F.i,
        portN = sys.R1.F.o,
    )
    test.assert_almost_equal(sys.RAC1.AC_sensitivity, 1)

