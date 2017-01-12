"""
"""
from __future__ import (division, print_function)
from unittest import TestCase, main

try:
    from IPython.lib.pretty import pprint
except ImportError:
    from pprint import pprint

#import numpy as np

from declarative.bunch import (
    DeepBunch,
)

from BGSF.optics import (
    Mirror,
    PD,
    Laser,
    HalfWavePlate,
    QuarterWavePlate,
    OpticalCirculator,
    FaradayRotator,
)

from BGSF.optics.bases import (
    OpticalCouplerBase,
    SystemElementBase,
    OOA_ASSIGN,
)

from BGSF.system.optical import (
    OpticalSystem
)

from BGSF.readouts import (
    DCReadout,
)

from BGSF.optics.selective_mirrors import (
    PolarizingMirror,
)

#from BGSF.utilities.np import logspaced

class PolTester(
    OpticalCouplerBase, SystemElementBase
):
    def __init__(self, **kwargs):
        super(PolTester, self).__init__(**kwargs)
        self.my.PSL = Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            polarization = 'S',
        )

        self.my.mBS = PolarizingMirror(
            mirror_S = Mirror(
                T_hr = 0,
            ),
            mirror_P = Mirror(
                T_hr = 1,
            ),
            AOI_deg = 45,
            facing_cardinal = 'NW',
        )
        self.my.PD_S = PD()
        self.my.PD_P = PD()

        self.system.optical_link_sequence_WtoE(
            self.PSL,
            self.mBS,
            self.PD_P,
        )
        self.system.optical_link_sequence_StoN(
            self.mBS,
            self.PD_S,
        )

        self.my.DC_P = DCReadout(
            port = self.PD_P.Wpd.o,
        )
        self.my.DC_S = DCReadout(
            port = self.PD_S.Wpd.o,
        )


class WavePlateTester(
    OpticalCouplerBase, SystemElementBase
):
    def __init__(self, **kwargs):
        super(WavePlateTester, self).__init__(**kwargs)
        self.my.PSL = Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            polarization = 'S',
        )

        OOA_ASSIGN(self).waveplate_type = 'half'

        if self.waveplate_type == 'half':
            self.my.waveplate = HalfWavePlate(
                facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'quarter':
            self.my.waveplate = QuarterWavePlate(
                facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'faraday':
            self.my.waveplate = FaradayRotator(
                rotate_deg = 0
            )

        self.my.mBS = PolarizingMirror(
            mirror_S = Mirror(
                T_hr = 0,
            ),
            mirror_P = Mirror(
                T_hr = 1,
            ),
            AOI_deg = 45,
            facing_cardinal = 'NW',
        )
        self.my.PD_S = PD()
        self.my.PD_P = PD()

        self.system.optical_link_sequence_WtoE(
            self.PSL,
            self.waveplate,
            self.mBS,
            self.PD_P,
        )
        self.system.optical_link_sequence_StoN(
            self.mBS,
            self.PD_S,
        )

        self.my.DC_P = DCReadout(
            port = self.PD_P.Wpd.o,
        )
        self.my.DC_S = DCReadout(
            port = self.PD_S.Wpd.o,
        )


class WavePlateTesterRetro(
    OpticalCouplerBase, SystemElementBase
):
    def __init__(self, **kwargs):
        super(WavePlateTesterRetro, self).__init__(**kwargs)
        self.my.PSL = Laser(
            F = self.system.F_carrier_1064,
            power_W = 1.,
            polarization = 'S',
        )

        OOA_ASSIGN(self).waveplate_type = 'half'

        self.my.circulator = OpticalCirculator(N_ports = 3)

        if self.waveplate_type == 'half':
            self.my.waveplate = HalfWavePlate(
                facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'quarter':
            self.my.waveplate = QuarterWavePlate(
                facing_cardinal = 'W',
            )
        elif self.waveplate_type == 'faraday':
            self.my.waveplate = FaradayRotator(
                rotate_deg = 0,
            )

        self.my.reflector = Mirror(
            T_hr = 0,
            facing_cardinal = 'W',
        )
        self.my.mBS = PolarizingMirror(
            mirror_S = Mirror(
                T_hr = 0,
            ),
            mirror_P = Mirror(
                T_hr = 1,
            ),
            AOI_deg = 45,
            facing_cardinal = 'NW',
        )
        self.my.PD_S = PD()
        self.my.PD_P = PD()

        self.system.optical_link_sequence_WtoE(
            self.PSL,
            self.circulator.P0,
        )
        self.system.optical_link_sequence_WtoE(
            self.circulator.P1,
            self.waveplate,
            self.reflector,
        )
        self.system.optical_link_sequence_WtoE(
            self.circulator.P2,
            self.mBS,
            self.PD_P,
        )
        self.system.optical_link_sequence_StoN(
            self.mBS,
            self.PD_S,
        )

        self.my.DC_P = DCReadout(
            port = self.PD_P.Wpd.o,
        )
        self.my.DC_S = DCReadout(
            port = self.PD_S.Wpd.o,
        )


class TestPolarizations(TestCase):
    def test_split(self):
        sys = OpticalSystem()
        sys.sled.my.test = PolTester()
        print("A")
        pprint(sys.ooa_params.test.PSL)
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.PSL.polarization = 'P'
        sys = OpticalSystem(
            ooa_params = db,
        )
        sys.sled.my.test = PolTester()
        sol = sys.solve()
        print("B")
        pprint(db)
        pprint(sys.ooa_params.test.PSL)

        print("DC_S:", sol.views.test.DC_S.DC_readout)
        print("DC_P:", sol.views.test.DC_P.DC_readout)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 0)

    def test_waveplate(self):
        sys = OpticalSystem()
        sys.sled.my.test = WavePlateTester()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db = DeepBunch()
        db.test.waveplate.rotate_deg = 90
        sys = OpticalSystem(
            ooa_params = db,
        )
        sys.sled.my.test = WavePlateTester()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate_deg = 45
        sys = OpticalSystem(
            ooa_params = db,
        )
        sys.sled.my.test = WavePlateTester()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 1)

    def test_waveplateQ(self):
        db = DeepBunch()
        db.test.waveplate_type = 'quarter'

        db.test.waveplate.rotate_deg = 0
        sys = OpticalSystem()
        sys.sled.my.test = WavePlateTester()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db.test.waveplate.rotate_deg = 90
        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTester()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)

        db.test.waveplate.rotate_deg = 45
        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTester()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, .5)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, .5)

    def test_waveplateF(self):
        db = DeepBunch()
        db.test.waveplate_type = 'faraday'

        db.test.waveplate.rotate_deg = 0
        sys = OpticalSystem()
        sys.sled.my.test = WavePlateTester()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db.test.waveplate.rotate_deg = 90
        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTester()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate_deg = 45
        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTester()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, .5)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, .5)

    def test_waveplate_retro(self):
        sys = OpticalSystem()
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db = DeepBunch()
        db.test.waveplate.rotate_deg = 90
        sys = OpticalSystem(
            ooa_params = db,
        )
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate_deg = 45
        sys = OpticalSystem(
            ooa_params = db,
        )
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate_deg = 11
        sys = OpticalSystem(
            ooa_params = db,
        )
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)

        db = DeepBunch()
        db.test.waveplate.rotate_deg = 232
        sys = OpticalSystem(
            ooa_params = db,
        )
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)

    def test_waveplate_retro_quarter(self):
        db = DeepBunch()
        db.test.waveplate_type = 'quarter'

        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db.test.waveplate.rotate_deg = 90
        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)

        db.test.waveplate.rotate_deg = 45
        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate_deg = -45
        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 1)

    def test_waveplate_retro_faraday(self):
        db = DeepBunch()
        db.test.waveplate_type = 'faraday'

        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)
        pprint(sys.ooa_params.test.waveplate)

        db.test.waveplate.rotate_deg = 90
        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 1)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 0)

        db.test.waveplate.rotate_deg = 45
        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate_deg = -45
        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, 0)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, 1)

        db.test.waveplate.rotate_deg = 45/2
        sys = OpticalSystem(ooa_params = db)
        sys.sled.my.test = WavePlateTesterRetro()
        sol = sys.solve()
        self.assertAlmostEqual(sol.views.test.DC_S.DC_readout, .5)
        self.assertAlmostEqual(sol.views.test.DC_P.DC_readout, .5)



if __name__ == '__main__':
    main()
