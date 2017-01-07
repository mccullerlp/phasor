"""
"""

from __future__ import division
from __future__ import print_function

import numpy as np

from declarative.bunch import (
    Bunch,
)

from BGSF.optics import (
    Mirror,
    PD,
    MagicPD,
    Space,
    Laser,
)

from BGSF.system.optical import (
    OpticalSystem
)

from BGSF.readouts import (
    DCReadout,
    ACReadout,
)

from unittest import TestCase, main
#from YALL.utilities.np import logspaced

def gensys(
    L_detune_m = -1e-10,
    no_ac      = False,
    L_m        = 1,
    T1         = .001,
    T2         = .001,
):
    R1 = 1 - T1
    R2 = 1 - T1

    sys = OpticalSystem(
        freq_order_max_default = 40,
    )
    sled = sys.sled
    sled.laser = Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
        name = "Laser",
    )

    sled.itm = Mirror(
        T_hr=.001,
        name = 'ITM',
        facing_cardinal = 'E',
    )
    sled.etm = Mirror(
        T_hr=.001,
        name = 'ETM',
        facing_cardinal = 'W',
    )

    sled.s1 = Space(
        L_m,
        L_detune_m = L_detune_m,
        name = 's1',
    )

    sled.reflPD = MagicPD(
        name = 'reflPD',
        facing_cardinal = 'E',
    )
    sled.itmPD = MagicPD(
        name = 'ITMPD',
        facing_cardinal = 'W',
    )
    sled.etmPD = MagicPD(
        name = 'ETMPD',
        facing_cardinal = 'E',
    )
    sled.transPD = PD(
        name = 'transmon',
    )

    sys.optical_link_sequence_WtoE(
        sled.laser,
        sled.reflPD,
        sled.itm,
        sled.itmPD,
        sled.s1,
        sled.etmPD,
        sled.etm,
        sled.transPD
    )

    sled.refl_DC     = DCReadout(port = sled.reflPD.Wpd.o)
    sled.transmon_DC = DCReadout(port = sled.transPD.Wpd.o)
    sled.etm_DC      = DCReadout(port = sled.etmPD.Wpd.o)
    sled.itm_DC      = DCReadout(port = sled.itmPD.Wpd.o)
    sled.itm_ForceZ  = DCReadout(port = sled.itm.forceZ.o)
    sled.etm_ForceZ  = DCReadout(port = sled.etm.forceZ.o)

    if not no_ac:
        sled.ETM_Drive = ACReadout(portD = sled.etm.posZ.i, portN = sled.etmPD.Wpd.o)
        sled.ITM_Drive = ACReadout(portD = sled.etm.posZ.i, portN = sled.itmPD.Wpd.o)

    #analytic sensitivity calculations
    k          = 2 * np.pi * sys.F_carrier_1064.iwavelen_m
    d          = 1 + R1 * R2 - 2 * (R1 * R2)**.5 * np.cos(2*k*(L_detune_m))
    PcavITM    = 1 * T1/d
    dPcavITMdL = -4*T1*(R1 * R2)**.5 * k * np.sin(2 * k * (L_detune_m)) / d**2
    return Bunch(locals())


class TestFabryPerot(TestCase):
    def test_FP_base(self):
        print('test_FP_base')
        b = gensys(
            L_detune_m = -1e-10,
        )
        #F_AC_Hz = logspaced(.001, 1e6, 100)
        sys = b.sys
        #sys.solve_to_order(1)
        #print("BUILDING THE REST")
        sol = sys.solve()
        #sys.coupling_matrix_print()
        #sys.source_vector_print()
        #sys.solution_vector_print()
        print("refl_DC",      sol.views.refl_DC.DC_readout     )
        print("transmon_DC",  sol.views.transmon_DC.DC_readout )
        print("itm_DC",       sol.views.itm_DC.DC_readout      )
        print("etm_DC",       sol.views.etm_DC.DC_readout      )
        print("etm_Force[N]", sol.views.etm_ForceZ.DC_readout  )

        self.assertAlmostEqual(sol.views.refl_DC.DC_readout    , 0.582198960706    , 7 )
        self.assertAlmostEqual(sol.views.transmon_DC.DC_readout, 0.417801039293    , 7 )
        self.assertAlmostEqual(sol.views.itm_DC.DC_readout     , 417.801039293     , 7 )
        self.assertAlmostEqual(sol.views.etm_DC.DC_readout     , 417.383238254     , 7 )
        self.assertAlmostEqual(sol.views.etm_ForceZ.DC_readout , -2.78587453006e-06, 7 )

        #sys.coupling_matrix_print(select_from = b.etm.posZ.i, select_to = b.etm.Fr.o)
        #sys.coupling_matrix_print(
        #    #select_from = b.etm.Fr.o,
        #    select_to = b.etmPD.Wpd.o,
        #)

        #print('inverse')
        #sys.coupling_matrix_inv_print(
        #    select_from = b.etm.Fr.o,
        #    select_to = b.etm.Fr.o,
        #)
        #sys.coupling_matrix_inv_print(
        #    select_from = b.etm.posZ.i,
        #    select_to = b.etm.Fr.o,
        #)

        #from BGSF.optics.dictionary_keys import (
        #    DictKey,
        #    FrequencyKey,
        #)
        #from BGSF.optics.optical_elements import (
        #    OpticalFreqKey, ClassicalFreqKey,
        #    LOWER, RAISE,
        #)
        #rt_inv = sys.invert_system()
        #usb_keyL = DictKey({OpticalFreqKey: FrequencyKey(b.laser.optical_f_dict), ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})}) | b.laser.polarization | LOWER
        #usb_keyR = DictKey({OpticalFreqKey: FrequencyKey(b.laser.optical_f_dict), ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})}) | b.laser.polarization | RAISE
        #lsb_keyL = DictKey({OpticalFreqKey: FrequencyKey(b.laser.optical_f_dict), ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})}) | b.laser.polarization | LOWER
        #lsb_keyR = DictKey({OpticalFreqKey: FrequencyKey(b.laser.optical_f_dict), ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})}) | b.laser.polarization | RAISE
        #ucl_key = DictKey({ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})})
        #lcl_key = DictKey({ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})})
        #print("USBLU: ", rt_inv.get((b.etm.Fr.o, usb_keyL), (b.etm.posZ.i, ucl_key), 0))
        #print("USBRU: ", rt_inv.get((b.etm.Fr.o, usb_keyR), (b.etm.posZ.i, ucl_key), 0))
        #print("USBLL: ", rt_inv.get((b.etm.Fr.o, usb_keyL), (b.etm.posZ.i, lcl_key), 0))
        #print("USBRL: ", rt_inv.get((b.etm.Fr.o, usb_keyR), (b.etm.posZ.i, lcl_key), 0))
        #print("LSBLL: ", rt_inv.get((b.etm.Fr.o, lsb_keyL), (b.etm.posZ.i, lcl_key), 0))
        #print("LSBRL: ", rt_inv.get((b.etm.Fr.o, lsb_keyR), (b.etm.posZ.i, lcl_key), 0))
        #print("LSBLU: ", rt_inv.get((b.etm.Fr.o, lsb_keyL), (b.etm.posZ.i, ucl_key), 0))
        #print("LSBRU: ", rt_inv.get((b.etm.Fr.o, lsb_keyR), (b.etm.posZ.i, ucl_key), 0))

        AC = sol.views.ETM_Drive.AC_sensitivity
        print("AC:", AC)

        #from YALL.utilities.mpl.autoniceplot import (mplfigB)
        #F = mplfigB(Nrows = 2)
        #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
        #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC))
        #F.save('trans_xfer')

    def test_FP_DC(self):
        print('test_FP_DC')
        from test_FP import gensys
        b = gensys(
            L_detune_m = 0,
            no_ac = True,
        )
        sys = b.sys
        sol = sys.solve()
        #sol.coupling_matrix_print()
        #sol.source_vector_print()
        #print()
        #sol.solution_vector_print()
        print("refl_DC",      sol.views.refl_DC.DC_readout)
        print("transmon_DC",  sol.views.transmon_DC.DC_readout)
        print("itm_DC",       sol.views.itm_DC.DC_readout)
        print("etm_DC",       sol.views.etm_DC.DC_readout)
        print("etm_Force[N]", sol.views.etm_ForceZ.DC_readout)

        self.assertAlmostEqual(sol.views.refl_DC.DC_readout    , 1.21042817297e-26 , 7 )
        self.assertAlmostEqual(sol.views.transmon_DC.DC_readout, 1.0               , 7 )
        self.assertAlmostEqual(sol.views.itm_DC.DC_readout     , 1000.0            , 7 )
        self.assertAlmostEqual(sol.views.etm_DC.DC_readout     , 999.0             , 7 )
        self.assertAlmostEqual(sol.views.etm_ForceZ.DC_readout , -6.66794542869e-06, 7 )

    def test_FP_sensitivity(self):
        print('test_FP_sensitivity')
        from test_FP import gensys
        b = gensys(
            L_detune_m = np.linspace(-1e-9, 1e-9, 1),
        )
        sys = b.sys
        sol = sys.solve()

        print("refl_DC",      sol.views.refl_DC.DC_readout)
        print("transmon_DC",  sol.views.transmon_DC.DC_readout)
        print()
        print("itm_DC",       sol.views.itm_DC.DC_readout)
        print("itm_DC_calc",  b.PcavITM)
        self.assertAlmostEqual(sol.views.itm_DC.DC_readout , b.PcavITM, 7 )
        print()
        print("etm_DC",       sol.views.etm_DC.DC_readout)
        print("etm_Force[N]", sol.views.etm_ForceZ.DC_readout)

        AC = sol.views.ITM_Drive.AC_sensitivity
        print("AC:", AC)
        print ("AC ratio: ", AC / b.dPcavITMdL)
        self.assertAlmostEqual(AC , b.dPcavITMdL, 1 )

    def test_FP_OOA(self):
        print('test_FP_OOA')
        from test_FP import gensys
        b = gensys()
        sys = b.sys
        import pprint
        pp = pprint.PrettyPrinter()
        print("OOA")
        pp.pprint(sys.ooa_params)

if __name__ == '__main__':
    main()
