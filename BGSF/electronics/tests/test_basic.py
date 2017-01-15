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
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSource(V_DC = 1)
    sled.my.T1 = electronics.TerminatorOpen()
    sys.bond(sled.V1.A, sled.T1.A)
    sled.my.R1 = electronics.VoltageReadout(
        terminal =sled.V1.A,
    )
    test.assert_almost_equal(sled.R1.DC_readout, 1)

    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V1 = electronics.VoltageSource(V_DC = 1)
    sled.my.R1 = electronics.VoltageReadout(
        terminal =sled.V1.A,
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

def test_bdV():
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

    #This one actually probably should be wrong
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




if __name__ == '__main__':
    test_basic()
