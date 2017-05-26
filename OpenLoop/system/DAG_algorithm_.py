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

    a = 1 - self_edge
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
                    if snode == lnode:
                        lval = lval + edge * (1 - edge2)
                        d_mat[lnode, snode] = (1 - edge2)
                    else:
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
    #at this stage all of the alpha_reqs are only single move
    req_alpha = defaultdict(set)
    for node, rset in req.items():
        winode = wrap_input_node(node)
        if winode in rset:
            req_alpha[node].add(winode)

    check_seq_req_balance(seq, req, edge_map)
    node_costs_invalid_in_queue = set()
    #this is just a heuristic
    def generate_node_cost(node):
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
        ##TODO, deal with bad loops
        #self_edge = edge_map.get((node, node), None)
        #if self_edge is not None:
        #    if np.any(self_edge == 1):
        #        return float('inf')
        #    else:
        #        return 10
        return s_n * r_n_full + r_n * s_n_full

    def generate_node_cost_loop(node):
        self_edge = edge_map.get((node, node), None)
        return 0#np.max(abs(1 - self_edge))

    pqueue = HeapPriorityQueue()
    nrem = list()
    pqueue_loop = HeapPriorityQueue()

    for node in seq.keys():
        if not seq[node] or not req[node]:
            #then this is an edge node and exempt
            continue
        cost = generate_node_cost(node)
        pqueue.push((cost, node))
        nrem.append(node)
    nrem.sort()
    if not sorted_order:
        nrem = None
    if verbose: print("pqueue length: ", len(pqueue))
    nrem = None

    while pqueue or pqueue_loop:
        if pqueue:
            if nrem:
                node = nrem[0]
                nrem = nrem[1:]
                if not nrem:
                    while pqueue:
                        pqueue.pop()
            else:
                cost, node = pqueue.pop()

                #get new nodes to minimize cost at removal
                while node in node_costs_invalid_in_queue:
                    node_costs_invalid_in_queue.remove(node)
                    cost = generate_node_cost(node)
                    cost, node = pqueue.pushpop((cost, node))

                #move to other queue if self-edge node
                #if node in seq[node]:
                #    cost = generate_node_cost_loop(node)
                #    pqueue_loop.push((cost, node))
                #    if not pqueue:
                #        if verbose: print("pqueue_loop length: ", len(pqueue_loop))
                #    continue

        else:
            cost, node = pqueue_loop.pop()
            #get new nodes to minimize cost at removal
            while node in node_costs_invalid_in_queue:
                node_costs_invalid_in_queue.remove(node)
                cost = generate_node_cost_loop(node)
                cost, node = pqueue_loop.pushpop((cost, node))
            newcost = generate_node_cost_loop(node)
            #TODO, deal with bad loops
            print(node, newcost, cost)
            assert(np.isfinite(newcost))
            if newcost != cost:
                pqueue_loop.push((newcost, node))
                continue
            print("SOLVING LOOP ON: ", node)

        if not np.isfinite(cost) and pqueue:
            assert(False)
            pqueue.push((cost, node))
            continue

        #print("SOLVING ON: ", node)
        #Q-conditioning
        if False and node in seq[node]:
            print("Q: ", Q_conditioning)
            condition_node(
                seq       = seq,
                req       = req,
                req_alpha = req_alpha,
                edge_map  = edge_map,
                node      = node,
            )
        #now check if it is a loop node, adjusting the action accordingly
        if node in seq[node]:
            self_edge = edge_map[node, node]
            del edge_map[node, node]
            #assert(len(pqueue) == 0)
            #print("SELF_EDGE min: ", generate_node_cost_loop(node))
            CLG = -1 / self_edge
            #remove the self edge for the simplification stage
            seq[node].remove(node)
            req[node].remove(node)
        else:
            CLG = None

        #if CLG is not None:
        #    print("Popping : ", node)
        #else:
        #    print("Reducing: ", node)

        #print("REQ: ", req_alpha)
        for snode in seq[node]:
            sedge = edge_map[node, snode]
            for rnode in req[node]:
                redge = edge_map[rnode, node]
                if CLG is None:
                    if sedge is 1:
                        prod = redge
                    elif redge is 1:
                        prod = sedge
                    else:
                        prod = (sedge * redge)
                else:
                    if sedge is 1:
                        prod = (CLG * redge)
                    elif redge is 1:
                        prod = (sedge * CLG)
                    else:
                        prod = (sedge * CLG * redge)
                prev_edge = edge_map.get((rnode, snode), None)
                if prev_edge is not None:
                    edge_map[(rnode, snode)] = prev_edge + prod
                    #TODO, should probably invalidate here, but its probably OK
                else:
                    if rnode == snode:
                        edge_map[(rnode, snode)] = prod + 1
                    else:
                        edge_map[(rnode, snode)] = prod
                    node_costs_invalid_in_queue.add(rnode)
                    node_costs_invalid_in_queue.add(snode)
                    seq[rnode].add(snode)
                    req[snode].add(rnode)
                    if rnode in req_alpha[node]:
                        req_alpha[snode].add(rnode)
            req[snode].remove(node)
            del edge_map[node, snode]
        for rnode in req[node]:
            del edge_map[rnode, node]
            seq[rnode].remove(node)
        del seq[node]
        del req[node]
        #nodes may not have alphas
        try:
            del req_alpha[node]
        except KeyError:
            pass
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
        seq      = seq,
        req      = req,
        edge_map = edge_map,
        verbose  = verbose,
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
