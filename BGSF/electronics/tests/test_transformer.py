"""
"""
from __future__ import (division, print_function)
import pytest
import numpy.testing as test
import numpy as np

from declarative import Bunch

import BGSF.electronics as electronics
import BGSF.readouts as readouts

from BGSF.system.optical import (
    OpticalSystem
)

import unittest
assertions = unittest.TestCase('__init__')


def test_transformer():
    sys = OpticalSystem()
    sled = sys.sled
    sys.F_AC.F_Hz = 100.
    sled.my.V1 = electronics.VoltageSource()
    sled.my.Tr1 = electronics.Transformer(
        L1_inductance_Henries = 1e-6,
        L2_inductance_Henries = 100e-6,
    )
    sys.bond(sled.Tr1.A, sled.V1.A)
    sled.my.Tr1BT = electronics.TerminatorMatched()
    sys.bond(sled.Tr1.B, sled.Tr1BT.A)
    sled.my.Tr1CT = electronics.TerminatorOpen()
    sys.bond(sled.Tr1.C, sled.Tr1CT.A)
    sled.my.Tr1DT = electronics.TerminatorMatched()
    sys.bond(sled.Tr1.D, sled.Tr1DT.A)

    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.V1.A,
    )
    sled.my.RAC1 = readouts.ACReadout(
        portD = sled.V1.V.i,
        portN = sled.R1.V.o,
    )
    sled.my.R2 = electronics.VoltageReadout(
        terminal = sled.Tr1.C,
    )
    sled.my.RAC2 = readouts.ACReadout(
        portD = sled.V1.V.i,
        portN = sled.R2.V.o,
    )

    test.assert_almost_equal(sled.RAC1.AC_sensitivity, 1)
    test.assert_almost_equal(abs(sled.RAC2.AC_sensitivity), 10)

def test_transformer2():
    sys = OpticalSystem()
    sled = sys.sled
    sys.F_AC.F_Hz = 100.
    sled.my.V1 = electronics.VoltageSource()
    sled.my.Tr1 = electronics.Transformer(
        L1_inductance_Henries = 1e-6,
        L2_inductance_Henries = 100e-6,
    )
    sys.bond(sled.Tr1.A, sled.V1.A)
    sled.my.Tr1BT = electronics.TerminatorResistor(
        resistance_Ohms = 1,
    )
    sys.bond(sled.Tr1.B, sled.Tr1BT.A)
    sled.my.Tr1CT = electronics.TerminatorOpen()
    sys.bond(sled.Tr1.C, sled.Tr1CT.A)
    sled.my.Tr1DT = electronics.TerminatorResistor(
        resistance_Ohms = np.linspace(.00001, 1e6, 10)
    )
    sys.bond(sled.Tr1.D, sled.Tr1DT.A)

    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.V1.A,
    )
    sled.my.RAC1 = readouts.ACReadout(
        portD = sled.V1.V.i,
        portN = sled.R1.V.o,
    )
    sled.my.R2 = electronics.VoltageReadout(
        terminal = sled.Tr1.C,
    )
    sled.my.RAC2 = readouts.ACReadout(
        portD = sled.V1.V.i,
        portN = sled.R2.V.o,
    )

    test.assert_almost_equal(abs(sled.RAC1.AC_sensitivity), 1)
    test.assert_almost_equal(abs(sled.RAC2.AC_sensitivity), 10)


def test_transformer_stepdown():
    sys = OpticalSystem()
    sled = sys.sled
    sys.F_AC.F_Hz = 100.
    sled.my.V1 = electronics.VoltageSource()
    sled.my.Tr1 = electronics.Transformer(
        L1_inductance_Henries = 100e-6,
        L2_inductance_Henries = 1e-6,
        #transformer_k_by_freq = lambda F : .99,
    )
    sys.bond(sled.Tr1.A, sled.V1.A)
    sled.my.Tr1BT = electronics.TerminatorResistor(
        resistance_Ohms = 1,
    )
    sys.bond(sled.Tr1.B, sled.Tr1BT.A)
    sled.my.Tr1CT = electronics.TerminatorOpen()
    sys.bond(sled.Tr1.C, sled.Tr1CT.A)
    sled.my.Tr1DT = electronics.TerminatorResistor(
        resistance_Ohms = np.linspace(.00001, 1e6, 10)
    )
    sys.bond(sled.Tr1.D, sled.Tr1DT.A)

    sled.my.R1 = electronics.VoltageReadout(
        terminal = sled.V1.A,
    )
    sled.my.RAC1 = readouts.ACReadout(
        portD = sled.V1.V.i,
        portN = sled.R1.V.o,
    )
    sled.my.R2 = electronics.VoltageReadout(
        terminal = sled.Tr1.C,
    )
    sled.my.RAC2 = readouts.ACReadout(
        portD = sled.V1.V.i,
        portN = sled.R2.V.o,
    )

    test.assert_almost_equal(abs(sled.RAC1.AC_sensitivity), 1)
    test.assert_almost_equal(abs(sled.RAC2.AC_sensitivity), 1/10)


if __name__ == '__main__':
    test_V()
