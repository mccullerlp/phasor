"""
"""
from __future__ import (division, print_function)
import pytest
import numpy.testing as test

from declarative import Bunch

import BGSF.electronics as electronics
import BGSF.readouts as readouts

from BGSF.system.optical import (
    OpticalSystem
)

import unittest
assertions = unittest.TestCase('__init__')


def test_V():
    #with explicit terminator
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSource(V_DC = 1)
    sled.my.T1 = electronics.TerminatorOpen()
    sys.bond(sled.V1.A, sled.T1.A)
    sled.my.R1 = electronics.VoltageReadout(
        terminal =sled.V1.A,
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)

    #without explicit terminator
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSource(V_DC = 1)
    sled.my.R1 = electronics.VoltageReadout(
        terminal =sled.V1.A,
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)

    #measure across terminator
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSource(V_DC = 1)
    sled.my.T1 = electronics.TerminatorOpen()
    sys.bond(sled.V1.A, sled.T1.A)
    sled.my.R1 = electronics.VoltageReadout(
        terminal =sled.T1.A,
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)


def test_I():
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.I1 = electronics.CurrentSource(I_DC = 1)
    sled.my.T1 = electronics.TerminatorShorted()
    sys.bond(sled.I1.A, sled.T1.A)
    sled.my.R1 = electronics.CurrentReadout(
        terminal = sled.I1.A,
        direction = 'out',
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)

    #measure across terminator
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.I1 = electronics.CurrentSource(I_DC = 1)
    sled.my.T1 = electronics.TerminatorShorted()
    sys.bond(sled.I1.A, sled.T1.A)
    sled.my.R1 = electronics.CurrentReadout(
        terminal = sled.T1.A,
        direction = 'in',
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)

def test_VIR():
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.I1 = electronics.CurrentSource(I_DC = 1)
    sled.my.T1 = electronics.TerminatorResistor(
        resistance_Ohms = 10,
    )
    sys.bond(sled.I1.A, sled.T1.A)
    sled.my.R1 = electronics.CurrentReadout(
        terminal = sled.I1.A,
        direction = 'out',
    )
    sled.my.R2 = electronics.VoltageReadout(
        terminal = sled.I1.A,
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)
    test.assert_almost_equal(sled.R2.DC_readout, 10)

    #2
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.I1 = electronics.CurrentSource(I_DC = 1)
    sled.my.T1 = electronics.TerminatorResistor(
        resistance_Ohms = 50,
    )
    sys.bond(sled.I1.A, sled.T1.A)
    sled.my.R1 = electronics.CurrentReadout(
        terminal = sled.I1.A,
        direction = 'out',
    )
    sled.my.R2 = electronics.VoltageReadout(
        terminal = sled.I1.A,
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)
    test.assert_almost_equal(sled.R2.DC_readout, 50)

def test_bdV():
    """
    Test the balanced voltage source with different pairs of terminations. Not allowed to short both sides or have
    both sides open.
    """
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    sled.my.T1 = electronics.TerminatorOpen()
    sys.bond(sled.V1.A, sled.T1.A)
    sled.my.T2 = electronics.TerminatorShorted()
    sys.bond(sled.V1.B, sled.T2.A)
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.V1.A,
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)

    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    #sled.my.T1 = electronics.TerminatorOpen()
    #sys.bond(sled.V1.A, sled.T1.A)
    sled.my.T2 = electronics.TerminatorShorted()
    sys.bond(sled.V1.B, sled.T2.A)
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.V1.A,
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)

    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    sled.my.T2 = electronics.TerminatorMatched()
    sys.bond(sled.V1.B, sled.T2.A)
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.V1.A,
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)

    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    sled.my.T2 = electronics.TerminatorShorted()
    sys.bond(sled.V1.B, sled.T2.A)
    sled.my.T1 = electronics.TerminatorMatched()
    sys.bond(sled.V1.A, sled.T1.A)
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.V1.A,
        terminal_N = sled.V1.B,
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)

    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    sled.my.T1 = electronics.TerminatorMatched()
    sys.bond(sled.V1.A, sled.T1.A)
    sled.my.T2 = electronics.TerminatorMatched()
    sys.bond(sled.V1.B, sled.T2.A)
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.V1.A,
        terminal_N = sled.V1.B,
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)


def test_bdVIR():
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    sled.my.T1 = electronics.TerminatorResistor(
        resistance_Ohms = 10,
    )
    sys.bond(sled.V1.A, sled.T1.A)
    sled.my.T2 = electronics.TerminatorResistor(
        resistance_Ohms = 20,
    )
    sys.bond(sled.V1.B, sled.T2.A)
    sled.my.R1 = electronics.CurrentReadout(
        terminal = sled.T1.A,
        direction = 'in',
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1 / 30)

def test_bdVIR_AC():
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSourceBalanced()
    sled.my.T1 = electronics.TerminatorResistor(
        resistance_Ohms = 10,
    )
    sys.bond(sled.V1.A, sled.T1.A)
    sled.my.T2 = electronics.TerminatorResistor(
        resistance_Ohms = 20,
    )
    sys.bond(sled.V1.B, sled.T2.A)
    sled.my.R1 = electronics.CurrentReadout(
        terminal = sled.T1.A,
        direction = 'in',
    )
    sled.my.RAC1 = readouts.ACReadout(
        portD = sled.V1.V.i,
        portN = sled.R1.I.o,
    )
    test.assert_almost_equal(sled.RAC1.AC_sensitivity, 1 / 30)

def test_V_AC():
    sys = OpticalSystem()
    sled = sys.sled
    sys.F_AC.F_Hz = 1.
    sled.my.V1 = electronics.VoltageSource()
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.V1.A,
    )
    sled.my.RAC1 = readouts.ACReadout(
        portD = sled.V1.V.i,
        portN = sled.R1.V.o,
    )
    test.assert_almost_equal(sled.RAC1.AC_sensitivity, 1)




if __name__ == '__main__':
    test_V()
