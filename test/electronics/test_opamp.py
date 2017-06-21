"""
"""
from __future__ import (division, print_function)
import pytest
import numpy.testing as test

from declarative import Bunch

import phasor.electronics as electronics
import phasor.readouts as readouts

from phasor.system import (
    BGSystem
)


pytest.mark.parametrize('gain', [(1), (10), (100)])
def test_open_loop_opamp(gain = 10):
    sys = BGSystem()
    sys.own.V_P = electronics.VoltageSource()
    sys.own.V_N = electronics.VoltageSource()
    sys.own.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sys.amp.in_p, sys.V_P.pe_A)
    sys.bond(sys.amp.in_n, sys.V_N.pe_A)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.amp.out,
    )
    sys.own.RAC_P = readouts.ACReadout(
        portD = sys.V_P.V.i,
        portN = sys.R1.V.o,
    )
    sys.own.RAC_N = readouts.ACReadout(
        portD = sys.V_N.V.i,
        portN = sys.R1.V.o,
    )
    test.assert_almost_equal(sys.RAC_P.AC_sensitivity, gain)
    test.assert_almost_equal(sys.RAC_N.AC_sensitivity, -gain)


pytest.mark.parametrize('gain', [(1), (10), (100)])
def test_closed_loop_opamp(gain = 10):
    sys = BGSystem()
    sys.own.V_P = electronics.VoltageSource()
    sys.own.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sys.amp.in_p, sys.V_P.pe_A)
    sys.bond(sys.amp.out, sys.amp.in_n)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.amp.out,
    )
    sys.own.RAC_P = readouts.ACReadout(
        portD = sys.V_P.V.i,
        portN = sys.R1.V.o,
    )
    test.assert_almost_equal(sys.RAC_P.AC_sensitivity, gain/(1 + gain))


pytest.mark.parametrize('gain', [(1), (10), (100)])
def test_noise_open_loop(gain = 1):
    sys = BGSystem()
    sys.own.V_N = electronics.VoltageSource()
    sys.own.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sys.amp.in_n, sys.V_N.pe_A)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.amp.out,
    )
    sys.own.RAC_N = readouts.ACReadout(
        portD = sys.V_N.V.i,
        portN = sys.R1.V.o,
    )
    sys.own.T1 = electronics.TerminatorShorted()
    sys.bond(sys.amp.in_p, sys.T1.pe_A)
    #sys.own.T1 = electronics.TerminatorMatched()
    #sys.bond(sys.amp.in_p, sys.T1.pe_A)

    sys.own.VN = electronics.VoltageFluctuation(
        #port = sys.amp.in_p,
        port = sys.T1.pe_A,
        Vsq_Hz_by_freq = lambda F : 1,
        sided = 'one-sided',
    )
    #sys.solution.coupling_matrix_inv_print()
    test.assert_almost_equal(sys.RAC_N.AC_sensitivity, -gain)
    test.assert_almost_equal(sys.RAC_N.AC_PSD, 1)

    resistance_Ohms = 10
    sys = BGSystem()
    sys.own.V_N = electronics.VoltageSource()
    sys.own.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sys.amp.in_n, sys.V_N.pe_A)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.amp.out,
    )
    sys.own.RAC_N = readouts.ACReadout(
        portD = sys.V_N.V.i,
        portN = sys.R1.V.o,
    )
    sys.own.T1 = electronics.TerminatorResistor(
        resistance_Ohms = resistance_Ohms,
    )
    sys.bond(sys.amp.in_p, sys.T1.pe_A)

    sys.own.VN = electronics.CurrentFluctuation(
        port = sys.amp.in_p,
        #port = sys.T1.pe_A,
        Isq_Hz_by_freq = lambda F : 1,
        sided = 'one-sided',
    )
    test.assert_almost_equal(sys.RAC_N.AC_sensitivity, -gain)
    test.assert_almost_equal(sys.RAC_N.AC_PSD / (gain**2 * resistance_Ohms**2), 1)

def test_closed_loop_opamp_noise():
    gain = 10
    sys = BGSystem()
    sys.own.V_P = electronics.VoltageSource()
    sys.own.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sys.amp.in_p, sys.V_P.pe_A)
    sys.bond(sys.amp.out, sys.amp.in_n)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.amp.out,
    )
    sys.own.VN = electronics.VoltageFluctuation(
        port = sys.amp.in_n,
        #port = sys.amp.out,
        Vsq_Hz_by_freq = lambda F : 1,
        sided = 'one-sided',
    )
    sys.own.RAC_P = readouts.ACReadout(
        portD = sys.V_P.V.i,
        portN = sys.R1.V.o,
    )
    #sys.solution.coupling_matrix_print()
    test.assert_almost_equal(sys.RAC_P.AC_sensitivity, gain/(1 + gain))
    test.assert_almost_equal(sys.RAC_P.AC_PSD / (gain/(1 + gain))**2, 1)

    gain = 10
    resistance_Ohms = 10
    sys = BGSystem()
    sys.own.V_P = electronics.VoltageSource()
    sys.own.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sys.amp.in_p, sys.V_P.pe_A)
    sys.own.RTRans = electronics.SeriesResistor(
        resistance_Ohms = resistance_Ohms,
    )
    sys.bond_sequence(sys.amp.out, sys.RTRans.pe_A, sys.amp.in_n)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.amp.out,
    )
    sys.own.VN = electronics.CurrentFluctuation(
        port = sys.amp.in_n,
        #port = sys.RTRans.pe_B,
        Isq_Hz_by_freq = lambda F : 1,
        sided = 'one-sided',
    )
    sys.own.RAC_P = readouts.ACReadout(
        portD = sys.V_P.V.i,
        portN = sys.R1.V.o,
    )
    test.assert_almost_equal(sys.RAC_P.AC_sensitivity, gain/(1 + gain))
    test.assert_almost_equal(sys.RAC_P.AC_PSD / (resistance_Ohms**2 * (gain/(1 + gain))**2), 1)


def test_closed_loop_opamp_noise_regen():
    gain = 10
    resistance_Ohms = 10
    sys = BGSystem()
    sys.own.V_P = electronics.VoltageSource()
    sys.own.amp = electronics.OpAmp(
        gain_by_freq = lambda F : gain
    )
    sys.bond(sys.amp.in_p, sys.V_P.pe_A)
    sys.own.RTRans = electronics.SeriesResistor(
        resistance_Ohms = resistance_Ohms,
    )
    sys.bond_sequence(sys.amp.out, sys.RTRans.pe_A, sys.amp.in_n)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.amp.out,
    )
    sys.own.VN = electronics.CurrentFluctuation(
        port = sys.amp.in_n,
        #port = sys.RTRans.pe_B,
        Isq_Hz_by_freq = lambda F : 1,
        sided = 'one-sided',
    )
    sys.own.RAC_P = readouts.ACReadout(
        portD = sys.V_P.V.i,
        portN = sys.R1.V.o,
    )
    test.assert_almost_equal(sys.RAC_P.AC_sensitivity, gain/(1 + gain))
    test.assert_almost_equal(sys.RAC_P.AC_PSD / (resistance_Ohms**2 * (gain/(1 + gain))**2), 1)

    sys2 = sys.regenerate()
    test.assert_almost_equal(sys2.RAC_P.AC_sensitivity, gain/(1 + gain))
    test.assert_almost_equal(sys2.RAC_P.AC_PSD / (resistance_Ohms**2 * (gain/(1 + gain))**2), 1)


def test_johnson_noise():
    resistance_Ohms = 1000
    sys = BGSystem()
    sys.own.Z1 = electronics.TerminatorResistor(
        resistance_Ohms = resistance_Ohms,
    )
    sys.own.T1 = electronics.TerminatorOpen()
    sys.bond(sys.Z1.pe_A, sys.T1.pe_A)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.T1.pe_A,
    )
    sys.own.RN = readouts.NoiseReadout(
        portN = sys.R1.V.o,
    )
    test.assert_almost_equal(sys.RN.CSD['R', 'R'] / (4 * sys.symbols.kB_J_K * sys.symbols.temp_K * resistance_Ohms), 1)

    #now connect to other terminal
    sys = BGSystem()
    sys.own.Z1 = electronics.TerminatorResistor(
        resistance_Ohms = resistance_Ohms,
    )
    sys.own.T1 = electronics.TerminatorOpen()
    sys.bond(sys.Z1.pe_A, sys.T1.pe_A)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.Z1.pe_A,
    )
    sys.own.RN = readouts.NoiseReadout(
        portN = sys.R1.V.o,
    )
    test.assert_almost_equal(sys.RN.CSD['R', 'R'] / (4 * sys.symbols.kB_J_K * sys.symbols.temp_K * resistance_Ohms), 1)

def test_johnson_noise_shorted():
    resistance_Ohms = 1000
    #now connect to other terminal
    sys = BGSystem()
    sys.own.Z1 = electronics.TerminatorResistor(
        resistance_Ohms = resistance_Ohms,
    )
    sys.own.T1 = electronics.TerminatorShorted()
    sys.bond(sys.Z1.pe_A, sys.T1.pe_A)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.Z1.pe_A,
    )
    sys.own.RN = readouts.NoiseReadout(
        portN = sys.R1.V.o,
    )
    test.assert_almost_equal(sys.RN.CSD['R', 'R'] / (4 * sys.symbols.kB_J_K * sys.symbols.temp_K * resistance_Ohms), 0)

def test_johnson_noise_parallel():
    resistance_Ohms = 1000
    #now connect to other terminal
    sys = BGSystem()
    sys.own.Z1 = electronics.TerminatorResistor(
        resistance_Ohms = resistance_Ohms,
    )
    sys.own.Z2 = electronics.TerminatorResistor(
        resistance_Ohms = resistance_Ohms,
    )
    sys.bond(sys.Z1.pe_A, sys.Z2.pe_A)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.Z1.pe_A,
    )
    sys.own.RN = readouts.NoiseReadout(
        portN = sys.R1.V.o,
    )
    test.assert_almost_equal(sys.RN.CSD['R', 'R'] / (4 * sys.symbols.kB_J_K * sys.symbols.temp_K * resistance_Ohms / 2), 1)


def test_johnson_noise_terminator():
    sys = BGSystem()
    sys.own.Z1 = electronics.TerminatorMatched()
    sys.own.T1 = electronics.TerminatorOpen()
    sys.bond(sys.Z1.pe_A, sys.T1.pe_A)
    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.Z1.pe_A,
    )
    sys.own.RN = readouts.NoiseReadout(
        portN = sys.R1.V.o,
    )
    test.assert_almost_equal(sys.RN.CSD['R', 'R'] / (4 * sys.symbols.kB_J_K * sys.symbols.temp_K * sys.Z1.Z_termination.real), 1)







if __name__ == '__main__':
    test_V()
