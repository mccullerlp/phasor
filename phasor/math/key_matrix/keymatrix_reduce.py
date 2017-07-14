# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import declarative
from .dictionary_keys import (
    DictKey,
)
import operator
from collections import defaultdict

from .keymatrix_reduce_tarjan import topological_sort
from functools import reduce


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


def reduce_keymatrix(
        km,
        #non_commutative = False,
):
    pre = set()
    post = set()
    active = set()
    edges = dict()
    seq = defaultdict(set)
    req = defaultdict(set)

    PRE = DictKey(tag = 'pre')
    POST = DictKey(tag = 'post')

    #setup all linkage data
    for kfrom, kto, val in km:
        kpre  = kfrom | PRE
        kpost = kto  | POST
        pre.add(kpre)
        post.add(kpost)
        active.add(kfrom)
        active.add(kto)
        edges[kpre, kfrom] = 1
        edges[kto, kpost] = 1
        edges[kfrom, kto] = val
        seq[kpre].append(kfrom)
        seq[kfrom].append(kto)
        seq[kto].append(kpost)
        req[kfrom].append(kpre)
        req[kto].append(kfrom)
        req[kpost].append(kto)

    def split_reduce(active_set):
        def successor_func(node):
            for snode in seq[node]:
                if snode in active_set:
                    yield snode
        SCCs = []
        for nodelist in topological_sort(active_set, successor_func):
            if len(nodelist) == 1:
                continue
            else:
                SCCs.append(nodelist)

        while SCCs:
            scc = SCCs.pop()
            SCC_reduce(scc)
        return

    split_reduce(active)
    return

def SCC_reduce(scc):
    scc_set = set(scc)
    def first_successor_func(node):
        #since we are in an SCC, all nodes must have at least one successor
        for snode in seq[node]:
            if snode in scc_set:
                return snode
        raise RuntimeError("HMM")
    node = scc[0]
    loop_seq = [node]
    loop_set = set(loop_seq)
    while True:
        node = first_successor_func(node)
        if node in loop_set:
            #get just the loop that was found, clipping any nodes before the loop
            loop_seq = loop_seq[loop_seq.index(node):]
            loop_set = set(loop_seq)
            break
        loop_seq.append(node)
        loop_set.add(node)

    N_loop = len(loop_seq)

    loop_gazoutas = []
    loop_edges = []
    for idx, node in enumerate(loop_seq[:N_loop]):
        snodes = seq.pop(node)
        #this even works for idx == 0
        gazoutas = [snode for snode in snodes if snode is not loop_seq[idx - 1]]
        #remove the output edges as we find them
        loop_edges.append(edges.pop(node, loop_seq[idx+1]))
        gazoutas_edges = [edges.pop(node, snode) for snode in gazoutas]
        loop_gazoutas.append((gazoutas, gazoutas_edges))
    #also for indexing
    loop_edges = loop_edges + loop_edges

    #so that ps_In don't have to have tricky indexing later
    loop_seq = loop_seq + loop_seq
    #now pop the loop
    if not non_commutative:
        G_loop = reduce(operator.mul, loop_edges)
    for idx, node in enumerate(loop_seq[:N_loop]):
        if non_commutative:
            G_loop = reduce(operator.mul, loop_seq[idx:idx + N_loop])
        #this even works for idx == 0
        rnodes = req.pop(node)
        gazintas = [rnode for rnode in rnodes if rnode is not loop_seq[idx - 1]]
        if not gazintas:
            continue
        #remove the input edges as we find them
        gazintas_edges = [edges.pop(rnode, node) for rnode in gazintas]
        #now go down the dependent nodes of the loop
        for idx_ln2, lnode2 in enumerate(loop_seq[idx:idx+N_loop]):
            #TODO
            pass
    return

