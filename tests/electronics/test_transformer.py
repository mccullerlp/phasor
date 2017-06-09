"""
"""
from __future__ import (division, print_function)
import pytest
import numpy.testing as test
import numpy as np

from declarative import Bunch

import openLoop.electronics as electronics
import openLoop.readouts as readouts
import openLoop.system as system


def test_transformer():
    sys = system.BGSystem(
        F_AC = 100,
    )
    sys.my.V1 = electronics.VoltageSource()
    sys.my.Tr1 = electronics.Transformer(
        L1_inductance_Henries = 1e-6,
        L2_inductance_Henries = 100e-6,
    )
    sys.bond(sys.Tr1.A, sys.V1.A)
    sys.my.Tr1BT = electronics.TerminatorMatched()
    sys.bond(sys.Tr1.B, sys.Tr1BT.A)
    sys.my.Tr1CT = electronics.TerminatorOpen()
    sys.bond(sys.Tr1.C, sys.Tr1CT.A)
    sys.my.Tr1DT = electronics.TerminatorMatched()
    sys.bond(sys.Tr1.D, sys.Tr1DT.A)

    sys.my.R1 = electronics.VoltageReadout(
        terminal = sys.V1.A,
    )
    sys.my.RAC1 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R1.V.o,
    )
    sys.my.R2 = electronics.VoltageReadout(
        terminal = sys.Tr1.C,
    )
    sys.my.RAC2 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R2.V.o,
    )

    test.assert_almost_equal(sys.RAC1.AC_sensitivity, 1)
    test.assert_almost_equal(abs(sys.RAC2.AC_sensitivity), 10)

def test_transformer2():
    sys = system.BGSystem(
        F_AC = 100.,
    )
    sys.my.V1 = electronics.VoltageSource()
    sys.my.Tr1 = electronics.Transformer(
        L1_inductance_Henries = 1e-6,
        L2_inductance_Henries = 100e-6,
    )
    sys.bond(sys.Tr1.A, sys.V1.A)
    sys.my.Tr1BT = electronics.TerminatorResistor(
        resistance_Ohms = 1,
    )
    sys.bond(sys.Tr1.B, sys.Tr1BT.A)
    sys.my.Tr1CT = electronics.TerminatorOpen()
    sys.bond(sys.Tr1.C, sys.Tr1CT.A)
    sys.my.Tr1DT = electronics.TerminatorResistor(
        resistance_Ohms = np.linspace(.00001, 1e6, 10)
    )
    sys.bond(sys.Tr1.D, sys.Tr1DT.A)

    sys.my.R1 = electronics.VoltageReadout(
        terminal = sys.V1.A,
    )
    sys.my.RAC1 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R1.V.o,
    )
    sys.my.R2 = electronics.VoltageReadout(
        terminal = sys.Tr1.C,
    )
    sys.my.RAC2 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R2.V.o,
    )

    test.assert_almost_equal(abs(sys.RAC1.AC_sensitivity), 1)
    test.assert_almost_equal(abs(sys.RAC2.AC_sensitivity), 10)


def test_transformer_stepdown():
    sys = system.BGSystem(
        F_AC = 100.,
    )
    sys.my.V1 = electronics.VoltageSource()
    sys.my.Tr1 = electronics.Transformer(
        L1_inductance_Henries = 100e-6,
        L2_inductance_Henries = 1e-6,
        #transformer_k_by_freq = lambda F : .99,
    )
    sys.bond(sys.Tr1.A, sys.V1.A)
    sys.my.Tr1BT = electronics.TerminatorResistor(
        resistance_Ohms = 1,
    )
    sys.bond(sys.Tr1.B, sys.Tr1BT.A)
    sys.my.Tr1CT = electronics.TerminatorOpen()
    sys.bond(sys.Tr1.C, sys.Tr1CT.A)
    sys.my.Tr1DT = electronics.TerminatorResistor(
        resistance_Ohms = np.linspace(.00001, 1e6, 10)
    )
    sys.bond(sys.Tr1.D, sys.Tr1DT.A)

    sys.my.R1 = electronics.VoltageReadout(
        terminal = sys.V1.A,
    )
    sys.my.RAC1 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R1.V.o,
    )
    sys.my.R2 = electronics.VoltageReadout(
        terminal = sys.Tr1.C,
    )
    sys.my.RAC2 = readouts.ACReadout(
        portD = sys.V1.V.i,
        portN = sys.R2.V.o,
    )

    test.assert_almost_equal(abs(sys.RAC1.AC_sensitivity), 1)
    test.assert_almost_equal(abs(sys.RAC2.AC_sensitivity), 1/10)


if __name__ == '__main__':
    test_V()
