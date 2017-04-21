# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
import warnings
from numbers import Number
import numpy as np
from collections import defaultdict
import declarative

from BGSF.utilities.priority_queue import HeapPriorityQueue

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


def mgraph_simplify_inplace(
    seq, req,
    edge_map,
):
    #TODO: add logic to help numerical stability

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

    pqueue = HeapPriorityQueue()
    pqueue_loop = HeapPriorityQueue()

    for node in seq.keys():
        if not seq[node] or not req[node]:
            #then this is an edge node and exempt
            continue
        cost = generate_node_cost(node)
        pqueue.push((cost, node))

    while pqueue or pqueue_loop:
        if pqueue:
            cost, node = pqueue.pop()
            #move to other queue if self-edge node
            if node in seq[node]:
                cost = generate_node_cost(node)
                pqueue_loop.push((cost, node))
                continue
        else:
            cost, node = pqueue_loop.pop()

        #newcost = generate_node_cost(node)
        #TODO, deal with bad loops
        #if newcost != cost:
        #    pqueue.push((newcost, node))
        #    continue
        #print(node, cost)
        if not np.isfinite(cost) and pqueue:
            pqueue.push((cost, node))
            continue

        #get new nodes to minimize cost at removal
        while node in node_costs_invalid_in_queue:
            node_costs_invalid_in_queue.remove(node)
            cost = generate_node_cost(node)
            cost, node = pqueue.pushpop((cost, node))

        #now check if it is a loop node, adjusting the action accordingly
        if node in seq[node]:
            self_edge = edge_map[node, node]
            CLG = 1 / (1 - self_edge)
            #remove the self edge for the simplification stage
            seq[node].remove(node)
            req[node].remove(node)
        else:
            CLG = None

        #if CLG is not None:
        #    print("Popping : ", node)
        #else:
        #    print("Reducing: ", node)

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
                    edge_map[(rnode, snode)] = prod
                    node_costs_invalid_in_queue.add(rnode)
                    node_costs_invalid_in_queue.add(snode)
                    seq[rnode].add(snode)
                    req[snode].add(rnode)
            req[snode].remove(node)
            del edge_map[node, snode]
        for rnode in req[node]:
            del edge_map[rnode, node]
            seq[rnode].remove(node)
        del seq[node]
        del req[node]
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

def inverse_solve_inplace(
    seq, req,
    edge_map,
    inputs_set,
    outputs_set,
    purge_in = True,
    purge_out = True,
):
    pre_purge_inplace(seq, req, edge_map)

    #first dress the nodes
    wrapped_inodes = set()
    for inode in inputs_set:
        winode = ('INPUT', inode)
        wrapped_inodes.add(winode)
        seq[winode].add(inode)
        req[inode].add(winode)
        edge_map[winode, inode] = 1

    wrapped_onodes = set()
    for onode in outputs_set:
        wonode = ('OUTPUT', onode)
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
        seq = seq,
        req = req,
        edge_map = edge_map,
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
        winode = ('INPUT', inode)
        #print("WINODEA", winode)
        wrapped_inodes.add(winode)
        seq[winode].add(inode)
        req[inode].add(winode)
        edge_map[winode, inode] = 1

    wrapped_onodes = set()
    for onode in outputs_set:
        wonode = ('OUTPUT', onode)
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
