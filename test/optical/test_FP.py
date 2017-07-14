# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np
import numpy.testing as np_test
import pytest
import declarative

from phasor.utilities.print import pprint

from phasor import system
from phasor import optics
from phasor import readouts


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
    sys.own.laser = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
    )

    sys.own.itm = optics.Mirror(
        T_hr=.001,
    )
    sys.own.etm = optics.Mirror(
        T_hr=.001,
    )

    sys.own.s1 = optics.Space(
        L_m = L_m,
        L_detune_m = L_detune_m,
    )

    sys.own.reflPD = optics.MagicPD()
    sys.own.itmPD = optics.MagicPD()
    sys.own.etmPD = optics.MagicPD()
    sys.own.transPD = optics.PD()

    sys.bond_sequence(
        sys.laser.po_Fr,
        sys.reflPD.po_Bk,
        sys.itm.po_Bk,
        sys.itmPD.po_Fr,
        sys.s1.po_Fr,
        sys.etmPD.po_Bk,
        sys.etm.po_Fr,
        sys.transPD.po_Fr,
    )

    sys.own.refl_DC     = readouts.DCReadout(port = sys.reflPD.Wpd.o)
    sys.own.transmon_DC = readouts.DCReadout(port = sys.transPD.Wpd.o)
    sys.own.etm_DC      = readouts.DCReadout(port = sys.etmPD.Wpd.o)
    sys.own.itm_DC      = readouts.DCReadout(port = sys.itmPD.Wpd.o)
    sys.own.itm_ForceZ  = readouts.DCReadout(port = sys.itm.Z.F.i)
    sys.own.etm_ForceZ  = readouts.DCReadout(port = sys.etm.Z.F.i)

    if not no_ac:
        sys.own.ETM_Drive = readouts.ACReadout(portD = sys.etm.Z.d.o, portN = sys.etmPD.Wpd.o)
        sys.own.ITM_Drive = readouts.ACReadout(portD = sys.etm.Z.d.o, portN = sys.itmPD.Wpd.o)

    #analytic sensitivity calculations
    k          = 2 * np.pi * sys.F_carrier_1064.iwavelen_m
    d          = 1 + R1 * R2 - 2 * (R1 * R2)**.5 * np.cos(2*k*(L_detune_m))
    PcavITM    = 1 * T1/d
    dPcavITMdL = -4*T1*(R1 * R2)**.5 * k * np.sin(2 * k * (L_detune_m)) / d**2
    return declarative.Bunch(locals())


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

    np_test.assert_almost_equal(sys.refl_DC.DC_readout    , 0.582198960706    , 7 )
    np_test.assert_almost_equal(sys.transmon_DC.DC_readout, 0.417801039293    , 7 )
    np_test.assert_almost_equal(sys.itm_DC.DC_readout     , 417.801039293     , 7 )
    np_test.assert_almost_equal(sys.etm_DC.DC_readout     , 417.383238254     , 7 )
    np_test.assert_almost_equal(sys.etm_ForceZ.DC_readout , -2.78587453006e-06, 7 )

    #sys.coupling_matrix_print(select_from = b.etm.Z.d.o, select_to = b.etm.po_Fr.o)
    #sys.coupling_matrix_print(
    #    #select_from = b.etm.po_Fr.o,
    #    select_to = b.etmPD.Wpd.o,
    #)

    #print('inverse')
    #sys.coupling_matrix_inv_print(
    #    select_from = b.etm.po_Fr.o,
    #    select_to = b.etm.po_Fr.o,
    #)
    #sys.coupling_matrix_inv_print(
    #    select_from = b.etm.Z.d.o,
    #    select_to = b.etm.po_Fr.o,
    #)

    #from phasor.optics.dictionary_keys import (
    #    DictKey,
    #    FrequencyKey,
    #)
    #from phasor.optics.optical_elements import (
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
    #print("USBLU: ", rt_inv.get((b.etm.po_Fr.o, usb_keyL), (b.etm.Z.d.o, ucl_key), 0))
    #print("USBRU: ", rt_inv.get((b.etm.po_Fr.o, usb_keyR), (b.etm.Z.d.o, ucl_key), 0))
    #print("USBLL: ", rt_inv.get((b.etm.po_Fr.o, usb_keyL), (b.etm.Z.d.o, lcl_key), 0))
    #print("USBRL: ", rt_inv.get((b.etm.po_Fr.o, usb_keyR), (b.etm.Z.d.o, lcl_key), 0))
    #print("LSBLL: ", rt_inv.get((b.etm.po_Fr.o, lsb_keyL), (b.etm.Z.d.o, lcl_key), 0))
    #print("LSBRL: ", rt_inv.get((b.etm.po_Fr.o, lsb_keyR), (b.etm.Z.d.o, lcl_key), 0))
    #print("LSBLU: ", rt_inv.get((b.etm.po_Fr.o, lsb_keyL), (b.etm.Z.d.o, ucl_key), 0))
    #print("LSBRU: ", rt_inv.get((b.etm.po_Fr.o, lsb_keyR), (b.etm.Z.d.o, ucl_key), 0))

    AC = abs(sys.ETM_Drive.AC_sensitivity)
    print("AC:", AC)

    #from phasor.utilities.mpl.autoniceplot import (mplfigB)
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
    #sol.coupling_matrix_print()
    #sol.source_vector_print()
    #print()
    #sol.solution_vector_print()
    print("refl_DC",      sys.refl_DC.DC_readout)
    print("transmon_DC",  sys.transmon_DC.DC_readout)
    print("itm_DC",       sys.itm_DC.DC_readout)
    print("etm_DC",       sys.etm_DC.DC_readout)
    print("etm_Force[N]", sys.etm_ForceZ.DC_readout)

    np_test.assert_almost_equal(sys.refl_DC.DC_readout    , 1.21042817297e-26 , 7 )
    np_test.assert_almost_equal(sys.transmon_DC.DC_readout, 1.0               , 7 )
    np_test.assert_almost_equal(sys.itm_DC.DC_readout     , 1000.0            , 7 )
    np_test.assert_almost_equal(sys.etm_DC.DC_readout     , 999.0             , 7 )
    np_test.assert_almost_equal(sys.etm_ForceZ.DC_readout , -6.66794542869e-06, 7 )

def test_FP_sensitivity():
    print('test_FP_sensitivity')
    from test_FP import gensys
    b = gensys(
        L_detune_m = np.linspace(-1e-9, 1e-9, 1),
    )
    sys = b.sys

    print("refl_DC",      sys.refl_DC.DC_readout)
    print("transmon_DC",  sys.transmon_DC.DC_readout)
    print()
    print("itm_DC",       sys.itm_DC.DC_readout)
    print("itm_DC_calc",  b.PcavITM)
    np_test.assert_almost_equal(sys.itm_DC.DC_readout , b.PcavITM, 7 )
    print()
    print("etm_DC",       sys.etm_DC.DC_readout)
    print("etm_Force[N]", sys.etm_ForceZ.DC_readout)

    AC = abs(sys.ITM_Drive.AC_sensitivity)
    print("AC:", AC)
    print ("AC ratio: ", AC / b.dPcavITMdL)
    np_test.assert_almost_equal(AC , b.dPcavITMdL, 1 )

def test_FP_OOA():
    print('test_FP_OOA')
    from test_FP import gensys
    b = gensys()
    sys = b.sys
    import pprint
    pp = pprint.PrettyPrinter()
    print("OOA")
    pp.pprint(sys.ctree)

if __name__ == '__main__':
    test_FP_base()
