"""
"""
from __future__ import print_function, division
import pytest

from openLoop.utilities.mpl.autoniceplot import (
    #AutoPlotSaver,
    #mplfigB,
    asavefig,
)
import matplotlib as mpl

import os.path as path

#from YALL.alm.beam import *
from openLoop.alm.measurements import CRootSystem
import openLoop.alm.beam as CB
import openLoop.alm.system as CS
#from openLoop.alm.beam_param import ComplexBeamParam
#import openLoop.alm.system as CS
from openLoop.alm.mplot import MPlotter
mplot = MPlotter()
asavefig.org_subfolder = path.join(path.dirname(__file__), 'tests')

#mpl.rc('font', family='DejaVu Sans')

from IPython.lib.pretty import pprint as print


def test_cavity(plot):
    print(CRootSystem.loc_m)
    sys = CRootSystem()
    sys.my.q1 = CB.BeamTarget(
        loc_m = 0,
        q_system = CS.CSystem(loc_m = 0),
        #q_raw = CB.ComplexBeamParam.from_Z_ZR(0, .04),
    )
    sys.q1.q_system.my.m1 = CB.CMirror(
        R_m = .2,
        loc_m = 0,
    )
    sys.q1.q_system.my.m2 = CB.CMirror(
        R_m = .2,
        loc_m = .1,
    )
    sys.q1.q_system.my.c_return = CB.CNoP(
        loc_m = .2,
    )
    sys.my.cav = sys.q1.q_system.replica_generate(loc_m = .0001)
    print(("WIDTH", sys.cav.width_m))
    #sys.my.cav._complete()
    #print(("WIDTH", sys.cav.width_m))
    sys.my.cav2 = sys.q1.q_system.replica_generate(loc_m = sys.cav.width_m + sys.cav.loc_m.ref)
    print(sys.cav2.loc_in)
    print(sys.cav2.loc_ft)
    #print(sys._registry_inserted)
    #print(sys._registry_children)
    #print("A", sys.cav._registry_inserted_pre)
    #sys._complete()
    #print(sys.cav._registry_children)
    #print(sys.cav._registry_inserted)
    #print(("A", sys.cav._registry_inserted_pre))
    #print(("B", sys.cav2._registry_inserted_pre))
    #print(("A", sys.cav._registry_children))
    #print(("B", sys.cav2._registry_children))
    #sys._complete()

    #assert(False)
    if plot:
        mplot.plot('test_cavity', sys = sys.measurements)
    return sys


if __name__=='__main__':
    print("CAVITY")
    test_cavity(True)
