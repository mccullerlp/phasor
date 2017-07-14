# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from numbers import Number
import numpy as np
from collections import defaultdict
import declarative

#from ..math.dispatched import abs_sq

from ..utilities.priority_queue import HeapPriorityQueue, Empty
from ..utilities.print import pprint

from .matrix_generic import (
    pre_purge_inplace,
    purge_seqless_inplace,
    purge_reqless_inplace,
    check_seq_req_balance,
)

from .DAG_algorithm_impl import (
    reduceLU,
    reduceLUQ_row,
)

from ..base import (
    DictKey,
)

N_limit_rel = 100

def abssq(arr):
    return arr.real**2 + arr.imag**2

def enorm(arr):
    return np.max(abssq(arr))


def mgraph_simplify_inplace(
    SRABE,
    verbose        = False,
    sorted_order   = False,
    **kwargs
):
    if verbose:
        def vprint(*p):
            print(*p)
    else:
        def vprint(*p):
            return

    (seq, req, req_alpha, seq_beta, edge_map) = SRABE
    check_seq_req_balance(seq, req, edge_map)

    #TODO temporary to check broadcasting logic
    #arr_keys = []
    #arr_arrays = []
    #for k, a in edge_map.items():
    #    arr_keys.append(k)
    #    arr_arrays.append(np.asarray(a))

    #arr_type = np.common_type(*arr_arrays)
    #arr_arrays = np.broadcast_arrays(*arr_arrays)

    #edge_map_bcast = dict()
    #for k, a in zip(arr_keys, arr_arrays):
    #    edge_map_bcast[k] = a

    #edge_map.update(edge_map_bcast)

    SRABE = (seq, req, req_alpha, seq_beta, edge_map)

    if sorted_order:
        mgraph_simplify_sorted(SRABE = SRABE, **kwargs)
    else:
        vprint("TRIVIAL STAGE, REMAINING {0}".format(len(req)))
        mgraph_simplify_trivial(SRABE = SRABE, **kwargs)
        vprint("TRIVIAL STAGE, REMAINING {0}".format(len(req)))
        mgraph_simplify_trivial(SRABE = SRABE, **kwargs)
        vprint("BADGUY STAGE, REMAINING {0}".format(len(req)))
        mgraph_simplify_badguys(SRABE = SRABE, **kwargs)
    return


def mgraph_simplify_sorted(
    SRABE,
    **kwargs
):
    seq, req, req_alpha, seq_beta, edge_map, = SRABE

    def generate_node_cost(node):
        return node

    pqueue = HeapPriorityQueue()

    for node in seq.keys():
        cost = generate_node_cost(node)
        pqueue.push((cost, node))

    while req:
        cost, node = pqueue.pop()

        reduceLU(
            SRABE = SRABE,
            node  = node,
            **kwargs
        )


def mgraph_simplify_trivial(
    SRABE,
    **kwargs
):
    seq, req, req_alpha, seq_beta, edge_map, = SRABE

    def generate_node_count_tup(node):
        s_n = 0
        s_n_full = 0
        for enode in seq[node]:
            edge_val = edge_map[node, enode]
            s_n += 1
            if isinstance(edge_val, Number):
                s_n_full += 1
            else:
                s_n_full += len(np.asanyarray(edge_val).flatten())
        r_n = 0
        r_n_full = 0
        for enode in req[node]:
            edge_val = edge_map[enode, node]
            r_n += 1
            if isinstance(edge_val, Number):
                r_n_full += 1
            else:
                r_n_full += len(np.asanyarray(edge_val).flatten())
        return (s_n * r_n, s_n * r_n_full + r_n * s_n_full)

    pqueue = HeapPriorityQueue()
    for node in seq.keys():
        cost = generate_node_count_tup(node)
        pqueue.push((cost, node))

    node_costs_invalid_in_queue = set()

    while pqueue:
        cost, node = pqueue.pop()
        if node in node_costs_invalid_in_queue:
            cost = generate_node_count_tup(node)

        edge_cost, arr_cost = cost

        self_edge = edge_map.get((node, node), None)
        if self_edge is None:
            continue
        sedge_abssq = abssq(self_edge)

        #check conditions for numerical stability, if they are bad, drop the node

        if np.all(sedge_abssq == 0):
            continue

        badness = 0
        #columns
        for rnode in req[node]:
            if rnode == node:
                continue
            edge = edge_map[rnode, node]
            badness = max(badness, np.max(abssq(edge) / sedge_abssq))

        for snode in seq[node]:
            if snode == node:
                continue
            edge = edge_map[node, snode]
            badness = max(badness, np.max(abssq(edge) / sedge_abssq))

        #drop the node from the queue!
        if badness > N_limit_rel:
            continue

        reduceLU(
            SRABE,
            node = node,
            node_costs_invalid_in_queue = node_costs_invalid_in_queue,
            **kwargs
        )
    return

def mgraph_simplify_badguys(
    SRABE,
    verbose = False,
    **kwargs
):
    seq, req, seq_beta, req_alpha, edge_map, = SRABE

    #verbose = True
    if verbose:
        def vprint(*p):
            print(*p)
    else:
        def vprint(*p):
            return

    edge_norms = dict()

    #this is just a heuristic
    def generate_node_count(node):
        s_n = len(seq[node])
        r_n = len(req[node])
        return s_n * r_n

    def generate_node_count_arr(node):
        s_n = 0
        s_n_full = 0
        for enode in seq[node]:
            edge_val = edge_map[node, enode]
            s_n += 1
            if isinstance(edge_val, Number):
                s_n_full += 1
            else:
                s_n_full += len(np.asanyarray(edge_val).flatten())
        r_n = 0
        r_n_full = 0
        for enode in req[node]:
            edge_val = edge_map[enode, node]
            r_n += 1
            if isinstance(edge_val, Number):
                r_n_full += 1
            else:
                r_n_full += len(np.asanyarray(edge_val).flatten())
        return s_n * r_n_full + r_n * s_n_full

    def generate_row_cost(node):
        tot_norm = 0
        for snode in seq[node]:
            norm = edge_norms.get((node, snode), None)
            if norm is None:
                norm = enorm(edge_map[node, snode])
                edge_norms[node, snode] = norm
            tot_norm = tot_norm + norm
        return tot_norm

    def generate_col_cost(node):
        tot_norm = 0
        for rnode in req[node]:
            norm = edge_norms.get((node, rnode), None)
            if norm is None:
                norm = enorm(edge_map[rnode, node])
                edge_norms[node, rnode] = norm
            tot_norm = tot_norm + norm
        return tot_norm

    def generate_max_cost(node):
        rcost = generate_row_cost(node)
        ccost = generate_col_cost(node)
        return max(rcost, ccost)
    generate_node_cost = generate_max_cost

    pqueue = HeapPriorityQueue()
    node_costs_invalid_in_queue = set()
    for node in seq.keys():
        cost = generate_node_cost(node)
        pqueue.push((cost, node))
    vprint("pqueue length: ", len(pqueue))

    try:
        while req:
            while node_costs_invalid_in_queue:
                node = node_costs_invalid_in_queue.pop()
                if node not in seq:
                    continue
                cost = generate_node_cost(node)
                pqueue.push((cost, node))
            #vprint("REQ: ", req)
            #vprint("REQ_A: ", req_alpha)
            #vprint("SEQ: ", seq)
            #vprint("SEQ_B: ", seq_beta)
            cost, node = pqueue.pop()
            if node not in seq:
                continue

            vprint("MY NODE: ", node)
            new_cost = generate_node_cost(node)
            while abs(abs(cost / new_cost) - 1) > .1:
                cost, node = pqueue.pushpop((new_cost, node))
                while node not in seq:
                    cost, node = pqueue.pop()
                new_cost = generate_node_cost(node)
                vprint("NCOST: ", node, new_cost)

            if node not in seq:
                vprint("MY GOD: ", node)

            if node in seq[node]:
                #node must at least have a self-loop
                min_rnode = None
                min_rnode_cost = float('inf')
                for rnode in seq[node]:
                    rcost = generate_row_cost(rnode)
                    if rcost < min_rnode_cost:
                        min_rnode = rnode
                        min_rnode_cost = rcost
                vprint("MIN_MAX: ", node, min_rnode)

            reduceLUQ_row(
                SRABE  = SRABE,
                node   = node,
                node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                vprint = vprint,
                **kwargs
            )
    except Empty:
        assert(req)


def wrap_input_node(node):
    return ('INPUT', node)

def wrap_output_node(node):
    return ('OUTPUT', node)

def inverse_solve_inplace(
    seq, req,
    edge_map,
    outputs_set,
    inputs_set     = frozenset(),
    inputs_map     = None,
    inputs_map_sym = None,
    edge_map_sym   = None,
    purge_in       = True,
    purge_out      = True,
    verbose        = False,
    negative       = False,
    scattering     = False,
    **kwargs
):
    if scattering:
        keys = set(seq.keys()) | set(req.keys())
        for node in keys:
            if node in seq[node]:
                edge_map[node, node] = edge_map[node, node] - 1
            else:
                edge_map[node, node] = -1
                seq[node].add(node)
                req[node].add(node)
            if edge_map_sym is not None:
                edge_sym = edge_map_sym.get((node, node), None)
                if edge_sym is not None:
                    edge_map_sym[node, node] = edge_sym - 1
                else:
                    edge_map_sym[node, node] = -1
        #sign conventions reversed for scattering matrix
        negative = not negative

    if edge_map_sym or inputs_map_sym:
        sym = declarative.Bunch()
        sym.seq       = defaultdict(set)
        sym.req       = defaultdict(set)
        sym.seq_beta  = defaultdict(set)
        sym.req_alpha = defaultdict(set)
        if inputs_map_sym is None:
            inputs_map_sym = dict()
        if edge_map_sym is None:
            edge_map_sym = dict()
        sym.edge_map = edge_map_sym
    else:
        sym = None


    pre_purge_inplace(seq, req, edge_map)

    req_alpha = defaultdict(set)
    seq_beta  = defaultdict(set)

    VACUUM_STATE = DictKey(special = 'vacuum')
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

    #this convention is correct for how this solver operates!
    if negative:
        value = 1
    else:
        value = -1
    for onode in outputs_set:
        wonode = wrap_output_node(onode)
        seq_beta[onode].add(wonode)
        edge_map[onode, wonode] = value

    #purge_in = False
    #purge_out = False
    if purge_in:
        purge_reqless_inplace(
            seq        = seq,
            req        = req,
            seq_beta   = seq_beta,
            req_alpha  = req_alpha,
            edge_map   = edge_map,
        )
    if purge_out:
        purge_seqless_inplace(
            seq        = seq,
            req        = req,
            seq_beta   = seq_beta,
            req_alpha  = req_alpha,
            edge_map   = edge_map,
        )

    if sym:
        for kf, kt in sym.edge_map:
            sym.seq[kf].add(kt)
            sym.req[kt].add(kf)

        for node, rset in req_alpha.items():
            e = inputs_map_sym.get(node, None)
            if e is not None:
                sym.req_alpha[node].add(VACUUM_STATE)
                sym.edge_map[VACUUM_STATE, node] = e
        SRABE_SYM = sym.seq, sym.req, sym.req_alpha, sym.seq_beta, sym.edge_map
    else:
        SRABE_SYM = None

    #print("SEQ")
    #print_seq(seq, edge_map)

    #subN = len(wrapped_onodes) + len(wrapped_inodes)
    #print("SPARSITY ", len(seq) - subN, len(edge_map) - subN, (len(edge_map) - subN) / (len(seq) - subN))

    #simplify with the wrapped nodes
    mgraph_simplify_inplace(
        SRABE     = (seq, req, req_alpha, seq_beta, edge_map,),
        verbose   = verbose,
        SRABE_SYM = SRABE_SYM,
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

    if sym:
        sym_seq_beta = sym.seq_beta
        sym_edge_map = sym.edge_map
        for inode in inputs_set:
            winode = ('INPUT', inode)
            #Could get exceptions here if we don't purge and the input maps have spurious
            #outputs (nodes with no seq) other than the wrapped ones generated here
            sbeta_sym = sym_seq_beta[winode]
            sbeta_nosym = seq_beta[winode] - sbeta_sym

            for wonode in sbeta_sym:
                sourced_edge = sym_edge_map[winode, wonode]
                k, onode = wonode
                assert(k == 'OUTPUT')
                unwrapped_edge_map[inode, onode] = sourced_edge
                unwrapped_seq_map[inode].add(onode)
                unwrapped_req_map[onode].add(inode)
            for wonode in sbeta_nosym:
                sourced_edge = edge_map[winode, wonode]
                k, onode = wonode
                assert(k == 'OUTPUT')
                unwrapped_edge_map[inode, onode] = sourced_edge
                unwrapped_seq_map[inode].add(onode)
                unwrapped_req_map[onode].add(inode)
    else:
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
