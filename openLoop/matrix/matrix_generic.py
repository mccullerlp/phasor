# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
import warnings
from collections import defaultdict
import declarative

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
        seq,
        req,
        except_set = None,
        req_alpha  = None,
        seq_beta   = None,
        edge_map   = None,
):
    if except_set is None:
        except_set = set(req_alpha.keys())
    color_purge_inplace(
        except_set, seq,
        seq, req, edge_map,
    )
    if seq_beta is not None:
        rmnodes = list()
        for node in seq_beta.keys():
            if not req.get(node, None):
                rmnodes.append(node)
        for node in rmnodes:
            del seq_beta[node]


def purge_seqless_inplace(
        seq,
        req,
        except_set = None,
        req_alpha  = None,
        seq_beta   = None,
        edge_map   = None,
):
    if except_set is None:
        except_set = set(seq_beta.keys())
    color_purge_inplace(
        except_set, req,
        seq, req, edge_map,
    )
    if req_alpha is not None:
        rmnodes = list()
        for node in req_alpha.keys():
            if not seq.get(node, None):
                rmnodes.append(node)
        for node in rmnodes:
            del req_alpha[node]


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


