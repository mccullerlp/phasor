"""
TODO: isolate the RMS
"""
from __future__ import (division, print_function)

import numpy.testing as np_test
import declarative

from phasor import system
from phasor import optics
from phasor import readouts
from phasor import signals

#from phasor.utilities.np import logspaced


#http://journals.aps.org/pra/pdf/10.1103/PhysRevA.43.5022
#note that the sideband order must be at least 2 to show the effect
def gensys(
        loss_BS = 0,
        freq_order_max_default = 10,
):
    sys = system.BGSystem(
        freq_order_max_default = freq_order_max_default,
    )
    sled = sys

    sled.own.F_shift = system.Frequency(
        F_Hz = 1000,
        F_center_Hz = 1000,
    )
    sled.own.laser_upper = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
        classical_fdict = {
            sled.F_shift : 1,
        },
    )
    sled.own.laser_lower = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
        classical_fdict = {
            sled.F_shift : -1,
        },
    )

    sled.own.mBS = optics.Mirror(
        T_hr = .5,
        L_hr = loss_BS,
        AOI_deg = 45,
    )

    sled.own.PD1 = optics.PD()
    sled.own.PD2 = optics.PD()

    sled.own.mix_LO = signals.SignalGenerator(
        F = sled.F_shift,
        multiple = 1,
        amplitude = 2,
    )
    sled.own.mixer = signals.Mixer(
    )
    #sled.own.mixerIRMS = RMSMixer(
    #)
    #sled.own.mixerQRMS = RMSMixer(
    #)
    sled.own.sDelay = optics.Space(
        L_m = 1,
        #L_detune_m = 1064e-9 / 4,
    )
    sys.bond(sled.mix_LO.ps_Out, sled.mixer.LO)
    sys.bond(sled.PD2.Wpd,   sled.mixer.ps_In)
    #sys.link(sled.mixer.ps_R_I, sled.mixerIRMS.ps_In)
    #sys.link(sled.mixer.ps_R_Q, sled.mixerQRMS.ps_In)

    sys.bond_sequence(
        sled.laser_upper.po_Fr,
        sled.mBS.po_FrA,
        sled.PD1.po_Fr,
    )
    sys.bond_sequence(
        sled.laser_lower.po_Fr,
        sled.mBS.po_BkB,
        sled.PD2.po_Fr,
    )

    sled.own.PD1_DC       = readouts.DCReadout(port = sled.PD1.Wpd.o)
    sled.own.PD2_DC       = readouts.DCReadout(port = sled.PD2.Wpd.o)
    sled.own.PD1_MIX_I    = readouts.DCReadout(port = sled.mixer.ps_R_I.o)
    sled.own.PD1_MIX_Q    = readouts.DCReadout(port = sled.mixer.ps_R_Q.o)
    #sled.own.PD1_MIX_IRMS = readouts.DCReadout(port = sled.mixerIRMS.RMS.o)
    #sled.own.PD1_MIX_QRMS = readouts.DCReadout(port = sled.mixerQRMS.RMS.o)
    sled.own.PD1_AC       = readouts.NoiseReadout(portN = sled.PD1.Wpd.o)
    sled.own.PD1_MIX_I_N  = readouts.NoiseReadout(portN = sled.mixer.ps_R_I.o)
    sled.own.PD1_MIX_Q_N  = readouts.NoiseReadout(portN = sled.mixer.ps_R_Q.o)
    return declarative.Bunch(locals())

def test_cyclostationary():
    #TODO speed this up!
    b = gensys(
        #F_AC_Hz = logspaced(.001, 1e6, 10),
        #F_AC_Hz = np.array([10]),
        freq_order_max_default = 3,
    )
    sys = b.sys
    print()
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sys.solution_vector_print()
    import pprint
    pp = pprint.PrettyPrinter()
    pp.pprint(sys)
    print("DC1",  sys.PD1_DC.DC_readout)
    print("DC2",  sys.PD2_DC.DC_readout)
    print("AC1",  sys.PD1_AC.CSD['R', 'R'])
    E1064_J = 1.2398 / 1.064 / 6.24e18
    N_expect = (2 * sys.PD1_DC.DC_readout * E1064_J)
    print("AC1 rel",  (sys.PD1_AC.CSD['R', 'R'] / N_expect)**.5)

    print("DC1_MIX_I",  sys.PD1_MIX_I.DC_readout)
    print("DC1_MIX_Q",  sys.PD1_MIX_Q.DC_readout)

    print("AC1_MIX_I_N",  sys.PD1_MIX_I_N.CSD['R', 'R'])
    print("AC1_MIX_I_N rel",  (sys.PD1_MIX_I_N.CSD['R', 'R'] / N_expect))
    np_test.assert_almost_equal(sys.PD1_MIX_I_N.CSD['R', 'R'] / N_expect, 3, 2)
    #print("DC1_MIX_I_RMS",  sys.PD1_MIX_IRMS.DC_readout)
    print("AC1_MIX_Q_N",  sys.PD1_MIX_Q_N.CSD['R', 'R'])
    print("AC1_MIX_Q_N rel",  (sys.PD1_MIX_Q_N.CSD['R', 'R'] / N_expect))
    np_test.assert_almost_equal(sys.PD1_MIX_Q_N.CSD['R', 'R'] / N_expect, 1, 2)
    #print("DC1_MIX_Q_RMS",  sys.PD1_MIX_QRMS.DC_readout)
    #sol.coupling_matrix_print(select_to = b.sled.mixerIRMS.RMS.o)
    sys.solution.solution_vector_print(select_to = b.sled.mixer.ps_R_I.o)
    sys.solution.solution_vector_print(select_to = b.sled.mixer.ps_R_Q.o)

    #TODO isolate this test
    #from phasor.system_graphs import (
    #    coherent_sparsity_graph
    #)

    #gdata = coherent_sparsity_graph(sol)
    #print("Order: ", gdata.order)
    #print("Inputs: ")
    #def lprint(s):
    #    p = [repr(l) for l in s]
    #    p.sort()
    #    for x in p:
    #        print(x)
    #lprint(gdata.inputs_set)
    #print("Outputs: ")
    #lprint(gdata.outputs_set)
    #print(len(gdata.inputs_set) * len(gdata.outputs_set))
    #print(len(gdata.active) * len(gdata.active))
    ##print("Active: ")
    ##lprint(gdata.active)

    #sys.coupling_matrix_print(select_to = b.sled.mixer.ps_R_Q.o)

    #sys.coupling_matrix_inv_print(
    #    select_to = b.sled.mixer.ps_R_I.o,
    #    select_from = b.sled.laser_upper.po_Fr.o,
    #)
    #sys.coupling_matrix_inv_print(
    #    select_to = b.sled.mixer.ps_R_I.o,
    #    select_from = b.sled.laser_lower.po_Fr.o,
    #)

    #print()
    #sys.coupling_matrix_inv_print(
    #    select_to = b.sled.mixer.ps_R_Q.o,
    #    select_from = b.sled.laser_upper.po_Fr.o,
    #)
    #sys.coupling_matrix_inv_print(
    #    select_to = b.sled.mixer.ps_R_Q.o,
    #    select_from = b.sled.laser_lower.po_Fr.o,
    #)


if __name__ == '__main__':
    test_cyclostationary()
