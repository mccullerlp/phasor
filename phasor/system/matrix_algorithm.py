# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from builtins import object
from collections import defaultdict
import copy

import declarative

from ..base.ports import PostBondKey

from ..math.key_matrix import (
    KVSpace,
)

from ..matrix.matrix_generic import (
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


def setdict_copy(orig):
    duplicate = defaultdict(set)
    for k, vset in orig.items():
        duplicate[k] = set(vset)
    return duplicate



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

        self.source_vector_injlist             = defaultdict(list)
        self.source_vector_inj_funclist        = defaultdict(list)
        self.coupling_matrix_injlist           = defaultdict(list)
        self.coupling_matrix_inj_funclist      = defaultdict(list)
        self.floating_in_out_func_pair_injlist = []
        self.floating_req_set_injlist          = []
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
        self.source_vector_injlist             = dict(self.source_vector_injlist.items())
        self.source_vector_inj_funclist        = dict(self.source_vector_inj_funclist.items())
        self.coupling_matrix_injlist           = dict(self.coupling_matrix_injlist.items())
        self.coupling_matrix_inj_funclist      = dict(self.coupling_matrix_inj_funclist.items())
        self.floating_in_out_func_pair_injlist = tuple(self.floating_in_out_func_pair_injlist)
        self.floating_req_set_injlist          = tuple(self.floating_req_set_injlist)

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

    def noise_pair_insert(self, pe_1, k1, pe_2, k2, genfunc):
        #print('noise pair: ', pe_1, k2, pe_2, k2)
        ptofull1 = self.port_cplgs.get(pe_1.purge_keys(PostBondKey), declarative.NOARG)
        if (k1 not in ptofull1):
            raise RuntimeError("k1 [{0}] missing for port pe_1 [{1}]".format(k1, pe_1))
        ptofull2 = self.port_cplgs.get(pe_2.purge_keys(PostBondKey), declarative.NOARG)
        if (k2 not in ptofull2):
            raise RuntimeError("k2 [{0}] missing for port pe_2 [{1}]".format(k2, pe_2))

        self.field_space.keys_add((pe_1, k1))
        self.field_space.keys_add((pe_2, k2))
        self.noise_pk_set.add((pe_1, k1))
        self.noise_pk_set.add((pe_2, k2))

        #self.coupling_matrix_print(select_from = (pe_1, k2))
        nmap_inner = self._nmap.setdefault((pe_1, k1), dict())
        nmap_inner.setdefault((pe_2, k2), []).append((pe_1, k1, pe_2, k2, genfunc))
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
        if inj_obj.floating_in_out_func_pairs is not None:
            self.floating_in_out_func_pair_injlist.append(inj_obj)
            for ins, outs, func in inj_obj.floating_in_out_func_pairs:
                for pkt in ins:
                    self.field_space.keys_add(pkt)
                for pkf in ins:
                    self.field_space.keys_add(pkf)

        if inj_obj.floating_req_set is not None:
            self.floating_req_set_injlist.append(inj_obj)
            for pkf in inj_obj.floating_req_set:
                self.field_space.keys_add(pkf)

        for (pkf, pkt), func in inj_obj.edges_pkpk_dict.items():
            pto, kto = pkt
            ptofull = self.port_cplgs.get(pto, declarative.NOARG)
            if ptofull is declarative.NOARG:
                print("Missing Connection:", pto, kto)
            else:
                if (kto not in ptofull):
                    raise RuntimeError(
                        "kto ({0}) missing in ports of {1}".format(kto, pto)
                    )

            self.coupling_matrix_injlist[pkf, pkt].append(inj_obj)
            self.coupling_matrix_inj_funclist[pkf, pkt].append(func)

            #to ensure only single edges for now
            if not (len(self.coupling_matrix_injlist[pkf, pkt]) == 1):
                #TODO make this a warning as many things now use these edges
                #print("WARNING: multiple redundant edges {0}, {1}".format(pkf, pkt))
                pass

            self.field_space.keys_add(pkf)
            self.field_space.keys_add(pkt)
        for pks, func in inj_obj.sources_pk_dict.items():
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

        #holds nodes used for in-out-func couplings which will be purged after graph simplification
        virtual_nodes = set()

        #if a node hits order 0, then it should be in the subgraph set
        node_sourcing_order = dict()
        #if an edge hits order 0, then it should be in seq/req and should influence the sparsity graph
        edge_sourcing_order = dict()
        seq = defaultdict(set)
        req = defaultdict(set)
        self.bonds_trivial = defaultdict(dict)

        def bond_trivial(pkfrom, pkto, val):
            edge_sourcing_order[pkfrom, pkto] = []
            seq[pkfrom].add(pkto)
            req[pkto].add(pkfrom)
            #pkfrom = (pfrom, kkey)
            #pkto = (pto, kkey)
            self.bonds_trivial[pkfrom][pkto] = val

        #Setup all of the bond linkages first
        for pfrom, pto_dict in self.system.bond_pairs.items():
            pfrom_orig = pfrom
            for pto, val in pto_dict.items():
                while True:
                    pfrom_post = self.system.ports_post.get(pfrom, None)
                    if pfrom_post is None:
                        break
                    for kkey in self.port_set_get(pfrom_orig):
                        bond_trivial((pfrom, kkey), (pfrom_post, kkey), val)
                    pfrom = pfrom_post
                while True:
                    pto_pre = self.system.ports_pre.get(pto, None)
                    if pto_pre is None:
                        break
                    for kkey in self.port_set_get(pfrom_orig):
                        bond_trivial((pto_pre, kkey), (pto, kkey), val)
                    pto = pto_pre
                for kkey in self.port_set_get(pfrom_orig):
                    bond_trivial((pfrom, kkey), (pto, kkey), val)

        #now all of the forced NZ requirements:
        for inj in self.floating_req_set_injlist:
            outputs_set.update(inj.floating_req_set)

        #now couple to all of the in-out pairs via virtual nodes for the subgraph detection
        for idx_inj, inj in enumerate(self.floating_in_out_func_pair_injlist):
            for idx, (ins, outs, func) in enumerate(inj.floating_in_out_func_pairs):
                #ps_In wish these were more abstract, but the deepcopy later
                #can mess with using the inj object itself. Could use str(inj) if debugging
                vnode = (idx_inj, idx)
                virtual_nodes.add(vnode)
                for pkt in ins:
                    seq[pkt].add(vnode)
                    req[vnode].add(pkt)
                for pkf in outs:
                    seq[vnode].add(pkf)
                    req[pkf].add(vnode)

        #begin the linkage algorithm
        source_invlist = defaultdict(list)
        for pkto, injlist in self.source_vector_injlist.items():
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
        for (pkfrom, pkto), injlist in self.coupling_matrix_injlist.items():
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

        seq_perturb = setdict_copy(seq)
        req_perturb = setdict_copy(req)
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

        #now purge all virtual nodes
        #from both seq req sets
        def remove_vnode(vnode, req, seq):
            for pkt in seq[vnode]:
                req[pkt].remove(vnode)
            for pkf in req[vnode]:
                seq[pkf].remove(vnode)
            del seq[vnode]
            del req[vnode]
        for vnode in virtual_nodes:
            remove_vnode(
                vnode,
                req,
                seq
            )
            remove_vnode(
                vnode,
                req_perturb,
                seq_perturb
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



