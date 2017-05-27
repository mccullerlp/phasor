"""
"""
from __future__ import (division, print_function)

import numpy.testing as np_test
import numpy as np
import declarative
import collections

#import numpy as np

from OpenLoop.system import DAG_algorithm as graph_algorithm
from OpenLoop.utilities.print import pprint

#from OpenLoop.utilities.np import logspaced

def isolve_mat(
        arr,
        Q_conditioning = True,
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
                edge_map[idx_c, idx_r] = -v
                seq[idx_c].add(idx_r)
                req[idx_r].add(idx_c)

    sbunch = graph_algorithm.inverse_solve_inplace(
        seq = seq,
        req = req,
        inputs_set = inputs_set,
        outputs_set = outputs_set,
        edge_map = edge_map,
        verbose = True,
        Q_conditioning = Q_conditioning,
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
#def test_graph_solver_r4():
#    arr = np.random.rand(4, 4)
#    check_arr(arr, Q_conditioning = False)
#
#def test_graph_solver_r4():
#    arr = np.random.rand(4, 4)
#    check_arr(arr, Q_conditioning = False, sorted_order = True)
#
#def test_graph_solver_r10():
#    arr = np.random.rand(10, 10)
#    check_arr(arr, Q_conditioning = False)


## Should tag as "slow"
#def test_graph_solver_r100():
#    arr = np.random.rand(300, 300)
#    check_arr(arr, Q_conditioning = False)
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

if __name__ == '__main__':
    test_graph_solver()
