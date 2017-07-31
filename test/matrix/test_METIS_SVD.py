# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from os import path
import pytest

import numpy.testing as np_test
import numpy as np

#import numpy as np

from phasor.matrix import DAG_algorithm
from phasor.matrix import SRE_matrix_algorithms

from phasor.utilities.print import pprint

from test_SVD import (
    #mfunc,
    #mfunc_randargs,
    gen_rand_unitary
)

#from phasor.utilities.np import logspaced

def test_sparse_SVDinv():
    N = 100
    length = 10
    U = gen_rand_unitary(
        N = N,
        length = length,
        unit_density = .9,
    )
    V = gen_rand_unitary(
        N = N,
        length = length,
        unit_density = .9,
    )

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
    METIS_fname = path.join(
        path.split(__file__)[0],
        'test.ndmetis',
    )
    sbunch = DAG_algorithm.inverse_solve_inplace(
        seq = Mseq,
        req = Mreq,
        edge_map = Medge_map,
        inputs_set = inputs_set,
        outputs_set = outputs_set,
        verbose = True,
        negative = False,
        METIS_fname = METIS_fname,
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
            np_test.assert_almost_equal(edge - 1, 0)
        else:
            em0_ll[k_t, k_f] = -np.log10(np.maximum(abs(edge), 1e-30))
            np_test.assert_almost_equal(edge, 0)
    pprint(em1_ll)
    pprint(em0_ll)
    return

