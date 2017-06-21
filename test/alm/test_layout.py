"""
"""
from __future__ import print_function, division
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
#from phasor.alm.beam_param import ComplexBeamParam
#import phasor.alm.system as CS
from phasor.alm.mplot import MPlotter
mplot = MPlotter()
asavefig.org_subfolder = path.join(path.dirname(__file__), 'tests')

#mpl.rc('font', family='DejaVu Sans')

from IPython.lib.pretty import pprint as print


def test_layout(plot):
    sys = CRootSystem(
        env_principle_target = 'q1',
    )

    sys.own.q1 = CB.BeamTarget(
        loc_m = 0,
        q_raw = CB.ComplexBeamParam.from_Z_ZR(0, .04),
    )
    sys.own.lens1 = CB.CThinLens(
        f_m = .1,
        loc_in = 7,
    )
    sys.own.q2 = CB.BeamTarget(
        loc_m = .4,
        q_raw = CB.ComplexBeamParam.from_Z_ZR(0, .04),
    )

    sys.components
    print(sys.measurements.target_idx('q1'))

    if plot:
        mplot.plot('test_layout', sys = sys.measurements)
    return sys


def test_regenerate(plot):
    sys = test_layout(plot = False)

    sys2 = sys.regenerate()
    print(sys2.q1.loc_m.val)
    print(sys2.q2.loc_m.val)
    print(sys2.lens1.loc_m.val)

    sys.component_pos_pairings
    sys2.component_pos_pairings
    assert(set(sys._registry_inserted.keys()) == set(sys2._registry_inserted.keys()))
    assert(set(sys._registry_children.keys()) == set(sys2._registry_children.keys()))
    #TODO make the plot optional
    if plot:
        mplot.plot('test_regen', sys = sys2.measurements)
    print(sys2._registry_children)
    print(sys2._registry_inserted)
    return

def test_regenerate_auto(plot):
    sys = test_layout(plot = False)
    print("SYS INS: ", sys._registry_inserted)
    sys2 = sys.regenerate()
    print("SYS INS2: ", sys2._registry_inserted_pre)

    sys.component_pos_pairings
    sys2.component_pos_pairings
    assert(set(sys._registry_inserted.keys()) == set(sys2._registry_inserted.keys()))
    assert(set(sys._registry_children.keys()) == set(sys2._registry_children.keys()))
    if plot:
        mplot.plot('test_regen_auto', sys = sys2.measurements)
    print(sys2._registry_children)
    print(sys2._registry_inserted)
    return

def test_regenerate_auto_ooa(plot):
    sys = test_layout(plot = False)
    sys2 = sys.regenerate()

    sys.component_pos_pairings
    sys2.component_pos_pairings
    assert(set(sys._registry_inserted.keys()) == set(sys2._registry_inserted.keys()))
    assert(set(sys._registry_children.keys()) == set(sys2._registry_children.keys()))
    print('OOA1')
    print(sys.ctree)
    print('OOA2')
    print(sys2.ctree)
    sys2.print_yaml()
    return

if __name__=='__main__':
    #print("LAYOUT")
    #test_layout(True)
    #print("REGEN")
    #test_regenerate(True)
    print("REGEN_AUTO")
    test_regenerate_auto_ooa(True)
