# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

from unittest import TestCase, main

#import numpy as np

from phasor import system
from phasor import optics
from phasor import readouts

import pytest
pytestmark = pytest.mark.skip('Faraday still WIP')
#pytest.skip("Want to skip!")

class FaradayTestSled(
    optics.OpticalCouplerBase, optics.SystemElementBase
):
    def __init__(
            self,
            PSL_pol = 'S',
            **kwargs
    ):
        super(FaradayTestSled, self).__init__(**kwargs)

        self.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            polarization = PSL_pol,
        )

        self.faraday = optics.FaradayIsolator(
            pol_from = 'S',
            pol_to   = 'S',
        )

        self.circulator_Fr      = optics.OpticalCirculator(N_ports = 3)
        self.circulator_Bk      = optics.OpticalCirculator(N_ports = 3)
        self.circulator_Fr_Prej = optics.OpticalCirculator(N_ports = 3)
        self.circulator_Bk_Prej = optics.OpticalCirculator(N_ports = 3)
        self.circulator_Fr_ins  = optics.OpticalCirculator(N_ports = 3)

        self.PD_Fr      = optics.PD()
        self.PD_Bk      = optics.PD()
        self.PD_Fr_Prej = optics.PD()
        self.PD_Bk_Prej = optics.PD()
        self.PD_Fr_ins  = optics.PD()

        self.system.bond(self.circulator_Fr.P2,      self.PD_Fr.po_Fr     )
        self.system.bond(self.circulator_Bk.P2,      self.PD_Bk.po_Fr     )
        self.system.bond(self.circulator_Fr_Prej.P2, self.PD_Fr_Prej.po_Fr)
        self.system.bond(self.circulator_Bk_Prej.P2, self.PD_Bk_Prej.po_Fr)
        self.system.bond(self.circulator_Fr_ins.P2,  self.PD_Fr_ins.po_Fr )

        self.system.bond(self.circulator_Fr.P1,      self.faraday.po_Fr     )
        self.system.bond(self.circulator_Bk.P1,      self.faraday.po_Bk     )
        self.system.bond(self.circulator_Fr_Prej.P1, self.faraday.Fr_Prej)
        self.system.bond(self.circulator_Bk_Prej.P1, self.faraday.Bk_Prej)
        self.system.bond(self.circulator_Fr_ins.P1,  self.faraday.Fr_ins )

        self.DC_Fr      = readouts.DCReadout(port = self.PD_Fr.Wpd.o,      )
        self.DC_Bk      = readouts.DCReadout(port = self.PD_Bk.Wpd.o,      )
        self.DC_Fr_Prej = readouts.DCReadout(port = self.PD_Fr_Prej.Wpd.o, )
        self.DC_Bk_Prej = readouts.DCReadout(port = self.PD_Bk_Prej.Wpd.o, )
        self.DC_Fr_ins  = readouts.DCReadout(port = self.PD_Fr_ins.Wpd.o,  )


class TestFaradayIsolator(TestCase):
    def test_inj(self):
        sys = system.BGSystem()
        sys.test = FaradayTestSled(PSL_pol = 'S')
        sys.link(sys.test.PSL.po_Fr, sys.test.circulator_Fr.P0)
        sol = sys.solve()

        print("DC_Fr     : ", sys.test.DC_Fr.DC_readout)
        print("DC_Bk     : ", sys.test.DC_Bk.DC_readout)
        print("DC_Fr_Prej: ", sys.test.DC_Fr_Prej.DC_readout)
        print("DC_Bk_Prej: ", sys.test.DC_Bk_Prej.DC_readout)
        print("DC_Fr_ins : ", sys.test.DC_Fr_ins.DC_readout)
        self.assertAlmostEqual(sys.test.DC_Fr.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_Bk.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_Fr_Prej.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_Bk_Prej.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_Fr_ins.DC_readout, 0)


if __name__ == '__main__':
    main()
