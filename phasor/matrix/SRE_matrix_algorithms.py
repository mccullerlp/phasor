# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np
from collections import defaultdict
import declarative

def abssq(arr):
    return arr * arr.conjugate()

def enorm(arr):
    return np.max(abssq(arr))

def matrix_mult_sre(sre1, sre2):
    seq1, req1, edge_mape_1 = sre1
    seq2, req2, edge_mape_2 = sre2

    seq = dict()
    req = dict()
    edge_map = dict()

    for k_mid, mseq in seq2.items():
        if not mseq:
            continue
        for k_from in req1[k_mid]:
            e1 = edge_mape_1[k_from, k_mid]
            seq.setdefault(k_from, set())
            for k_to in mseq:
                if k_to not in seq2[k_mid]:
                    continue
                e2 = edge_mape_2[k_mid, k_to]
                if k_to in seq[k_from]:
                    edge_map[k_from, k_to] = edge_map[k_from, k_to] + e2 * e1
                else:
                    edge_map[k_from, k_to] = e2 * e1
                    seq[k_from].add(k_to)
                    req.setdefault(k_to, set()).add(k_from)

    check_sre((seq, req, edge_map))
    return seq, req, edge_map

def check_sre(sre):
    seq, req, edge_map = sre
    for node in req:
        for rnode in req[node]:
            assert(node in seq[rnode])
    for node in seq:
        for snode in seq[node]:
            assert(node in req[snode])
            edge_map[node, snode]

def copy_sre(sre):
    Oseq, Oreq, Oedge_map = sre
    seq = defaultdict(set)
    req = defaultdict(set)
    for k, s in Oseq.items():
        seq[k] = set(s)
    for k, s in Oreq.items():
        req[k] = set(s)
    edge_map = dict(Oedge_map)
    return seq, req, edge_map


def generate_unitary_by_gram_schmidt(edge_dict_SRE, added_vect, vect_from):
    """
    Adds column by column
    """
    added_vect = dict(added_vect)
    seq, req, edge_map = edge_dict_SRE
    for k_from, fseq in seq.items():
        #projection
        #with norm
        norm_sq = 0
        proj = 0
        for k_to in fseq:
            e = edge_map[k_from, k_to]
            proj = proj + e.conjugate() * added_vect.get(k_to, 0)
            norm_sq = norm_sq + abssq(e)

        for k_to in fseq:
            added_vect[k_to] = added_vect.get(k_to, 0) - proj * edge_map[k_from, k_to] / norm_sq

    finfo = np.finfo(float)
    norm_sq = 0
    for k_to, edge in added_vect.items():
        norm_sq = norm_sq + abssq(edge)
    norm = norm_sq**.5
    seq[vect_from] = set()
    for k_to, edge in added_vect.items():
        lval = abs(edge.real) + abs(edge.imag)
        #only add if sufficiently large

        if np.all(lval > finfo.eps * 10):
            seq[vect_from].add(k_to)
            req.setdefault(k_to, set()).add(vect_from)
            edge_map[vect_from, k_to] = edge / norm

def edge_matrix_to_unitary_sre(edge_map):
    seq = defaultdict(set)
    for k_f, k_t in edge_map:
        seq[k_f].add(k_t)

    useq = dict()
    ureq = dict()
    uemap = dict()

    for k_f in sorted(seq.keys()):
        vect = dict()
        for k_t in seq[k_f]:
            vect[k_t] = edge_map[k_f, k_t]

        generate_unitary_by_gram_schmidt((useq, ureq, uemap), vect, k_f)
    return useq, ureq, uemap

#def srq_prune_eps(sre):
#    seq, req, edge_map = sre
#    finfo = np.finfo(float)
#    for (k_from, k_to), edge in edge_map:
#        lval = abs(edge.real) + abs(edge.imag)
#        if 


def adjoint_sre(sre):
    seq, req, edge_map = sre
    edge_mape_2 = dict()
    for (k_from, k_to), edge in edge_map.items():
        edge_mape_2[k_to, k_from] = edge.conjugate()
    seq2 = dict()
    for k, s in req.items():
        seq2[k] = set(s)
    req2 = dict()
    for k, s in seq.items():
        req2[k] = set(s)
    return seq2, req2, edge_mape_2

def SRE_count_sparsity(sre):
    seq, req, edge_map = sre

    N = 0
    for k_f, fseq in seq.items():
        N += len(fseq)

    return declarative.Bunch(
        density_sq = N / len(seq)**2,
        density_lin = N / len(seq),
        Nedges = N,
        Nnodes = len(seq),
    )








