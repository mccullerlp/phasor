from __future__ import (division, print_function)
from os import path
import numpy as np
import declarative
import numpy.testing as np_test
import pytest
from declarative.bunch import (
    DeepBunch
)

from phasor.utilities.np import logspaced
from phasor import system

from ligo_sled import (
    LIGOBasicOperation
)
import pickle


try:
    stresstest = pytest.mark.skipif(
        not pytest.config.getoption("--do-stresstest"),
        reason="need --do-stresstest option to run"
    )
except AttributeError:
    #needed for importing when py.test isn't in test mode
    stresstest = lambda x : x

@stresstest
def test_LIGO_noise_inversion():
    with open(path.join(path.split(__file__)[0], 'aLIGO_outspec.pckl'), 'rb') as F:
        output = declarative.Bunch(pickle.load(F))

    def test_inverse():
        db = DeepBunch()
        db.det.input.PSL.power.val = 27 * 7
        db.det.input.PSL.power.units = 'W'
        db.det.LIGO.S_BS_IX.L_detune.val = 1064e-9 * .001
        db.det.LIGO.S_BS_IX.L_detune.units = 'm'
        db.det.output.AS_efficiency_percent = 85
        db.environment.F_AC.frequency.val = logspaced(.5, 10000, 1000)
        sys = system.BGSystem(
            ctree = db,
            solver_name = 'loop_LUQ',
        )
        sys.own.det = LIGOBasicOperation()

        print(sys.det.LIGO.YarmDC.DC_readout)
        print(sys.det.LIGO.XarmDC.DC_readout)
        print(sys.det.LIGO.REFLDC.DC_readout)
        print(sys.det.LIGO.POPTrueDC.DC_readout)
        print(sys.det.output.ASPD_DC.DC_readout)

        readoutI = sys.det.output.ASPDHD_AC
        ASPDHD_AC_nls = readoutI.AC_noise_limited_sensitivity

        rel = (ASPDHD_AC_nls / output.ASPDHD_AC_nls).real
        print("RELMINMAX: ", np.min(rel), np.max(rel))
        np_test.assert_almost_equal(
            rel, 1, 2
        )
    for i in range(20):
        test_inverse()


