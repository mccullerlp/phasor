"""
"""
from __future__ import print_function, division
import pytest

from BGSF.utilities.mpl.autoniceplot import (
    #AutoPlotSaver,
    #mplfigB,
    asavefig,
)

import os.path as path

import BGSF.fitting.casadi as FIT
#from YALL.alm.beam import *
from BGSF.alm.measurements import CRootSystem
import BGSF.alm.beam as CB
#from BGSF.alm.beam_param import ComplexBeamParam
#import BGSF.alm.system as CS
from BGSF.alm.mplot import MPlotter

mplot = MPlotter()
asavefig.org_subfolder = path.join(path.dirname(__file__), 'tests')

#mpl.rc('font', family='DejaVu Sans')


def buildsys():
    sys = CRootSystem(
        env_principle_target = 'q1',
    )
    sys.my.q1 = CB.BeamTarget(
        loc_m = 0,
        q_raw = CB.ComplexBeamParam.from_Z_ZR(0, .04),
    )
    sys.my.lens1 = CB.CThinLens(
        f_m = .1,
        loc_in = 7,
    )
    sys.my.lens2 = CB.CThinLens(
        f_m = .1,
        loc_in = 21,
    )

    sys2 = CRootSystem(
        env_principle_target = 'q1',
    )
    sys2.my.q1 = CB.BeamTarget(
        loc_m = 0,
        q_raw = CB.ComplexBeamParam.from_Z_ZR(0, .04),
    )
    sys2.my.q2 = CB.BeamTarget(
        loc_in = 28,
        q_raw = sys.measurements.q_target_z(.4, 'q1'),
    )
    sys2.my.lens1 = CB.CThinLens(
        f_m = .1,
        loc_in = 5,
    )
    sys2.my.lens2 = CB.CThinLens(
        f_m = .1,
        loc_in = 23,
    )
    return sys2

def test_fitter(plot):
    sys = buildsys()
    froot = FIT.FitterRoot()
    froot.my.sym = FIT.FitterSym()
    print(froot.targets_recurse('self'))
    froot.systems.alm = sys
    froot.sym.parameter(sys.lens1.loc_in)
    froot.my.overlap = FIT.FitterExpression(
        function = lambda alm : abs(alm.measurements.overlap('q1', 'q2'))**4
    )

    sys.components
    sys.print_yaml()
    print(sys.measurements.target_idx('q1'))

    froot.fit_systems
    print(froot.fit_systems)
    print(froot.symbol_map)
    #print(froot.systems.alm.ooa_params)
    print(froot.fit_systems.alm.measurements.overlap('q1', 'q2'))
    print(froot.overlap.expression_remapped)

    #print(froot.systems.alm.ooa_params)
    ret = froot.overlap.minimize_function()
    print("OLAP: ", ret.systems.alm.measurements.overlap('q1', 'q2'))
    print(plot)
    if plot:
        mplot.plot('test_post_fit', sys = ret.systems.alm.measurements)
    return


@pytest.mark.skip(reason="Need to fix Jitter Placement")
def test_fitter_jitter(plot):
    sys = buildsys()
    froot = FIT.FitterRoot()
    froot.my.sym = FIT.FitterSymJitterPlacement(
        shift_val = 1e-3,
    )
    print(froot.targets_recurse('self'))
    froot.systems.alm = sys
    froot.sym.parameter(sys.lens1.loc_in)
    froot.my.overlap = FIT.FitterExpression(
        function = lambda alm : abs(alm.measurements.overlap('q1', 'q2'))**4
    )

    sys.components
    sys.print_yaml()
    print(sys.measurements.target_idx('q1'))

    froot.fit_systems
    print(froot.fit_systems)
    print(froot.symbol_map)
    #print(froot.systems.alm.ooa_params)
    print(froot.fit_systems.alm.measurements.overlap('q1', 'q2'))
    print(froot.overlap.expression_remapped)

    #print(froot.systems.alm.ooa_params)
    ret = froot.overlap.minimize_function()
    return

if __name__=='__main__':
    print("Fitter")
    test_fitter(True)
