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

import os.path as path

import phasor.fitting.casadi as FIT
#from YALL.alm.beam import *
from phasor.alm.measurements import CRootSystem
import phasor.alm.beam as CB
#from phasor.alm.beam_param import ComplexBeamParam
#import phasor.alm.system as CS
from phasor.alm.mplot import MPlotter

mplot = MPlotter()
asavefig.org_subfolder = path.join(path.dirname(__file__), 'tests')

#mpl.rc('font', family='DejaVu Sans')


def buildsys():
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
    sys.own.lens2 = CB.CThinLens(
        f_m = .1,
        loc_in = 21,
    )

    sys2 = CRootSystem(
        env_principle_target = 'q1',
    )
    sys2.own.q1 = CB.BeamTarget(
        loc_m = 0,
        q_raw = CB.ComplexBeamParam.from_Z_ZR(0, .04),
    )
    sys2.own.q2 = CB.BeamTarget(
        loc_in = 28,
        q_raw = sys.measurements.q_target_z(.4, 'q1'),
    )
    sys2.own.lens1 = CB.CThinLens(
        f_m = .1,
        loc_in = 5,
    )
    sys2.own.lens2 = CB.CThinLens(
        f_m = .1,
        loc_in = 23,
    )
    return sys2

def test_fitter(plot):
    sys = buildsys()
    froot = FIT.FitterRoot()
    froot.own.sym = FIT.FitterSym()
    print(froot.targets_recurse('self'))
    froot.systems.alm = sys
    froot.sym.parameter(sys.lens1.loc_in)
    froot.own.overlap = FIT.FitterExpression(
        function = lambda alm : abs(alm.measurements.overlap('q1', 'q2'))**4
    )

    sys.components
    sys.print_yaml()
    print(sys.measurements.target_idx('q1'))

    froot.fit_systems
    print(froot.fit_systems)
    print(froot.symbol_map)
    #print(froot.systems.alm.ctree)
    print(froot.fit_systems.alm.measurements.overlap('q1', 'q2'))
    print(froot.overlap.expression_remapped)

    #print(froot.systems.alm.ctree)
    ret = froot.overlap.minimize_function()
    print("OLAP: ", ret.systems.alm.measurements.overlap('q1', 'q2'))
    print(plot)
    if plot:
        mplot.plot('test_post_fit', sys = ret.systems.alm.measurements)
    return


#@pytest.mark.skip(reason="Need to fix Jitter Placement")
def test_fitter_jitter(plot):
    sys = buildsys()
    froot = FIT.FitterRoot()
    froot.own.sym = FIT.FitterSymJitterPlacement(
        shift = '1e-3in',
    )
    print(froot.targets_recurse('self'))
    froot.systems.alm = sys
    froot.sym.parameter(sys.lens1.loc_in)
    froot.own.overlap = FIT.FitterExpression(
        function = lambda alm : abs(alm.measurements.overlap('q1', 'q2'))**4
    )

    sys.components
    sys.print_yaml()
    print(sys.measurements.target_idx('q1'))

    froot.fit_systems
    print(froot.fit_systems)
    print(froot.symbol_map)
    #print(froot.systems.alm.ctree)
    print(froot.fit_systems.alm.measurements.overlap('q1', 'q2'))
    print(froot.overlap.expression_remapped)

    #print(froot.systems.alm.ctree)
    ret = froot.overlap.minimize_function()
    return

if __name__=='__main__':
    print("Fitter")
    test_fitter(True)
