# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
#from builtins import object
import numpy as np
import copy
from collections import defaultdict
import declarative

from ..utilities.print import pprint

from ..base import (
    DictKey,
)

from ..math.key_matrix import (
    KVSpace,
    KeyVector,
    KeyMatrix,
)

from .graph_algorithm import (
    push_solve_inplace,
    inverse_solve_inplace,
)


class SystemSolver(object):
    field_space_proto = KVSpace('ports', dtype=np.complex128)
    #TODO, I loath how the iterative state is stored for this object, clean it up...

    #TODO make this take ooa_params
    def __init__(
        self,
        system,
        ports_algorithm,
        matrix_algorithm,
        max_N       = 100,
        warning_N   = 20,
        max_epsilon = 1e-4,
        **kwargs
    ):
        super(SystemSolver, self).__init__(**kwargs)
        self.system = system
        self.ports_algorithm   = ports_algorithm
        self.matrix_algorithm  = matrix_algorithm

        #each index stores a dict, indexed by the output set
        self.driven_solution_bunches = [
            dict(
                perturbative = declarative.Bunch(
                    solution    = dict(),
                    source      = dict(),
                    delta_v     = float('inf'),
                    AC_solution = None,
                    AC_seq      = None,
                    AC_req      = None,
                )
            )
        ]
        self.coupling_solution_bunches = defaultdict(dict)

        self.drive_pk_sets      = copy.deepcopy(ports_algorithm.drive_pk_sets)
        self.readout_pk_sets    = copy.deepcopy(ports_algorithm.readout_pk_sets)

        #build the special sets
        #TODO these special sets should be protected during the ports_algorithm
        csgb = self.matrix_algorithm.coherent_subgraph_bunch
        assert('perturbative' not in self.drive_pk_sets)
        assert('perturbative' not in self.readout_pk_sets)
        self.drive_pk_sets['perturbative']   = csgb.inputs_set
        self.readout_pk_sets['perturbative'] = csgb.outputs_set

        self.drive_pk_sets['noise'] = set(self.matrix_algorithm.noise_pk_set)
        #pprint(("NSET: ", self.matrix_algorithm.noise_pk_set))

        all_set = set(csgb.seq_full.keys())
        assert('all' not in self.drive_pk_sets)
        assert('all' not in self.readout_pk_sets)
        self.drive_pk_sets['all'] = all_set
        self.readout_pk_sets['all'] = all_set
        #TODO
        #self.drive_pk_sets['noise'].update(csgb.inputs_set)

        self.max_N       = max_N
        self.warning_N   = warning_N
        self.max_epsilon = max_epsilon

        self._setup_views()
        return

    @declarative.mproperty
    def views(self):
        return declarative.DeepBunch(vpath = False)

    def _setup_views(self):
        views_insert = []
        for el in self.system.elements:
            try:
                sarv = el.system_associated_readout_view
            except AttributeError:
                pass
            else:
                view_obj = sarv(self)
                views_insert.append(
                    (el.fully_resolved_name_tuple, view_obj)
                )
        #sort this so that shorter name_tups are first
        views_insert.sort()
        views = declarative.DeepBunch()
        for name_tup, view_obj in views_insert:
            subview = views
            for idx, name in enumerate(name_tup[:-1]):
                if not isinstance(subview, declarative.DeepBunch):
                    #this can't really be called on the first one
                    subview.subview_insert(name_tup[idx - 1:], view_obj)
                    break
                subview = subview[name]
            else:
                if not isinstance(subview, declarative.DeepBunch):
                    subview.subview_insert(name_tup[-1:], view_obj)
                else:
                    subview[name_tup[-1]] = view_obj
        self.views.update_recursive(views.sled)
        return

    def _source_vector_generate(
        self,
        inputs_iter,
        solution_vector_prev,
        solution_bunch_prev,
    ):
        malgo                = self.matrix_algorithm
        field_space          = self.matrix_algorithm.field_space

        source_vector        = KeyVector(field_space)
        for pkto in inputs_iter:
            factor_func_list = malgo.source_vector_inj_funclist[pkto]
            if not factor_func_list:
                continue
            factor_func = factor_func_list[0]
            val = factor_func(solution_vector_prev, solution_bunch_prev)
            for factor_func in factor_func_list[1:]:
                val = val + factor_func(solution_vector_prev, solution_bunch_prev)
            source_vector[pkto] = val
        return source_vector

    def noise_map(self):
        return self.matrix_algorithm.coupling_noise_map

    def _edge_matrix_generate(
        self,
        seq,
        req,
        solution_vector_prev,
        solution_bunch_prev,
    ):
        malgo                = self.matrix_algorithm
        field_space          = self.matrix_algorithm.field_space
        coupling_matrix      = KeyMatrix(field_space, field_space)
        #generate only the edges needed
        for pkfrom, seq_set in list(seq.items()):
            for pkto in seq_set:
                try:
                    factor_func_list = malgo.coupling_matrix_inj_funclist[pkfrom, pkto]
                except KeyError:
                    #if it's not in the injection funclist then it must be a bond
                    #TODO: assert that bond are not stacked with the funclist
                    pfrom, kfrom = pkfrom
                    pto, kto     = pkto
                    assert(kto == kfrom)
                    #pkey = kto
                    #assert(pkey in malgo.port_set_get(pto))
                    #assert(pto in self.system.bond_pairs[pfrom])
                    assert(pkto in malgo.bonds_trivial[pkfrom])
                    coupling_matrix[pkfrom, pkto] = 1
                else:
                    assert(pkto not in malgo.bonds_trivial[pkfrom])
                    #pfrom, kfrom = pkfrom
                    #pto, kto     = pkto
                    #assert(pto not in self.system.bond_pairs[pfrom])
                    if not factor_func_list:
                        coupling_matrix[pkfrom, pkto] = 0
                        continue
                    factor_func = factor_func_list[0]
                    val = factor_func(
                        solution_vector_prev,
                        solution_bunch_prev
                    )
                    for factor_func in factor_func_list[1:]:
                        val = val + factor_func(
                            solution_vector_prev,
                            solution_bunch_prev
                        )
                        #print('multi-edge: ', pkto, factor_func)
                    coupling_matrix[pkfrom, pkto] = val
        return coupling_matrix

    def _perturbation_iterate(self, N):
        solution_bunch_prev = self.driven_solution_get(
            readout_set = 'perturbative',
            N = N - 1
        )
        solution_vector_prev = solution_bunch_prev.solution
        #print("MAP: ", N - 1)
        #try:
        #    pprint(solution_bunch_prev.solution._data_map)
        #except Exception as e:
        #    print(e)
        field_space = self.matrix_algorithm.field_space
        malgo = self.matrix_algorithm

        csgb = malgo.coherent_subgraph_bunch
        #TODO, fix the perturb version
        if (not self.matrix_algorithm.AC_out_all) and (not self.matrix_algorithm.AC_in_all):
            seq = copy.deepcopy(csgb.seq_perturb)
            req = copy.deepcopy(csgb.req_perturb)
        else:
            seq = copy.deepcopy(csgb.seq_full)
            req = copy.deepcopy(csgb.req_full)

        coupling_matrix = self._edge_matrix_generate(
            seq = seq,
            req = req,
            solution_vector_prev = solution_vector_prev,
            solution_bunch_prev  = solution_bunch_prev,
        )
        source_vector = self._source_vector_generate(
            inputs_iter          = csgb.inputs_set,
            solution_vector_prev = solution_vector_prev,
            solution_bunch_prev  = solution_bunch_prev,
        )

        outputs_set = csgb.outputs_set

        #TODO purging should no longer be necessary
        #print("PERTURBER RUNNING: ")
        solution_bunch = push_solve_inplace(
            seq           = seq,
            req           = req,
            outputs_set   = outputs_set.union(self.matrix_algorithm.AC_out_all),
            inputs_map    = source_vector,
            inputs_AC_set = self.matrix_algorithm.AC_in_all,
            edge_map      = dict(coupling_matrix.items()),
            purge_in      = True,
            purge_out     = True,
        )
        solution_dict = solution_bunch.outputs_map
        solution_vector_kv = KeyVector(field_space)
        #TODO make be able to avoid this copy
        for node, val in solution_dict.items():
            solution_vector_kv[node] = val

        delta_v, k_worst = self.delta_v_compute(
            solution_vector_prev,
            solution_vector_kv,
        )
        solution_bunch = declarative.Bunch(
            source      = source_vector,
            solution    = solution_vector_kv,
            delta_v     = delta_v,
            k_worst     = k_worst,
            AC_solution = solution_bunch.AC_edge_map,
            AC_seq      = solution_bunch.AC_seq,
            AC_req      = solution_bunch.AC_req,
        )
        if self.system.ooa_params.debug.solver.get('delta_V_max', False):
            print(
                "DELTA V MAX: ",
                solution_bunch.delta_v,
                " AT ORDER: ",
                len(self.driven_solution_bunches)
            )
        self.driven_solution_bunches[N]['perturbative'] = solution_bunch
        return solution_bunch

    def delta_v_compute(
            self,
            solution_vector_prev,
            solution_vector
    ):
        delta_v_rel_max = 0
        k_worst = None
        for k, v in solution_vector.items():
            v_prev = solution_vector_prev.get(k, 0)
            v = np.asarray(v)
            v_prev = np.asarray(v_prev)
            av_maxel = np.maximum(abs(v), abs(v_prev))
            avdiff = abs(v - v_prev)
            v_nz = (av_maxel != 0)
            minel = avdiff[v_nz] / av_maxel[v_nz]
            if len(minel) > 0:
                #minel[av_maxel < 1e-18] = 0
                local_max = np.max(minel)
                #print("DELTA V: ", k, local_max, minel, v, v_prev)
                delta_v_rel_max = max(delta_v_rel_max, local_max)
                if delta_v_rel_max == local_max:
                    k_worst = k, abs(v)
        return delta_v_rel_max, k_worst

    def driven_solution_get(self, readout_set = 'all', N=None):
        if N is None:
            if len(self.driven_solution_bunches) == 1:
                #solve without order, to use heuristics for finishing
                self.solve()
            N = len(self.driven_solution_bunches) - 1
        elif N < 0:
            N = len(self.driven_solution_bunches) + N

        if N < len(self.driven_solution_bunches):
            bdict = self.driven_solution_bunches[N]
        else:
            self.solve(order = N)
            bdict = self.driven_solution_bunches[N]

        collection_key = readout_set
        set_dict = bdict.get(collection_key, None)
        if set_dict is not None:
            #print(set_dict)
            return set_dict

        #special case the standard iteration
        if readout_set == 'perturbative':
            sbunch = self._perturbation_iterate(N)
            return sbunch

        outputs_set = self.readout_pk_sets[readout_set]

        #otherwise the solution must be generated, this proceeds much like the _perturbation_iterate,
        #but that one is special-cased for speed
        solution_bunch_prev = self.driven_solution_get(
            readout_set = 'perturbative',
            N = N - 1
        )
        solution_vector_prev = solution_bunch_prev.solution

        field_space = self.matrix_algorithm.field_space
        malgo = self.matrix_algorithm

        csgb = malgo.coherent_subgraph_bunch
        #use the full edge list
        seq = copy.deepcopy(csgb.seq_full)
        req = copy.deepcopy(csgb.req_full)

        coupling_matrix = self._edge_matrix_generate(
            seq                  = seq,
            req                  = req,
            solution_vector_prev = solution_vector_prev,
            solution_bunch_prev  = solution_bunch_prev,
        )
        source_vector = self._source_vector_generate(
            inputs_iter          = csgb.inputs_set,
            solution_vector_prev = solution_vector_prev,
            solution_bunch_prev  = solution_bunch_prev,
        )

        #TODO purging should no longer be necessary
        #print("PROPAGAGOR RUNNING: ", readout_set)
        solution_bunch = push_solve_inplace(
            seq           = seq,
            req           = req,
            outputs_set   = outputs_set,
            inputs_map    = source_vector,
            edge_map      = dict(coupling_matrix.items()),
            purge_in      = True,
            purge_out     = True,
        )
        solution_dict = solution_bunch.outputs_map
        solution_vector_kv = KeyVector(field_space)
        #TODO may be able to avoid this copy
        for node in outputs_set:
            node_val = solution_dict.get(node, 0)
            if np.any(node_val != 0):
                node_val = np.asarray(node_val)
                #now adjust so that it cannot be modified. Can prevent some
                #nasty bugs arising from the mutability of numpy arrays (which is nice usually for speed)
                node_val.flags.writeable = False
                solution_vector_kv[node] = node_val

        solution_bunch = declarative.Bunch(
            source   = source_vector,
            solution = solution_vector_kv,
        )
        bdict[readout_set] = solution_bunch
        return solution_bunch

    def coupling_solution_get(self, drive_set, readout_set, N=-1):
        if N is None:
            if len(self.driven_solution_bunches) == 1:
                #solve without order, to use heuristics for finishing
                self.solve()
            N = len(self.driven_solution_bunches) - 1
        elif N <= 0:
            N = len(self.driven_solution_bunches) + N

        bdict = self.coupling_solution_bunches[N]

        collection_key = (drive_set, readout_set)
        set_dict = bdict.get(collection_key, None)
        if set_dict is not None:
            return set_dict

        inputs_set = self.drive_pk_sets[drive_set]
        outputs_set = self.readout_pk_sets[readout_set]
        #print("INSET", drive_set, inputs_set)
        #print("OUTSET", readout_set, outputs_set)

        #otherwise the solution must be generated, this proceeds much like the _perturbation_iterate,
        #but that one is special-cased for speed
        solution_bunch_prev = self.driven_solution_get(
            readout_set = 'perturbative',
            N = N - 1
        )
        solution_vector_prev = solution_bunch_prev.solution
        #field_space = self.matrix_algorithm.field_space
        malgo = self.matrix_algorithm

        csgb = malgo.coherent_subgraph_bunch
        #use the full edge list
        seq = copy.deepcopy(csgb.seq_full)
        req = copy.deepcopy(csgb.req_full)

        coupling_matrix = self._edge_matrix_generate(
            seq                  = seq,
            req                  = req,
            solution_vector_prev = solution_vector_prev,
            solution_bunch_prev  = solution_bunch_prev,
        )

        #TODO purging should no longer be necessary
        #print("SOLVER RUNNING: ", drive_set, readout_set)
        inverse_bunch = inverse_solve_inplace(
            seq           = seq,
            req           = req,
            inputs_set    = inputs_set,
            outputs_set   = outputs_set,
            edge_map      = dict(coupling_matrix.items()),
            purge_in      = True,
            purge_out     = True,
        )

        solution_bunch = declarative.Bunch(
            inputs_set          = inputs_set,
            outputs_set         = outputs_set,
            seq                 = inverse_bunch.seq,
            req                 = inverse_bunch.req,
            coupling_matrix_inv = inverse_bunch.edge_map,
            coupling_matrix     = coupling_matrix,
        )
        bdict[collection_key] = solution_bunch
        return solution_bunch

    def solve(self, order = None):
        if order is None:
            to_order = self.max_N
        else:
            to_order = order

        while len(self.driven_solution_bunches) <= to_order:
            self.driven_solution_bunches.append(dict())
            sbunch = self._perturbation_iterate(N = len(self.driven_solution_bunches) - 1)
            if order is None and sbunch.delta_v < self.max_epsilon:
                break
            if order is None and len(self.driven_solution_bunches) > self.warning_N:
                print(
                    "WARNING: DELTA V MAX: ",
                    sbunch.delta_v,
                    " AT ORDER: ",
                    len(self.driven_solution_bunches),
                    " Worst k: ",
                    sbunch.k_worst,
                )

        if len(self.driven_solution_bunches) == to_order:
            #append one last dictionary for this set of solutions to use the previous
            self.driven_solution_bunches.append(dict())
        return

    def solution_vector_print(
            self,
            select_to   = DictKey(),
            readout_set = 'all',
            N           =None,
    ):
        solution_bunch = self.driven_solution_get(
            readout_set = readout_set,
            N = N,
        )
        for key, value in solution_bunch.solution:
            dk = key[0] | key[1]
            if dk.contains(select_to):
                print(("[{0: <50}]={1}".format(str(key), str(value))))

    def source_vector_print(
            self,
            select_to = DictKey(),
            N = -2,
    ):
        solution_bunch = self.driven_solution_get(
            readout_set = 'perturbative',
            N = N,
        )
        for key, value in solution_bunch.source:
            dk = key[0] | key[1]
            if dk.contains(select_to):
                print(("[{0: <50}]={1}".format(key, value)))

    def coupling_matrix_print(
            self,
            select_from = DictKey(),
            select_to   = DictKey(),
            drive_set   = 'all',
            readout_set = 'all',
            N           = -1,
    ):
        solution_bunch = self.coupling_solution_get(
            drive_set   = drive_set,
            readout_set = readout_set,
            N           = N,
        )
        vals = []
        for (key_from, key_to), value in list(solution_bunch.coupling_matrix.items()):
            dk_from = key_from[0] | key_from[1]
            dk_to = key_to[0] | key_to[1]
            if dk_from.contains(select_from) and dk_to.contains(select_to):
                vals.append(("[{0: <50},{1: <60}]={2}".format(
                    str(key_from),
                    str(key_to),
                    str(value),
                )))
        vals.sort()
        for val in vals:
            print(val)

    def coupling_matrix_get(
            self,
            select_from = DictKey(),
            select_to   = DictKey(),
            drive_set   = 'all',
            readout_set = 'all',
            N           = -1,
    ):
        solution_bunch = self.coupling_solution_get(
            drive_set   = drive_set,
            readout_set = readout_set,
            N           = N,
        )
        return solution_bunch.coupling_matrix

    def coupling_matrix_inv_print(
            self,
            select_from = DictKey(),
            select_to   = DictKey(),
            drive_set   = 'all',
            readout_set = 'all',
            N           = -1,
    ):
        solution_bunch = self.coupling_solution_get(
            drive_set   = drive_set,
            readout_set = readout_set,
            N           = N,
        )
        rt_inv = solution_bunch.coupling_matrix_inv
        vals = []
        for (key_from, key_to), value in list(rt_inv.items()):
            dk_from = key_from[0] | key_from[1]
            dk_to = key_to[0] | key_to[1]
            if dk_from.contains(select_from) and dk_to.contains(select_to):
                vals.append(("[{0: <50},{1: <60}]={2}".format(
                    str(key_from),
                    str(key_to),
                    str(value),
                )))
        vals.sort()
        for val in vals:
            print(val)


