"""
"""
from __future__ import (division, print_function)
import numpy as np
import numpy.testing as test
import pytest

try:
    from IPython.lib.pretty import pprint
except ImportError:
    from pprint import pprint

from declarative import (
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
    sled.my.laser = Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
    )

    sled.my.itm = Mirror(
        T_hr=.001,
    )
    sled.my.etm = Mirror(
        T_hr=.001,
    )

    sled.my.s1 = Space(
        L_m = L_m,
        L_detune_m = L_detune_m,
    )

    sled.my.reflPD = MagicPD()
    sled.my.itmPD = MagicPD()
    sled.my.etmPD = MagicPD()
    sled.my.transPD = PD()

    sys.bond_sequence(
        sled.laser.Fr,
        sled.reflPD.Bk,
        sled.itm.Bk,
        sled.itmPD.Fr,
        sled.s1.Fr,
        sled.etmPD.Bk,
        sled.etm.Fr,
        sled.transPD.Fr,
    )

    sled.my.refl_DC     = DCReadout(port = sled.reflPD.Wpd.o)
    sled.my.transmon_DC = DCReadout(port = sled.transPD.Wpd.o)
    sled.my.etm_DC      = DCReadout(port = sled.etmPD.Wpd.o)
    sled.my.itm_DC      = DCReadout(port = sled.itmPD.Wpd.o)
    sled.my.itm_ForceZ  = DCReadout(port = sled.itm.forceZ.o)
    sled.my.etm_ForceZ  = DCReadout(port = sled.etm.forceZ.o)

    if not no_ac:
        sled.my.ETM_Drive = ACReadout(portD = sled.etm.posZ.i, portN = sled.etmPD.Wpd.o)
        sled.my.ITM_Drive = ACReadout(portD = sled.etm.posZ.i, portN = sled.itmPD.Wpd.o)

    #analytic sensitivity calculations
    k          = 2 * np.pi * sys.F_carrier_1064.iwavelen_m
    d          = 1 + R1 * R2 - 2 * (R1 * R2)**.5 * np.cos(2*k*(L_detune_m))
    PcavITM    = 1 * T1/d
    dPcavITMdL = -4*T1*(R1 * R2)**.5 * k * np.sin(2 * k * (L_detune_m)) / d**2
    return Bunch(locals())


@pytest.mark.optics_fast
def test_FP_base():
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
    pprint(sys.sled)
    print("Detune [m]: ", b.sys.sled.s1.L_detune_m)
    print("refl_DC",      sys.sled.refl_DC.DC_readout     )
    print("transmon_DC",  sys.sled.transmon_DC.DC_readout )
    print("itm_DC",       sys.sled.itm_DC.DC_readout      )
    print("etm_DC",       sys.sled.etm_DC.DC_readout      )
    print("etm_Force[N]", sys.sled.etm_ForceZ.DC_readout  )

    test.assert_almost_equal(sys.sled.refl_DC.DC_readout    , 0.582198960706    , 7 )
    test.assert_almost_equal(sys.sled.transmon_DC.DC_readout, 0.417801039293    , 7 )
    test.assert_almost_equal(sys.sled.itm_DC.DC_readout     , 417.801039293     , 7 )
    test.assert_almost_equal(sys.sled.etm_DC.DC_readout     , 417.383238254     , 7 )
    test.assert_almost_equal(sys.sled.etm_ForceZ.DC_readout , -2.78587453006e-06, 7 )

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

    AC = sys.sled.ETM_Drive.AC_sensitivity
    print("AC:", AC)

    #from BGSF.utilities.mpl.autoniceplot import (mplfigB)
    #F = mplfigB(Nrows = 2)
    #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
    #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC))
    #F.save('trans_xfer')

def test_FP_DC():
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
    print("refl_DC",      sys.sled.refl_DC.DC_readout)
    print("transmon_DC",  sys.sled.transmon_DC.DC_readout)
    print("itm_DC",       sys.sled.itm_DC.DC_readout)
    print("etm_DC",       sys.sled.etm_DC.DC_readout)
    print("etm_Force[N]", sys.sled.etm_ForceZ.DC_readout)

    test.assert_almost_equal(sys.sled.refl_DC.DC_readout    , 1.21042817297e-26 , 7 )
    test.assert_almost_equal(sys.sled.transmon_DC.DC_readout, 1.0               , 7 )
    test.assert_almost_equal(sys.sled.itm_DC.DC_readout     , 1000.0            , 7 )
    test.assert_almost_equal(sys.sled.etm_DC.DC_readout     , 999.0             , 7 )
    test.assert_almost_equal(sys.sled.etm_ForceZ.DC_readout , -6.66794542869e-06, 7 )

def test_FP_sensitivity():
    print('test_FP_sensitivity')
    from test_FP import gensys
    b = gensys(
        L_detune_m = np.linspace(-1e-9, 1e-9, 1),
    )
    sys = b.sys
    sol = sys.solve()

    print("refl_DC",      sys.sled.refl_DC.DC_readout)
    print("transmon_DC",  sys.sled.transmon_DC.DC_readout)
    print()
    print("itm_DC",       sys.sled.itm_DC.DC_readout)
    print("itm_DC_calc",  b.PcavITM)
    test.assert_almost_equal(sys.sled.itm_DC.DC_readout , b.PcavITM, 7 )
    print()
    print("etm_DC",       sys.sled.etm_DC.DC_readout)
    print("etm_Force[N]", sys.sled.etm_ForceZ.DC_readout)

    AC = sys.sled.ITM_Drive.AC_sensitivity
    print("AC:", AC)
    print ("AC ratio: ", AC / b.dPcavITMdL)
    test.assert_almost_equal(AC , b.dPcavITMdL, 1 )

def test_FP_OOA():
    print('test_FP_OOA')
    from test_FP import gensys
    b = gensys()
    sys = b.sys
    import pprint
    pp = pprint.PrettyPrinter()
    print("OOA")
    pp.pprint(sys.ooa_params)

if __name__ == '__main__':
    test_FP_base()
