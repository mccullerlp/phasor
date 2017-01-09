"""
"""

from __future__ import (division, print_function)
import pytest

from declarative import Bunch

import BGSF.optics as optics
import BGSF.readouts as readouts

from BGSF.system.optical import (
    OpticalSystem
)


#from BGSF.utilities.np import logspaced

def gensys():
    sys = OpticalSystem(
    )
    sled = sys.sled
    sled.laser = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
        name = "laser",
    )

    sled.etm = optics.Mirror(
        T_hr=.001,
        name = 'ETM',
        facing_cardinal = 'W',
    )
    sled.etmPD = optics.MagicPD(
        name = 'ETMPD',
        facing_cardinal = 'E',
    )
    sled.s1 = optics.Space(
        L_m = 100,
        L_detune_m = 0,
        name = 's1'
    )

    sys.optical_link_sequence_WtoE(
        sled.laser,
        sled.etmPD,
        sled.s1,
        sled.etm
    )

    sled.etm_DC = readouts.DCReadout(port = sled.etmPD.Wpd.o)
    sled.etm_drive = readouts.ACReadout(
        portN = sled.etmPD.Wpd.o,
        portD = sled.etm.posZ.i,
    )
    #sys.AC_freq(np.array([1]))
    return Bunch(locals())


@pytest.mark.optics_fast
def test_mirror():
    b = gensys()
    sys = b.sys
    sol = sys.solve()
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sol.solution_vector_print()
    print("etm_DC", sol.views.etm_DC.DC_readout)
    print("etm_drive", sol.views.etm_drive.AC_sensitivity)
    #print("etm_Force[N]", sys.DC_readout('etm_ForceZ'))

    #print("A")
    #sys.coupling_matrix_print(select_from = b.sled.etm.posZ.i, select_to = b.sled.etm.Fr.o)
    #print("B")
    #sol.coupling_matrix_print(
    #    select_to= b.sled.etm.Fr.i,
    #)
    print("inv")
    #sol.coupling_matrix_inv_print()
    print('A')
    sol.coupling_matrix_inv_print(
        select_from = b.sled.etm.posZ.i,
        select_to = b.sled.etmPD.Fr.i,
    )
    print('B')

    sol.coupling_matrix_print(
        select_from = b.sled.etmPD.Fr.i,
        select_to = b.sled.etmPD.Wpd.o,
        drive_set = 'AC',
        readout_set = 'AC',
    )
    print('B inv')
    sol.coupling_matrix_inv_print(
        select_from = b.sled.etmPD.Fr.i,
        select_to = b.sled.etmPD.Wpd.o,
        drive_set = 'AC',
        readout_set = 'AC',
    )
    sol.coupling_matrix_inv_print(
        select_from = b.sled.etm.posZ.i,
        select_to = b.sled.etmPD.Wpd.o,
        drive_set = 'AC',
        readout_set = 'AC',
    )

    #from BGSF.key_matrix import (
    #    DictKey,
    #    FrequencyKey,
    #)

    #rt_inv = sys.invert_system()
    #usb_keyL = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sled.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})}) | b.sled.laser.polarization | optics.LOWER
    #usb_keyR = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sled.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})}) | b.sled.laser.polarization | optics.RAISE
    #lsb_keyL = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sled.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})}) | b.sled.laser.polarization | optics.LOWER
    #lsb_keyR = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sled.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})}) | b.sled.laser.polarization | optics.RAISE
    #ucl_key = DictKey({optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})})
    #lcl_key = DictKey({optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})})
    #print("USBLU: ", rt_inv.get((b.sled.etm.Fr.o, usb_keyL), (b.sled.etm.posZ.i, ucl_key), 0))
    #print("USBRU: ", rt_inv.get((b.sled.etm.Fr.o, usb_keyR), (b.sled.etm.posZ.i, ucl_key), 0))
    #print("USBLL: ", rt_inv.get((b.sled.etm.Fr.o, usb_keyL), (b.sled.etm.posZ.i, lcl_key), 0))
    #print("USBRL: ", rt_inv.get((b.sled.etm.Fr.o, usb_keyR), (b.sled.etm.posZ.i, lcl_key), 0))
    #print("LSBLU: ", rt_inv.get((b.sled.etm.Fr.o, lsb_keyL), (b.sled.etm.posZ.i, ucl_key), 0))
    #print("LSBRU: ", rt_inv.get((b.sled.etm.Fr.o, lsb_keyR), (b.sled.etm.posZ.i, ucl_key), 0))
    #print("LSBLL: ", rt_inv.get((b.sled.etm.Fr.o, lsb_keyL), (b.sled.etm.posZ.i, lcl_key), 0))
    #print("LSBRL: ", rt_inv.get((b.sled.etm.Fr.o, lsb_keyR), (b.sled.etm.posZ.i, lcl_key), 0))
    #print("AC:", sys.AC_sensitivity('ETM_Drive'))

    #from BGSF.utilities.mpl.autoniceplot import (mplfigB)
    #F = mplfigB(Nrows = 2)
    #F.ax0.loglog(sys.F_AC_Hz, abs(sys.AC_sensitivity('ETM_Drive')))
    #F.ax1.semilogx(sys.F_AC_Hz, np.angle(sys.AC_sensitivity('ETM_Drive')))
    #F.save('trans_xfer')
    #print("etm_Force[N]", sys.DC_readout('etm_ForceZ'))

if __name__ == '__main__':
    test_mirror()
