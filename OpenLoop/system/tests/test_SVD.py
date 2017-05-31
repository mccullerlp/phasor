"""
"""
from __future__ import (division, print_function)
from os import path

from OpenLoop.utilities.mpl import mplfigB

import numpy.testing as np_test
import numpy as np
import declarative
import collections
import pickle

#import numpy as np

from OpenLoop.system import DAG_algorithm
from OpenLoop.system import SRE_matrix_algorithms
from OpenLoop.utilities.print import pprint

#from OpenLoop.utilities.np import logspaced

def test_sre_unitary():
    tmatrix = {
        (0, 0) : 1,
        (1, 1) : 1,
        (1, 0) : 1j,
    }
    sre1 = SRE_matrix_algorithms.edge_matrix_to_unitary_sre(tmatrix)
    seq, req, edge_map = sre1
    pprint(edge_map)
    sre2 = SRE_matrix_algorithms.adjoint_sre((seq, req, edge_map))
    pprint(sre2[2])
    sre3 = SRE_matrix_algorithms.matrix_mult_sre(sre1, sre2)
    pprint(sre3[2])
    for (k_t, k_f), edge in sre3[2].items():
        assert(k_t == k_f)
        np_test.assert_almost_equal(edge, 1)
    return

def rand_phase(N = 1):
    return np.exp(np.pi * 2j * np.random.random(N))

def randNZ(N = 1):
    return 1 - np.random.random()

def test_sparse_SVD():
    N = 10
    length = 10
    def mfunc_randargs(fname = None):
        if fname is None:
            names = [
                'constant',
                'cplx_constant',
                'linear',
                'cplx_linear',
                'sine',
                'exp',
                'cplx_exp',
            ]
            fname = names[np.random.randint(0, len(names))]
        if fname == 'constant':
            return ('constant', randNZ(),)
        if fname == 'cplx_constant':
            return ('constant', rand_phase() * randNZ(),)
        elif fname == 'linear':
            return ('linear', randNZ(), randNZ())
        elif fname == 'cplx_linear':
            return ('linear', rand_phase() * randNZ(), rand_phase() * randNZ())
        elif fname == 'sine':
            #amplitude, freq, phase, const
            return ('sine', randNZ(), 30 * np.random.random(), 2 * np.pi * np.random.random(), randNZ())
        elif fname == 'exp':
            #const, gain
            return ('exp', randNZ(), 100 * np.random.random())
        elif fname == 'cplx_exp':
            #const, gain
            return ('exp', randNZ(), 100 * np.random.random() * rand_phase())

    print(mfunc_randargs())
    print(mfunc_randargs())
    print(mfunc_randargs())
    print(mfunc_randargs())

    def mfunc(length, fname, *args):
        if fname == 'constant':
            val, = args
            return val
        elif fname == 'linear':
            v1, v2 = args
            X = np.linspace(0, 1, length)
            return v1 + X * (v2 - v1)
        elif fname == 'sine':
            amp, F, phase, const = args
            X = np.linspace(0, 1, length)
            return amp * np.sin(X * F + phase) + const
        elif fname == 'exp':
            const, gain = args
            X = np.linspace(0, 1, length)
            return const * np.exp(X * gain)
    print(mfunc(length, *mfunc_randargs()))

    edge_map = dict()
    for idx in range(N):
        to1 = idx
        edge_map[idx, to1] = mfunc(length, *mfunc_randargs())

        if np.random.randint(0, 2) == 0:
            to2 = np.random.randint(0, N)
            if to2 == to1:
                if idx + 1 != N:
                    to2 = to1 + 1
                else:
                    to2 = to1 - 1
            edge_map[idx, to2] = mfunc(length, *mfunc_randargs())
    pprint(edge_map)
    sre1 = SRE_matrix_algorithms.edge_matrix_to_unitary_sre(edge_map)
    print("SPARSITY FRAC: ", SRE_matrix_algorithms.SRE_count_sparsity(sre1))
    sre2 = SRE_matrix_algorithms.adjoint_sre(sre1)
    pprint(sre2[2])
    sre3 = SRE_matrix_algorithms.matrix_mult_sre(sre1, sre2)
    pprint(sre3[2])
    for (k_t, k_f), edge in sre3[2].items():
        if (k_t == k_f):
            np_test.assert_almost_equal(edge, 1)
        else:
            np_test.assert_almost_equal(edge, 0)
    return

if __name__ == '__main__':
    test_LIGOX()
