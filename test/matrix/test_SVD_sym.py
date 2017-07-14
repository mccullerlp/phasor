# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import pytest

import numpy.testing as np_test
import numpy as np

#import numpy as np

from phasor.matrix import DAG_algorithm
from phasor.matrix import SRE_matrix_algorithms
from phasor.utilities.print import pprint

from test_SVD import mfunc, mfunc_randargs, gen_rand_unitary

#from phasor.utilities.np import logspaced


def SVD_gen_check_sym(
    N = 10,
    length = 10,
    solver = DAG_algorithm,
    benchmark = None,
    prevent_assert = False,
):
    U = gen_rand_unitary(N = N, length = length)
    V = gen_rand_unitary(N = N, length = length)

    seq = dict()
    req = dict()
    edge_map = dict()
    for idx in range(N):
        edge_map[idx, idx] = 10**(-5 + 10 * np.random.random())
        seq[idx] = set([idx])
        req[idx] = set([idx])
    S = seq, req, edge_map

    M = SRE_matrix_algorithms.matrix_mult_sre(
        SRE_matrix_algorithms.matrix_mult_sre(U, S), V
    )

    SRE_matrix_algorithms.check_sre(M)

    print("SPARSITY FRAC: ", SRE_matrix_algorithms.SRE_count_sparsity(M))

    inputs_set = set(range(N))
    outputs_set = set(range(N))

    Mseq, Mreq, Medge_map = SRE_matrix_algorithms.copy_sre(M)

    sym_dict = dict()
    for k, e in Medge_map.items():
        if np.random.randint(4) == 0:
            sym_dict[k] = e

    sbunch = solver.inverse_solve_inplace(
        seq          = Mseq,
        req          = Mreq,
        edge_map     = Medge_map,
        edge_map_sym = sym_dict,
        inputs_set   = inputs_set,
        outputs_set  = outputs_set,
        verbose      = True,
        negative     = False,
    )

    Minv = sbunch.seq, sbunch.req, sbunch.edge_map
    SRE_matrix_algorithms.check_sre(M)
    SRE_matrix_algorithms.check_sre(Minv)

    Meye = SRE_matrix_algorithms.matrix_mult_sre(M, Minv)
    #pprint(Meye)
    em1_ll = dict()
    em0_ll = dict()
    for (k_t, k_f), edge in Meye[2].items():
        if (k_t == k_f):
            em1_ll[k_t, k_f] = -np.log10(np.maximum(abs(edge - 1), 1e-30))
            if not prevent_assert:
                np_test.assert_almost_equal(edge - 1, 0, 5)
        else:
            em0_ll[k_t, k_f] = -np.log10(np.maximum(abs(edge), 1e-30))
            if not prevent_assert:
                np_test.assert_almost_equal(edge, 0, 5)
    #pprint(em1_ll)
    #pprint(em0_ll)
    #double check that diagonal exists
    for k_t in range(N):
        edge = Meye[2][k_t, k_t]
        em1_ll[k_t, k_t] = -np.log10(np.maximum(abs(edge - 1), 1e-30))
        if not prevent_assert:
            np_test.assert_almost_equal(edge - 1, 0, 5)

def test_sparse_SVDinv_sym():
    SVD_gen_check_sym()
    return


if __name__ == '__main__':
    test_LIGOX()
