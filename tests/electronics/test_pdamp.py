"""
"""
from __future__ import (division, print_function)
import pytest
import numpy.testing as test

from declarative import Bunch

import OpenLoop.electronics as electronics
import OpenLoop.readouts as readouts
import OpenLoop.system as system
from OpenLoop.electronics.models.PDAmp import PDTransimpedance


#pytest.mark.parametrize('gain', [(1), (10), (100)])
def test_PD_amp():
    sys = system.BGSystem()
    sys.my.pd = PDTransimpedance()
    t_gain = (10e3 * (-1e6 + 1) / 1e6)
    test.assert_almost_equal(sys.pd.VOutTrans_AC.AC_sensitivity / t_gain, 1)


if __name__ == '__main__':
    test_PD_amp()
