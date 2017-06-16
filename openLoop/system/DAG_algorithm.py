# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
from numbers import Number
import numpy as np
from collections import defaultdict
import declarative

from ..utilities.priority_queue import HeapPriorityQueue, Empty
from ..utilities.print import pprint

from .matrix_generic import (
    pre_purge_inplace,
    purge_seqless_inplace,
    purge_reqless_inplace,
    check_seq_req_balance,
)

from ..base import (
    DictKey,
)

N_limit_rel = 100

def abssq(arr):
    return arr * arr.conjugate()

def enorm(arr):
    return np.max(abssq(arr))


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
    req_alpha = defaultdict(set)
    seq_beta  = defaultdict(set)
    beta_set  = set()
    alpha_set = set()
    for node in req:
        if not seq.get(node, None):
            for rnode in req[node]:
                seq_beta[rnode].add(node)
                beta_set.add(node)
    for node in seq:
        if not req.get(node, None):
            for snode in seq[node]:
                req_alpha[snode].add(node)
                alpha_set.add(node)

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

    kwargs = dict(
        seq                         = seq,
        req                         = req,
        req_alpha                   = req_alpha,
        seq_beta                    = seq_beta,
        edge_map                    = edge_map,
    )

    if sorted_order:
        mgraph_simplify_sorted(**kwargs)
    else:
        vprint("TRIVIAL STAGE, REMAINING {0}".format(len(req)))
        mgraph_simplify_trivial(**kwargs)
        vprint("TRIVIAL STAGE, REMAINING {0}".format(len(req)))
        mgraph_simplify_trivial(**kwargs)
        vprint("BADGUY STAGE, REMAINING {0}".format(len(req)))
        mgraph_simplify_badguys(**kwargs)

    #now reapply the seq and req lists
    reqO.clear()
    reqO.update(req_alpha)
    seqO.clear()
    seqO.update(seq_beta)
    return


def mgraph_simplify_sorted(
    seq,
    req,
    seq_beta,
    req_alpha,
    edge_map,
):
    kwargs = dict(
        seq                         = seq,
        req                         = req,
        req_alpha                   = req_alpha,
        seq_beta                    = seq_beta,
        edge_map                    = edge_map,
    )

    def generate_node_cost(node):
        return node

    pqueue = HeapPriorityQueue()

    for node in seq.keys():
        cost = generate_node_cost(node)
        pqueue.push((cost, node))

    while req:
        cost, node = pqueue.pop()

        assert(np.isfinite(cost))

        reduceLU(
            node = node,
            **kwargs
        )


def mgraph_simplify_trivial(
    seq,
    req,
    seq_beta,
    req_alpha,
    edge_map,
):
    kwargs = dict(
        seq                         = seq,
        req                         = req,
        req_alpha                   = req_alpha,
        seq_beta                    = seq_beta,
        edge_map                    = edge_map,
    )

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
            node = node,
            node_costs_invalid_in_queue = node_costs_invalid_in_queue,
            **kwargs
        )
    return

def mgraph_simplify_badguys(
    seq,
    req,
    seq_beta,
    req_alpha,
    edge_map,
    verbose = False,
):
    if verbose:
        def vprint(*p):
            print(*p)
    else:
        def vprint(*p):
            return

    kwargs = dict(
        seq                         = seq,
        req                         = req,
        req_alpha                   = req_alpha,
        seq_beta                    = seq_beta,
        edge_map                    = edge_map,
    )
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

            normr = 0
            for rnode in req[node]:
                normr += abs(edge_map[rnode, node])**2
            normr = normr ** .5
            #row norm
            normc = 0
            for snode in seq[node]:
                normc += abs(edge_map[node, snode])**2
            normc = normc ** .5

            vprint("SHAPE: ", np.asarray(normr).shape)
            if np.asarray(normr).shape or np.asarray(normc).shape:
                rel_r_to_c = np.asarray(np.count_nonzero(normr > normc))
                vprint(rel_r_to_c)
                rel_r_to_c = np.mean(rel_r_to_c)
                vprint("SHAPE: ", rel_r_to_c.shape)
            else:
                rel_r_to_c = normr > normc
            vprint("REL LARGER: ", rel_r_to_c)

            rvec = []
            rvec_N = []
            rvec_self_idx = None
            for idx, rnode in enumerate(req[node]):
                if node == rnode:
                    rvec_self_idx = idx
                rvec.append(np.max(abs(edge_map[rnode, node] / normr)))
                rvec_N.append(rnode)

            vprint("RVEC: ", rvec)
            bignodes_r = np.array(rvec) >= 1./(len(req[node]))**.5
            rcount = np.count_nonzero(bignodes_r)
            vprint("R: ", np.count_nonzero(bignodes_r), len(req[node]), bignodes_r[rvec_self_idx], rel_r_to_c > .5)
            cvec = []
            cvec_N = []
            cvec_self_idx = None
            for idx, snode in enumerate(seq[node]):
                if node == snode:
                    cvec_self_idx = idx
                    vprint(cvec_self_idx, idx, node)
                cvec.append(np.max(abs(edge_map[node, snode] / normc)))
                cvec_N.append(snode)
            vprint("CVEC: ", cvec)
            bignodes_c = np.array(cvec) >= 1./(len(seq[node]))**.5
            ccount = np.count_nonzero(bignodes_c)
            vprint(bignodes_c, cvec_self_idx, ccount)
            vprint("pe_C: ", np.count_nonzero(bignodes_c), len(seq[node]), bignodes_c[cvec_self_idx], rel_r_to_c < .5)

            if node in req[node]:
                norma = abs(edge_map[node, node])
                vprint("NORM: ", np.max(normr / norma), np.max(normc / norma))

            if rel_r_to_c > .5:
                vprint("Using ROW Operations")
                if rcount >= 2:
                    vprint("MUST USE HOUSEHOLDER {0}x".format(rcount))
                    if rvec_self_idx is None or not bignodes_r[rvec_self_idx]:
                        vprint("MUST PIVOT")
                        idx_pivot = np.nonzero(bignodes_r)[0][0]
                        vprint("SELF: ", rvec_self_idx)
                        vprint("PIVO: ", idx_pivot)
                        node_pivot = rvec_N[idx_pivot]
                        vprint("SWAP: ", node, node_pivot)
                        pivotROW_OP(
                            node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                            node1 = node,
                            node2 = node_pivot,
                            **kwargs
                        )
                        node_costs_invalid_in_queue.add(node)
                        node_costs_invalid_in_queue.add(node_pivot)
                        node = node_pivot
                    #make more efficient
                    nfrom = set()
                    vprint(bignodes_r.shape)
                    for idx in range(bignodes_r.shape[0]):
                        if np.any(bignodes_r[idx]):
                            nfrom.add(rvec_N[idx])
                    vprint("NFROM: ", nfrom, node)
                    nfrom.remove(node)
                    for kf in nfrom:
                        assert(node in seq[kf])
                    vprint("NFROM: ", nfrom, node)
                    householderREFL_ROW_OP(
                        node_into = node,
                        nodes_from = nfrom,
                        node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                        **kwargs
                    )
                elif rcount == 1:
                    vprint("DIRECT")
                    if rvec_self_idx is None or not bignodes_r[rvec_self_idx]:
                        vprint("MUST PIVOT")
                        vprint('bignodes', bignodes_r)
                        #could choose pivot node based on projected fill-in
                        idx_pivot = np.nonzero(bignodes_r)[0][0]
                        vprint("SELF: ", rvec_self_idx)
                        vprint("PIVO: ", idx_pivot)
                        node_pivot = rvec_N[idx_pivot]
                        vprint("SWAP: ", node, node_pivot)
                        pivotROW_OP(
                            node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                            node1 = node,
                            node2 = node_pivot,
                            **kwargs
                        )
                        node_costs_invalid_in_queue.add(node)
                        node_costs_invalid_in_queue.add(node_pivot)
                        node = node_pivot
                        #continue
            else:
                vprint("Using COLUMN Operations")
                vprint("bignodes_c[cvec_self_idx]", bignodes_c[cvec_self_idx])
                if ccount >= 2:
                    vprint("MUST USE HOUSEHOLDER {0}x".format(ccount))
                    if cvec_self_idx is None or not bignodes_c[cvec_self_idx]:
                        vprint("MUST PIVOT")
                        vprint('bignodes', bignodes_c)
                        #could choose pivot node based on projected fill-in
                        idx_pivot = np.nonzero(bignodes_c)[0][0]
                        vprint(idx_pivot)
                        node_pivot = cvec_N[idx_pivot]
                        vprint("SWAP: ", node, node_pivot)
                        pivotCOL_OP(
                            node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                            node1 = node,
                            node2 = node_pivot,
                            **kwargs
                        )
                        node_costs_invalid_in_queue.add(node)
                        node_costs_invalid_in_queue.add(node_pivot)
                        node = node_pivot
                    #make more efficient
                    nfrom = set()
                    vprint(bignodes_c.shape)
                    for idx in range(bignodes_c.shape[0]):
                        if np.any(bignodes_c[idx]):
                            nfrom.add(cvec_N[idx])
                    vprint("NFROM: ", nfrom, node)
                    nfrom.remove(node)
                    householderREFL_COL_OP(
                        node_into = node,
                        nodes_from = nfrom,
                        node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                        **kwargs
                    )
                elif ccount == 1:
                    vprint("DIRECT")
                    if cvec_self_idx is None or not bignodes_c[cvec_self_idx]:
                        vprint("MUST PIVOT")
                        vprint('bignodes', bignodes_c)
                        #could choose pivot node based on projected fill-in
                        idx_pivot = np.nonzero(bignodes_c)[0][0]
                        vprint(idx_pivot)
                        node_pivot = cvec_N[idx_pivot]
                        vprint("SWAP: ", node, node_pivot)
                        pivotCOL_OP(
                            node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                            node1 = node,
                            node2 = node_pivot,
                            **kwargs
                        )
                        node_costs_invalid_in_queue.add(node)
                        node_costs_invalid_in_queue.add(node_pivot)
                        node = node_pivot
                        #continue
            assert(np.isfinite(cost))

            reduceLU(
                node = node,
                node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                **kwargs
            )
    except Empty:
        assert(req)

def pivotROW_OP(
    seq,
    req,
    seq_beta,
    req_alpha,
    edge_map,
    node1,
    node2,
    node_costs_invalid_in_queue,
):
    """
    Swaps ROWS within a column. So all edges TO node1 go to node2 and vice-versa.

    column ops affect ALPHA.
    """
    #print("SEQ 1: ", node1, seq[node1])
    #print("REQ 1: ", node1, req[node1])
    #print("SEQ 2: ", node2, seq[node2])
    #print("REQ 2: ", node2, req[node2])

    #check graph
    for snode in seq[node2]:
        assert(node2 in req[snode])
    for snode in seq[node1]:
        assert(node1 in req[snode])
    for rnode in req[node2]:
        assert(node2 in seq[rnode])
    for rnode in req[node1]:
        assert(node1 in seq[rnode])

    edge_mape_2 = dict()
    #gets all edges to node1/2
    for rnode in req[node1]:
        edge = edge_map.pop((rnode, node1))
        edge_mape_2[rnode, node2] = edge
        seq[rnode].remove(node1)
        seq[rnode].add(node2)
        node_costs_invalid_in_queue.add(rnode)

    for rnode in req_alpha[node1]:
        edge = edge_map.pop((rnode, node1))
        edge_mape_2[rnode, node2] = edge

    for rnode in req[node2]:
        edge = edge_map.pop((rnode, node2))
        edge_mape_2[rnode, node1] = edge
        #since this one follows the other, we must be careful about uniqueness of removes
        if rnode not in req[node1]:
            seq[rnode].remove(node2)
        seq[rnode].add(node1)
        node_costs_invalid_in_queue.add(rnode)

    for rnode in req_alpha[node2]:
        edge = edge_map.pop((rnode, node2))
        edge_mape_2[rnode, node1] = edge

    rn1 = req[node1]
    rnA1 = req_alpha[node1]

    req[node1] = req[node2]
    req_alpha[node1] = req_alpha[node2]

    req[node2] = rn1
    req_alpha[node2] = rnA1

    #print("SEQ 1: ", node1, seq[node1])
    #print("REQ 1: ", node1, req[node1])
    #print("SEQ 2: ", node2, seq[node2])
    #print("REQ 2: ", node2, req[node2])

    #check graph
    for snode in seq[node2]:
        assert(node2 in req[snode])
    for snode in seq[node1]:
        assert(node1 in req[snode])
    for rnode in req[node2]:
        assert(node2 in seq[rnode])
    for rnode in req[node1]:
        assert(node1 in seq[rnode])

    edge_map.update(edge_mape_2)
    return

def householderREFL_ROW_OP(
    seq,
    req,
    seq_beta,
    req_alpha,
    edge_map,
    node_into,
    nodes_from,
    node_costs_invalid_in_queue,
):
    """
    Moves COLUMN (from) COEFFS within a row (to). All of the edges of node_into to nodes_from are zerod.

    row ops affect BETA.
    """

    for rnode in req[node_into]:
        assert(node_into in seq[rnode])
    for rnode in req[node_into]:
        assert(node_into in seq[rnode])

    u_vec = dict()
    norm_sq = 0

    for node_from in nodes_from:
        edge = edge_map[node_from, node_into]
        norm_sq = norm_sq + abssq(edge)
        u_vec[node_from] = edge

    #this algorithm assumes that node_into also defines the column (so is on the "diagonal")
    edge = edge_map[node_into, node_into]
    norm_rem_sq = norm_sq
    norm_orig_sq = norm_sq + abssq(edge)
    norm_orig = norm_orig_sq**.5
    u_mod_edge = edge + norm_orig * edge / abs(edge)
    norm_sq = norm_sq + abssq(u_mod_edge)
    norm = norm_sq**.5
    #print("NORM_ORG", norm_orig[0])
    edge_remem = edge

    for k, u_edge in list(u_vec.items()):
        u_vec[k] = u_edge / norm
    u_mod_edge = u_mod_edge / norm
    u_vec[node_into] = u_mod_edge

    edge_inject = edge_remem - 2 * u_mod_edge * (u_mod_edge.conjugate() * edge_remem + norm_rem_sq / norm)

    #for k, edge in u_vec.items():
    #    print("UVEC: ", k , edge[0])

    #Q = I - 2 u * u^dagger / |u|**2
    #tau = |u|**2 / 2
    #Q = I - u * u^dagger / tau

    fnode_edges = dict()

    #these loops could probably be transposed
    for fnode, fnode_req in req.items():
        #don't need to do the diagonal since that one is explicit later
        #if fnode is node_into:
        #    continue
        gen_edge = 0
        for k, edge in u_vec.items():
            if k in fnode_req:
                gen_edge = gen_edge + edge.conjugate() * edge_map[k, fnode]
        if np.any(gen_edge != 0):
            fnode_edges[fnode] = gen_edge

    edge_mape_2 = dict()
    for fnode, fedge in fnode_edges.items():
        for k, edge in u_vec.items():
            if fnode in seq[k]:
                edge_map[k, fnode] = edge_map[k, fnode] - 2 * edge * fedge
            else:
                edge_map[k, fnode] = - 2 * edge * fedge
                seq[k].add(fnode)
                req[fnode].add(k)

    #now do node_into column explicitely so we get the exact zeros/edge removal
    edge_map[node_into, node_into] = edge_inject
    for node_from in nodes_from:
        seq[node_from].remove(node_into)
        req[node_into].remove(node_from)
        del edge_map[node_from, node_into]

    #now also apply to BETA
    #This could probably be accelerated..
    #gotta be careful with intermediates if trying a live update. Maybe could do a triangular loop?
    edge_mape_2 = dict()
    for k, edge in u_vec.items():
        edge_c = edge.conjugate()
        for snode in seq_beta[k]:
            edge_beta = edge_map[k, snode]
            gain = -2 * edge_c * edge_beta
            for k_to, edge_to in u_vec.items():
                edge_mape_2[snode, k_to] = edge_mape_2.get((snode, k_to), 0) + edge_to * gain

    for (snode, k_to), edge in edge_mape_2.items():
        if snode in seq_beta[k_to]:
            edge_map[k_to, snode] = edge_map[k_to, snode] + edge
        else:
            edge_map[k_to, snode] = edge
            seq_beta[k_to].add(snode)

    for rnode in req[node_into]:
        assert(node_into in seq[rnode])
    for rnode in req[node_into]:
        assert(node_into in seq[rnode])

    #print("INTO: ", node_into)
    #print("FROM: ", nodes_from)
    #for k1k2, edge in list(edge_mape_2.items()):
    #    edge_mape_2[k1k2] = edge[0]
    #print("EMAP")
    #pprint(edge_mape_2)
    #print("SELF: ", edge_mape_2[node_into, node_into])
    #print("ECHECK: ", edge_inject[0]),
    #for nfrom in nodes_from:
    #    print("NFROM: ", nfrom, edge_mape_2[node_into, nfrom])
    return

def householderREFL_COL_OP(
    seq,
    req,
    seq_beta,
    req_alpha,
    edge_map,
    node_into,
    nodes_from,
    node_costs_invalid_in_queue,
):
    """
    Moves ROW COEFFS within a column. All of the edges of node_into to nodes_from are zerod.

    column ops affect ALPHA.
    """

    #check graph
    for rnode in req[node_into]:
        assert(node_into in seq[rnode])
    for rnode in req[node_into]:
        assert(node_into in seq[rnode])

    u_vec = dict()
    norm_sq = 0

    for node_from in nodes_from:
        edge = edge_map[node_into, node_from]
        norm_sq = norm_sq + abssq(edge)
        u_vec[node_from] = edge

    #this algorithm assumes that node_into also defines the column (so is on the "diagonal")
    edge = edge_map[node_into, node_into]
    norm_rem_sq = norm_sq
    norm_orig_sq = norm_sq + abssq(edge)
    norm_orig = norm_orig_sq**.5
    u_mod_edge = edge + norm_orig * edge / abs(edge)
    norm_sq = norm_sq + abssq(u_mod_edge)
    norm = norm_sq**.5
    #print("NORM_ORG", norm_orig[0])
    edge_remem = edge

    for k, u_edge in list(u_vec.items()):
        u_vec[k] = u_edge / norm
    u_mod_edge = u_mod_edge / norm
    u_vec[node_into] = u_mod_edge

    edge_inject = edge_remem - 2 * u_mod_edge * (u_mod_edge.conjugate() * edge_remem + norm_rem_sq / norm)

    #for k, edge in u_vec.items():
    #    print("UVEC: ", k , edge[0])

    #Q = I - 2 u * u^dagger / |u|**2
    #tau = |u|**2 / 2
    #Q = I - u * u^dagger / tau

    fnode_edges = dict()

    #these loops could probably be transposed
    for fnode, fnode_seq in seq.items():
        #don't need to do the diagonal since that one is explicit later
        #if fnode is node_into:
        #    continue
        gen_edge = 0
        for k, edge in u_vec.items():
            if k in fnode_seq:
                gen_edge = gen_edge + edge.conjugate() * edge_map[fnode, k]
        if np.any(gen_edge != 0):
            fnode_edges[fnode] = gen_edge

    edge_mape_2 = dict()
    for fnode, fedge in fnode_edges.items():
        for k, edge in u_vec.items():
            if fnode in req[k]:
                edge_map[fnode, k] = edge_map[fnode, k] - 2 * edge * fedge
            else:
                edge_map[fnode, k] = - 2 * edge * fedge
                req[k].add(fnode)
                seq[fnode].add(k)

    #now do node_into column explicitely so we get the exact zeros/edge removal
    edge_map[node_into, node_into] = edge_inject
    for node_from in nodes_from:
        seq[node_into].remove(node_from)
        req[node_from].remove(node_into)
        del edge_map[node_into, node_from]

    #now also apply to ALPHA
    #This could probably be accelerated..
    #gotta be careful with intermediates if trying a live update. Maybe could do a triangular loop?
    edge_mape_2 = dict()
    for k, edge in u_vec.items():
        edge_c = edge.conjugate()
        for rnode in req_alpha[k]:
            edge_alpha = edge_map[rnode, k]
            gain = -2 * edge_c * edge_alpha
            for k_to, edge_to in u_vec.items():
                edge_mape_2[rnode, k_to] = edge_mape_2.get((rnode, k_to), 0) + edge_to * gain

    for (rnode, k_to), edge in edge_mape_2.items():
        if rnode in req_alpha[k_to]:
            edge_map[rnode, k_to] = edge_map[rnode, k_to] + edge
        else:
            edge_map[rnode, k_to] = edge
            req_alpha[k_to].add(rnode)

    for rnode in req[node_into]:
        assert(node_into in seq[rnode])
    for rnode in req[node_into]:
        assert(node_into in seq[rnode])

    #print("INTO: ", node_into)
    #print("FROM: ", nodes_from)
    #for k1k2, edge in list(edge_mape_2.items()):
    #    edge_mape_2[k1k2] = edge[0]
    #print("EMAP")
    #pprint(edge_mape_2)
    #print("SELF: ", edge_mape_2[node_into, node_into])
    #print("ECHECK: ", edge_inject[0]),
    #for nfrom in nodes_from:
    #    print("NFROM: ", nfrom, edge_mape_2[node_into, nfrom])
    return

def pivotCOL_OP(
    seq,
    req,
    seq_beta,
    req_alpha,
    edge_map,
    node1,
    node2,
    node_costs_invalid_in_queue,
):
    """
    Swaps COLUMNS within a row . So all edges FROM node1 go to node2 and vice-versa.

    row ops affect BETA.
    """
    #print("SEQ 1: ", node1, seq[node1])
    #print("REQ 1: ", node1, req[node1])
    #print("SEQ 2: ", node2, seq[node2])
    #print("REQ 2: ", node2, req[node2])

    #check graph
    for rnode in req[node2]:
        assert(node2 in seq[rnode])
    for rnode in req[node1]:
        assert(node1 in seq[rnode])
    for snode in seq[node2]:
        assert(node2 in req[snode])
    for snode in seq[node1]:
        assert(node1 in req[snode])

    edge_mape_2 = dict()
    #gets all edges from node1/2
    for snode in seq[node1]:
        edge = edge_map.pop((node1, snode))
        edge_mape_2[node2, snode] = edge
        if snode != node2:
            req[snode].remove(node1)
            req[snode].add(node2)
        node_costs_invalid_in_queue.add(snode)

    for snode in seq_beta[node1]:
        edge = edge_map.pop((node1, snode))
        edge_mape_2[node2, snode] = edge

    for snode in seq[node2]:
        edge = edge_map.pop((node2, snode))
        edge_mape_2[node1, snode] = edge
        #since this one follows the other, we must be careful about uniqueness of removes
        if snode not in seq[node1]:
            req[snode].remove(node2)
        req[snode].add(node1)
        node_costs_invalid_in_queue.add(snode)

    for snode in seq_beta[node2]:
        edge = edge_map.pop((node2, snode))
        edge_mape_2[node1, snode] = edge

    sn1 = seq[node1]
    snB1 = seq_beta[node1]

    seq[node1] = seq[node2]
    seq_beta[node1] = seq_beta[node2]

    seq[node2] = sn1
    seq_beta[node2] = snB1

    #check graph
    for rnode in req[node2]:
        assert(node2 in seq[rnode])
    for rnode in req[node1]:
        assert(node1 in seq[rnode])
    for snode in seq[node2]:
        assert(node2 in req[snode])
    for snode in seq[node1]:
        assert(node1 in req[snode])

    #print("SEQ 1: ", node1, seq[node1])
    #print("REQ 1: ", node1, req[node1])
    #print("SEQ 2: ", node2, seq[node2])
    #print("REQ 2: ", node2, req[node2])

    edge_map.update(edge_mape_2)
    return


def reduceLU(
    seq,
    req,
    seq_beta,
    req_alpha,
    edge_map,
    node,
    node_costs_invalid_in_queue = None,
):
    self_edge = edge_map[node, node]

    CLG = -1 / self_edge
    #remove the self edge for the simplification stage
    seq[node].remove(node)
    req[node].remove(node)
    del edge_map[node, node]

    for snode in seq[node]:
        sedge = edge_map[node, snode]
        prod_L = sedge * CLG

        for rnode in req[node]:
            redge = edge_map[rnode, node]
            prod = prod_L * redge

            prev_edge = edge_map.get((rnode, snode), None)
            if prev_edge is not None:
                edge_map[(rnode, snode)] = prev_edge + prod
            else:
                edge_map[(rnode, snode)] = prod

            seq.setdefault(rnode, set()).add(snode)
            req.setdefault(snode, set()).add(rnode)

        for rnode in req_alpha[node]:
            redge = edge_map[rnode, node]
            prod = prod_L * redge

            prev_edge = edge_map.get((rnode, snode), None)
            if prev_edge is not None:
                edge_map[(rnode, snode)] = prev_edge + prod
            else:
                edge_map[(rnode, snode)] = prod

            req_alpha.setdefault(snode, set()).add(rnode)

    for snode in seq_beta[node]:
        sedge = edge_map[node, snode]
        prod_L = sedge * CLG

        for rnode in req[node]:
            redge = edge_map[rnode, node]
            prod = prod_L * redge

            prev_edge = edge_map.get((rnode, snode), None)
            if prev_edge is not None:
                edge_map[(rnode, snode)] = prev_edge + prod
            else:
                edge_map[(rnode, snode)] = prod

            seq_beta.setdefault(rnode, set()).add(snode)

        for rnode in req_alpha[node]:
            redge = edge_map[rnode, node]
            prod = prod_L * redge

            prev_edge = edge_map.get((rnode, snode), None)
            if prev_edge is not None:
                edge_map[(rnode, snode)] = prev_edge + prod
            else:
                edge_map[(rnode, snode)] = prod

            seq_beta.setdefault(rnode, set()).add(snode)
            req_alpha.setdefault(snode, set()).add(rnode)

    for snode in seq[node]:
        if node_costs_invalid_in_queue:
            node_costs_invalid_in_queue.add(snode)
        del edge_map[node, snode]
        req[snode].remove(node)
    del seq[node]

    for snode in seq_beta[node]:
        del edge_map[node, snode]
    del seq_beta[node]

    for rnode in req[node]:
        if node_costs_invalid_in_queue:
            node_costs_invalid_in_queue.add(rnode)
        del edge_map[rnode, node]
        seq[rnode].remove(node)
    del req[node]

    for rnode in req_alpha[node]:
        del edge_map[rnode, node]
    del req_alpha[node]
    return

def wrap_input_node(node):
    return ('INPUT', node)

def wrap_output_node(node):
    return ('OUTPUT', node)

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
        keys = set(seq.keys()) | set(req.keys())
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

    #this convention is correct for how this solver operates!
    if negative:
        value = 1
    else:
        value = -1
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
    print("POST_PURGE_SPARSITY: ", len(seq), len(edge_map), len(edge_map) / len(seq))
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
        keys = set(seq.keys()) | set(req.keys())
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
    VACUUM_STATE = DictKey(special = 'vacuum')
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

    #this convention is correct for how this solver operates!
    if negative:
        value = 1
    else:
        value = -1
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
    print("POST_PURGE_SPARSITY: ", len(seq), len(edge_map), len(edge_map) / len(seq))

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
