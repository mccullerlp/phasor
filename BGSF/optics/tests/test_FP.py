"""
"""
from __future__ import (division, print_function)
import numpy as np
import numpy.testing as test
import pytest


from declarative import (
    Bunch,
)

from BGSF.utilities.print import pprint

from BGSF import system
from BGSF import optics
from BGSF import readouts


def gensys(
    L_detune_m = -1e-10,
    no_ac      = False,
    L_m        = 1,
    T1         = .001,
    T2         = .001,
):
    R1 = 1 - T1
    R2 = 1 - T1

    sys = system.BGSystem(
        freq_order_max_default = 40,
    )
    sys = sys
    sys.my.laser = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
    )

    sys.my.itm = optics.Mirror(
        T_hr=.001,
    )
    sys.my.etm = optics.Mirror(
        T_hr=.001,
    )

    sys.my.s1 = optics.Space(
        L_m = L_m,
        L_detune_m = L_detune_m,
    )

    sys.my.reflPD = optics.MagicPD()
    sys.my.itmPD = optics.MagicPD()
    sys.my.etmPD = optics.MagicPD()
    sys.my.transPD = optics.PD()

    sys.bond_sequence(
        sys.laser.Fr,
        sys.reflPD.Bk,
        sys.itm.Bk,
        sys.itmPD.Fr,
        sys.s1.Fr,
        sys.etmPD.Bk,
        sys.etm.Fr,
        sys.transPD.Fr,
    )

    sys.my.refl_DC     = readouts.DCReadout(port = sys.reflPD.Wpd.o)
    sys.my.transmon_DC = readouts.DCReadout(port = sys.transPD.Wpd.o)
    sys.my.etm_DC      = readouts.DCReadout(port = sys.etmPD.Wpd.o)
    sys.my.itm_DC      = readouts.DCReadout(port = sys.itmPD.Wpd.o)
    sys.my.itm_ForceZ  = readouts.DCReadout(port = sys.itm.forceZ.o)
    sys.my.etm_ForceZ  = readouts.DCReadout(port = sys.etm.forceZ.o)

    if not no_ac:
        sys.my.ETM_Drive = readouts.ACReadout(portD = sys.etm.posZ.i, portN = sys.etmPD.Wpd.o)
        sys.my.ITM_Drive = readouts.ACReadout(portD = sys.etm.posZ.i, portN = sys.itmPD.Wpd.o)

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
    pprint(sys)
    print("Detune [m]: ", b.sys.s1.L_detune_m)
    print("refl_DC",      sys.refl_DC.DC_readout     )
    print("transmon_DC",  sys.transmon_DC.DC_readout )
    print("itm_DC",       sys.itm_DC.DC_readout      )
    print("etm_DC",       sys.etm_DC.DC_readout      )
    print("etm_Force[N]", sys.etm_ForceZ.DC_readout  )

    test.assert_almost_equal(sys.refl_DC.DC_readout    , 0.582198960706    , 7 )
    test.assert_almost_equal(sys.transmon_DC.DC_readout, 0.417801039293    , 7 )
    test.assert_almost_equal(sys.itm_DC.DC_readout     , 417.801039293     , 7 )
    test.assert_almost_equal(sys.etm_DC.DC_readout     , 417.383238254     , 7 )
    test.assert_almost_equal(sys.etm_ForceZ.DC_readout , -2.78587453006e-06, 7 )

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

    AC = sys.ETM_Drive.AC_sensitivity
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
    print("refl_DC",      sys.refl_DC.DC_readout)
    print("transmon_DC",  sys.transmon_DC.DC_readout)
    print("itm_DC",       sys.itm_DC.DC_readout)
    print("etm_DC",       sys.etm_DC.DC_readout)
    print("etm_Force[N]", sys.etm_ForceZ.DC_readout)

    test.assert_almost_equal(sys.refl_DC.DC_readout    , 1.21042817297e-26 , 7 )
    test.assert_almost_equal(sys.transmon_DC.DC_readout, 1.0               , 7 )
    test.assert_almost_equal(sys.itm_DC.DC_readout     , 1000.0            , 7 )
    test.assert_almost_equal(sys.etm_DC.DC_readout     , 999.0             , 7 )
    test.assert_almost_equal(sys.etm_ForceZ.DC_readout , -6.66794542869e-06, 7 )

def test_FP_sensitivity():
    print('test_FP_sensitivity')
    from test_FP import gensys
    b = gensys(
        L_detune_m = np.linspace(-1e-9, 1e-9, 1),
    )
    sys = b.sys
    sol = sys.solve()

    print("refl_DC",      sys.refl_DC.DC_readout)
    print("transmon_DC",  sys.transmon_DC.DC_readout)
    print()
    print("itm_DC",       sys.itm_DC.DC_readout)
    print("itm_DC_calc",  b.PcavITM)
    test.assert_almost_equal(sys.itm_DC.DC_readout , b.PcavITM, 7 )
    print()
    print("etm_DC",       sys.etm_DC.DC_readout)
    print("etm_Force[N]", sys.etm_ForceZ.DC_readout)

    AC = sys.ITM_Drive.AC_sensitivity
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
