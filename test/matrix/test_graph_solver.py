"""
"""
from __future__ import (division, print_function)
import warnings
from os import path
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
from phasor.matrix import SRE_matrix_algorithms
from phasor.utilities.print import pprint

#from phasor.utilities.np import logspaced

def isolve_mat(
        arr,
        solver = scisparse_algorithm,
        **kwargs
):
    arr = arr.astype(float)
    inputs_set = set(range(arr.shape[0]))
    outputs_set = set(range(arr.shape[1]))
    seq = collections.defaultdict(set)
    req = collections.defaultdict(set)
    edge_map = dict()
    for idx_c in range(arr.shape[0]):
        for idx_r in range(arr.shape[1]):
            v = arr[idx_c, idx_r]
            if v != 0:
                edge_map[idx_c, idx_r] = v
                seq[idx_c].add(idx_r)
                req[idx_r].add(idx_c)

    sbunch = solver.inverse_solve_inplace(
        seq = seq,
        req = req,
        inputs_set = inputs_set,
        outputs_set = outputs_set,
        edge_map = edge_map,
        verbose = True,
        **kwargs
    )
    arr2 = np.zeros_like(arr)
    for (idx_c, idx_r), v in sbunch.edge_map.items():
        arr2[idx_c, idx_r] = v
    return arr2

def check_arr(arr, **kwargs):
    pprint(arr)
    arr_inv = np.linalg.inv(arr)
    pprint(arr_inv)
    arr_inv2 = isolve_mat(arr, **kwargs)
    pprint(arr_inv2)

    #pprint(np.eye(arr.shape[0]) - np.dot(arr_inv, arr))
    diff = np.eye(arr.shape[0]) - np.dot(arr_inv2, arr)
    #pprint(diff)

    print("DIAG: ")
    pprint(np.diagonal(diff))

    np_test.assert_almost_equal(arr_inv, arr_inv2)


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


def test_graph_solver0():
    arr = np.array([[1, 0.], [0, 1]])
    check_arr(arr)
#
#def test_graph_solver01():
#    arr = np.array([[1, 0], [1, 1]])
#    check_arr(arr)
#
#def test_graph_solver02():
#    arr = np.array([[1, -1.], [0, 1]])
#    check_arr(arr)

def test_graph_solver01():
    arr = np.array([[-.1, -1.], [0, 1]])
    check_arr(arr)
#
def test_graph_solver02():
    arr = np.array([[-1, 3.], [1, -1]])
    check_arr(arr)
#
def test_graph_solver03():
    arr = np.array([[2, 3., 0], [1, -1, 0], [0, 0, .1]])
    check_arr(arr)

def test_graph_solver():
    arr = np.array([[.1, 1., 1.], [0, 1.001, 0.], [0, 0, 1.]])
    check_arr(arr)

def test_graph_solver2():
    #no c_edges
    arr = np.array([[.1, 0, 0], [1, 1, 0], [1, 1, 1]])
    check_arr(arr)
#
#
def test_graph_solver_x():
    arr = np.array([[3, 1, 0], [0, .9999, 0], [0, 0, .9999]])
    check_arr(arr)

def test_graph_solver3b():
    arr = np.array([[1, 2, 0], [-1, 1, 1], [0, 0, 1]])
    check_arr(arr)

#def test_graph_solver3b():
#    arr = np.array([[.1, -1, 0.00000], [0, 1.1, 1], [0, 0, 1.1]])
#    check_arr(arr)

def test_graph_solver3c():
    arr = np.array([[.1, 1, 0], [0.01, 1.1, 0], [0, 0, 1.1]])
    check_arr(arr)

def test_graph_solver4():
    arr = np.array([[.1, 1, 1], [1, 1, -1], [-1, 1, 1]])
    check_arr(arr)
#
#def test_graph_solver_rT():
#    arr = np.random.rand(10,10)
#    for idx in range(10):
#        arr[0:idx,idx] = 0
#    check_arr(arr)
##
#def test_graph_solver_r3():
#    arr = np.random.rand(3,3)
#    check_arr(arr)
#
def test_graph_solver_r4():
    arr = np.random.rand(4, 4)
    check_arr(arr, )
#
#def test_graph_solver_r4():
#    arr = np.random.rand(4, 4)
#    check_arr(arr, sorted_order = True)
#
def test_graph_solver_r10():
    arr = np.random.rand(10, 10)
    check_arr(arr, )


## Should tag as "slow"
#def test_graph_solver_r100():
#    arr = np.random.rand(300, 300)
#    check_arr(arr, )
#    assert(False)
#
#
##def test_graph_solver_rT2():
##    arr = np.random.rand(10,10)
##    for idx in range(10):
##        arr[idx + 1:,idx] = 0
##    check_arr(arr)
#
##def test_graph_solver_r4():
##    arr = np.random.rand(10,10)
##    check_arr(arr)
##
##    arr = np.random.rand(100,100)
##    check_arr(arr)

@pytest.mark.skipif(sys.version_info < (3, 0), reason="Requires pickle version 3")
def test_LIGOX_scisparse():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        check_system(
            fname = path.join(path.dirname(__file__), './LIGOX_mat.pckl'),
            solver = scisparse_algorithm,
        )

#@pytest.mark.skipif(sys.version_info < (3, 0), reason="Requires pickle version 3")
#def test_HTTS():
    #check_system(fname = path.join(path.dirname(__file__), './HTTS_UL_UL.pckl'))

if __name__ == '__main__':
    test_LIGOX()
