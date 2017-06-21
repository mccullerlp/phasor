# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
import numpy as np
from collections import defaultdict
import declarative
from numbers import Number

import scipy.sparse as scisparse
import scipy.sparse.linalg as scisparselin
from phasor.utilities.print import pprint

from .matrix_generic import (
    pre_purge_inplace,
    purge_seqless_inplace,
    purge_reqless_inplace,
    check_seq_req_balance,
)

def pk_prefs(*preflist, cut = False):
    def key(pk):
        if cut:
            inout, pk = pk
        if isinstance(pk, tuple):
            p, k = pk
            pk = p | k
            ksort = []
            for ktype in preflist:
                ksort.append(
                    str(pk.get(ktype, None))
                )
            pk.purge_keys(*preflist)
            ksort.extend(sorted(pk.items()))
            return tuple(ksort)
        else:
            return pk
    return key

def sortkeys_inplace(pklist):
    from ..optics import ports
    pklist.sort(key = pk_prefs(
        ports.QuantumKey,
        ports.ElementKey,
        ports.PortKey,
        ports.OpticalFreqKey,
        ports.ClassicalFreqKey,
        ports.PolKEY,
    ))
    return pklist

def sortkeys_inplace_split(pklist):
    from ..optics import ports
    pklist.sort(key = pk_prefs(
        ports.QuantumKey,
        ports.ElementKey,
        ports.PortKey,
        ports.OpticalFreqKey,
        ports.ClassicalFreqKey,
        ports.PolKEY,
        cut = True
    ))
    return pklist

#from phasor.utilities.print import pprint

from ..base import (
    DictKey,
)

def abssq(arr):
    return arr * arr.conjugate()

def enorm(arr):
    return np.max(abssq(arr))

def wrap_input_node(node):
    return ('INPUT', node)

def wrap_output_node(node):
    return ('OUTPUT', node)


def mgraph_simplify_inplace(
    seq, req, req_alpha, seq_beta, edge_map,
    verbose        = False,
    sorted_order   = False,
):
    if verbose:
        def vprint(*p):
            print(*p)
    else:
        def vprint(*p):
            return

    check_seq_req_balance(seq, req, edge_map)

    sbetaO    = seq_beta
    ralphaO   = req_alpha
    seq_beta  = dict(seq_beta)
    req_alpha = dict(req_alpha)
    req       = dict(req)
    seq       = dict(seq)

    keys = set(seq.keys()) | set(req.keys())
    for node, rset in req.items():
        keys.add(node)
        keys.update(rset)
    for node, sset in seq.items():
        keys.add(node)
        keys.update(sset)

    keys_alpha = set()
    for node, rset in req_alpha.items():
        keys_alpha.update(rset)

    edge_map_beta = dict()
    for node, sset in seq_beta.items():
        for snode in sset:
            edge_map_beta[node, snode] = edge_map[node, snode]

    #pprint(req)
    #pprint(seq)
    #pprint(req_alpha)
    #pprint(seq_beta)

    #keys = (keys - keys_alpha) - keys_beta

    keys = list(keys)
    #pprint(keys)
    sortkeys_inplace(keys)
    keys_alpha = list(keys_alpha)
    #print(keys_alpha)
    sortkeys_inplace_split(keys_alpha)

    keys_inv = dict()
    for idx, k in enumerate(keys):
        keys_inv[k] = idx

    keys_alpha_inv = dict()
    for idx, k in enumerate(keys_alpha):
        keys_alpha_inv[k] = idx

    #CSR generation routine

    arr_keys = []
    arr_arrays = []
    for k, a in edge_map.items():
        arr_keys.append(k)
        arr_arrays.append(np.asarray(a))

    arr_type = np.common_type(*arr_arrays)
    arr_arrays = np.broadcast_arrays(*arr_arrays)

    edge_map_bcast = dict()
    for k, a in zip(arr_keys, arr_arrays):
        edge_map_bcast[k] = a

    data_ind = []
    row_ind = []
    col_ind = []

    for k_fr, seqset in seq.items():
        for k_to in seqset:
            a = edge_map_bcast[k_fr, k_to]
            data_ind.append(a)
            col_ind.append(keys_inv[k_fr])
            row_ind.append(keys_inv[k_to])

    data_alpha_ind = []
    row_alpha_ind = []
    col_alpha_ind = []

    for k_to, reqset in req_alpha.items():
        for k_fr in reqset:
            #print(k_fr, k_to)
            a = edge_map_bcast[k_fr, k_to]
            data_alpha_ind.append(a)
            col_alpha_ind.append(keys_alpha_inv[k_fr])
            row_alpha_ind.append(keys_inv[k_to])

    #TODO: should use the direct constructor after sorting and converting to data, indices, indptr!

    edge_map_ab = defaultdict(lambda : np.zeros_like(a, dtype = arr_type))
    for index in np.ndindex(a.shape):
        #uses 4th constructor of https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html#scipy.sparse.csr_matrix
        A_csc = scisparse.csc_matrix(
            (
                [d[index] for d in data_ind],
                (row_ind, col_ind)
            ),
            shape = (len(keys), len(keys)),
            dtype = arr_type,
        )
        b_csc = scisparse.csc_matrix(
            (
                [d[index] for d in data_alpha_ind],
                (row_alpha_ind, col_alpha_ind)
            ),
            shape = (len(keys), len(keys_alpha)),
            dtype = arr_type,
        )
        #print(arr_type)
        #print(A_csc.dtype)
        #print(b_csc.dtype)
        x_csc = scisparselin.spsolve(A_csc, b_csc)
        if b_csc.ndim > 1 and b_csc.shape[1] > 1:
            #the output of spsolve depends on if b_csc is a vector or not
            #arr1 = x_csc.toarray()
            #arr = np.zeros_like(arr1, dtype = arr_type)
            ind_prev = x_csc.indptr[0]
            if index:
                for idx_col, ind in enumerate(x_csc.indptr[1:]):
                    idx_row = x_csc.indices[ind_prev : ind]
                    data    = x_csc.data[ind_prev : ind]
                    for sub_idx_row, sub_data in zip(idx_row, data):
                        edge_map_ab[idx_col, sub_idx_row][index] = sub_data
                    #arr[idx_row, idx_col] = data
                    ind_prev = ind
            else:
                for idx_col, ind in enumerate(x_csc.indptr[1:]):
                    idx_row = x_csc.indices[ind_prev : ind]
                    data    = x_csc.data[ind_prev : ind]
                    for sub_idx_row, sub_data in zip(idx_row, data):
                        edge_map_ab[idx_col, sub_idx_row] = sub_data
                    #arr[idx_row, idx_col] = data
                    ind_prev = ind
            #pprint(arr - arr1)
        else:
            if index:
                for idx_row in np.nonzero(x_csc)[0]:
                    edge_map_ab[0, idx_row][index] = x_csc[idx_row]
            else:
                for idx_row in np.nonzero(x_csc)[0]:
                    edge_map_ab[0, idx_row] = x_csc[idx_row]
            #pprint(arr - arr1)

    #now reapply the seq and req lists
    edge_map.clear()
    #pprint(edge_map_ab)

    for (idx_col, idx_row), data in edge_map_ab.items():
        k_fr = keys_alpha[idx_col]
        #TODO can only currently deal with 1:1 seq_beta map
        k_to = keys[idx_row]
        sset = seq_beta.get(k_to, None)
        #print(k_fr, k_to, sset)
        if sset:
            assert(len(sset) == 1)
            s_k_to = next(iter(sset))
            edge_map[k_fr, s_k_to] = data * edge_map_beta[k_to, s_k_to]
            sbetaO[k_fr].add(s_k_to)
            ralphaO[s_k_to].add(k_fr)
    #pprint(seqO)
    #pprint(reqO)
    return


def inverse_solve_inplace(
    seq, req,
    edge_map,
    outputs_set,
    inputs_set   = frozenset(),
    inputs_map   = None,
    purge_in     = True,
    purge_out    = True,
    verbose      = False,
    negative     = False,
    scattering   = False,
    **kwargs
):
    #the later inverter balks if the edge map is empty, so exit early in that case
    if not outputs_set or (inputs_map is None and not inputs_set):
        return declarative.Bunch(
            outputs_map = dict(),
            edge_map    = dict(),
            seq         = seq,
            req         = req,
        )

    if scattering:
        keys = set(seq.keys()) | set(req.keys()) | inputs_set | outputs_set
        if inputs_map is not None:
            keys.update(inputs_map.keys())
        print("IMAP: ", inputs_set)
        for node in keys:
            if node in seq[node]:
                edge_map[node, node] = edge_map[node, node] - 1
            else:
                edge_map[node, node] = -1
                seq[node].add(node)
                req[node].add(node)
        #sign conventions reversed for scattering matrix
        negative = not negative

    pre_purge_inplace(seq, req, edge_map)

    req_alpha = defaultdict(set)
    seq_beta  = defaultdict(set)

    VACUUM_STATE = wrap_input_node(DictKey(special = 'vacuum'))
    if inputs_map is not None:
        #first dress the nodes. The source vectors is converted into edges with a special
        #source node
        #the inputs are from the special state (with implicit vector value of '1')
        for inode, val in inputs_map.items():
            req_alpha[inode].add(VACUUM_STATE)
            edge_map[VACUUM_STATE, inode] = val

    #first dress the nodes
    for inode in inputs_set:
        winode = wrap_input_node(inode)
        req_alpha[inode].add(winode)
        edge_map[winode, inode] = 1

    if negative:
        value = -1
    else:
        value = 1
    for onode in outputs_set:
        wonode = wrap_output_node(onode)
        #seq[onode].add(wonode)
        #req[wonode].add(onode)
        seq_beta[onode].add(wonode)
        edge_map[onode, wonode] = value

    #purge_in = False
    #purge_out = False
    if purge_in:
        purge_reqless_inplace(
            seq       = seq,
            req       = req,
            seq_beta  = seq_beta,
            req_alpha = req_alpha,
            edge_map  = edge_map,
        )
    if purge_out:
        purge_seqless_inplace(
            seq        = seq,
            req        = req,
            seq_beta   = seq_beta,
            req_alpha  = req_alpha,
            edge_map   = edge_map,
        )
    #print("SEQ")
    #print_seq(seq, edge_map)

    #subN = len(wrapped_onodes) + len(wrapped_inodes)
    #print("SPARSITY ", len(seq) - subN, len(edge_map) - subN, (len(edge_map) - subN) / (len(seq) - subN))

    #simplify with the wrapped nodes
    mgraph_simplify_inplace(
        seq       = seq,
        req       = req,
        seq_beta  = seq_beta,
        req_alpha = req_alpha,
        edge_map  = edge_map,
        verbose   = verbose,
        **kwargs
    )

    if inputs_map is not None:
        #now unwrap the single state
        outputs_map = dict()
        for onode in outputs_set:
            wonode = ('OUTPUT', onode)
            sourced_edge = edge_map.get((VACUUM_STATE, wonode), None)
            if sourced_edge is not None:
                outputs_map[onode] = sourced_edge
    else:
        outputs_map = None

    #now unwrap the nodes
    unwrapped_edge_map = dict()
    unwrapped_seq_map = defaultdict(set)
    unwrapped_req_map = defaultdict(set)

    for inode in inputs_set:
        winode = ('INPUT', inode)
        #Could get exceptions here if we don't purge and the input maps have spurious
        #outputs (nodes with no seq) other than the wrapped ones generated here
        for wonode in seq_beta[winode]:
            sourced_edge = edge_map[winode, wonode]
            k, onode = wonode
            assert(k == 'OUTPUT')
            unwrapped_edge_map[inode, onode] = sourced_edge
            unwrapped_seq_map[inode].add(onode)
            unwrapped_req_map[onode].add(inode)

    return declarative.Bunch(
        outputs_map = outputs_map,
        edge_map    = unwrapped_edge_map,
        seq         = unwrapped_seq_map,
        req         = unwrapped_req_map,
    )
