"""
"""
from __future__ import print_function, division
import pytest

from phasor.utilities.mpl.autoniceplot import (
    #AutoPlotSaver,
    #mplfigB,
    asavefig,
)
#import matplotlib as mpl
from IPython.lib.pretty import pprint as print

import os.path as path

import phasor.alm.beam as alm_beam
import phasor.alm.system as alm_system
import phasor.alm.measurements as alm_measurements
import phasor.alm.mplot as alm_mplot
import phasor.alm.composites as alm_composites

mplot = alm_mplot.MPlotter()
asavefig.org_subfolder = path.join(path.dirname(__file__), 'tests')

#mpl.rc('font', family='DejaVu Sans')


def test_composites(plot):
    def gensys(reversed):
        sys = alm_measurements.CRootSystem()
        sys.own.sub1 = alm_system.CSystem(
            loc_m = 0,
            reversed = reversed,
        )
        sys.sub1.own.q1 = alm_beam.BeamTarget(
            loc_m = 0,
            q_raw = alm_beam.ComplexBeamParam.from_Z_ZR(0, .5),
        )
        #sys.sub1.own.m1 = alm_beam.CThinLens(
        #    f_m = .5,
        #    loc_m = .5,
        #)
        sys.sub1.own.m1 = alm_composites.PLCX(
            R_m = .24,
            loc_m = .5,
            L_m = .02,
        )
        sys.sub1.own.c_return = alm_beam.CNoP(
            loc_m = 1,
        )
        return sys
    sys = gensys(False)
    sysR = gensys(True)
    #print("pm_A")
    q_end = sys.measurements.q_target_z(1.0)
    #print(("INVAL: ", sys.measurements._registry_invalidate))
    #sys = gensys(False)
    sys.sub1.own.q2 = alm_beam.BeamTarget(
        loc_m = 1.00001,
        q_raw = q_end,
    )
    #sys.invalidate()
    #print("pm_B")
    #q_end2 = sys.measurements.q_target_z(1.0)
    sysR.sub1.own.q2 = alm_beam.BeamTarget(
        loc_m = 1.00001,
        q_raw = q_end,
    )
    print(("REV: ", sys.sub1.env_reversed))
    print(("REV: ", sysR.sub1.env_reversed))
    #print(sys.sub1.component_pos_pairings)

    q_out = sysR.measurements.target_q('sub1.q1', 'sub1.q2')
    print(abs(sys.measurements.overlap('sub1.q1', 'sub1.q2'))**4)
    print(abs(sysR.measurements.overlap('sub1.q1', 'sub1.q2'))**4)

    assert(abs(sys.measurements.overlap('sub1.q1', 'sub1.q2')) > .99999)
    assert(abs(sysR.measurements.overlap('sub1.q1', 'sub1.q2')) > .99999)

    if plot:
        mplot.plot('test_composites', sys = sys.measurements)
        mplot.plot('test_compositesR', sys = sysR.measurements)
        #print(("INVAL: ", sys.measurements._registry_invalidate))
    #assert(False)
    return sys


if __name__ == '__main__':
    print("composites")
    test_composites(True)
