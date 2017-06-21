"""
"""

from __future__ import (division, print_function)
import pytest
import declarative


import phasor.optics as optics
import phasor.readouts as readouts
from phasor import system

import unittest
assertions = unittest.TestCase('__init__')


#from phasor.utilities.np import logspaced

def gensys():
    sys = system.BGSystem()
    sys.own.laser = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
    )

    sys.own.etmPD = optics.MagicPD()

    sys.bond_sequence(
        sys.laser.po_Fr,
        sys.etmPD.po_Fr,
    )

    sys.own.etm_DC = readouts.DCReadout(port = sys.etmPD.Wpd.o)
    #sys.AC_freq(np.array([1]))
    return declarative.Bunch(locals())


def gensys_full():
    sys = system.BGSystem()
    sys = sys
    sys.own.laser = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
        name = "laser",
    )

    sys.own.etm = optics.Mirror(
        T_hr = 0.25,
    )
    sys.own.etmPD = optics.MagicPD()
    sys.own.s1 = optics.Space(
        L_m = 100,
        L_detune_m = 0,
    )

    sys.bond_sequence(
        sys.laser.po_Fr,
        sys.etmPD.po_Bk,
        sys.s1.po_Fr,
        sys.etm.po_Fr,
    )

    sys.own.etm_DC = readouts.DCReadout(port = sys.etmPD.Wpd.o)
    sys.own.etm_drive = readouts.ACReadout(
        portN = sys.etmPD.Wpd.o,
        portD = sys.etm.Z.d.o,
    )
    #sys.AC_freq(np.array([1]))
    return declarative.Bunch(locals())

@pytest.mark.optics_trivial
@pytest.mark.optics_fast
def test_trivial():
    b = gensys()
    sys = b.sys
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sys.solution.solution_vector_print()
    print("etm_DC", sys.etm_DC.DC_readout)
    assertions.assertAlmostEqual(sys.etm_DC.DC_readout, 1)


@pytest.mark.optics_fast
def test_mirror():
    b = gensys_full()
    sys = b.sys
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sys.solution.solution_vector_print()
    print("etm_DC", sys.etm_DC.DC_readout)
    print("etm_drive", sys.etm_drive.AC_sensitivity)
    #print("etm_Force[N]", sys.DC_readout('etm_ForceZ'))

    #print("pm_A")
    #sys.coupling_matrix_print(select_from = b.sys.etm.Z.d.o, select_to = b.sys.etm.po_Fr.o)
    #print("pm_B")
    #sys.solution.coupling_matrix_print(
    #    select_to= b.sys.etm.po_Fr.i,
    #)
    assertions.assertAlmostEqual(sys.etm_DC.DC_readout, .75)
    print("inv")
    #sys.solution.coupling_matrix_inv_print()
    print('pm_A')
    sys.solution.coupling_matrix_inv_print(
        select_from = b.sys.etm.Z.d.o,
        select_to = b.sys.etmPD.po_Fr.i,
    )
    print('pm_B')

    sys.solution.coupling_matrix_print(
        select_from = b.sys.etmPD.po_Fr.i,
        select_to = b.sys.etmPD.Wpd.o,
        drive_set = 'AC',
        readout_set = 'AC',
    )
    print('pm_B inv')
    sys.solution.coupling_matrix_inv_print(
        select_from = b.sys.etmPD.po_Fr.i,
        select_to = b.sys.etmPD.Wpd.o,
        drive_set = 'AC',
        readout_set = 'AC',
    )
    sys.solution.coupling_matrix_inv_print(
        select_from = b.sys.etm.Z.d.o,
        select_to = b.sys.etmPD.Wpd.o,
        drive_set = 'AC',
        readout_set = 'AC',
    )

    #from phasor.key_matrix import (
    #    DictKey,
    #    FrequencyKey,
    #)

    #rt_inv = sys.invert_system()
    #usb_keyL = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sys.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})}) | b.sys.laser.polarization | optics.LOWER
    #usb_keyR = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sys.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})}) | b.sys.laser.polarization | optics.RAISE
    #lsb_keyL = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sys.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})}) | b.sys.laser.polarization | optics.LOWER
    #lsb_keyR = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sys.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})}) | b.sys.laser.polarization | optics.RAISE
    #ucl_key = DictKey({optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})})
    #lcl_key = DictKey({optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})})
    #print("USBLU: ", rt_inv.get((b.sys.etm.po_Fr.o, usb_keyL), (b.sys.etm.Z.d.o, ucl_key), 0))
    #print("USBRU: ", rt_inv.get((b.sys.etm.po_Fr.o, usb_keyR), (b.sys.etm.Z.d.o, ucl_key), 0))
    #print("USBLL: ", rt_inv.get((b.sys.etm.po_Fr.o, usb_keyL), (b.sys.etm.Z.d.o, lcl_key), 0))
    #print("USBRL: ", rt_inv.get((b.sys.etm.po_Fr.o, usb_keyR), (b.sys.etm.Z.d.o, lcl_key), 0))
    #print("LSBLU: ", rt_inv.get((b.sys.etm.po_Fr.o, lsb_keyL), (b.sys.etm.Z.d.o, ucl_key), 0))
    #print("LSBRU: ", rt_inv.get((b.sys.etm.po_Fr.o, lsb_keyR), (b.sys.etm.Z.d.o, ucl_key), 0))
    #print("LSBLL: ", rt_inv.get((b.sys.etm.po_Fr.o, lsb_keyL), (b.sys.etm.Z.d.o, lcl_key), 0))
    #print("LSBRL: ", rt_inv.get((b.sys.etm.po_Fr.o, lsb_keyR), (b.sys.etm.Z.d.o, lcl_key), 0))
    #print("AC:", sys.AC_sensitivity('ETM_Drive'))

    #from phasor.utilities.mpl.autoniceplot import (mplfigB)
    #F = mplfigB(Nrows = 2)
    #F.ax0.loglog(sys.F_AC_Hz, abs(sys.AC_sensitivity('ETM_Drive')))
    #F.ax1.semilogx(sys.F_AC_Hz, np.angle(sys.AC_sensitivity('ETM_Drive')))
    #F.save('trans_xfer')
    #print("etm_Force[N]", sys.DC_readout('etm_ForceZ'))

if __name__ == '__main__':
    test_mirror()
