"""
"""
from __future__ import (division, print_function)
from builtins import zip
import numpy as np
import operator

from . import visitors as VISIT
import casadi

from declarative import (
    dproperty,
    mproperty,
    NOARG,
)

from declarative.bunch import (
    DeepBunch
)

from ...base.multi_unit_args import (
    SimpleUnitfulGroup,
)

from declarative.bunch import Bunch

from .base import (
    FitterBase,
    casadi_sparsity_ravel,
    casadi_sparsity_unravel,
)
from functools import reduce


class FitterExpression(FitterBase):
    def func_solve_map(self, f):
        return -f

    def func_solve_map_inv(self, out_val):
        return -out_val

    @staticmethod
    def function(self, **kwargs):
        return 1

    @dproperty
    def expression(self, val = NOARG):
        if val is NOARG:
            val = self.function(**self.root.fit_systems)
        return val

    @mproperty
    def symbol_map(self):
        return self.root.symbol_map

    @mproperty
    def constraints(self):
        return self.root.constraints

    @mproperty
    def expression_remapped(self):
        expr = self.expression

        #type I
        tlengths = []
        sbunches_w_trans = []
        for sbunch in self.symbol_map.sbunch_list:
            if sbunch.transforms:
                sbunches_w_trans.append(sbunch)
                tlengths.append(len(sbunch.transforms))

        total_n = reduce(operator.mul, tlengths, 1)
        total_sum = reduce(operator.add, tlengths, 1)

        total_pairs = 0
        for num in tlengths:
            total_pairs += num * (total_sum - num)
        total_pairs = total_pairs / 2
        print("total_number: ", total_n)
        print("total_sum: ", total_sum)
        print("total_pairs: ", total_sum)

        def sbunch_val(sbunch):
            return SimpleUnitfulGroup(
                val = sbunch.symbol,
                ref = sbunch.initial_value,
                units = sbunch.units,
            )

        def t_eval(expr, transform, val):
            val2 = transform(val)
            return casadi.graph_substitute(
                expr,
                [val.val],
                [val2.val],
            )

        expr_combine = []
        type1 = 'double'
        if type1 in ['None', None]:
            pass
        elif type1 == 'all':
            expr_combine = []
            for sbunch in sbunches_w_trans:
                expr_combine2 = []
                for transform in sbunch.transforms:
                    val = sbunch_val(sbunch)
                    for expr in expr_combine:
                        expr2 = t_eval(expr, transform, val)
                        expr_combine2.append(expr2)
                expr_combine = expr_combine2
        elif type1 == 'single':
            for sbunch in sbunches_w_trans:
                for transform in sbunch.transforms:
                    val = sbunch_val(sbunch)
                    expr2 = t_eval(expr, transform, val)
                    expr_combine.append(expr2)
        elif type1 == 'double':
            for idx, sbunch in enumerate(sbunches_w_trans):
                for transform in sbunch.transforms:
                    val = sbunch_val(sbunch)
                    expr2 = t_eval(expr, transform, val)
                    expr_combine.append(expr2)
                    for sbunch2 in enumerate(sbunches_w_trans[idx+1:]):
                        for transform in sbunch.transforms:
                            val = sbunch_val(sbunch)
                            expr3 = t_eval(expr2, transform, val)
                            expr_combine.append(expr3)
            pass
        else:
            raise RuntimeError("Not Recognized")
        expr_combine.append(expr)

        N_expr = len(expr_combine)

        while len(expr_combine) > 1:
            expr_combine2 = [e1 + e2 for e1, e2 in zip(expr_combine[::2], expr_combine[1::2])]
            if len(expr_combine) % 2 == 1:
                expr_combine2.append(expr_combine[-1])
            expr_combine = expr_combine2

        expr = expr_combine[0]

        #type II
        for remapper in self.root.targets_recurse(VISIT.expression_remap):
            expr = remapper(expr)

        N_total = N_expr * expr.shape[0] * expr.shape[1]

        onesA = np.ones(expr.shape[0])
        onesB = np.ones(expr.shape[1])

        print("Final Ntotal T1: ", N_expr)
        print("Final Ntotal T2: ", N_total)
        #form the average
        return Bunch(
            expr = ((onesA * expr) * onesB) / N_total,
            expr_expanded = expr / N_expr,
        )

    print_level = 3
    def minimize_function(self):
        #TODO expression remapping
        print_time = True
        if self.print_level <= 0:
            print_time = False
        sol = casadi.nlpsol(
            self.name_system,
            'ipopt',
            dict(
                x = casadi_sparsity_ravel(self.symbol_map.sym_list),
                f = self.func_solve_map(self.expression_remapped.expr),
                g = casadi_sparsity_ravel(self.constraints.expr),
                p = casadi.vertcat([]),
            ), dict(
                #verbose = True,
                #expand = self.use_SX,
                print_time = print_time,
                ipopt = dict(
                    print_level = self.print_level,
                    #mehrotra_algorithm = "yes",
                    #mu_strategy = 'adaptive',
                    tol = 1e-15,
                    acceptable_tol = 1e-11,
                    acceptable_iter = 300,
                ),
            )
        )
        #print casadi_sparsity_ravel(param_ival_vec).shape
        #print casadi_sparsity_ravel(param_lb).shape
        #print casadi_sparsity_ravel(param_ub).shape
        #print casadi_sparsity_ravel(constraints).shape
        #print casadi_sparsity_ravel(constraints_lb).shape
        #print casadi_sparsity_ravel(constraints_ub).shape
        sols = sol(
            x0  = casadi_sparsity_ravel(self.symbol_map.ival_list),
            lbx = casadi_sparsity_ravel(self.symbol_map.lb_list),
            ubx = casadi_sparsity_ravel(self.symbol_map.ub_list),
            lbg = casadi_sparsity_ravel(self.constraints.lb),
            ubg = casadi_sparsity_ravel(self.constraints.ub),
        )

        sol_vec = casadi_sparsity_unravel(self.symbol_map.sym_list, sols['x'])
        sol_map = dict()
        for datum, sol_val in zip(
                self.symbol_map.datum_list,
                sol_vec,
        ):
            #casadi.DM types screw up matplotlib and others
            #so reconvert to numpy
            #but be careful because casadi DM always uses 2d indices
            idx = len(sol_val.shape) - 1
            while sol_val.shape[idx] == 1 and idx > 0:
                idx -= 1
            if idx == 0:
                sol_val = float(sol_val)
            else:
                sol_val = np.array(sol_val).reshape(sol_val.shape[:idx])
            sol_map[datum] = sol_val

        ooa_meta = Bunch()
        for sysname in list(self.root.systems.keys()):
            ooa_meta[sysname] = DeepBunch()

        injectors = self.root.targets_recurse(VISIT.ooa_reinject)
        for injector in injectors:
            injector(ooa_meta, sol_map)

        systems = Bunch()
        systems_map = dict()
        for obj, sysname in list(self.root.object_roots_inv.items()):
            new_obj = obj.regenerate(
                ooa_params = ooa_meta[sysname],
            )
            systems[sysname] = new_obj
            systems_map[sysname] = new_obj
        return self.root.regenerate(
            _system_map = systems_map
        )
        return Bunch(
            ipopt_sol = sols,
            sol_vec = sols['x'],
            val_map = sol_map,
            systems   = systems,
        )
        return
