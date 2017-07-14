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

    sys.own.reflPD  = optics.MagicPD()
    sys.own.itmPD   = optics.MagicPD()
    sys.own.etmPD   = optics.MagicPD()
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

    sys.own.ETM_Drive = readouts.ACReadout(portD = sys.etm.posZ.i, portN = sys.etmPD.Wpd.o)
    sys.own.ITM_Drive = readouts.ACReadout(portD = sys.etm.posZ.i, portN = sys.itmPD.Wpd.o)

    #analytic sensitivity calculations
    k          = 2 * np.pi * sys.F_carrier_1064.iwavelen_m
    d          = 1 + R1 * R2 - 2 * (R1 * R2)**.5 * np.cos(2*k*(L_detune_m))
    PcavITM    = 1 * T1/d
    dPcavITMdL = -4*T1*(R1 * R2)**.5 * k * np.sin(2 * k * (L_detune_m)) / d**2
    return declarative.Bunch(locals())


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

    sys2 = sys.regenerate()
    AC2 = abs(sys2.ITM_Drive.AC_sensitivity)
    np_test.assert_almost_equal(AC2/AC, 1 )


if __name__ == '__main__':
    test_FP_sensitivity()
