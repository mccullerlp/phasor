"""
"""
from __future__ import division, print_function
#from builtins import zip
import numpy as np
import casadi

import declarative
from declarative import bunch
from ...math.complex import Complex

from . import visitors as VISIT

from ...base.autograft import (
    RootElement,
    invalidate_auto,
)

from .base import (
    FitterBase,
)


class FitterRoot(RootElement, FitterBase):

    casadi_sol_obj = None
    sequence_N = 0

    @declarative.mproperty
    def _system_map(self, val = declarative.NOARG):
        if val is declarative.NOARG:
            val = None
        return val

    #maps names to systems
    @declarative.dproperty
    def systems(self):
        prefill = dict()
        if self.inst_preincarnation is not None:
            for sysname, sys in list(self.inst_preincarnation.systems.items()):
                newsys = self._system_map[sysname]
                prefill[sysname] = self._system_map[sysname]
                self._root_register(sysname, newsys)
        return bunch.HookBunch(
            prefill,
            insert_hook = self._root_register
        )

    #maps systems to names
    @declarative.mproperty
    def object_roots_inv(self):
        return dict()

    #maps systems to ooas
    @declarative.mproperty
    def meta_ooa(self):
        return dict()

    @declarative.mproperty
    def _registry_parameters(self):
        return dict()

    def _root_register(self, name, system):
        self.object_roots_inv[system] = name
        self.meta_ooa[name] = system.ctree
        self.invalidate()
        return

    def parameter_add(self, system, fitter_datum):
        pkey = fitter_datum.parameter_key
        if system not in self.object_roots_inv:
            raise RuntimeError("Must register system")
        for okey, odatum in list(self._registry_parameters.items()):
            okeyshort = okey[:len(pkey)]
            pkeyshort = pkey[:len(okey)]
            if okeyshort == pkeyshort and odatum is not fitter_datum:
                raise RuntimeError("Parameter Keys Must be Unique")
        #TODO, minimal checks on the fitter_datum included data
        self.invalidate()
        return

    @declarative.mproperty
    @invalidate_auto
    def fit_systems(self, value = declarative.NOARG, oldvalue = None):
        #allow this to be replaced
        assert(value is declarative.NOARG)

        ctree_meta = declarative.Bunch()
        for sysname in list(self.systems.keys()):
            ctree = bunch.DeepBunch(vpath=True)
            ctree_meta[sysname] = ctree

            prev = self.systems[sysname].ctree.extractidx('previous', dict())
            ctree.update_recursive(prev)

            ctree.hints.symbolic = 'casadi'
            ctree.hints.symbolic_fiducials = self.symbol_fiducials
            ctree.hints.symbolic_fiducial_substitute = self.symbol_fiducial_substitute

        injectors = self.targets_recurse(VISIT.ctree_inject)
        for injector in injectors:
            injector(ctree_meta)

        systems = declarative.Bunch()
        for system, name in list(self.object_roots_inv.items()):
            new_obj = system.regenerate(
                ctree = ctree_meta[name],
            )
            systems[name] = new_obj
        return systems

    @declarative.mproperty
    @invalidate_auto
    def constraints(self):
        constraints = []
        for name, obj in list(self.fit_systems.items()):
            try:
                clist = obj.constraints
            except AttributeError:
                continue
            constraints.extend(clist)
        constraint_expr = []
        constraint_lb = []
        constraint_ub = []
        for expr, lb, ub in constraints:
            constraint_expr.append(expr)
            constraint_lb.append(lb)
            constraint_ub.append(ub)

        constraints_remapped = constraint_expr[:]
        for remapper in self.targets_recurse(VISIT.constraints_remap):
            constraints_remapped = remapper(constraints_remapped)

        ret = declarative.Bunch(
            expr = [],
            lb   = [],
            ub   = [],
        )
        for constraint, lb, ub in zip(
            constraints_remapped,
            constraint_lb,
            constraint_ub
        ):
            ret.expr.append(constraint)
            try:
                shape = constraint.shape
            except AttributeError:
                pass
            else:
                ones = np.ones(shape)
                lb = ones * lb
                ub = ones * ub
            ret.lb.append(lb)
            ret.ub.append(ub)
        #TODO expression remapping on the constraints
        return ret

    @declarative.mproperty
    @invalidate_auto
    def symbol_map(self):
        smappers   = self.targets_recurse(VISIT.symbol_map)
        sym_list   = []
        ival_list  = []
        datum_list = []
        type_list  = []
        lb_list    = []
        ub_list    = []
        transform_list = []
        sbunch_list = []
        for smapper in smappers:
            for sbunch in smapper():
                #TODO check sizes of ival and syms
                if isinstance(sbunch.symbol, Complex):
                    ival_list.append(sbunch.initial_value.real)
                    datum_list.append(sbunch.datum)
                    type_list.append('cplx.real')
                    sym_list.append(sbunch.symbol.real)
                    ub_list.append(sbunch.get('upper_bound', float('inf')).real)
                    lb_list.append(sbunch.get('lower_bound', -float('inf')).real)
                    #not used in the current expressions and wont currently work with the
                    #complex symbols
                    #transform_list.append(sbunch.setdefault('transforms', []))
                    sbunch_list.append(sbunch)

                    ival_list.append(sbunch.initial_value.imag)
                    datum_list.append(sbunch.datum)
                    type_list.append('cplx.imag')
                    sym_list.append(sbunch.symbol.imag)
                    ub_list.append(sbunch.get('upper_boundI', float('inf')))
                    lb_list.append(sbunch.get('lower_boundI', -float('inf')))
                    #not used in the current expressions and wont currently work with the
                    #complex symbols
                    #transform_list.append(sbunch.setdefault('transforms', []))
                    sbunch_list.append(sbunch)
                else:
                    ival_list.append(sbunch.initial_value)
                    datum_list.append(sbunch.datum)
                    sym_list.append(sbunch.symbol)
                    type_list.append('real')
                    ub_list.append(sbunch.get('upper_bound', float('inf')))
                    lb_list.append(sbunch.get('lower_bound', -float('inf')))
                    #not used in the current expressions and wont currently work with the
                    #complex symbols
                    #transform_list.append(sbunch.setdefault('transforms', []))
                    sbunch_list.append(sbunch)
        return declarative.Bunch(
            sym_list       = sym_list,
            ival_list      = ival_list,
            datum_list     = datum_list,
            type_list      = type_list,
            lb_list        = lb_list,
            ub_list        = ub_list,
            sbunch_list    = sbunch_list,
            #transform_list = transform_list,
        )

    @declarative.mproperty
    @invalidate_auto
    def symbol_fiducials(self):
        """
        Generates a list of fiducial parameters to re-substitute for fiducial matrix 
        """
        return dict(zip(self.symbol_map.sym_list, self.symbol_map.ival_list))

    def symbol_fiducial_substitute(self, expr):
        keys = []
        vals = []
        a = casadi.MX.sym('a')
        for k, v in self.symbol_fiducials.items():
            keys.append(k)
            vals.append(v)
        if isinstance(expr, Complex):
            rval = casadi.graph_substitute(
                expr.real,
                keys,
                vals,
            )
            rval = casadi.Function('x', [a], [rval])(0)
            rval = np.asarray(rval).squeeze()
            ival = casadi.graph_substitute(
                expr.imag,
                keys,
                vals,
            )
            ival = casadi.Function('x', [a], [ival])(0)
            ival = np.asarray(ival).squeeze()
            return rval + 1j*ival
        else:
            rval = casadi.graph_substitute(
                expr,
                keys,
                vals,
            )
            rval = casadi.Function('x', [a], [rval])(0)
            rval = np.asarray(rval).squeeze()
            return rval


