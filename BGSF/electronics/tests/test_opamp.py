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


def test_open_loop_opamp():
    gain = 10
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V_P = electronics.VoltageSource()
    sled.my.V_N = electronics.VoltageSource()
    sled.my.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sled.amp.in_p, sled.V_P.A)
    sys.bond(sled.amp.in_n, sled.V_N.A)
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.amp.out,
    )
    sled.my.RAC_P = readouts.ACReadout(
        portD = sled.V_P.V.i,
        portN = sled.R1.V.o,
    )
    sled.my.RAC_N = readouts.ACReadout(
        portD = sled.V_N.V.i,
        portN = sled.R1.V.o,
    )
    test.assert_almost_equal(sled.RAC_P.AC_sensitivity, gain)
    test.assert_almost_equal(sled.RAC_N.AC_sensitivity, -gain)


def test_closed_loop_opamp():
    gain = 10
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V_P = electronics.VoltageSource()
    sled.my.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sled.amp.in_p, sled.V_P.A)
    sys.bond(sled.amp.out, sled.amp.in_n)
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.amp.out,
    )
    sled.my.RAC_P = readouts.ACReadout(
        portD = sled.V_P.V.i,
        portN = sled.R1.V.o,
    )
    test.assert_almost_equal(sled.RAC_P.AC_sensitivity, gain/(1 + gain))


def test_noise_open_loop():
    gain = 1
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V_N = electronics.VoltageSource()
    sled.my.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sled.amp.in_n, sled.V_N.A)
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.amp.out,
    )
    sled.my.RAC_N = readouts.ACReadout(
        portD = sled.V_N.V.i,
        portN = sled.R1.V.o,
    )
    sled.my.T1 = electronics.TerminatorShorted()
    sys.bond(sled.amp.in_p, sled.T1.A)
    #sled.my.T1 = electronics.TerminatorMatched()
    #sys.bond(sled.amp.in_p, sled.T1.A)

    sled.my.VN = electronics.VoltageFluctuation(
        port = sled.amp.in_p,
        Vsq_Hz_by_freq = lambda F : 1,
    )
    test.assert_almost_equal(sled.RAC_N.AC_sensitivity, -gain)
    test.assert_almost_equal(sled.RAC_N.AC_PSD, 1)

    resistance_Ohms = 10
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V_N = electronics.VoltageSource()
    sled.my.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sled.amp.in_n, sled.V_N.A)
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.amp.out,
    )
    sled.my.RAC_N = readouts.ACReadout(
        portD = sled.V_N.V.i,
        portN = sled.R1.V.o,
    )
    sled.my.T1 = electronics.TerminatorResistor(
        resistance_Ohms = resistance_Ohms,
    )
    sys.bond(sled.amp.in_p, sled.T1.A)

    sled.my.VN = electronics.CurrentFluctuation(
        port = sled.amp.in_p,
        Isq_Hz_by_freq = lambda F : 1,
    )
    test.assert_almost_equal(sled.RAC_N.AC_sensitivity, -gain)
    test.assert_almost_equal(sled.RAC_N.AC_PSD, gain**2 * resistance_Ohms**2)

def test_closed_loop_opamp_noise():
    gain = 10
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V_P = electronics.VoltageSource()
    sled.my.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sled.amp.in_p, sled.V_P.A)
    sys.bond(sled.amp.out, sled.amp.in_n)
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.amp.out,
    )
    sled.my.VN = electronics.VoltageFluctuation(
        port = sled.amp.in_n,
        Vsq_Hz_by_freq = lambda F : 1,
    )
    sled.my.RAC_P = readouts.ACReadout(
        portD = sled.V_P.V.i,
        portN = sled.R1.V.o,
    )
    test.assert_almost_equal(sled.RAC_P.AC_sensitivity, gain/(1 + gain))
    test.assert_almost_equal(sled.RAC_P.AC_PSD, (gain/(1 + gain))**2)

    gain = 10
    resistance_Ohms = 10
    sys = OpticalSystem()
    sled = sys.sled
    sled.my.V_P = electronics.VoltageSource()
    sled.my.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sled.amp.in_p, sled.V_P.A)
    sled.my.RTRans = electronics.SeriesResistor(
        resistance_Ohms = resistance_Ohms,
    )
    sys.bond_sequence(sled.amp.out, sled.RTRans.A, sled.amp.in_n)
    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.amp.out,
    )
    sled.my.VN = electronics.CurrentFluctuation(
        port = sled.amp.in_n,
        Isq_Hz_by_freq = lambda F : 1,
    )
    sled.my.RAC_P = readouts.ACReadout(
        portD = sled.V_P.V.i,
        portN = sled.R1.V.o,
    )
    test.assert_almost_equal(sled.RAC_P.AC_sensitivity, gain/(1 + gain))
    test.assert_almost_equal(sled.RAC_P.AC_PSD, resistance_Ohms**2 * (gain/(1 + gain))**2)







if __name__ == '__main__':
    test_V()
