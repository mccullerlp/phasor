# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np

#from ..math.dispatched import abs_sq

N_limit_rel = 100


def abssq(arr):
    return arr.real**2 + arr.imag**2


def enorm(arr):
    return np.max(abssq(arr))


def check_graph_at_node(SRABE, node):
    seq, req, req_alpha, seq_beta, edge_map, = SRABE
    for snode in seq[node]:
        assert(node in req[snode])
    for rnode in req[node]:
        assert(node in seq[rnode])


def reduceLUQ_row(
    SRABE,
    node,
    node_costs_invalid_in_queue,
    vprint = lambda *x: None,
    **kwargs
):
    seq, req, seq_beta, req_alpha, edge_map, = SRABE

    normr = 0
    for rnode in req[node]:
        normr = normr + abs(edge_map[rnode, node])**2
    normr = normr ** .5

    vprint("Using ROW Operations")

    assert(req[node])
    rvec = []
    rvec_N = []
    rvec_self_idx = None
    for idx, rnode in enumerate(req[node]):
        if node == rnode:
            rvec_self_idx = idx
        rvec.append(np.max(abs(edge_map[rnode, node] / normr)))
        rvec_N.append(rnode)

    vprint("RVEC: ", rvec)
    if not np.all(np.isfinite(rvec)):
        print("NORMR: ", normr)
        assert(False)
    bignodes_r = np.array(rvec) >= 1./(len(req[node]))**.5
    rcount = np.count_nonzero(bignodes_r)
    vprint("R: ", np.count_nonzero(bignodes_r), len(req[node]), bignodes_r[rvec_self_idx])

    do_save = False
    if rcount >= 2:
        if rvec_self_idx is not None:
            if not bignodes_r[rvec_self_idx]:
                if rvec[rvec_self_idx] > 1./(len(req[node]))**.5 / N_limit_rel:
                    #print("COULD SAVE! ", node, len(seq), len(edge_map))
                    do_save = True
                else:
                    #print("CANT SAVE! ", node)
                    pass
        vprint("MUST USE HOUSEHOLDER {0}x".format(rcount))
        if not do_save and rvec_self_idx is None or not bignodes_r[rvec_self_idx]:
            vprint("MUST PIVOT")
            idx_pivot = np.nonzero(bignodes_r)[0][0]
            vprint("SELF: ", rvec_self_idx)
            vprint("PIVO: ", idx_pivot)
            node_pivot = rvec_N[idx_pivot]
            vprint("SWAP: ", node, node_pivot)
            pivotROW_OP(
                SRABE = SRABE,
                node1 = node,
                node2 = node_pivot,
                node_costs_invalid_in_queue = node_costs_invalid_in_queue,
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
            SRABE = SRABE,
            node_into = node,
            nodes_from = nfrom,
            node_costs_invalid_in_queue = node_costs_invalid_in_queue,
            **kwargs
        )
    elif rcount == 1:
        vprint("DIRECT")
        if rvec_self_idx is not None:
            if not bignodes_r[rvec_self_idx] and rvec[rvec_self_idx] > 1./(len(req[node]))**.5 / N_limit_rel:
                #print("COULD PREVENT PIVOT! ", node)
                do_save = True
        if not do_save and rvec_self_idx is None or not bignodes_r[rvec_self_idx]:
            vprint("MUST PIVOT")
            vprint('bignodes', bignodes_r)
            #could choose pivot node based on projected fill-in
            idx_pivot = np.nonzero(bignodes_r)[0][0]
            vprint("SELF: ", rvec_self_idx)
            vprint("PIVO: ", idx_pivot)
            node_pivot = rvec_N[idx_pivot]
            vprint("SWAP: ", node, node_pivot)
            pivotROW_OP(
                SRABE = SRABE,
                node1 = node,
                node2 = node_pivot,
                node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                **kwargs
            )
            node_costs_invalid_in_queue.add(node)
            node_costs_invalid_in_queue.add(node_pivot)
            node = node_pivot
            #continue
    reduceLU(
        SRABE = SRABE,
        node = node,
        node_costs_invalid_in_queue = node_costs_invalid_in_queue,
        **kwargs
    )


def reduceLUQ_col(
    SRABE,
    node,
    node_costs_invalid_in_queue,
    vprint = lambda *x: None,
    **kwargs
):
    seq, req, seq_beta, req_alpha, edge_map, = SRABE

    normc = 0
    for snode in seq[node]:
        normc = normc + abs(edge_map[node, snode])**2
    normc = normc ** .5

    vprint("Using COLUMN Operations")

    assert(seq[node])
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
    if not np.all(np.isfinite(cvec)):
        print("NORMC: ", normc)
        assert(False)
    bignodes_c = np.array(cvec) >= 1./(len(seq[node]))**.5
    ccount = np.count_nonzero(bignodes_c)
    vprint(bignodes_c, cvec_self_idx, ccount)
    vprint("pe_C: ", np.count_nonzero(bignodes_c), len(seq[node]), bignodes_c[cvec_self_idx])

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
                SRABE = SRABE,
                node1 = node,
                node2 = node_pivot,
                node_costs_invalid_in_queue = node_costs_invalid_in_queue,
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
            SRABE = SRABE,
            node_into = node,
            nodes_from = nfrom,
            node_costs_invalid_in_queue = node_costs_invalid_in_queue,
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
                SRABE = SRABE,
                node1 = node,
                node2 = node_pivot,
                node_costs_invalid_in_queue = node_costs_invalid_in_queue,
            )
            node_costs_invalid_in_queue.add(node)
            node_costs_invalid_in_queue.add(node_pivot)
            node = node_pivot
            #continue
    reduceLU(
        SRABE = SRABE,
        node = node,
        node_costs_invalid_in_queue = node_costs_invalid_in_queue,
        **kwargs
    )
    return


def pivotROW_OP(
    SRABE,
    node1,
    node2,
    node_costs_invalid_in_queue,
    **kwargs
):
    """
    Swaps ROWS within a column. So all edges TO node1 go to node2 and vice-versa.

    column ops affect ALPHA.
    """
    #print("SEQ 1: ", node1, seq[node1])
    #print("REQ 1: ", node1, req[node1])
    #print("SEQ 2: ", node2, seq[node2])
    #print("REQ 2: ", node2, req[node2])

    seq, req, req_alpha, seq_beta, edge_map, = SRABE
    check_graph_at_node(SRABE, node1)
    check_graph_at_node(SRABE, node2)

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

    check_graph_at_node(SRABE, node1)
    check_graph_at_node(SRABE, node2)

    edge_map.update(edge_mape_2)
    return


def pivotCOL_OP(
    SRABE,
    node1,
    node2,
    node_costs_invalid_in_queue,
    **kwargs
):
    """
    Swaps COLUMNS within a row . So all edges FROM node1 go to node2 and vice-versa.

    row ops affect BETA.
    """
    #print("SEQ 1: ", node1, seq[node1])
    #print("REQ 1: ", node1, req[node1])
    #print("SEQ 2: ", node2, seq[node2])
    #print("REQ 2: ", node2, req[node2])
    seq, req, req_alpha, seq_beta, edge_map, = SRABE

    check_graph_at_node(SRABE, node1)
    check_graph_at_node(SRABE, node2)

    edge_mape_2 = dict()
    #gets all edges from node1/2
    for snode in seq[node1]:
        edge = edge_map.pop((node1, snode))
        edge_mape_2[node2, snode] = edge
        #if snode != node2:
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

    check_graph_at_node(SRABE, node1)
    check_graph_at_node(SRABE, node2)

    #print("SEQ 1: ", node1, seq[node1])
    #print("REQ 1: ", node1, req[node1])
    #print("SEQ 2: ", node2, seq[node2])
    #print("REQ 2: ", node2, req[node2])

    edge_map.update(edge_mape_2)
    return


def householderREFL_ROW_OP(
    SRABE,
    node_into,
    nodes_from,
    node_costs_invalid_in_queue,
    **kwargs
):
    """
    Moves COLUMN (from) COEFFS within a row (to). All of the edges of node_into to nodes_from are zerod.

    row ops affect BETA.
    """
    seq, req, req_alpha, seq_beta, edge_map, = SRABE

    check_graph_at_node(SRABE, node_into)

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

    #Q = ps_In - 2 u * u^dagger / |u|**2
    #tau = |u|**2 / 2
    #Q = ps_In - u * u^dagger / tau

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

    check_graph_at_node(SRABE, node_into)

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
    SRABE,
    node_into,
    nodes_from,
    node_costs_invalid_in_queue,
    **kwargs
):
    """
    Moves ROW COEFFS within a column. All of the edges of node_into to nodes_from are zerod.

    column ops affect ALPHA.
    """
    seq, req, req_alpha, seq_beta, edge_map, = SRABE

    #check graph
    check_graph_at_node(SRABE, node_into)

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

    #Q = ps_In - 2 u * u^dagger / |u|**2
    #tau = |u|**2 / 2
    #Q = ps_In - u * u^dagger / tau

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


def reduceLU(
    SRABE,
    node,
    node_costs_invalid_in_queue = None,
    **kwargs
):
    seq, req, req_alpha, seq_beta, edge_map, = SRABE

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


def reduceLUQ_row(
    SRABE,
    node,
    node_costs_invalid_in_queue,
    vprint = lambda *x: None,
    **kwargs
):
    seq, req, seq_beta, req_alpha, edge_map, = SRABE

    normr = 0
    for rnode in req[node]:
        normr = normr + abs(edge_map[rnode, node])**2
    normr = normr ** .5

    vprint("Using ROW Operations")

    assert(req[node])
    rvec = []
    rvec_N = []
    rvec_self_idx = None
    for idx, rnode in enumerate(req[node]):
        if node == rnode:
            rvec_self_idx = idx
        rvec.append(np.max(abs(edge_map[rnode, node] / normr)))
        rvec_N.append(rnode)

    vprint("RVEC: ", rvec)
    if not np.all(np.isfinite(rvec)):
        print("NORMR: ", normr)
        assert(False)
    bignodes_r = np.array(rvec) >= 1./(len(req[node]))**.5
    rcount = np.count_nonzero(bignodes_r)
    vprint("R: ", np.count_nonzero(bignodes_r), len(req[node]), bignodes_r[rvec_self_idx])

    do_save = False
    if rcount >= 2:
        if rvec_self_idx is not None:
            if not bignodes_r[rvec_self_idx]:
                if rvec[rvec_self_idx] > 1./(len(req[node]))**.5 / N_limit_rel:
                    #print("COULD SAVE! ", node, len(seq), len(edge_map))
                    do_save = True
                else:
                    #print("CANT SAVE! ", node)
                    pass
        vprint("MUST USE HOUSEHOLDER {0}x".format(rcount))
        if not do_save and rvec_self_idx is None or not bignodes_r[rvec_self_idx]:
            vprint("MUST PIVOT")
            idx_pivot = np.nonzero(bignodes_r)[0][0]
            vprint("SELF: ", rvec_self_idx)
            vprint("PIVO: ", idx_pivot)
            node_pivot = rvec_N[idx_pivot]
            vprint("SWAP: ", node, node_pivot)
            pivotROW_OP(
                SRABE = SRABE,
                node1 = node,
                node2 = node_pivot,
                node_costs_invalid_in_queue = node_costs_invalid_in_queue,
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
            SRABE = SRABE,
            node_into = node,
            nodes_from = nfrom,
            node_costs_invalid_in_queue = node_costs_invalid_in_queue,
            **kwargs
        )
    elif rcount == 1:
        vprint("DIRECT")
        if rvec_self_idx is not None:
            if not bignodes_r[rvec_self_idx] and rvec[rvec_self_idx] > 1./(len(req[node]))**.5 / N_limit_rel:
                #print("COULD PREVENT PIVOT! ", node)
                do_save = True
        if not do_save and rvec_self_idx is None or not bignodes_r[rvec_self_idx]:
            vprint("MUST PIVOT")
            vprint('bignodes', bignodes_r)
            #could choose pivot node based on projected fill-in
            idx_pivot = np.nonzero(bignodes_r)[0][0]
            vprint("SELF: ", rvec_self_idx)
            vprint("PIVO: ", idx_pivot)
            node_pivot = rvec_N[idx_pivot]
            vprint("SWAP: ", node, node_pivot)
            pivotROW_OP(
                SRABE = SRABE,
                node1 = node,
                node2 = node_pivot,
                node_costs_invalid_in_queue = node_costs_invalid_in_queue,
                **kwargs
            )
            node_costs_invalid_in_queue.add(node)
            node_costs_invalid_in_queue.add(node_pivot)
            node = node_pivot
            #continue
    reduceLU(
        SRABE = SRABE,
        node = node,
        node_costs_invalid_in_queue = node_costs_invalid_in_queue,
        **kwargs
    )


def reduceLUQ_col(
    SRABE,
    node,
    node_costs_invalid_in_queue,
    vprint = lambda *x: None,
    **kwargs
):
    seq, req, seq_beta, req_alpha, edge_map, = SRABE

    normc = 0
    for snode in seq[node]:
        normc = normc + abs(edge_map[node, snode])**2
    normc = normc ** .5

    vprint("Using COLUMN Operations")

    assert(seq[node])
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
    if not np.all(np.isfinite(cvec)):
        print("NORMC: ", normc)
        assert(False)
    bignodes_c = np.array(cvec) >= 1./(len(seq[node]))**.5
    ccount = np.count_nonzero(bignodes_c)
    vprint(bignodes_c, cvec_self_idx, ccount)
    vprint("pe_C: ", np.count_nonzero(bignodes_c), len(seq[node]), bignodes_c[cvec_self_idx])

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
                SRABE = SRABE,
                node1 = node,
                node2 = node_pivot,
                node_costs_invalid_in_queue = node_costs_invalid_in_queue,
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
            SRABE = SRABE,
            node_into = node,
            nodes_from = nfrom,
            node_costs_invalid_in_queue = node_costs_invalid_in_queue,
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
                SRABE = SRABE,
                node1 = node,
                node2 = node_pivot,
                node_costs_invalid_in_queue = node_costs_invalid_in_queue,
            )
            node_costs_invalid_in_queue.add(node)
            node_costs_invalid_in_queue.add(node_pivot)
            node = node_pivot
            #continue
    reduceLU(
        SRABE = SRABE,
        node = node,
        node_costs_invalid_in_queue = node_costs_invalid_in_queue,
        **kwargs
    )
    return
