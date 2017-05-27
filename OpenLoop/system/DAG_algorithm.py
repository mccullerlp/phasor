# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
import warnings
from numbers import Number
import numpy as np
from collections import defaultdict
import declarative

from OpenLoop.utilities.priority_queue import HeapPriorityQueue

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
    Q_conditioning = False,
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
        if not seq[node]:
            for rnode in req[node]:
                seq_beta[rnode].add(node)
                seq[rnode].remove(node)
                beta_set.add(node)
    for node in seq:
        if not req[node]:
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
                norm = enorm(edge_map[node, rnode])
                edge_norms[node, rnode] = norm
            tot_norm = tot_norm + norm
        return tot_norm
    generate_node_cost = generate_row_cost

    pqueue = HeapPriorityQueue()

    for node in seq.keys():
        cost = generate_node_cost(node)
        pqueue.push((cost, node))
    if verbose: print("pqueue length: ", len(pqueue))

    while req:
        #print("REQ: ", req)
        #print("REQ_A: ", req_alpha)
        #print("SEQ: ", seq)
        #print("SEQ_B: ", seq_beta)
        cost, node = pqueue.pop()

        #get new nodes to minimize cost at removal
        if False and node_costs_invalid_in_queue:
            while node in node_costs_invalid_in_queue:
                node_costs_invalid_in_queue.remove(node)
                cost = generate_node_cost(node)
                cost, node = pqueue.pushpop((cost, node))

        #node must at least have a self-loop
        areq_set = req_alpha[node]
        min_rnode = None
        min_rnode_cost = float('inf')
        for rnode in req[node]:
            if rnode in areq_set:
                continue
            rcost = generate_row_cost(rnode)
            if rcost < min_rnode_cost:
                min_rnode = rnode
                min_rnode_cost = rcost
        print("MIN_MAX: ", node, min_rnode)

        #row norm
        if len(seq[node]) > 1:
            normr = 0
            for snode in seq[node]:
                normr += abs(edge_map[node, snode])**2
            normr = normr ** .5
            #row norm
            normc = 0
            for rnode in req[node]:
                normc += abs(edge_map[rnode, node])**2
            normc = normc ** .5

            rel_r_to_c = np.count_nonzero(normr > normc) / len(normr)
            print("REL LARGER: ", rel_r_to_c)

            rvec = []
            for idx, snode in enumerate(seq[node]):
                if node == snode:
                    rvec_self_idx = idx
                rvec.append(np.max(abs(edge_map[node, snode] / normr)))

            bignodes_r = np.array(rvec) >= 1./(len(seq[node]))**.5
            rcount = np.count_nonzero(bignodes_r)
            print("R: ", np.count_nonzero(bignodes_r), len(seq[node]), bignodes_r[rvec_self_idx], rel_r_to_c > .5)
            cvec = []
            for idx, rnode in enumerate(req[node]):
                if node == rnode:
                    cvec_self_idx = idx
                cvec.append(np.max(abs(edge_map[rnode, node] / normc)))
            bignodes_c = np.array(cvec) >= 1./(len(req[node]))**.5
            ccount = np.count_nonzero(bignodes_c)
            print("C: ", np.count_nonzero(bignodes_c), len(req[node]), bignodes_c[cvec_self_idx], rel_r_to_c < .5)

            if node in seq[node]:
                norma = abs(edge_map[node, node])
                print("NORM: ", np.max(normr / norma), np.max(normc / norma))

            if rel_r_to_c > .5:
                print("Using ROW Operations")
                if not bignodes_r[rvec_self_idx]:
                    print("MUST PIVOT")
                if rcount >= 2:
                    print("MUST USE HOUSEHOLDER {0}x".format(rcount))
                elif rcount == 1:
                    print("DIRECT")
            else:
                print("Using COLUMN Operations")
                if not bignodes_c[cvec_self_idx]:
                    print("MUST PIVOT")
                if ccount >= 2:
                    print("MUST USE HOUSEHOLDER {0}x".format(ccount))
                elif ccount == 1:
                    print("DIRECT")
        assert(np.isfinite(cost))

        reduceLU(
            node = node,
            **kwargs
        )

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
    Q_conditioning = False,
    **kwargs
):
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
    for onode in outputs_set:
        wonode = wrap_output_node(onode)
        wrapped_onodes.add(wonode)
        seq[onode].add(wonode)
        req[wonode].add(onode)
        edge_map[onode, wonode] = 1

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
        Q_conditioning = Q_conditioning,
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
):
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

    wrapped_onodes = set()
    for onode in outputs_set:
        wonode = wrap_output_node(onode)
        #print("WONODEA", wonode)
        wrapped_onodes.add(wonode)
        seq[onode].add(wonode)
        req[wonode].add(onode)
        edge_map[onode, wonode] = 1

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
