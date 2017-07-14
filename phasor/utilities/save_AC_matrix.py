# -*- coding: utf-8 -*-
"""
simple interface for saving matrix problems to pickles for later analysis and work on the matrix solving subsystem
"""
from __future__ import division, print_function, unicode_literals
import pickle


def save_AC_matrix(fname, readout = None):

    sys = readout.system
    sol = sys.solution.coupling_solution_get(N=-1, drive_set = 'AC', readout_set='AC')
    cmat = sol.coupling_matrix
    try:
        portN = readout.portNI
    except AttributeError:
        portN = readout.portN

    k_to = (portN,  readout.keyP)
    k_from = (readout.portD,  readout.keyP)
    AC = sol.coupling_matrix_inv[k_from, k_to]
    combo = dict(
        coupling_matrix = cmat.idx_dict,
        AC_solution = AC,
        AC_index = (cmat.vspace_from.key_map(k_from), cmat.vspace_to.key_map(k_to)),
    )
    with open(fname, 'wb') as F:
        pickle.dump(combo, F)


def save_AC_matrix_noise(fname, sys):

    sol = sys.solution.coupling_solution_get(N=-1, drive_set = 'noise', readout_set='noise')
    cmat = sol.coupling_matrix
    combo = dict(
        coupling_matrix = cmat.idx_dict,
        readouts = [cmat.vspace_from.key_map(pk) for pk in sys.solution.readout_pk_sets['noise']],
        drives   = [cmat.vspace_from.key_map(pk) for pk in sys.solution.drive_pk_sets['noise']],
    )

    with open(fname, 'wb') as F:
        pickle.dump(combo, F)
