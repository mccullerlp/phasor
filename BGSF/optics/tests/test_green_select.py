"""
"""
from __future__ import (division, print_function)

import numpy.testing as np_test
import declarative as decl
from declarative.bunch import (
    DeepBunch,
)

#import numpy as np

from BGSF import system
from BGSF import readouts
from BGSF import optics
from BGSF.utilities.print import pprint

#from BGSF.utilities.np import logspaced

class RedGreenSelectTester(
    optics.OpticalCouplerBase, optics.SystemElementBase
):
    def __build__(self):
        super(RedGreenSelectTester, self).__build__()
        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 2.,
            polarization = 'S',
        )

        self.my.PSLG = optics.Laser(
            F = self.system.F_carrier_1064,
            multiple = 2,
            power_W = 1.,
            polarization = 'S',
        )

        self.my.mDC1 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 1,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
            ),
            AOI_deg = 45,
        )
        self.my.mDC2 = optics.HarmonicMirror(
            mirror_H1 = optics.Mirror(
                T_hr = 1,
            ),
            mirror_H2 = optics.Mirror(
                T_hr = 0,
            ),
            AOI_deg = 45,
        )
        self.my.PD_R = optics.PD()
        self.my.PD_G = optics.PD()

        self.system.bond_sequence(
            self.PSL.Fr,
            self.mDC1.FrA,
            self.mDC2.FrA,
            self.PD_R.Fr,
        )
        self.system.bond_sequence(
            self.PSLG.Fr,
            self.mDC1.BkB,
        )
        self.system.bond_sequence(
            self.mDC2.FrB,
            self.PD_G.Fr,
        )
        self.my.DC_R = readouts.DCReadout(
            port = self.PD_R.Wpd.o,
        )
        self.my.DC_G = readouts.DCReadout(
            port = self.PD_G.Wpd.o,
        )


def test_split():
    sys = system.BGSystem()
    sys.my.test = RedGreenSelectTester()
    print("A")
    pprint(sys.ooa_params.test.PSL)
    np_test.assert_almost_equal(sys.test.DC_R.DC_readout, 2)
    np_test.assert_almost_equal(sys.test.DC_G.DC_readout, 1)


if __name__ == '__main__':
    main()
