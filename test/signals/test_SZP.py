"""
"""
from __future__ import (division, print_function)
#import pytest
import declarative
import numpy as np
import numpy.testing as np_test

import phasor.signals as signals
import phasor.readouts as readouts
import phasor.system as system

from phasor.utilities.np import logspaced

from phasor.utilities.print import pprint

import phasor.math.dispatched as dmath


def test_Xfer():
    #with explicit terminator
    sys = system.BGSystem(
        F_AC = np.linspace(0, 10, 10)
    )
    sys.own.X1 = signals.SRationalFilter(
        poles_r = (-1, ),
        gain    = 1,
    )
    sys.own.R1 = readouts.ACReadout(
        portN = sys.X1.ps_Out.o,
        portD = sys.X1.ps_In.i,
    )
    compare = 1/(1 + 1j*sys.F_AC.F_Hz.val)
    np_test.assert_almost_equal(sys.R1.AC_sensitivity / compare, 1)
    return


def test_XFer_fit():
    db = declarative.DeepBunch()
    db.symbols.math = dmath
    sys = system.BGSystem(
        F_AC = logspaced(0.1, 100, 10),
        ctree = db,
        exact_order = 5,
    )
    sys.own.X1 = signals.SRationalFilter(
        #poles_c = (-2 - 10j, ),
        zeros_r = (-10, -10),
        gain    = 1.1,
    )
    sys.own.R1 = readouts.ACReadout(
        portN = sys.X1.ps_Out.o,
        portD = sys.X1.ps_In.i,
    )

    size = len(sys.R1.F_Hz.val)
    relscale = .01
    AC_data = sys.R1.AC_sensitivity * (
        2
        + np.random.normal(0, relscale, size)
        + 1j*np.random.normal(0, relscale, size)
    )
    #print(sys.X1.ctree_as_yaml())

    import phasor.fitting.casadi as FIT
    import phasor.fitting.casadi.transfer_functions as FIT_TF
    froot = FIT.FitterRoot()
    froot.own.sym = FIT.FitterSym()
    froot.systems.xfer = sys
    froot.sym.parameter(sys.X1)
    froot.own.residual = FIT_TF.TransferACExpression(
        ACData = AC_data,
        ACReadout = sys.R1,
        SNR_weights = 1/relscale,
    )
    #print("VAR: ", froot.fit_systems.xfer.R1.AC_sensitivity)
    #pprint(froot.fit_systems.xfer.ctree.extractidx('previous'))
    #pprint(froot.fit_systems.xfer.X1.gain.ref)
    #pprint(froot.fit_systems.xfer.X1.gain.val)
    minimized = froot.residual.minimize_function()
    #print(minimized)
    xsys = froot.fit_systems.xfer
    #print("AC_sensitivity", xsys.R1.AC_sensitivity)

    np_test.assert_almost_equal(minimized.systems.xfer.R1.AC_sensitivity / sys.R1.AC_sensitivity, 2, 1)
    return


if __name__ == '__main__':
    test_XFer_fit()
