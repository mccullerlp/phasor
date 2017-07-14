# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

from phasor import system
from phasor import optics

import pytest
pytestmark = pytest.mark.skip('optics.EZSqz still WIP')
#pytest.skip("Want to skip!")

#from phasor.utilities.np import logspaced


def gensys(
        F_AC_Hz,
        loss_EM = 0,
        loss_BS = 0,
):
    sys = system.BGSystem()
    sled = sys
    sled.sqz = optics.EZSqz(
        rel_variance_1 = .1,
        rel_variance_2 = 12,
    )
    sled.sqz = optics.EZSqz(
        nonlinear_power_gain = 10,
        loss = .1,
    )

    sled.laser = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
        name = "PSL",
    )

    sled.mX = optics.Mirror(
        T_hr = 0,
        L_hr = loss_EM,
        name = 'mX',
        facing_cardinal = 'W',
    )
    sled.mY = optics.Mirror(
        T_hr = 0,
        L_hr = loss_EM,
        name = 'mY',
        facing_cardinal = 'S',
    )
    #T_hr = sys.optical_harmonic_value(.3),
    sled.mBS = optics.Mirror(
        T_hr = .5,
        L_hr = loss_BS,
        AOI_deg = 45,
        facing_cardinal = 'NW',
    )

    sled.sX = optics.Space(
        1,
        L_detune_m = 1064e-9 / 8,
        name = 'sX',
    )
    sled.sY = optics.Space(
        1,
        L_detune_m = 0,
        name = 'sY',
    )

    sled.symPD = optics.MagicPD(
        name = 'symPD',
        facing_cardinal = 'E',
    )
    sled.asymPD = optics.PD(
        name = 'asymPD',
    )

    #sys.link(laser.po_Fr, symPD.po_Bk)
    #sys.link(symPD.po_Fr, mBS.po_FrA)
    #sys.link(mBS.po_FrB, sY.po_Fr)
    #sys.link(sY.po_Bk, mY.po_Fr)
    #sys.link(mBS.po_BkA, sX.po_Fr)
    #sys.link(sX.po_Bk, mX.po_Fr)
    #sys.link(mBS.po_BkB, asymPD.po_Fr)
    sys.optical_link_sequence_WtoE(
        sled.laser, sled.symPD, sled.mBS, sled.sX, sled.mX,
    )
    sys.optical_link_sequence_StoN(
        sled.asymPD, sled.mBS, sled.sY, sled.mY,
    )

    #vterm = VacuumTerminator(name = 'vterm')
    #sys.optical_link_sequence_StoN(
    #    vterm, mBS,
    #)

    sys.AC_freq(F_AC_Hz)
    sys.DC_readout_add('sym_DC', sled.symPD.Wpd.o)
    sys.DC_readout_add('asym_DC', sled.asymPD.Wpd.o)
    sys.AC_sensitivity_add('asym_Drive', sled.mX.posZ.i, sled.asymPD.Wpd.o)
    return declarative.Bunch(locals())

def test_mich():
    b = gensys(
        #F_AC_Hz = logspaced(.001, 1e6, 10),
        F_AC_Hz = np.array([0]),
    )
    sys = b.sys
    sys.solve_to_order(1, no_AC = True)
    print()
    sys.solve_to_order(2)
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sys.solution_vector_print()
    print("sym_DC",  sys.DC_readout('sym_DC'))
    print("asym_DC", sys.DC_readout('asym_DC'))

    ptot = sys.DC_readout('sym_DC') + sys.DC_readout('asym_DC')
    pfrac = sys.DC_readout('asym_DC') / ptot
    sense = (pfrac * (1-pfrac))**.5 * 4 * np.pi * sys.F_carrier_1064.iwavelen_m

    AC = sys.AC_sensitivity('asym_Drive')
    print("ACmag:", abs(AC) / sense)
    print("ACdeg:", np.angle(AC, deg = True))

    E1064_J = 1.2398 / 1.064 / 6.24e18
    N_expect = (sys.DC_readout('asym_DC') * E1064_J)**.5
    AC_noise = sys.AC_noise('asym_Drive')
    print("ACnoise", AC_noise)
    print("ACnoise_rel", (N_expect / AC_noise)**2)

    #sys.port_set_print(b.mBS.po_BkB.i)
    #sys.port_set_print(b.vterm.po_Fr.o)
    #sys.coupling_matrix_inv_print(select_to = b.asymPD.Wpd.o)

    #from phasor.utilities.mpl.autoniceplot import (mplfigB)
    #F = mplfigB(Nrows = 2)
    #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
    #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC, deg = True))
    #F.save('trans_xfer_mich')

def test_mich_lossy():
    b = gensys(
        #F_AC_Hz = logspaced(.001, 1e6, 10),
        F_AC_Hz = np.array([0]),
        #loss_EM = .2,
        loss_BS = .2,
    )
    sys = b.sys
    sys.solve_to_order(1, no_AC = True)
    print()
    sys.solve_to_order(2)
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sys.solution_vector_print()
    print("sym_DC",  sys.DC_readout('sym_DC'))
    print("asym_DC", sys.DC_readout('asym_DC'))

    ptot = sys.DC_readout('sym_DC') + sys.DC_readout('asym_DC')
    pfrac = sys.DC_readout('asym_DC') / ptot
    sense = (pfrac * (1-pfrac))**.5 * 4 * np.pi * sys.F_carrier_1064.iwavelen_m

    AC = sys.AC_sensitivity('asym_Drive')
    print("ACmag:", abs(AC) / sense)
    print("ACdeg:", np.angle(AC, deg = True))

    E1064_J = 1.2398 / 1.064 / 6.24e18
    N_expect = (sys.DC_readout('asym_DC') * E1064_J)**.5
    AC_noise = sys.AC_noise('asym_Drive')
    print("ACnoise", AC_noise)
    print("ACnoise_rel", (N_expect / AC_noise)**2)

    sys.port_set_print(b.mX._LFr.i)
    #print("X")
    #sys.coupling_matrix_inv_print(select_from = b.mBS._LBkB.i)

    #print("X")
    #sys.coupling_matrix_print(select_to = b.mBS._LFrB.i)

    #from phasor.utilities.mpl.autoniceplot import (mplfigB)
    #F = mplfigB(Nrows = 2)
    #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
    #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC, deg = True))
    #F.save('trans_xfer_mich')

if __name__ == '__main__':
    test_mich()
