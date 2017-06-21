"""
"""
from __future__ import (division, print_function)
import pytest
import numpy.testing as test
import numpy as np

from declarative import Bunch

import phasor.electronics as electronics
import phasor.readouts as readouts
import phasor.system as system


def test_transformer():
    sys = system.BGSystem(
        F_AC = 100,
    )
    sys.own.V1 = electronics.VoltageSource()
    sys.own.Tr1 = electronics.Transformer(
        L1_inductance_Henries = 1e-6,
        L2_inductance_Henries = 100e-6,
    )
    sys.bond(sys.Tr1.pe_A, sys.V1.pe_A)
    sys.own.Tr1BT = electronics.TerminatorMatched()
    sys.bond(sys.Tr1.pe_B, sys.Tr1BT.pe_A)
    sys.own.Tr1CT = electronics.TerminatorOpen()
    sys.bond(sys.Tr1.pe_C, sys.Tr1CT.pe_A)
    sys.own.Tr1DT = electronics.TerminatorMatched()
    sys.bond(sys.Tr1.pe_D, sys.Tr1DT.pe_A)

    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.V1.pe_A,
    )
    sys.own.RAC1 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R1.V.o,
    )
    sys.own.R2 = electronics.VoltageReadout(
        terminal = sys.Tr1.pe_C,
    )
    sys.own.RAC2 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R2.V.o,
    )

    test.assert_almost_equal(sys.RAC1.AC_sensitivity, 1)
    test.assert_almost_equal(abs(sys.RAC2.AC_sensitivity), 10)

def test_transformer2():
    sys = system.BGSystem(
        F_AC = 100.,
    )
    sys.own.V1 = electronics.VoltageSource()
    sys.own.Tr1 = electronics.Transformer(
        L1_inductance_Henries = 1e-6,
        L2_inductance_Henries = 100e-6,
    )
    sys.bond(sys.Tr1.pe_A, sys.V1.pe_A)
    sys.own.Tr1BT = electronics.TerminatorResistor(
        resistance_Ohms = 1,
    )
    sys.bond(sys.Tr1.pe_B, sys.Tr1BT.pe_A)
    sys.own.Tr1CT = electronics.TerminatorOpen()
    sys.bond(sys.Tr1.pe_C, sys.Tr1CT.pe_A)
    sys.own.Tr1DT = electronics.TerminatorResistor(
        resistance_Ohms = np.linspace(.00001, 1e6, 10)
    )
    sys.bond(sys.Tr1.pe_D, sys.Tr1DT.pe_A)

    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.V1.pe_A,
    )
    sys.own.RAC1 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R1.V.o,
    )
    sys.own.R2 = electronics.VoltageReadout(
        terminal = sys.Tr1.pe_C,
    )
    sys.own.RAC2 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R2.V.o,
    )

    test.assert_almost_equal(abs(sys.RAC1.AC_sensitivity), 1)
    test.assert_almost_equal(abs(sys.RAC2.AC_sensitivity), 10)


def test_transformer_stepdown():
    sys = system.BGSystem(
        F_AC = 100.,
    )
    sys.own.V1 = electronics.VoltageSource()
    sys.own.Tr1 = electronics.Transformer(
        L1_inductance_Henries = 100e-6,
        L2_inductance_Henries = 1e-6,
        #transformer_k_by_freq = lambda F : .99,
    )
    sys.bond(sys.Tr1.pe_A, sys.V1.pe_A)
    sys.own.Tr1BT = electronics.TerminatorResistor(
        resistance_Ohms = 1,
    )
    sys.bond(sys.Tr1.pe_B, sys.Tr1BT.pe_A)
    sys.own.Tr1CT = electronics.TerminatorOpen()
    sys.bond(sys.Tr1.pe_C, sys.Tr1CT.pe_A)
    sys.own.Tr1DT = electronics.TerminatorResistor(
        resistance_Ohms = np.linspace(.00001, 1e6, 10)
    )
    sys.bond(sys.Tr1.pe_D, sys.Tr1DT.pe_A)

    sys.own.R1 = electronics.VoltageReadout(
        terminal = sys.V1.pe_A,
    )
    sys.own.RAC1 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R1.V.o,
    )
    sys.own.R2 = electronics.VoltageReadout(
        terminal = sys.Tr1.pe_C,
    )
    sys.own.RAC2 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R2.V.o,
    )

    test.assert_almost_equal(abs(sys.RAC1.AC_sensitivity), 1)
    test.assert_almost_equal(abs(sys.RAC2.AC_sensitivity), 1/10)


if __name__ == '__main__':
    test_V()
