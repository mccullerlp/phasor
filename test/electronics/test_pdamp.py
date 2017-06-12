"""
"""
from __future__ import (division, print_function)
import pytest
import numpy.testing as test

from declarative import Bunch

import openLoop.electronics as electronics
import openLoop.readouts as readouts
import openLoop.system as system
from openLoop.electronics.models.PDAmp import PDTransimpedance


#pytest.mark.parametrize('gain', [(1), (10), (100)])
def test_PD_amp():
    sys = system.BGSystem()
    sys.own.pd = PDTransimpedance()
    t_gain = (10e3 * (-1e6 + 1) / 1e6)
    test.assert_almost_equal(sys.pd.VOutTrans_AC.AC_sensitivity / t_gain, 1)


if __name__ == '__main__':
    test_PD_amp()