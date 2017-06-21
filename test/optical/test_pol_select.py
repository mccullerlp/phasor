"""
"""
from __future__ import (division, print_function)
from unittest import TestCase, main

import declarative as decl
from declarative.bunch import (
    DeepBunch,
)

#import numpy as np

from phasor import system
from phasor import readouts
from phasor import optics
from phasor.utilities.print import pprint

#from phasor.utilities.np import logspaced

class PolTester(
    optics.OpticalCouplerBase, optics.SystemElementBase
):
    def __init__(self, **kwargs):
        super(PolTester, self).__init__(**kwargs)
        self.own.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            polarization = 'S',
        )

        self.own.mBS = optics.PolarizingMirror(
            mirror_S = optics.Mirror(
                T_hr = 0,
            ),
            mirror_P = optics.Mirror(
                T_hr = 1,
            ),
            AOI_deg = 45,
        )
        self.own.PD_S = optics.PD()
        self.own.PD_P = optics.PD()

        self.system.bond_sequence(
            self.PSL.po_Fr,
            self.mBS.po_FrA,
            self.PD_P.po_Fr,
        )
        self.system.bond_sequence(
            self.mBS.po_FrB,
            self.PD_S.po_Fr,
        )

        self.own.DC_P = readouts.DCReadout(
            port = self.PD_P.Wpd.o,
        )
        self.own.DC_S = readouts.DCReadout(
            port = self.PD_S.Wpd.o,
        )


class WavePlateTester(
    optics.OpticalCouplerBase, optics.SystemElementBase
):
    @decl.dproperty
    def waveplate_type(self, val = 'half'):
        val = self.ctree.setdefault('waveplate_type', 'half')
        return val

    def __init__(self, **kwargs):
        super(WavePlateTester, self).__init__(**kwargs)
        self.own.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            polarization = 'S',
        )

        if self.waveplate_type == 'half':
            self.own.waveplate = optics.HalfWavePlate(
                #facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'quarter':
            self.own.waveplate = optics.QuarterWavePlate(
                #facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'faraday':
            self.own.waveplate = optics.FaradayRotator(
                rotate_deg = 0
            )

        self.own.mBS = optics.PolarizingMirror(
            mirror_S = optics.Mirror(
                T_hr = 0,
            ),
            mirror_P = optics.Mirror(
                T_hr = 1,
            ),
            AOI_deg = 45,
            #facing_cardinal = 'NW',
        )
        self.own.PD_S = optics.PD()
        self.own.PD_P = optics.PD()

        self.system.bond_sequence(
            self.PSL.po_Fr,
            self.waveplate.po_Fr,
            self.mBS.po_FrA,
            self.PD_P.po_Fr,
        )
        self.system.bond_sequence(
            self.mBS.po_FrB,
            self.PD_S.po_Fr,
        )

        self.own.DC_P = readouts.DCReadout(
            port = self.PD_P.Wpd.o,
        )
        self.own.DC_S = readouts.DCReadout(
            port = self.PD_S.Wpd.o,
        )


class WavePlateTesterRetro(
    optics.OpticalCouplerBase, optics.SystemElementBase
):
    @decl.dproperty
    def waveplate_type(self, val = 'half'):
        val = self.ctree.setdefault('waveplate_type', 'half')
        return val

    def __init__(self, **kwargs):
        super(WavePlateTesterRetro, self).__init__(**kwargs)
        self.own.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            polarization = 'S',
        )

        self.own.circulator = optics.OpticalCirculator(N_ports = 3)

        if self.waveplate_type == 'half':
            self.own.waveplate = optics.HalfWavePlate(
                #facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'quarter':
            self.own.waveplate = optics.QuarterWavePlate(
                #facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'faraday':
            self.own.waveplate = optics.FaradayRotator(
                rotate_deg = 0,
            )

        self.own.reflector = optics.Mirror(
            T_hr = 0,
            #facing_cardinal = 'W',
        )
        self.own.mBS = optics.PolarizingMirror(
            mirror_S = optics.Mirror(
                T_hr = 0,
            ),
            mirror_P = optics.Mirror(
                T_hr = 1,
            ),
            AOI_deg = 45,
            #facing_cardinal = 'NW',
        )
        self.own.PD_S = optics.PD()
        self.own.PD_P = optics.PD()

        self.system.bond_sequence(
            self.PSL.po_Fr,
            self.circulator.P0,
        )
        self.system.bond_sequence(
            self.circulator.P1,
            self.waveplate.po_Fr,
            self.reflector.po_Fr,
        )
        self.system.bond_sequence(
            self.circulator.P2,
            self.mBS.po_FrA,
            self.PD_P.po_Fr,
        )
        self.system.bond_sequence(
            self.mBS.po_FrB,
            self.PD_S.po_Fr,
        )

        self.own.DC_P = readouts.DCReadout(
            port = self.PD_P.Wpd.o,
        )
        self.own.DC_S = readouts.DCReadout(
            port = self.PD_S.Wpd.o,
        )


class TestPolarizations(TestCase):
    def test_split(self):
        sys = system.BGSystem()
        sys.own.test = PolTester()
        print("pm_A")
        pprint(sys.ctree.test.PSL)
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.PSL.polarization = 'P'
        sys = system.BGSystem(
            ctree = db,
        )
        sys.own.test = PolTester()
        print("pm_B")
        pprint(db)
        pprint(sys.ctree.test.PSL)

        print("DC_S:", sys.test.DC_S.DC_readout)
        print("DC_P:", sys.test.DC_P.DC_readout)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)

    def test_waveplate(self):
        sys = system.BGSystem()
        sys.own.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ctree.test.waveplate)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(
            ctree = db,
        )
        sys.own.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(
            ctree = db,
        )
        sys.own.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

    def test_waveplateQ(self):
        db = DeepBunch()
        db.test.waveplate_type = 'quarter'

        db.test.waveplate.rotate.val = 0
        sys = system.BGSystem()
        sys.own.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ctree.test.waveplate)

        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, .5)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, .5)

    def test_waveplateF(self):
        db = DeepBunch()
        db.test.waveplate_type = 'faraday'

        db.test.waveplate.rotate.val = 0
        sys = system.BGSystem()
        sys.own.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ctree.test.waveplate)

        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, .5)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, .5)

    def test_waveplate_retro(self):
        sys = system.BGSystem()
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ctree.test.waveplate)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(
            ctree = db,
        )
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(
            ctree = db,
        )
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 11
        sys = system.BGSystem(
            ctree = db,
        )
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 232
        sys = system.BGSystem(
            ctree = db,
        )
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

    def test_waveplate_retro_quarter(self):
        db = DeepBunch()
        db.test.waveplate_type = 'quarter'

        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ctree.test.waveplate)

        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate.val = -45
        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

    def test_waveplate_retro_faraday(self):
        db = DeepBunch()
        db.test.waveplate_type = 'faraday'

        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ctree.test.waveplate)

        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate.val = -45
        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate.val = 45/2
        sys = system.BGSystem(ctree = db)
        sys.own.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, .5)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, .5)


if __name__ == '__main__':
    main()
