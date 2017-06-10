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
from openLoop.utilities.print import pprint

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

#from openLoop.utilities.print import pprint

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
    seq, req,
    edge_map,
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

    reqO = req
    seqO = seq
    req = dict(req)
    seq = dict(seq)

    #at this stage all of the alpha_reqs are only single move
    keys = set()
    keys_alpha = set()
    keys_beta  = set()
    req_alpha = defaultdict(set)
    seq_beta  = defaultdict(set)
    beta_set  = set()
    alpha_set = set()
    edge_map_beta = dict()
    for node in req:
        if not seq.get(node, None):
            for rnode in req[node]:
                seq_beta[rnode].add(node)
                beta_set.add(node)
                edge_map_beta[rnode, node] = edge_map[rnode, node]
            keys_beta.add(node)
        else:
            keys.add(node)
    for node in seq:
        if not req.get(node, None):
            for snode in seq[node]:
                req_alpha[snode].add(node)
                alpha_set.add(node)
            keys_alpha.add(node)
        else:
            keys.add(node)

    #this must be done separately otherwise some nodes are accidentally considered alpha or beta nodes
    for node, seqset in seq_beta.items():
        #print("BETA: ", node, seqset)
        for snode in seqset:
            req[snode].remove(node)
            seq[node].remove(snode)
    for node, reqset in req_alpha.items():
        #print("ALPHA: ", node, reqset)
        for rnode in reqset:
            seq[rnode].remove(node)
            req[node].remove(rnode)
    #remove the alpha and beta nodes from the standard sets
    for node in alpha_set:
        del seq[node]
        del req[node]
    for node in beta_set:
        del req[node]
        del seq[node]

    #pprint(req)
    #pprint(seq)
    #pprint(req_alpha)
    #pprint(seq_beta)

    keys = (keys - keys_alpha) - keys_beta

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
    reqO.clear()
    seqO.clear()
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
            reqO[s_k_to].add(k_fr)
            seqO[k_fr].add(s_k_to)
    #pprint(seqO)
    #pprint(reqO)
    return

def inverse_solve_inplace(
    seq, req,
    edge_map,
    inputs_set,
    outputs_set,
    purge_in = True,
    purge_out = True,
    verbose = False,
    negative = False,
    scattering = False,
    **kwargs
):
    if scattering:
        keys = set(seq.keys()) | set(req.keys()) | inputs_set | outputs_set
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

    #first dress the nodes
    wrapped_inodes = set()
    for inode in inputs_set:
        winode = wrap_input_node(inode)
        wrapped_inodes.add(winode)
        seq[winode].add(inode)
        req[inode].add(winode)
        edge_map[winode, inode] = 1

    wrapped_onodes = set()
    if negative:
        value = -1
    else:
        value = 1
    for onode in outputs_set:
        wonode = wrap_output_node(onode)
        wrapped_onodes.add(wonode)
        seq[onode].add(wonode)
        req[wonode].add(onode)
        edge_map[onode, wonode] = value

    #purge_in = False
    #purge_out = False
    if purge_in:
        purge_reqless_inplace(
            except_set = wrapped_inodes,
            seq = seq,
            req = req,
            edge_map = edge_map,
        )
    if purge_out:
        purge_seqless_inplace(
            except_set = wrapped_onodes,
            seq = seq,
            req = req,
            edge_map = edge_map,
        )
    #print("SEQ")
    #print_seq(seq, edge_map)

    #simplify with the wrapped nodes
    mgraph_simplify_inplace(
        seq            = seq,
        req            = req,
        edge_map       = edge_map,
        verbose        = verbose,
        **kwargs
    )

    #now unwrap the nodes
    unwrapped_edge_map = dict()
    unwrapped_seq_map = defaultdict(set)
    unwrapped_req_map = defaultdict(set)

    for inode in inputs_set:
        winode = ('INPUT', inode)
        #Could get exceptions here if we don't purge and the input maps have spurious
        #outputs (nodes with no seq) other than the wrapped ones generated here
        for wonode in seq[winode]:
            sourced_edge = edge_map[winode, wonode]
            k, onode = wonode
            assert(k == 'OUTPUT')
            unwrapped_edge_map[inode, onode] = sourced_edge
            unwrapped_seq_map[inode].add(onode)
            unwrapped_req_map[onode].add(inode)
    return declarative.Bunch(
        edge_map = unwrapped_edge_map,
        seq      = unwrapped_seq_map,
        req      = unwrapped_req_map,
    )

def push_solve_inplace(
    seq, req,
    edge_map,
    inputs_map,
    outputs_set,
    inputs_AC_set = frozenset(),
    purge_in = True,
    purge_out = True,
    negative = False,
    scattering = False,
):
    if scattering:
        keys = set(seq.keys()) | set(req.keys()) | set(inputs_map.keys()) | outputs_set
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
    #first dress the nodes. The source vectors is converted into edges with a special
    #source node
    #the inputs are from the special state (with implicit vector value of '1')
    VACUUM_STATE = wrap_input_node(DictKey(special = 'vacuum'))
    for inode, val in inputs_map.items():
        seq[VACUUM_STATE].add(inode)
        req[inode].add(VACUUM_STATE)
        edge_map[VACUUM_STATE, inode] = val

    wrapped_inodes = set()
    for inode in inputs_AC_set:
        winode = wrap_input_node(inode)
        #print("WINODEA", winode)
        wrapped_inodes.add(winode)
        seq[winode].add(inode)
        req[inode].add(winode)
        edge_map[winode, inode] = 1

    if negative:
        value = -1
    else:
        value = 1
    wrapped_onodes = set()
    for onode in outputs_set:
        wonode = wrap_output_node(onode)
        #print("WONODEA", wonode)
        wrapped_onodes.add(wonode)
        seq[onode].add(wonode)
        req[wonode].add(onode)
        edge_map[onode, wonode] = value

    #purge_in = False
    #purge_out = False
    #print_seq(seq, edge_map)
    if purge_in:
        purge_reqless_inplace(
            except_set = frozenset([VACUUM_STATE]).union(wrapped_inodes),
            seq = seq,
            req = req,
            edge_map = edge_map,
        )
    if purge_out:
        purge_seqless_inplace(
            except_set = wrapped_onodes,
            seq = seq,
            req = req,
            edge_map = edge_map,
        )
    #print_seq(seq, edge_map)

    if edge_map:
        #simplify with the wrapped nodes
        mgraph_simplify_inplace(
            seq = seq, req = req,
            edge_map = edge_map,
        )

    #now unwrap the
    outputs_map = dict()
    for onode in outputs_set:
        wonode = ('OUTPUT', onode)
        sourced_edge = edge_map.get((VACUUM_STATE, wonode), None)
        if sourced_edge is not None:
            outputs_map[onode] = sourced_edge

    #now unwrap the nodes
    unwrapped_edge_map = dict()
    unwrapped_seq_map = defaultdict(set)
    unwrapped_req_map = defaultdict(set)
    for inode in inputs_AC_set:
        winode = ('INPUT', inode)
        #print("WINODE", winode)
        #print("WINODE", seq[winode])
        #Could get exceptions here if we don't purge and the input maps have spurious
        #outputs (nodes with no seq) other than the wrapped ones generated here
        for wonode in seq[winode]:
            sourced_edge = edge_map[winode, wonode]
            k, onode = wonode
            #print("WONODE", wonode)
            assert(k == 'OUTPUT')
            unwrapped_edge_map[inode, onode] = sourced_edge
            unwrapped_seq_map[inode].add(onode)
            unwrapped_req_map[onode].add(inode)

    #print("AC edge map: ", unwrapped_edge_map)
    return declarative.Bunch(
        outputs_map = outputs_map,
        AC_edge_map = unwrapped_edge_map,
        AC_seq      = unwrapped_seq_map,
        AC_req      = unwrapped_req_map,
    )

