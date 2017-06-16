# -*- coding: utf-8 -*-
"""
"""
def condition_node(
    seq, req, req_alpha, edge_map, node
):
    self_edge = edge_map[node, node]
    #vprint("SELF_EDGE min: ", 1/np.max(abs(1 - self_edge)))
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
        #vprint("C_val: ", node, snode, edge)
        c_edges[snode] = edge
        c_edges_c[snode] = edge.conjugate()
        totC = totC + abs(edge_map[node, snode])**2
    #print("SELF_EDGE pe_C: ", np.max(1/abs(1 - self_edge)), np.max(totC), len(c_edges))
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

        #adjust pe_C itself
        correction = (1 - yc * a)
        if np.any(correction != 0):
            for snode, edge in c_edges.items():
                edge_map[node, snode] = correction * edge
                #print("pe_C: ", correction * edge)
        else:
            for snode, edge in c_edges.items():
                seq[node].remove(snode)
                req[snode].remove(node)
                del edge_map[node, snode]

        #adjust pe_B itself
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

        #adjust pe_D
        for cnode, cedge in c_edges.items():
            for bnode, bedge in b_edges.items():
                #print("ADD: ", bnode, cnode)
                seq[bnode].add(cnode)
                req[cnode].add(bnode)
                #does not affect req_alpha
                edge_map[bnode, cnode] = edge_map.get((bnode, cnode), 0) + yc * cedge * bedge

        #edge_map[node, snode] = edge_map[node, snode] + (a - yc) * edge
