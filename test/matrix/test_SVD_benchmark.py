"""
"""
from __future__ import (division, print_function)
import pytest
from os import path

from phasor.utilities.mpl import mplfigB

import numpy.testing as np_test
import numpy as np
import declarative
import collections
import pickle

#import numpy as np

from phasor.matrix import DAG_algorithm
from phasor.matrix import scisparse_algorithm
from phasor.matrix import SRE_matrix_algorithms
from phasor.utilities.print import pprint

#from phasor.utilities.np import logspaced

from test_SVD import SVD_gen_check


slow = pytest.mark.skipif(
    not pytest.config.getoption("--do-benchmarks"),
    reason="need --do-benchmarks option to run"
)


mark_10_10 = pytest.mark.benchmark(
    group = "SVD_inv_10_10",
    warmup = False,
)

@slow
@mark_10_10
def test_bench_SVDinv_loop_LUQ_10_10(benchmark):
    SVD_gen_check(
        N = 10,
        length = 10,
        solver = DAG_algorithm,
        benchmark = benchmark,
        prevent_assert = True,
    )
    return

@slow
@mark_10_10
def test_bench_SVDinv_scisparse_10_10(benchmark):
    SVD_gen_check(
        N = 10,
        length = 10,
        solver = scisparse_algorithm,
        benchmark = benchmark,
        prevent_assert = True,
    )
    return


mark_100_10 = pytest.mark.benchmark(
    group = "SVD_inv_100_10",
    warmup = False,
)

@slow
@mark_100_10
def test_bench_SVDinv_loop_LUQ_100_10(benchmark):
    SVD_gen_check(
        N = 100,
        length = 10,
        solver = DAG_algorithm,
        benchmark = benchmark,
        prevent_assert = True,
    )
    return

@slow
@mark_100_10
def test_bench_SVDinv_scisparse_100_10(benchmark):
    SVD_gen_check(
        N = 100,
        length = 10,
        solver = scisparse_algorithm,
        benchmark = benchmark,
        prevent_assert = True,
    )
    return


mark_10_1000 = pytest.mark.benchmark(
    group = "SVD_inv_10_1000",
    warmup = False,
)

@slow
@mark_10_1000
def test_bench_SVDinv_loop_LUQ_10_1000(benchmark):
    SVD_gen_check(
        N = 10,
        length = 1000,
        solver = DAG_algorithm,
        benchmark = benchmark,
        prevent_assert = True,
    )
    return

@slow
@mark_10_1000
def test_bench_SVDinv_scisparse_10_1000(benchmark):
    SVD_gen_check(
        N = 10,
        length = 1000,
        solver = scisparse_algorithm,
        benchmark = benchmark,
        prevent_assert = True,
    )
    return


mark_100_1000 = pytest.mark.benchmark(
    group = "SVD_inv_100_1000",
    warmup = False,
)

@slow
@mark_100_1000
def test_bench_SVDinv_loop_LUQ_100_1000(benchmark):
    SVD_gen_check(
        N = 100,
        length = 100,
        solver = DAG_algorithm,
        benchmark = benchmark,
        prevent_assert = True,
    )
    return

@slow
@mark_100_1000
def test_bench_SVDinv_scisparse_100_1000(benchmark):
    SVD_gen_check(
        N = 100,
        length = 100,
        solver = scisparse_algorithm,
        benchmark = benchmark,
        prevent_assert = True,
    )
    return


if __name__ == '__main__':
    test_LIGOX()
