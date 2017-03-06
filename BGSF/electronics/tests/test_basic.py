"""
"""
from __future__ import (division, print_function)
#import pytest
import numpy.testing as test

import BGSF.electronics as electronics
import BGSF.readouts as readouts
import BGSF.system as system


def test_V():
    #with explicit terminator
    sys = system.BGSystem()
    sys.my.V1 = electronics.VoltageSource(V_DC = 1)
    sys.my.T1 = electronics.TerminatorOpen()
    sys.bond(sys.V1.A, sys.T1.A)
    sys.my.R1 = electronics.VoltageReadout(
        terminal =sys.V1.A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)

    #without explicit terminator
    sys = system.BGSystem()
    sys.my.V1 = electronics.VoltageSource(V_DC = 1)
    sys.my.R1 = electronics.VoltageReadout(
        terminal =sys.V1.A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)

    #measure across terminator
    sys = system.BGSystem()
    sys.my.V1 = electronics.VoltageSource(V_DC = 1)
    sys.my.T1 = electronics.TerminatorOpen()
    sys.bond(sys.V1.A, sys.T1.A)
    sys.my.R1 = electronics.VoltageReadout(
        terminal =sys.T1.A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)


def test_I():
    sys = system.BGSystem()
    sys.my.I1 = electronics.CurrentSource(I_DC = 1)
    sys.my.T1 = electronics.TerminatorShorted()
    sys.bond(sys.I1.A, sys.T1.A)
    sys.my.R1 = electronics.CurrentReadout(
        terminal = sys.I1.A,
        direction = 'out',
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)

    #measure across terminator
    sys = system.BGSystem()
    sys.my.I1 = electronics.CurrentSource(I_DC = 1)
    sys.my.T1 = electronics.TerminatorShorted()
    sys.bond(sys.I1.A, sys.T1.A)
    sys.my.R1 = electronics.CurrentReadout(
        terminal = sys.T1.A,
        direction = 'in',
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)

def test_VIR():
    sys = system.BGSystem()
    sys.my.I1 = electronics.CurrentSource(I_DC = 1)
    sys.my.T1 = electronics.TerminatorResistor(
        resistance_Ohms = 10,
    )
    sys.bond(sys.I1.A, sys.T1.A)
    sys.my.R1 = electronics.CurrentReadout(
        terminal = sys.I1.A,
        direction = 'out',
    )
    sys.my.R2 = electronics.VoltageReadout(
        terminal = sys.I1.A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)
    test.assert_almost_equal(sys.R2.DC_readout, 10)

    #2
    sys = system.BGSystem()
    sys.my.I1 = electronics.CurrentSource(I_DC = 1)
    sys.my.T1 = electronics.TerminatorResistor(
        resistance_Ohms = 50,
    )
    sys.bond(sys.I1.A, sys.T1.A)
    sys.my.R1 = electronics.CurrentReadout(
        terminal = sys.I1.A,
        direction = 'out',
    )
    sys.my.R2 = electronics.VoltageReadout(
        terminal = sys.I1.A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)
    test.assert_almost_equal(sys.R2.DC_readout, 50)

def test_VIR_conn():
    sys = system.BGSystem()
    sys.my.I1 = electronics.CurrentSource(I_DC = 1)
    sys.my.Conn1 = electronics.Connection(N_ports = 3)
    sys.my.T1 = electronics.TerminatorResistor(
        resistance_Ohms = 10,
    )
    sys.my.T2 = electronics.TerminatorResistor(
        resistance_Ohms = 10,
    )
    sys.bond(sys.I1.A, sys.Conn1.p0)
    sys.bond(sys.Conn1.p1, sys.T1.A)
    sys.bond(sys.Conn1.p2, sys.T2.A)
    sys.my.R1 = electronics.CurrentReadout(
        terminal = sys.I1.A,
        direction = 'out',
    )
    sys.my.R2 = electronics.VoltageReadout(
        terminal = sys.I1.A,
    )
    sys.my.R3 = electronics.CurrentReadout(
        terminal = sys.T1.A,
        direction = 'in',
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)
    test.assert_almost_equal(sys.R2.DC_readout, 5)
    test.assert_almost_equal(sys.R3.DC_readout, .5)

def test_bdV():
    """
    Test the balanced voltage source with different pairs of terminations. Not allowed to short both sides or have
    both sides open.
    """
    sys = system.BGSystem()
    sys.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    sys.my.T1 = electronics.TerminatorOpen()
    sys.bond(sys.V1.A, sys.T1.A)
    sys.my.T2 = electronics.TerminatorShorted()
    sys.bond(sys.V1.B, sys.T2.A)
    sys.my.R1 = electronics.VoltageReadout(
        terminal = sys.V1.A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)

    sys = system.BGSystem()
    sys.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    #sys.my.T1 = electronics.TerminatorOpen()
    #sys.bond(sys.V1.A, sys.T1.A)
    sys.my.T2 = electronics.TerminatorShorted()
    sys.bond(sys.V1.B, sys.T2.A)
    sys.my.R1 = electronics.VoltageReadout(
        terminal = sys.V1.A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)

    sys = system.BGSystem()
    sys.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    sys.my.T2 = electronics.TerminatorMatched()
    sys.bond(sys.V1.B, sys.T2.A)
    sys.my.R1 = electronics.VoltageReadout(
        terminal = sys.V1.A,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)

    sys = system.BGSystem()
    sys.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    sys.my.T2 = electronics.TerminatorShorted()
    sys.bond(sys.V1.B, sys.T2.A)
    sys.my.T1 = electronics.TerminatorMatched()
    sys.bond(sys.V1.A, sys.T1.A)
    sys.my.R1 = electronics.VoltageReadout(
        terminal = sys.V1.A,
        terminal_N = sys.V1.B,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)

    sys = system.BGSystem()
    sys.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    sys.my.T1 = electronics.TerminatorMatched()
    sys.bond(sys.V1.A, sys.T1.A)
    sys.my.T2 = electronics.TerminatorMatched()
    sys.bond(sys.V1.B, sys.T2.A)
    sys.my.R1 = electronics.VoltageReadout(
        terminal = sys.V1.A,
        terminal_N = sys.V1.B,
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1)


def test_bdVIR():
    sys = system.BGSystem()
    sys.my.V1 = electronics.VoltageSourceBalanced(V_DC = 1)
    sys.my.T1 = electronics.TerminatorResistor(
        resistance_Ohms = 10,
    )
    sys.bond(sys.V1.A, sys.T1.A)
    sys.my.T2 = electronics.TerminatorResistor(
        resistance_Ohms = 20,
    )
    sys.bond(sys.V1.B, sys.T2.A)
    sys.my.R1 = electronics.CurrentReadout(
        terminal = sys.T1.A,
        direction = 'in',
    )
    test.assert_almost_equal(sys.R1.DC_readout, 1 / 30)

def test_bdVIR_AC():
    sys = system.BGSystem()
    sys.my.V1 = electronics.VoltageSourceBalanced()
    sys.my.T1 = electronics.TerminatorResistor(
        resistance_Ohms = 10,
    )
    sys.bond(sys.V1.A, sys.T1.A)
    sys.my.T2 = electronics.TerminatorResistor(
        resistance_Ohms = 20,
    )
    sys.bond(sys.V1.B, sys.T2.A)
    sys.my.R1 = electronics.CurrentReadout(
        terminal = sys.T1.A,
        direction = 'in',
    )
    sys.my.RAC1 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R1.I.o,
    )
    test.assert_almost_equal(sys.RAC1.AC_sensitivity, 1 / 30)

def test_V_AC():
    sys = system.system.BGSystem(
        F_AC = 100.,
    )
    sys.my.V1 = electronics.VoltageSource()
    sys.my.R1 = electronics.VoltageReadout(
        terminal = sys.V1.A,
    )
    sys.my.RAC1 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R1.V.o,
    )
    test.assert_almost_equal(sys.RAC1.AC_sensitivity, 1)




if __name__ == '__main__':
    test_V()
