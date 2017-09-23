# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import pytest

from phasor.utilities.mpl.autoniceplot import (
    asavefig,
)

import os.path as path

from phasor import alm
asavefig.org_subfolder = path.join(path.dirname(__file__), 'tests')

from IPython.lib.pretty import pprint as print


def test_cavity(plot):
    print(alm.RootSystem.loc_m)
    sys = alm.RootSystem()
    sys.own.q1 = alm.BeamTarget(
        loc_m = 0,
        q_system = alm.System(loc_m = 0),
        #q_raw = alm.ComplexBeamParam.from_Z_ZR(0, .04),
    )
    sys.q1.q_system.own.m1 = alm.Mirror(
        R_m = .2,
        loc_m = 0,
    )
    sys.q1.q_system.own.m2 = alm.Mirror(
        R_m = .2,
        loc_m = .1,
    )
    sys.q1.q_system.own.c_return = alm.NoP(
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
        sys.plot('test_cavity')
    return sys


if __name__=='__main__':
    print("CAVITY")
    test_cavity(True)
