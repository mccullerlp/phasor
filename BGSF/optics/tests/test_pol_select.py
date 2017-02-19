"""
"""
from __future__ import (division, print_function)
from unittest import TestCase, main

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

class PolTester(
    optics.OpticalCouplerBase, optics.SystemElementBase
):
    def __init__(self, **kwargs):
        super(PolTester, self).__init__(**kwargs)
        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            polarization = 'S',
        )

        self.my.mBS = optics.PolarizingMirror(
            mirror_S = optics.Mirror(
                T_hr = 0,
            ),
            mirror_P = optics.Mirror(
                T_hr = 1,
            ),
            AOI_deg = 45,
        )
        self.my.PD_S = optics.PD()
        self.my.PD_P = optics.PD()

        self.system.bond_sequence(
            self.PSL.Fr,
            self.mBS.FrA,
            self.PD_P.Fr,
        )
        self.system.bond_sequence(
            self.mBS.FrB,
            self.PD_S.Fr,
        )

        self.my.DC_P = readouts.DCReadout(
            port = self.PD_P.Wpd.o,
        )
        self.my.DC_S = readouts.DCReadout(
            port = self.PD_S.Wpd.o,
        )


class WavePlateTester(
    optics.OpticalCouplerBase, optics.SystemElementBase
):
    @decl.dproperty
    def waveplate_type(self, val = 'half'):
        val = self.ooa_params.setdefault('waveplate_type', 'half')
        return val

    def __init__(self, **kwargs):
        super(WavePlateTester, self).__init__(**kwargs)
        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            polarization = 'S',
        )

        if self.waveplate_type == 'half':
            self.my.waveplate = optics.HalfWavePlate(
                #facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'quarter':
            self.my.waveplate = optics.QuarterWavePlate(
                #facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'faraday':
            self.my.waveplate = optics.FaradayRotator(
                rotate_deg = 0
            )

        self.my.mBS = optics.PolarizingMirror(
            mirror_S = optics.Mirror(
                T_hr = 0,
            ),
            mirror_P = optics.Mirror(
                T_hr = 1,
            ),
            AOI_deg = 45,
            #facing_cardinal = 'NW',
        )
        self.my.PD_S = optics.PD()
        self.my.PD_P = optics.PD()

        self.system.bond_sequence(
            self.PSL.Fr,
            self.waveplate.Fr,
            self.mBS.FrA,
            self.PD_P.Fr,
        )
        self.system.bond_sequence(
            self.mBS.FrB,
            self.PD_S.Fr,
        )

        self.my.DC_P = readouts.DCReadout(
            port = self.PD_P.Wpd.o,
        )
        self.my.DC_S = readouts.DCReadout(
            port = self.PD_S.Wpd.o,
        )


class WavePlateTesterRetro(
    optics.OpticalCouplerBase, optics.SystemElementBase
):
    @decl.dproperty
    def waveplate_type(self, val = 'half'):
        val = self.ooa_params.setdefault('waveplate_type', 'half')
        return val

    def __init__(self, **kwargs):
        super(WavePlateTesterRetro, self).__init__(**kwargs)
        self.my.PSL = optics.Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            polarization = 'S',
        )

        self.my.circulator = optics.OpticalCirculator(N_ports = 3)

        if self.waveplate_type == 'half':
            self.my.waveplate = optics.HalfWavePlate(
                #facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'quarter':
            self.my.waveplate = optics.QuarterWavePlate(
                #facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'faraday':
            self.my.waveplate = optics.FaradayRotator(
                rotate_deg = 0,
            )

        self.my.reflector = optics.Mirror(
            T_hr = 0,
            #facing_cardinal = 'W',
        )
        self.my.mBS = optics.PolarizingMirror(
            mirror_S = optics.Mirror(
                T_hr = 0,
            ),
            mirror_P = optics.Mirror(
                T_hr = 1,
            ),
            AOI_deg = 45,
            #facing_cardinal = 'NW',
        )
        self.my.PD_S = optics.PD()
        self.my.PD_P = optics.PD()

        self.system.bond_sequence(
            self.PSL.Fr,
            self.circulator.P0,
        )
        self.system.bond_sequence(
            self.circulator.P1,
            self.waveplate.Fr,
            self.reflector.Fr,
        )
        self.system.bond_sequence(
            self.circulator.P2,
            self.mBS.FrA,
            self.PD_P.Fr,
        )
        self.system.bond_sequence(
            self.mBS.FrB,
            self.PD_S.Fr,
        )

        self.my.DC_P = readouts.DCReadout(
            port = self.PD_P.Wpd.o,
        )
        self.my.DC_S = readouts.DCReadout(
            port = self.PD_S.Wpd.o,
        )


class TestPolarizations(TestCase):
    def test_split(self):
        sys = system.BGSystem()
        sys.my.test = PolTester()
        print("A")
        pprint(sys.ooa_params.test.PSL)
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.PSL.polarization = 'P'
        sys = system.BGSystem(
            ooa_params = db,
        )
        sys.my.test = PolTester()
        print("B")
        pprint(db)
        pprint(sys.ooa_params.test.PSL)

        print("DC_S:", sys.test.DC_S.DC_readout)
        print("DC_P:", sys.test.DC_P.DC_readout)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)

    def test_waveplate(self):
        sys = system.BGSystem()
        sys.my.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(
            ooa_params = db,
        )
        sys.my.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(
            ooa_params = db,
        )
        sys.my.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

    def test_waveplateQ(self):
        db = DeepBunch()
        db.test.waveplate_type = 'quarter'

        db.test.waveplate.rotate.val = 0
        sys = system.BGSystem()
        sys.my.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, .5)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, .5)

    def test_waveplateF(self):
        db = DeepBunch()
        db.test.waveplate_type = 'faraday'

        db.test.waveplate.rotate.val = 0
        sys = system.BGSystem()
        sys.my.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTester()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, .5)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, .5)

    def test_waveplate_retro(self):
        sys = system.BGSystem()
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(
            ooa_params = db,
        )
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(
            ooa_params = db,
        )
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 11
        sys = system.BGSystem(
            ooa_params = db,
        )
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate.val = 232
        sys = system.BGSystem(
            ooa_params = db,
        )
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

    def test_waveplate_retro_quarter(self):
        db = DeepBunch()
        db.test.waveplate_type = 'quarter'

        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate.val = -45
        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

    def test_waveplate_retro_faraday(self):
        db = DeepBunch()
        db.test.waveplate_type = 'faraday'

        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db.test.waveplate.rotate.val = 90
        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 0)

        db.test.waveplate.rotate.val = 45
        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate.val = -45
        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate.val = 45/2
        sys = system.BGSystem(ooa_params = db)
        sys.my.test = WavePlateTesterRetro()
        self.assertAlmostEqual(sys.test.DC_S.DC_readout, .5)
        self.assertAlmostEqual(sys.test.DC_P.DC_readout, .5)


if __name__ == '__main__':
    main()
