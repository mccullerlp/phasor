# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
from numbers import Number
import numpy as np
from collections import defaultdict
import declarative

from phasor.utilities.priority_queue import HeapPriorityQueue

from .matrix_generic import (
    pre_purge_inplace,
    purge_seqless_inplace,
    purge_reqless_inplace,
    check_seq_req_balance,
)


from ..base import (
    DictKey,
)


def mgraph_simplify_inplace(
    seq, req,
    edge_map,
    verbose = False,
    Q_conditioning = False,
):
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

    for node in seq.keys():
        if not seq[node] or not req[node]:
            #then this is an edge node and exempt
            continue
        cost = generate_node_cost(node)
        pqueue.push((cost, node))

    if verbose:
        print("pqueue length: ", len(pqueue))

    while pqueue:
        cost, node = pqueue.pop()

        #get new nodes to minimize cost at removal
        while node in node_costs_invalid_in_queue:
            node_costs_invalid_in_queue.remove(node)
            cost = generate_node_cost(node)
            cost, node = pqueue.pushpop((cost, node))

        #newcost = generate_node_cost(node)
        #TODO, deal with bad loops
        #if newcost != cost:
        #    pqueue.push((newcost, node))
        #    continue
        #print(node, cost)
        if not np.isfinite(cost) and pqueue:
            pqueue.push((cost, node))
            continue

        #if len(seq) % 100 == 0:
            #print("REPORT: ", len(seq), len(edge_map), len(edge_map) / len(seq), len(edge_map) / len(seq)**2)

        #now check if it is a loop node, adjusting the action accordingly
        if node in seq[node]:
            self_edge = edge_map[node, node]
            #assert(len(pqueue) == 0)
            #print("SELF_EDGE min: ", generate_node_cost_loop(node))
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


def wrap_input_node(node):
    return ('INPUT', node)


def wrap_output_node(node):
    return ('OUTPUT', node)


def inverse_solve_inplace(
    seq, req,
    edge_map,
    outputs_set,
    inputs_set   = frozenset(),
    inputs_map   = None,
    edge_map_sym = None,
    purge_in     = True,
    purge_out    = True,
    verbose      = False,
    negative     = False,
    scattering   = False,
    **kwargs
):
    assert(scattering)
    pre_purge_inplace(seq, req, edge_map)

    VACUUM_STATE = DictKey(special = 'vacuum')
    if inputs_map is not None:
        #first dress the nodes. The source vectors is converted into edges with a special
        #source node
        #the inputs are from the special state (with implicit vector value of '1')
        for inode, val in inputs_map.items():
            seq[VACUUM_STATE].add(inode)
            req[inode].add(VACUUM_STATE)
            edge_map[VACUUM_STATE, inode] = val

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
    #print("SEQ")
    #print_seq(seq, edge_map)

    #subN = len(wrapped_onodes) + len(wrapped_inodes)
    #print("SPARSITY ", len(seq) - subN, len(edge_map) - subN, (len(edge_map) - subN) / (len(seq) - subN))

    #simplify with the wrapped nodes
    mgraph_simplify_inplace(
        seq            = seq,
        req            = req,
        edge_map       = edge_map,
        verbose        = verbose,
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
        for wonode in seq[winode]:
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
