# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import warnings
import os
import numpy as np
from collections import defaultdict
import tempfile

#from ..math.dispatched import abs_sq


def SRABE2METIS(
        SRABE,
        METIS_fname
):
    (seq, req, req_alpha, seq_beta, edge_map) = SRABE

    #TODO organize this sortkeys algorithm into system or somewhere
    from .scisparse_algorithm import sortkeys_inplace
    #generate arbitrary ordering
    nlist = list(seq.keys())
    sortkeys_inplace(nlist)
    nlist_inv = dict()
    for idx, node in enumerate(nlist):
        nlist_inv[node] = idx
    edge_weights = defaultdict(dict)
    edge_weights_r = defaultdict(dict)

    for (rnode, snode), edge in edge_map.items():
        #allow defaults since edge_map includes the alphas and betas as well
        ridx = nlist_inv.get(rnode, None)
        sidx = nlist_inv.get(snode, None)
        if ridx is None or sidx is None:
            continue

        if ridx > sidx:
            #canonicalize directed graph to undirected graph
            ridx, sidx = sidx, ridx

        #TODO, add symbolics ability to this
        edge_w = len(np.asarray(edge).flatten())

        #metis can't deal with loops!
        if ridx == sidx:
            continue

        edge_weights[ridx][sidx] = max(
            edge_w,
            edge_weights.get((ridx, sidx), 0),
        )
        edge_weights_r[sidx][ridx] = edge_weights[ridx][sidx]

    if isinstance(METIS_fname, str):
        Fmetis = open(METIS_fname, 'w')
    else:
        Fmetis = METIS_fname
    try:
        #write the header including edge weights
        n_edges = 0
        for idx, edict in edge_weights.items():
            if idx in edict:
                n_edges += len(edict)
            else:
                n_edges += len(edict)
        Fmetis.write("{vertices} {edges} 001\n".format(
            vertices = len(nlist),
            edges    = n_edges,
        ))
        print("NUM EDGES: ", len(edge_weights))

        for idx, node in enumerate(nlist):
            edict = edge_weights.get(idx, dict())
            for sidx, edge_w in edict.items():
                Fmetis.write("{sidx} {weight} ".format(
                    sidx = sidx + 1,
                    weight = edge_w,
                ))
            for sidx, edge_w in edge_weights_r[idx].items():
                #skip the self edge since it appears twice
                if sidx == idx:
                    continue
                Fmetis.write("{sidx} {weight} ".format(
                    sidx = sidx + 1,
                    weight = edge_w,
                ))
            Fmetis.write("\n")
    finally:
        if isinstance(METIS_fname, str):
            Fmetis.close()
    return nlist

def METIS_reorder(
    SRABE,
    METIS_fname,
    clear_file  = False,
):
    clear_results = True
    if METIS_fname is tempfile:
        #TODO create tempfile
        METIS_fd, METIS_fname = tempfile.mkstemp(
            suffix = '.metis',
            text = True
        )
        clear_file = True

        nlist = SRABE2METIS(
            SRABE,
            os.fdopen(os.dup(METIS_fd), 'w'),
        )
    else:
        METIS_fd = None

        nlist = SRABE2METIS(
            SRABE,
            METIS_fname,
        )

    import subprocess
    try:
        retoutput = subprocess.check_output(
            ['ndmetis', METIS_fname],
        )
    except subprocess.CalledProcessError as E:
        print(E.output)
        warnings.warn("Calling ndmetis failed. Is it installed? It will speed up the computation")
        return None

    nlistI = []
    with open(METIS_fname + '.iperm', 'r') as FmetisO:
        for line in FmetisO.readlines():
            nlistI.append(int(line))
    print(nlistI)
    nlistI = np.asarray(nlistI)
    nlist_reorder = []
    for idx in np.argsort(nlistI):
        nlist_reorder.append(nlist[idx])

    if METIS_fd is not None:
        os.close(METIS_fd)
    if clear_file:
        os.unlink(METIS_fname)
    if clear_results:
        os.unlink(METIS_fname + '.iperm')
    #return None
    return nlist
    return nlist_reorder
    #for idx_from, idx_to in enumerate(nlistI):



