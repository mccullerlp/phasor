"""
"""
from __future__ import (division, print_function)
#import pytest
import numpy as np
import numpy.testing as test

import openLoop.signals as signals
import openLoop.readouts as readouts
import openLoop.system as system

from openLoop.utilities.np import logspaced


def test_Xfer():
    #with explicit terminator
    sys = system.BGSystem(
        F_AC = np.linspace(0, 10, 10)
    )
    sys.my.X1 = signals.SRationalFilter(
        poles_r = (-1, ),
        gain    = 1,
    )
    sys.my.R1 = readouts.ACReadout(
        portN = sys.X1.Out.o,
        portD = sys.X1.In.i,
    )
    compare = 1/(1 + 1j*sys.F_AC.F_Hz.val)
    test.assert_almost_equal(sys.R1.AC_sensitivity / compare, 1)
    return


def test_XFer_fit():
    sys = system.BGSystem(
        F_AC = logspaced(0.1, 100, 10)
    )
    sys.my.X1 = signals.SRationalFilter(
        #poles_c = (-2 - 10j, ),
        zeros_r = (-10, -10),
        gain    = 1,
    )
    sys.my.R1 = readouts.ACReadout(
        portN = sys.X1.Out.o,
        portD = sys.X1.In.i,
    )

    size = len(sys.R1.F_Hz.val)
    relscale = .1
    AC_data = sys.R1.AC_sensitivity * (
        1
        + np.random.normal(0, relscale, size) 
        + 1j*np.random.normal(0, relscale, size)
    )
    print(sys.X1.ooa_as_yaml())

    import openLoop.fitting.casadi as FIT
    import openLoop.fitting.casadi.transfer_functions as FIT_TF
    froot = FIT.FitterRoot()
    froot.my.sym = FIT.FitterSym()
    froot.systems.xfer = sys
    froot.sym.parameter(sys.X1)
    froot.my.residual = FIT_TF.TransferACExpression(
        ACData = AC_data,
        ACReadout = sys.R1,
        SNR_weights = 1/relscale,
    )
    return froot.residual.minimize_function()


if __name__ == '__main__':
    test_V()
