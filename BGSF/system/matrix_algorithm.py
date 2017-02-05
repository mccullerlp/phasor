# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
from builtins import object
from collections import defaultdict
import copy

import declarative

from ..base.ports import PostBondKey

from ..math.key_matrix import (
    KVSpace,
)

from .graph_algorithm import (
    check_seq_req_balance,
    purge_reqless_inplace,
    purge_seqless_inplace,
)

from .matrix_injections import (
    ConstantEdgeCoupling,
    ConstantSourceCoupling,
    MultiplicativeEdgeCoupling,
    MultiplicativeSourceCoupling,
    TripletCoupling,
)

class MatrixBuildAlgorithm(object):

    def __init__(
        self,
        system,
        ports_algorithm,
    ):
        self.system = system
        self.ports_algo = ports_algorithm
        #TODO maybe copy?
        self.port_cplgs = ports_algorithm.port_cplgs

        #TODO, be smarter about this field space default
        if system.field_space is None:
            field_space = KVSpace('field_ports', dtype = object)
        else:
            field_space = system.field_space_proto.copy()
        self.field_space                 = field_space

        self.source_vector_injlist        = defaultdict(list)
        self.source_vector_inj_funclist   = defaultdict(list)
        self.coupling_matrix_injlist      = defaultdict(list)
        self.coupling_matrix_inj_funclist = defaultdict(list)
        self.all_injections = list()

        self.noise_pk_set = set()

        self._noise_map()
        self._setup_system()

        #TODO, stopgap for generating an exhaustive field space
        for p, k_set in self.port_cplgs.items():
            port = p
            while port is not None:
                for k in k_set:
                    self.field_space.keys_add((port, k))
                port = self.system.ports_post.get(port, None)
            port = p
            while True:
                port = self.system.ports_pre.get(port, None)
                if port is None:
                    break
                for k in k_set:
                    self.field_space.keys_add((port, k))

        self.field_space.freeze()

        #freeze the lists
        self.source_vector_injlist        = dict(list(self.source_vector_injlist.items()))
        self.source_vector_inj_funclist   = dict(list(self.source_vector_inj_funclist.items()))
        self.coupling_matrix_injlist      = dict(list(self.coupling_matrix_injlist.items()))
        self.coupling_matrix_inj_funclist = dict(list(self.coupling_matrix_inj_funclist.items()))

    def _setup_system(self):
        for el in self.system.elements:
            try:
                ssc = el.system_setup_coupling
            except AttributeError:
                pass
            else:
                ssc(self)

        AC_in_all = set()
        AC_out_all = set()
        for inj in self.all_injections:
            AC_in_all.update(inj.AC_ins_pk)
            AC_out_all.update(inj.AC_outs_pk)
        self.AC_in_all = AC_in_all
        self.AC_out_all = AC_out_all
        #print("IN  ALL: ", self.AC_in_all)
        #print("OUT ALL: ", self.AC_out_all)

        self.coherent_subgraph_bunch = self._coherent_sparsity_graph()
        return

    def _noise_map(self):
        self._nmap = dict()
        for el in self.system.elements:
            try:
                ssn = el.system_setup_noise
            except AttributeError:
                pass
            else:
                ssn(self)
        self.coupling_noise_map = self._nmap
        del self._nmap
        return self.coupling_noise_map

    def noise_pair_insert(self, p1, k1, p2, k2, genfunc):
        #print('noise pair: ', p1, k2, p2, k2)
        ptofull1 = self.port_cplgs.get(p1.purge_keys(PostBondKey), declarative.NOARG)
        assert(k1 in ptofull1)
        ptofull2 = self.port_cplgs.get(p2.purge_keys(PostBondKey), declarative.NOARG)
        assert(k2 in ptofull2)

        self.field_space.keys_add((p1, k1))
        self.field_space.keys_add((p2, k2))
        self.noise_pk_set.add((p1, k1))
        self.noise_pk_set.add((p2, k2))

        #self.coupling_matrix_print(select_from = (p1, k2))
        nmap_inner = self._nmap.setdefault((p1, k1), dict())
        nmap_inner.setdefault((p2, k2), []).append((p1, k1, p2, k2, genfunc))
        return

    def port_set_get(self, port):
        #maybe get rid of
        port = port.purge_keys(PostBondKey)
        pkey = self.port_cplgs[port]
        return pkey

    def port_coupling_insert(
            self,
            pfrom, kfrom, pto, kto,
            cplg, *vpairs
    ):
        if vpairs:
            inj = MultiplicativeEdgeCoupling(
                pkfrom     = (pfrom, kfrom),
                pkto       = (pto, kto),
                cplg       = cplg,
                pksrc_list = vpairs,
            )
        else:
            inj = ConstantEdgeCoupling(
                pkfrom     = (pfrom, kfrom),
                pkto       = (pto, kto),
                cplg       = cplg,
            )
        self.injection_insert(inj)
        return

    def coherent_sources_insert(self, pto, kto, val, *vpairs):
        if vpairs:
            inj = MultiplicativeSourceCoupling(
                pksrc = (pto, kto),
                cplg       = val,
                pksrc_list = vpairs,
            )
        else:
            inj = ConstantSourceCoupling(
                pksrc = (pto, kto),
                cplg       = val,
            )
        self.injection_insert(inj)
        return

    def injection_insert(self, inj_obj):
        self.all_injections.append(inj_obj)
        for (pkf, pkt), func in list(inj_obj.edges_pkpk_dict.items()):
            pto, kto = pkt
            ptofull = self.port_cplgs.get(pto, declarative.NOARG)
            if ptofull is declarative.NOARG:
                print("Missing Connection:", pto, kto)
            else:
                assert(kto in ptofull)

            self.coupling_matrix_injlist[pkf, pkt].append(inj_obj)
            self.coupling_matrix_inj_funclist[pkf, pkt].append(func)

            #to ensure only single edges for now
            if not (len(self.coupling_matrix_injlist[pkf, pkt]) == 1):
                print("WARNING: multiple redundant edges {0}, {1}".format(pkf, pkt))

            self.field_space.keys_add(pkf)
            self.field_space.keys_add(pkt)
        for pks, func in list(inj_obj.sources_pk_dict.items()):
            psrc , ksrc = pks
            ptofull = self.port_cplgs.get(psrc, declarative.NOARG)
            if ptofull is declarative.NOARG:
                print("Missing Connection:", psrc)
            else:
                assert(ksrc in ptofull)

            self.source_vector_injlist[pks].append(inj_obj)
            self.source_vector_inj_funclist[pks].append(func)

            self.field_space.keys_add(pks)
        return

    def nonlinear_triplet_insert(
            self,
            pkfrom1,
            pkfrom2,
            pkto,
            cplg
    ):
        inj = TripletCoupling(
            pkfrom1 = pkfrom1,
            pkfrom2 = pkfrom2,
            pkto    = pkto,
            cplg    = cplg,
        )
        self.injection_insert(inj)
        return

    def _coherent_sparsity_graph(self):
        #TODO: Comment this complicated, beautiful mess

        subgraph_set = set()
        inputs_set = set()
        outputs_set = set()
        #haven't had their edges swept
        subgraph_set_pending = set()
        subgraph_set_pending2 = set()

        #if a node hits order 0, then it should be in the subgraph set
        node_sourcing_order = dict()
        #if an edge hits order 0, then it should be in seq/req and should influence the sparsity graph
        edge_sourcing_order = dict()
        seq = defaultdict(set)
        req = defaultdict(set)
        self.bonds_trivial = defaultdict(set)

        def bond_trivial(pkfrom, pkto):
            edge_sourcing_order[pkfrom, pkto] = []
            seq[pkfrom].add(pkto)
            req[pkto].add(pkfrom)
            #pkfrom = (pfrom, kkey)
            #pkto = (pto, kkey)
            self.bonds_trivial[pkfrom].add(pkto)

        #Setup all of the bond linkages first
        for pfrom, pto_set in list(self.system.bond_pairs.items()):
            pfrom_orig = pfrom
            for pto in pto_set:
                while True:
                    pfrom_post = self.system.ports_post.get(pfrom, None)
                    if pfrom_post is None:
                        break
                    for kkey in self.port_set_get(pfrom_orig):
                        bond_trivial((pfrom, kkey), (pfrom_post, kkey))
                    pfrom = pfrom_post
                while True:
                    pto_pre = self.system.ports_pre.get(pto, None)
                    if pto_pre is None:
                        break
                    for kkey in self.port_set_get(pfrom_orig):
                        bond_trivial((pto_pre, kkey), (pto, kkey))
                    pto = pto_pre
                for kkey in self.port_set_get(pfrom_orig):
                    bond_trivial((pfrom, kkey), (pto, kkey))

        #begin the linkage algorithm
        source_invlist = defaultdict(list)
        for pkto, injlist in list(self.source_vector_injlist.items()):
            order_list = []
            any_order0 = False
            for inj in injlist:
                NZreqset = inj.sources_NZ_pkset_dict[pkto]
                NZreqset = set(NZreqset)
                order = len(NZreqset)
                if order == 0:
                    any_order0 = True
                    NZreqset = inj.sources_req_pkset_dict[pkto]
                    for onode in NZreqset:
                        outputs_set.add(onode)
                order_list.append(order)
                for NZreq in NZreqset:
                    source_invlist[NZreq].append([len(order_list) - 1, pkto, inj])
            node_sourcing_order[pkto] = order_list
            if any_order0:
                subgraph_set_pending.add(pkto)
                inputs_set.add(pkto)

        edge_invlist = defaultdict(list)
        for (pkfrom, pkto), injlist in list(self.coupling_matrix_injlist.items()):
            any_order0 = False
            order_list = []
            for inj in injlist:
                NZreqset = inj.edges_NZ_pkset_dict[pkfrom, pkto]
                NZreqset = set(NZreqset)
                order = len(NZreqset)
                if order == 0:
                    any_order0 = True
                    NZreqset = inj.edges_req_pkset_dict[pkfrom, pkto]
                    for onode in NZreqset:
                        outputs_set.add(onode)
                order_list.append(order)
                for NZreq in NZreqset:
                    edge_invlist[NZreq].append([len(order_list) - 1, (pkfrom, pkto), inj])
            edge_sourcing_order[pkfrom, pkto] = order_list
            if any_order0:
                seq[pkfrom].add(pkto)
                req[pkto].add(pkfrom)

        done = False
        solution_min_order = 0
        while not done:
            solution_min_order += 1
            while subgraph_set_pending:
                node_pk = subgraph_set_pending.pop()
                subgraph_set.add(node_pk)
                #print("node", node_pk)
                for rnode_pk in seq[node_pk]:
                    #print("node_seq", rnode_pk)
                    if rnode_pk not in subgraph_set:
                        subgraph_set_pending.add(rnode_pk)

                invlist = source_invlist.get(node_pk, None)
                if invlist:
                    for olist_idx, snode_pk, inj in invlist:
                        order = node_sourcing_order[snode_pk][olist_idx]
                        order -= 1
                        node_sourcing_order[snode_pk][olist_idx] = order
                        if order == 0:
                            if snode_pk not in subgraph_set:
                                subgraph_set_pending2.add(snode_pk)
                            #add this node to the inputs
                            inputs_set.add(snode_pk)
                            #now fill out the outputs list for the nodes sourcing this node
                            NZreqset = inj.sources_req_pkset_dict[snode_pk]
                            for onode in NZreqset:
                                outputs_set.add(onode)
                    del source_invlist[node_pk]

                invlist = edge_invlist.get(node_pk, None)
                if invlist:
                    for olist_idx, sedge_pkpk, inj in invlist:
                        order = edge_sourcing_order[sedge_pkpk][olist_idx]
                        order -= 1
                        edge_sourcing_order[sedge_pkpk][olist_idx] = order
                        if order == 0:
                            epkfrom, epkto = sedge_pkpk
                            seq[epkfrom].add(epkto)
                            req[epkto].add(epkfrom)
                            #if the edge source has already been processed, then process this edge now
                            if epkfrom in subgraph_set:
                                if epkto not in subgraph_set:
                                    subgraph_set_pending2.add(epkto)
                            #now fill out the outputs list for the nodes that source this edge
                            NZreqset = inj.edges_req_pkset_dict[sedge_pkpk]
                            for onode in NZreqset:
                                outputs_set.add(onode)
                    del edge_invlist[node_pk]
            subgraph_set_pending = subgraph_set_pending2 - subgraph_set
            if not subgraph_set_pending:
                done = True
            else:
                subgraph_set_pending2.clear()

        seq_perturb = copy.deepcopy(seq)
        req_perturb = copy.deepcopy(req)
        check_seq_req_balance(
            seq_perturb,
            req_perturb,
        )
        purge_reqless_inplace(
            except_set = inputs_set.union(self.AC_in_all),
            seq = seq_perturb,
            req = req_perturb,
        )
        purge_seqless_inplace(
            except_set = outputs_set.union(self.AC_out_all),
            seq = seq_perturb,
            req = req_perturb,
        )

        return declarative.Bunch(
            inputs_set = inputs_set,
            outputs_set = outputs_set,
            order = solution_min_order,
            active = subgraph_set,
            seq_full = seq,
            req_full = req,
            seq_perturb = seq_perturb,
            req_perturb = req_perturb,
        )



