# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import pytest

from phasor.utilities.mpl.autoniceplot import (
    #AutoPlotSaver,
    #mplfigB,
    asavefig,
)
import matplotlib as mpl

import os.path as path

#from YALL.alm.beam import *
from phasor.alm.measurements import CRootSystem
import phasor.alm.beam as CB
import phasor.alm.system as CS
#from phasor.alm.beam_param import ComplexBeamParam
#import phasor.alm.system as CS
from phasor.alm.mplot import MPlotter
mplot = MPlotter()
asavefig.org_subfolder = path.join(path.dirname(__file__), 'tests')

#mpl.rc('font', family='DejaVu Sans')

from IPython.lib.pretty import pprint as print


def test_cavity(plot):
    print(CRootSystem.loc_m)
    sys = CRootSystem()
    sys.own.q1 = CB.BeamTarget(
        loc_m = 0,
        q_system = CS.CSystem(loc_m = 0),
        #q_raw = CB.ComplexBeamParam.from_Z_ZR(0, .04),
    )
    sys.q1.q_system.own.m1 = CB.CMirror(
        R_m = .2,
        loc_m = 0,
    )
    sys.q1.q_system.own.m2 = CB.CMirror(
        R_m = .2,
        loc_m = .1,
    )
    sys.q1.q_system.own.c_return = CB.CNoP(
        loc_m = .2,
    )
    sys.own.cav = sys.q1.q_system.replica_generate(loc_m = .0001)
    print(("WIDTH", sys.cav.width_m))
    #sys.own.cav._complete()
    #print(("WIDTH", sys.cav.width_m))
    sys.own.cav2 = sys.q1.q_system.replica_generate(loc_m = sys.cav.width_m + sys.cav.loc_m.ref)
    print(sys.cav2.loc_in)
    print(sys.cav2.loc_ft)
    #print(sys._registry_inserted)
    #print(sys._registry_children)
    #print("pm_A", sys.cav._registry_inserted_pre)
    #sys._complete()
    #print(sys.cav._registry_children)
    #print(sys.cav._registry_inserted)
    #print(("pm_A", sys.cav._registry_inserted_pre))
    #print(("pm_B", sys.cav2._registry_inserted_pre))
    #print(("pm_A", sys.cav._registry_children))
    #print(("pm_B", sys.cav2._registry_children))
    #sys._complete()

    #assert(False)
    if plot:
        mplot.plot('test_cavity', sys = sys.measurements)
    return sys


if __name__=='__main__':
    print("CAVITY")
    test_cavity(True)
