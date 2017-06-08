# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
import warnings
from numbers import Number
import numpy as np
from collections import defaultdict
import declarative
import queue

from OpenLoop.utilities.priority_queue import HeapPriorityQueue
from OpenLoop.utilities.print import pprint

from ..base import (
    DictKey,
)

N_limit_rel = 100

def abssq(arr):
    return arr * arr.conjugate()

def enorm(arr):
    return np.max(abssq(arr))

def print_seq(seq, edge_map):
    print("Sequential Edges")
    for node, seq_set in seq.items():
        plist = []
        print(node)
        for snode in seq_set:
            etup = (u'➠\t', snode, edge_map.get((node, snode), None))
            plist.append(etup)
        plist.sort()
        for etup in plist:
            print(*etup)

def print_req(req, edge_map):
    print("Requisite Edges")
    for node, seq_set in req.items():
        plist = []
        print(node)
        for rnode in seq_set:
            etup = (u'⟽\t', rnode, edge_map[rnode, node])
            plist.append(etup)
        plist.sort()
        for etup in plist:
            print(*etup)


def check_seq_req_balance(seq, req, edge_map = None):
    for node, seq_set in seq.items():
        for snode in seq_set:
            assert(node in req[snode])
            if edge_map and (node, snode) not in edge_map:
                warnings.warn(repr((node, snode)) + 'not in edge map')
                edge_map[node, snode] = 0

    for node, req_set in req.items():
        for rnode in req_set:
            assert(node in seq[rnode])


def condition_node(
    seq, req, req_alpha, edge_map, node
):
    self_edge = edge_map[node, node]
    #if verbose: print("SELF_EDGE min: ", 1/np.max(abs(1 - self_edge)))
    totC = 0
    c_edges_c = dict()
    c_edges = dict()
    #print("seq: ", seq)
    for snode in seq[node]:
        #must be output node if not in seq
        if snode == node:
            continue
        #print("SNODE: ", snode, seq[snode])
        if not seq[snode]:
            continue
        if not req[snode]:
            continue
        assert(snode in req)
        edge = edge_map[node, snode]
        #print("C_EDGE: ", node, snode, edge)
        #if verbose: print("C_val: ", node, snode, edge)
        c_edges[snode] = edge
        c_edges_c[snode] = edge.conjugate()
        totC = totC + abs(edge_map[node, snode])**2
    #print("SELF_EDGE C: ", np.max(1/abs(1 - self_edge)), np.max(totC), len(c_edges))
    #print('c_edges', c_edges)

    a = -self_edge
    y = a / abs(a)
    y = 1/a.conjugate()
    #y = self_edge / totC

    yc = y.conjugate()

    condition = True
    #if np.all(totC < abs(a)):
        #condition = False
    if not c_edges:
        condition = False
    else:
        #assert(False)
        pass
    if condition:
        #print("Q-condition: ", node)
        b_edges = dict()
        for rnode in req[node]:
            #must be output node if not in seq
            if rnode == node:
                continue
            if not seq[rnode]:
                continue
            if not req[rnode]:
                continue
            assert(rnode in seq)
            edge = edge_map[rnode, node]
            b_edges[rnode] = edge
        #print("b_edges", b_edges)

        #wrap the loop
        edge_map[node, node] = edge_map[node, node] - y * totC

        emap_mod = dict()
        #print("REQ_ALPHA: ", req_alpha[node])
        #since alpha_2 modifies the list for alpha_1, we have to pre-store it
        pre_req_alpha = list(req_alpha[node])
        ##from alpha_2 to node
        for snode, edge in c_edges_c.items():
            #print("REQ_SNODE: ", snode, req_alpha[snode])
            for winode in list(req_alpha[snode]):
                seq[winode].add(node)
                req[node].add(winode)
                req_alpha[node].add(winode)
                #edge_map[winode, node] = edge_map.get((winode, node), 0) + -y * edge
                emap_mod[winode, node] = edge_map.get((winode, node), 0) + -y * edge * edge_map.get((winode, snode))

        ##from alpha_1 to node
        for winode in pre_req_alpha:
            for snode, edge in c_edges.items():
                seq[winode].add(snode)
                req[snode].add(winode)
                req_alpha[snode].add(winode)
                #edge_map[winode, snode] = edge_map.get((winode, snode), 0) + yc * edge
                emap_mod[winode, snode] = edge_map.get((winode, snode), 0) + yc * edge * edge_map.get((winode, node))

        for tf, e in emap_mod.items():
            edge_map[tf] = e

        #adjust C itself
        correction = (1 - yc * a)
        if np.any(correction != 0):
            for snode, edge in c_edges.items():
                edge_map[node, snode] = correction * edge
                #print("C: ", correction * edge)
        else:
            for snode, edge in c_edges.items():
                seq[node].remove(snode)
                req[snode].remove(node)
                del edge_map[node, snode]

        #adjust B itself
        scsd = dict()
        d_mat = dict()
        for lnode in seq:
            #print('lnode ', lnode)
            lval = 0
            if not req[lnode]:
                #must be an output node
                continue
            if not seq[lnode]:
                #must be an input node
                continue
            #ignore the current node
            if lnode == node:
                continue
            #print('lnode2 ', lnode)
            for snode, edge in c_edges_c.items():
                #print('snode ', snode)
                assert(snode != node)
                if snode in seq[lnode] or snode == lnode:
                    edge2 = edge_map.get((lnode, snode), 0)
                    lval = lval - edge * edge2
                    d_mat[lnode, snode] = -edge2
            scsd[lnode] = lval
        #print('d_mat: ', d_mat)
        #print('scsd: ', scsd)

        for lnode, edge in scsd.items():
            seq[lnode].add(node)
            req[node].add(lnode)
            #does not affect req_alpha
            edge_map[lnode, node] = edge_map.get((lnode, node), 0) + y * edge

        #adjust D
        for cnode, cedge in c_edges.items():
            for bnode, bedge in b_edges.items():
                #print("ADD: ", bnode, cnode)
                seq[bnode].add(cnode)
                req[cnode].add(bnode)
                #does not affect req_alpha
                edge_map[bnode, cnode] = edge_map.get((bnode, cnode), 0) + yc * cedge * bedge

        #edge_map[node, snode] = edge_map[node, snode] + (a - yc) * edge


def mgraph_simplify_inplace(
    seq, req,
    edge_map,
    verbose        = False,
    sorted_order   = False,
):
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
                seq[rnode].remove(node)
                beta_set.add(node)
    for node in seq:
        if not req.get(node, None):
            for snode in seq[node]:
                req_alpha[snode].add(node)
                req[snode].remove(node)
                alpha_set.add(node)

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
        if verbose: print("TRIVIAL STAGE, REMAINING {0}".format(len(req)))
        mgraph_simplify_trivial(**kwargs)
        if verbose: print("TRIVIAL STAGE, REMAINING {0}".format(len(req)))
        mgraph_simplify_trivial(**kwargs)
        if verbose: print("BADGUY STAGE, REMAINING {0}".format(len(req)))
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

        self_edge = edge_map[node, node]
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
    if verbose: print("pqueue length: ", len(pqueue))

    try:
        while req:
            while node_costs_invalid_in_queue:
                node = node_costs_invalid_in_queue.pop()
                if node not in seq:
                    continue
                cost = generate_node_cost(node)
                pqueue.push((cost, node))
            #print("REQ: ", req)
            #print("REQ_A: ", req_alpha)
            #print("SEQ: ", seq)
            #print("SEQ_B: ", seq_beta)
            cost, node = pqueue.pop()
            if node not in seq:
                continue

            print("MY NODE: ", node)
            new_cost = generate_node_cost(node)
            while abs(abs(cost / new_cost) - 1) > .1:
                cost, node = pqueue.pushpop((new_cost, node))
                while node not in seq:
                    cost, node = pqueue.pop()
                new_cost = generate_node_cost(node)
                print("NCOST: ", node, new_cost)

            if node not in seq:
                print("MY GOD: ", node)

            if node in seq[node]:
                #node must at least have a self-loop
                min_rnode = None
                min_rnode_cost = float('inf')
                for rnode in seq[node]:
                    rcost = generate_row_cost(rnode)
                    if rcost < min_rnode_cost:
                        min_rnode = rnode
                        min_rnode_cost = rcost
                print("MIN_MAX: ", node, min_rnode)

            normr = 0
            for rnode in req[node]:
                normr += abs(edge_map[rnode, node])**2
            normr = normr ** .5
            #row norm
            normc = 0
            for snode in seq[node]:
                normc += abs(edge_map[node, snode])**2
            normc = normc ** .5

            print("SHAPE: ", np.asarray(normr).shape)
            if np.asarray(normr).shape or np.asarray(normc).shape:
                rel_r_to_c = np.asarray(np.count_nonzero(normr > normc))
                print(rel_r_to_c)
                rel_r_to_c = np.mean(rel_r_to_c)
                print("SHAPE: ", rel_r_to_c.shape)
            else:
                rel_r_to_c = normr > normc
            print("REL LARGER: ", rel_r_to_c)

            rvec = []
            rvec_N = []
            rvec_self_idx = None
            for idx, rnode in enumerate(req[node]):
                if node == rnode:
                    rvec_self_idx = idx
                rvec.append(np.max(abs(edge_map[rnode, node] / normr)))
                rvec_N.append(rnode)

            print("RVEC: ", rvec)
            bignodes_r = np.array(rvec) >= 1./(len(req[node]))**.5
            rcount = np.count_nonzero(bignodes_r)
            print("R: ", np.count_nonzero(bignodes_r), len(req[node]), bignodes_r[rvec_self_idx], rel_r_to_c > .5)
            cvec = []
            cvec_N = []
            cvec_self_idx = None
            for idx, snode in enumerate(seq[node]):
                if node == snode:
                    cvec_self_idx = idx
                    print(cvec_self_idx, idx, node)
                cvec.append(np.max(abs(edge_map[node, snode] / normc)))
                cvec_N.append(snode)
            print("CVEC: ", cvec)
            bignodes_c = np.array(cvec) >= 1./(len(seq[node]))**.5
            ccount = np.count_nonzero(bignodes_c)
            print(bignodes_c, cvec_self_idx, ccount)
            print("C: ", np.count_nonzero(bignodes_c), len(seq[node]), bignodes_c[cvec_self_idx], rel_r_to_c < .5)

            if node in req[node]:
                norma = abs(edge_map[node, node])
                print("NORM: ", np.max(normr / norma), np.max(normc / norma))

            if rel_r_to_c > .5:
                print("Using ROW Operations")
                if rcount >= 2:
                    print("MUST USE HOUSEHOLDER {0}x".format(rcount))
                    if rvec_self_idx is None or not bignodes_r[rvec_self_idx]:
                        print("MUST PIVOT")
                        idx_pivot = np.nonzero(bignodes_r)[0][0]
                        print("SELF: ", rvec_self_idx)
                        print("PIVO: ", idx_pivot)
                        node_pivot = rvec_N[idx_pivot]
                        print("SWAP: ", node, node_pivot)
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
                    print(bignodes_r.shape)
                    for idx in range(bignodes_r.shape[0]):
                        if np.any(bignodes_r[idx]):
                            nfrom.add(rvec_N[idx])
                    print("NFROM: ", nfrom, node)
                    nfrom.remove(node)
                    for kf in nfrom:
                        assert(node in seq[kf])
                    print("NFROM: ", nfrom, node)
                    householderREFL_ROW_OP(
                        node_into = node,
                        nodes_from = nfrom,
                        node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                        **kwargs
                    )
                elif rcount == 1:
                    print("DIRECT")
                    if rvec_self_idx is None or not bignodes_r[rvec_self_idx]:
                        print("MUST PIVOT")
                        print('bignodes', bignodes_r)
                        #could choose pivot node based on projected fill-in
                        idx_pivot = np.nonzero(bignodes_r)[0][0]
                        print("SELF: ", rvec_self_idx)
                        print("PIVO: ", idx_pivot)
                        node_pivot = rvec_N[idx_pivot]
                        print("SWAP: ", node, node_pivot)
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
                print("Using COLUMN Operations")
                print("bignodes_c[cvec_self_idx]", bignodes_c[cvec_self_idx])
                if ccount >= 2:
                    print("MUST USE HOUSEHOLDER {0}x".format(ccount))
                    if cvec_self_idx is None or not bignodes_c[cvec_self_idx]:
                        print("MUST PIVOT")
                        print('bignodes', bignodes_c)
                        #could choose pivot node based on projected fill-in
                        idx_pivot = np.nonzero(bignodes_c)[0][0]
                        print(idx_pivot)
                        node_pivot = cvec_N[idx_pivot]
                        print("SWAP: ", node, node_pivot)
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
                    print(bignodes_c.shape)
                    for idx in range(bignodes_c.shape[0]):
                        if np.any(bignodes_c[idx]):
                            nfrom.add(cvec_N[idx])
                    print("NFROM: ", nfrom, node)
                    nfrom.remove(node)
                    householderREFL_COL_OP(
                        node_into = node,
                        nodes_from = nfrom,
                        node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                        **kwargs
                    )
                elif ccount == 1:
                    print("DIRECT")
                    if cvec_self_idx is None or not bignodes_c[cvec_self_idx]:
                        print("MUST PIVOT")
                        print('bignodes', bignodes_c)
                        #could choose pivot node based on projected fill-in
                        idx_pivot = np.nonzero(bignodes_c)[0][0]
                        print(idx_pivot)
                        node_pivot = cvec_N[idx_pivot]
                        print("SWAP: ", node, node_pivot)
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
    except queue.Empty:
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

    edge_map2 = dict()
    #gets all edges to node1/2
    for rnode in req[node1]:
        edge = edge_map.pop((rnode, node1))
        edge_map2[rnode, node2] = edge
        seq[rnode].remove(node1)
        seq[rnode].add(node2)
        node_costs_invalid_in_queue.add(rnode)

    for rnode in req_alpha[node1]:
        edge = edge_map.pop((rnode, node1))
        edge_map2[rnode, node2] = edge
        node_costs_invalid_in_queue.add(rnode)

    for rnode in req[node2]:
        edge = edge_map.pop((rnode, node2))
        edge_map2[rnode, node1] = edge
        #since this one follows the other, we must be careful about uniqueness of removes
        if rnode not in req[node1]:
            seq[rnode].remove(node2)
        seq[rnode].add(node1)
        node_costs_invalid_in_queue.add(rnode)

    for rnode in req_alpha[node2]:
        edge = edge_map.pop((rnode, node2))
        edge_map2[rnode, node1] = edge
        node_costs_invalid_in_queue.add(rnode)

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

    edge_map.update(edge_map2)
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

    edge_map2 = dict()
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
    edge_map2 = dict()
    for k, edge in u_vec.items():
        edge_c = edge.conjugate()
        for snode in seq_beta[k]:
            edge_beta = edge_map[k, snode]
            gain = -2 * edge_c * edge_beta
            for k_to, edge_to in u_vec.items():
                edge_map2[snode, k_to] = edge_map2.get((snode, k_to), 0) + edge_to * gain

    for (snode, k_to), edge in edge_map2.items():
        if snode in seq_beta[k_to]:
            edge_map[k_to, snode] = edge_map[k_to, snode] + edge
        else:
            edge_map[k_to, snode] = edge
            seq_beta[k_to].add(snode)

    #print("INTO: ", node_into)
    #print("FROM: ", nodes_from)
    #for k1k2, edge in list(edge_map2.items()):
    #    edge_map2[k1k2] = edge[0]
    #print("EMAP")
    #pprint(edge_map2)
    #print("SELF: ", edge_map2[node_into, node_into])
    #print("ECHECK: ", edge_inject[0]),
    #for nfrom in nodes_from:
    #    print("NFROM: ", nfrom, edge_map2[node_into, nfrom])
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

    edge_map2 = dict()
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
    edge_map2 = dict()
    for k, edge in u_vec.items():
        edge_c = edge.conjugate()
        for rnode in req_alpha[k]:
            edge_alpha = edge_map[rnode, k]
            gain = -2 * edge_c * edge_alpha
            for k_to, edge_to in u_vec.items():
                edge_map2[rnode, k_to] = edge_map2.get((rnode, k_to), 0) + edge_to * gain

    for (rnode, k_to), edge in edge_map2.items():
        if rnode in req_alpha[k_to]:
            edge_map[rnode, k_to] = edge_map[rnode, k_to] + edge
        else:
            edge_map[rnode, k_to] = edge
            req_alpha[k_to].add(rnode)

    #print("INTO: ", node_into)
    #print("FROM: ", nodes_from)
    #for k1k2, edge in list(edge_map2.items()):
    #    edge_map2[k1k2] = edge[0]
    #print("EMAP")
    #pprint(edge_map2)
    #print("SELF: ", edge_map2[node_into, node_into])
    #print("ECHECK: ", edge_inject[0]),
    #for nfrom in nodes_from:
    #    print("NFROM: ", nfrom, edge_map2[node_into, nfrom])
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

    edge_map2 = dict()
    #gets all edges from node1/2
    for snode in seq[node1]:
        edge = edge_map.pop((node1, snode))
        edge_map2[node2, snode] = edge
        if snode != node2:
            req[snode].remove(node1)
            req[snode].add(node2)
        node_costs_invalid_in_queue.add(snode)

    for snode in seq_beta[node1]:
        edge = edge_map.pop((node1, snode))
        edge_map2[node2, snode] = edge
        node_costs_invalid_in_queue.add(snode)

    for snode in seq[node2]:
        edge = edge_map.pop((node2, snode))
        edge_map2[node1, snode] = edge
        #since this one follows the other, we must be careful about uniqueness of removes
        if snode not in seq[node1]:
            req[snode].remove(node2)
        req[snode].add(node1)
        node_costs_invalid_in_queue.add(snode)

    for snode in seq_beta[node2]:
        edge = edge_map.pop((node2, snode))
        edge_map2[node1, snode] = edge
        node_costs_invalid_in_queue.add(snode)

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

    edge_map.update(edge_map2)
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


def color_purge_inplace(
    start_set, emap,
    seq, req,
    edge_map,
):
    #can't actually purge, must color all nodes
    #from the exception set and then subtract the
    #remainder.
    #purging algorithms otherwise have to deal with
    #strongly connected components, which makes them
    #no better than coloring
    active_set = set()
    active_set_pending = set()
    #print("PURGE START: ", start_set)
    for node in start_set:
        active_set_pending.add(node)

    while active_set_pending:
        node = active_set_pending.pop()
        #print("PURGE NODE: ", node)
        active_set.add(node)
        for snode in emap[node]:
            if snode not in active_set:
                active_set_pending.add(snode)
    full_set = set(seq.keys())
    purge_set = full_set - active_set
    #print("FULL_SET", active_set)
    #print("PURGE", len(purge_set), len(full_set))
    purge_subgraph_inplace(seq, req, edge_map, purge_set)


def purge_reqless_inplace(
        except_set,
        seq,
        req,
        edge_map = None,
):
    color_purge_inplace(
        except_set, seq,
        seq, req, edge_map,
    )


def purge_seqless_inplace(
        except_set,
        seq,
        req,
        edge_map = None,
):
    color_purge_inplace(
        except_set, req,
        seq, req, edge_map,
    )


def edgedelwarn(
        edge_map,
        nfrom,
        nto,
):
    if edge_map is None:
        return
    try:
        del edge_map[nfrom, nto]
    except KeyError:
        warnings.warn(repr(("Missing edge", nfrom, nto)))

def purge_subgraph_inplace(
    seq, req,
    edge_map,
    purge_set,
):
    for node in purge_set:
        for snode in seq[node]:
            edgedelwarn(edge_map, node, snode)
            if snode not in purge_set and (snode, node):
                req[snode].remove(node)
        del seq[node]
        for rnode in req[node]:
            #edgedelwarn(edge_map, rnode, node)
            if rnode not in purge_set and (rnode, node):
                seq[rnode].remove(node)
        del req[node]
    return


def pre_purge_inplace(seq, req, edge_map):
    #print("PRE-PURGING")
    total_N = 0
    purge_N = 0
    #actually needs to list this as seq is mutating
    for inode, smap in list(seq.items()):
        for snode in list(smap):
            total_N += 1
            if (inode, snode) not in edge_map:
                #if purge_N % 100:
                #    print("DEL: ", inode, snode)
                purge_N += 1
                smap.remove(snode)
    for snode, rmap in (req.items()):
        for inode in list(rmap):
            if (inode, snode) not in edge_map:
                rmap.remove(inode)
    #print("FRAC REMOVED: ", purge_N / total_N, purge_N)

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

def sparsity_graph(km):
    active = set()
    seq = defaultdict(set)
    req = defaultdict(set)

    #setup all linkage data
    for kfrom, kto, val in km:
        active.add(kfrom)
        active.add(kto)
        seq[kfrom].append(kto)
        req[kto].append(kfrom)
    return declarative.Bunch(
        active = active,
        seq = seq,
        req = req,
    )


