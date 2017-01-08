"""
"""
from __future__ import (division, print_function)

from unittest import TestCase, main

#import numpy as np

from BGSF.optics import (
    PD,
    Laser,
    OpticalCirculator,
)

from BGSF.optics.bases import (
    OpticalCouplerBase,
    SystemElementBase,
)

from BGSF.system.optical import (
    OpticalSystem
)

from BGSF.readouts import (
    DCReadout,
)

from BGSF.optics.faraday_isolator import (
    FaradayIsolator,
)

import pytest
pytestmark = pytest.mark.skip('Faraday still WIP')
pytest.skip("Want to skip!")

class FaradayTestSled(
    OpticalCouplerBase, SystemElementBase
):
    def __init__(
            self,
            PSL_pol = 'S',
            **kwargs
    ):
        super(FaradayTestSled, self).__init__(**kwargs)

        self.PSL = Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            polarization = PSL_pol,
        )

        self.faraday = FaradayIsolator(
            pol_from = 'S',
            pol_to   = 'S',
        )

        self.circulator_Fr      = OpticalCirculator(N_ports = 3)
        self.circulator_Bk      = OpticalCirculator(N_ports = 3)
        self.circulator_Fr_Prej = OpticalCirculator(N_ports = 3)
        self.circulator_Bk_Prej = OpticalCirculator(N_ports = 3)
        self.circulator_Fr_ins  = OpticalCirculator(N_ports = 3)

        self.PD_Fr      = PD()
        self.PD_Bk      = PD()
        self.PD_Fr_Prej = PD()
        self.PD_Bk_Prej = PD()
        self.PD_Fr_ins  = PD()

        self.system.link(self.circulator_Fr.P2,      self.PD_Fr.Fr     )
        self.system.link(self.circulator_Bk.P2,      self.PD_Bk.Fr     )
        self.system.link(self.circulator_Fr_Prej.P2, self.PD_Fr_Prej.Fr)
        self.system.link(self.circulator_Bk_Prej.P2, self.PD_Bk_Prej.Fr)
        self.system.link(self.circulator_Fr_ins.P2,  self.PD_Fr_ins.Fr )

        self.system.link(self.circulator_Fr.P1,      self.faraday.Fr     )
        self.system.link(self.circulator_Bk.P1,      self.faraday.Bk     )
        self.system.link(self.circulator_Fr_Prej.P1, self.faraday.Fr_Prej)
        self.system.link(self.circulator_Bk_Prej.P1, self.faraday.Bk_Prej)
        self.system.link(self.circulator_Fr_ins.P1,  self.faraday.Fr_ins )

        self.DC_Fr      = DCReadout(port = self.PD_Fr.Wpd.o,      )
        self.DC_Bk      = DCReadout(port = self.PD_Bk.Wpd.o,      )
        self.DC_Fr_Prej = DCReadout(port = self.PD_Fr_Prej.Wpd.o, )
        self.DC_Bk_Prej = DCReadout(port = self.PD_Bk_Prej.Wpd.o, )
        self.DC_Fr_ins  = DCReadout(port = self.PD_Fr_ins.Wpd.o,  )


class TestFaradayIsolator(TestCase):
    def test_inj(self):
        sys = OpticalSystem()
        sys.sled.test = FaradayTestSled(PSL_pol = 'S')
        sys.link(sys.sled.test.PSL.Fr, sys.sled.test.circulator_Fr.P0)
        sol = sys.solve()

        print("DC_Fr     : ", sol.views.test.DC_Fr.DC_readout)
        print("DC_Bk     : ", sol.views.test.DC_Bk.DC_readout)
        print("DC_Fr_Prej: ", sol.views.test.DC_Fr_Prej.DC_readout)
        print("DC_Bk_Prej: ", sol.views.test.DC_Bk_Prej.DC_readout)
        print("DC_Fr_ins : ", sol.views.test.DC_Fr_ins.DC_readout)
        self.assertAlmostEqual(sol.views.test.DC_Fr.DC_readout, 0)
        self.assertAlmostEqual(sol.views.test.DC_Bk.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_Fr_Prej.DC_readout, 0)
        self.assertAlmostEqual(sol.views.test.DC_Bk_Prej.DC_readout, 0)
        self.assertAlmostEqual(sol.views.test.DC_Fr_ins.DC_readout, 0)


if __name__ == '__main__':
    main()
