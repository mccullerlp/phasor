# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import numpy.testing as np_test
import numpy as np
import declarative as decl
from declarative.bunch import (
    DeepBunch,
)

#import numpy as np

from phasor import system
from phasor import readouts
from phasor import optics
from phasor.optics.nonlinear_crystal import NonlinearCrystal
from phasor.utilities.print import pprint

#from phasor.utilities.np import logspaced


def test_split():
    sys = system.BGSystem()
    sys.own.PSL = optics.Laser(
        F = sys.system.F_carrier_1064,
        power_W = 2.,
    )

    sys.own.PSLG = optics.Laser(
        F = sys.system.F_carrier_1064,
        multiple = 2,
        power_W = 1.,
    )

    sys.own.mDC1 = optics.HarmonicMirror(
        mirror_H1 = optics.Mirror(
            T_hr = 1,
        ),
        mirror_H2 = optics.Mirror(
            T_hr = 0,
        ),
        AOI_deg = 45,
    )
    sys.own.mDC2 = optics.HarmonicMirror(
        mirror_H1 = optics.Mirror(
            T_hr = 1,
        ),
        mirror_H2 = optics.Mirror(
            T_hr = 0,
        ),
        AOI_deg = 45,
    )
    sys.own.PD_R = optics.PD()
    sys.own.PD_G = optics.PD()

    sys.system.bond_sequence(
        sys.PSL.po_Fr,
        sys.mDC1.po_FrA,
        sys.mDC2.po_FrA,
        sys.PD_R.po_Fr,
    )
    sys.system.bond_sequence(
        sys.PSLG.po_Fr,
        sys.mDC1.po_BkB,
    )
    sys.system.bond_sequence(
        sys.mDC2.po_FrB,
        sys.PD_G.po_Fr,
    )
    sys.own.DC_R = readouts.DCReadout(
        port = sys.PD_R.Wpd.o,
    )
    sys.own.DC_G = readouts.DCReadout(
        port = sys.PD_G.Wpd.o,
    )
    print("pm_A")
    pprint(sys.ctree.test.PSL)
    np_test.assert_almost_equal(sys.DC_R.DC_readout, 2)
    np_test.assert_almost_equal(sys.DC_G.DC_readout, 1)


#def test_shg():
#    sys = system.BGSystem()
#    sys.own.PSL = optics.Laser(
#        F = sys.system.F_carrier_1064,
#        power_W = 1.,
#    )
#
#    sys.own.ktp = NonlinearCrystal(
#        nlg = 1,
#        length_mm = 1,
#        N_ode = 1000,
#        solution_order = 4,
#    )
#
#    sys.own.mDC2 = optics.HarmonicMirror(
#        mirror_H1 = optics.Mirror(
#            T_hr = 1,
#        ),
#        mirror_H2 = optics.Mirror(
#            T_hr = 0,
#        ),
#        AOI_deg = 45,
#    )
#    sys.own.PD_R = optics.PD()
#    sys.own.PD_G = optics.PD()
#
#    sys.system.bond_sequence(
#        sys.PSL.po_Fr,
#        sys.ktp.po_Fr,
#        sys.mDC2.po_FrA,
#        sys.PD_R.po_Fr,
#    )
#    sys.system.bond_sequence(
#        sys.mDC2.po_FrB,
#        sys.PD_G.po_Fr,
#    )
#    sys.own.DC_R = readouts.DCReadout(
#        port = sys.PD_R.Wpd.o,
#    )
#    sys.own.DC_G = readouts.DCReadout(
#        port = sys.PD_G.Wpd.o,
#    )
#    #print("pm_A")
#    #pprint(sys.ctree.test.PSL)
#    print("sys.DC_R.DC_readout", sys.DC_R.DC_readout, 2)
#    print("sys.DC_G.DC_readout", sys.DC_G.DC_readout, 1)
#    conv = 0.069527636785009506
#    conv = 1 - np.tanh(2)**2
#    np_test.assert_almost_equal(sys.DC_R.DC_readout / conv, 1, 2)
#    np_test.assert_almost_equal(sys.DC_G.DC_readout / (1 - conv), 1, 2)


def test_aom():
    from phasor.optics.models.AOMTestStand import AOMTestStand
    db = DeepBunch()
    sys = system.BGSystem(
        ctree = db,
    )
    sys.own.test = AOMTestStand()
    db = sys.ctree_shadow()
    sys.test.LO.amplitude
    print(sys.test.DC_R1.DC_readout)

if __name__ == '__main__':
    main()
