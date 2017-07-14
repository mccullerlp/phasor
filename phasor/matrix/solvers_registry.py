# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from ..utilities.future_from_2 import str, object

import numpy as np
from collections import defaultdict
import declarative

from ..utilities.print import pprint

from ..base import (
    DictKey,
)

from ..math import dispatched as dmath

from ..math.key_matrix import (
    KVSpace,
    KeyVector,
    KeyMatrix,
)


def setdict_copy(orig):
    duplicate = defaultdict(set)
    for k, vset in orig.items():
        duplicate[k] = set(vset)
    return duplicate


def loop_fast_unstable():
    from ..matrix import graph_algorithm
    return declarative.Bunch(
        inverse_solve_inplace = graph_algorithm.inverse_solve_inplace,
        symbolics_supported   = True,
        symbolics_inline      = True,
    )


def loop_LUQ():
    from ..matrix import DAG_algorithm
    return declarative.Bunch(
        inverse_solve_inplace = DAG_algorithm.inverse_solve_inplace,
        symbolics_supported   = True,
        symbolics_inline      = False,
    )


def scisparse():
    from ..matrix import scisparse_algorithm
    return declarative.Bunch(
        inverse_solve_inplace = scisparse_algorithm.inverse_solve_inplace,
        symbolics_supported   = False,
    )


def scisparse_superLU():
    from ..matrix import scisparse_algorithm
    from scipy.sparse.linalg import use_solver
    use_solver(useUmfpack = False)
    return declarative.Bunch(
        inverse_solve_inplace = scisparse_algorithm.inverse_solve_inplace,
        symbolics_supported   = False,
    )


def scisparse_umfpack():
    from ..matrix import scisparse_algorithm
    from scipy.sparse.linalg import use_solver
    use_solver(useUmfpack = True)
    return declarative.Bunch(
        inverse_solve_inplace = scisparse_algorithm.inverse_solve_inplace,
        symbolics_supported   = False,
    )

#TODO: Make a KLU solver since Finesse uses it. We could also reuse the symbolic solver portion!


solvers_symbolic = dict(
    loop_fast_unstable = loop_fast_unstable,
    loop_LUQ           = loop_LUQ,
)

solvers_numeric = dict(
    scisparse_umfpack = scisparse_umfpack,
    scisparse_superLU = scisparse_superLU,
    scisparse         = scisparse,
)

solvers_all = dict()
solvers_all.update(solvers_numeric)
solvers_all.update(solvers_symbolic)




