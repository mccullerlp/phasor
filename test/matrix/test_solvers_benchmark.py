# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from os import path
import warnings
import sys
import pytest

from phasor.utilities.mpl import mplfigB

import numpy.testing as np_test
import numpy as np
import declarative
import collections
import pickle

#import numpy as np

from phasor.matrix import graph_algorithm
from phasor.matrix import DAG_algorithm
from phasor.matrix import scisparse_algorithm
from phasor.utilities.print import pprint

#from phasor.utilities.np import logspaced


slow = pytest.mark.skipif(
    not pytest.config.getoption("--do-benchmarks"),
    reason="need --do-benchmarks option to run"
)

def check_system(
    fname = './LIGOX_mat.pckl',
    solver = scisparse_algorithm,
):
    #with open('./HTTS_UL_UL.pckl', 'rb') as F:
    with open(fname, 'rb') as F:
        data = declarative.Bunch(pickle.load(F))

    keys = set()
    mat_sub_one = dict()
    seq = collections.defaultdict(set)
    req = collections.defaultdict(set)
    for (k1, k2), edge in data.coupling_matrix.items():
        keys.add(k1)
        keys.add(k2)
        seq[k1].add(k2)
        req[k2].add(k1)
        mat_sub_one[k1, k2] = edge
        #if k1 == k2:
        #    mat_sub_one[k1, k2] = edge - 1
        #else:
        #    mat_sub_one[k1, k2] = edge

    #for k in keys:
    #    if (k, k) not in mat_sub_one:
    #        mat_sub_one[k, k] = -1
    #        seq[k].add(k)
    #        req[k].add(k)

    inputs_set = set([data.AC_index[0]])
    outputs_set = set([data.AC_index[1]])

    sbunch = solver.inverse_solve_inplace(
        seq = seq,
        req = req,
        inputs_set = inputs_set,
        outputs_set = outputs_set,
        edge_map = mat_sub_one,
        verbose = True,
        scattering = True,
        #negative = True,
    )

    rel_data = sbunch.edge_map[data.AC_index]/data.AC_solution
    rel_mag = abs(rel_data)
    rel_angle = np.angle(rel_data)

    bad_data = (abs(rel_mag - 1) > 1e-1) | (rel_angle > 1e-1)
    frac_bad = np.count_nonzero(bad_data) / len(bad_data)

    try:
        assert(frac_bad < .1)
    except AssertionError:
        #print(abs(rel_mag - 1))
        #print(rel_angle)
        X = np.linspace(0, 1, data.AC_solution.shape[0])
        axB = mplfigB(Nrows = 3)
        axB.ax0.semilogy(X, abs(data.AC_solution))
        axB.ax0.semilogy(X, abs(sbunch.edge_map[data.AC_index]))
        axB.ax1.plot(X, abs(sbunch.edge_map[data.AC_index]/data.AC_solution))
        axB.ax2.plot(X, ((.4 + np.angle(sbunch.edge_map[data.AC_index]/data.AC_solution)) % (2 * np.pi) - .4))

        axB.save(fname)
        raise


@slow
@pytest.mark.skipif(sys.version_info < (3, 0), reason="Requires pickle version 3")
def test_LIGOX_scisparse(benchmark):
    @benchmark
    def run():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            check_system(
                fname = path.join(path.dirname(__file__), './LIGOX_mat.pckl'),
                solver = scisparse_algorithm,
            )

@slow
@pytest.mark.skipif(sys.version_info < (3, 0), reason="Requires pickle version 3")
def test_LIGOX_loop_LUQ(benchmark):
    @benchmark
    def run():
        check_system(
            fname = path.join(path.dirname(__file__), './LIGOX_mat.pckl'),
            solver = DAG_algorithm,
        )

@slow
@pytest.mark.skipif(sys.version_info < (3, 0), reason="Requires pickle version 3")
def test_LIGOX_loop_fast_unstable(benchmark):
    @benchmark
    def run():
        check_system(
            fname = path.join(path.dirname(__file__), './LIGOX_mat.pckl'),
            solver = graph_algorithm,
        )

#@pytest.mark.skipif(sys.version_info < (3, 0), reason="Requires pickle version 3")
#def test_HTTS():
    #check_system(fname = path.join(path.dirname(__file__), './HTTS_UL_UL.pckl'))

if __name__ == '__main__':
    test_LIGOX()
