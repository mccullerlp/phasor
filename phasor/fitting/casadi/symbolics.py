# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import casadi
import declarative

from . import visitors as VISIT
from ...base.multi_unit_args import (
    arbunit_refval_attribute,
)

from .base import (
    FitterBase,
)

from ...math.complex import Complex

#from ...base import units


class FitterSym(FitterBase):

    @declarative.mproperty
    def _parameter_symbols(self):
        if self.inst_preincarnation is not None:
            return dict(self.inst_preincarnation._parameter_symbols)
        else:
            return dict()

    @declarative.mproperty
    def _parameter_sysnames(self):
        if self.inst_preincarnation is not None:
            return dict(self.inst_preincarnation._parameter_sysnames)
        else:
            return dict()

    def parameter(
            self,
            pvalue,
    ):
        for fdatum in pvalue.fitter_data:
            usecomplex = fdatum.get('usecomplex', False)
            system = pvalue.root
            sysname = self.root.object_roots_inv[system]
            self.root.parameter_add(system, fdatum)
            self._parameter_sysnames[fdatum] = sysname
            if not usecomplex:
                self._parameter_symbols[fdatum] = casadi.MX.sym(fdatum.name)
            else:
                self._parameter_symbols[fdatum] = Complex(
                    casadi.MX.sym(fdatum.name + '.real'),
                    casadi.MX.sym(fdatum.name + '.imag'),
                )
        return

    def targets_list(self, typename):
        #TODO, opt out of these if not carrying parameters
        if typename == VISIT.ctree_inject:
            return self.ctree_inject
        elif typename == VISIT.symbol_map:
            return self.fitter_symbol_map
        elif typename == VISIT.ctree_reinject:
            return self.ctree_reinject
        elif typename == VISIT.constraints:
            return self.constraints
        else:
            return super(FitterSym, self).targets_list(typename)

    def ctree_inject(self, meta_ooa):
        for datum, symbol in list(self._parameter_symbols.items()):
            sysname = self._parameter_sysnames[datum]
            ival = datum.initial(self.root.meta_ooa[sysname])
            datum.inject(meta_ooa[sysname], symbol, ival)
        return

    def ctree_reinject(self, meta_ooa, param_map):
        for datum, sysname in list(self._parameter_sysnames.items()):
            nval = param_map[datum]
            datum.reinject(meta_ooa[sysname], nval)
        return

    def transforms(self, datum):
        return []

    def fitter_symbol_map(self):
        symbol_map = []
        for datum, symbol in list(self._parameter_symbols.items()):
            #usecomplex = datum.get('usecomplex', False)
            sysname = self._parameter_sysnames[datum]
            ival = datum.initial(self.root.meta_ooa[sysname])
            #TODO: document or describe what this bunch type should hold
            sbunch = declarative.Bunch(
                datum         = datum,
                symbol        = symbol,
                initial_value = ival,
                upper_bound   = datum.get('upper_bound', float('inf')),
                lower_bound   = datum.get('lower_bound', -float('inf')),
                transforms    = self.transforms(datum),
                units         = datum.units,
            )
            if isinstance(symbol, Complex):
                sbunch.upper_boundI = datum.get('upper_boundI', float('inf')),
                sbunch.lower_boundI = datum.get('lower_boundI', -float('inf')),
            symbol_map.append(sbunch)
        return symbol_map


class FitterSymJitterPlacement(FitterSym):

    @declarative.dproperty_adv
    def shift(desc):
        return arbunit_refval_attribute(
            desc,
            prototypes = ['full'],
        )

    def transforms(self, datum):
        return [
            lambda v : v + self.shift,
            lambda v : v - self.shift,
        ]

class FitterSymJitterRelative(FitterSym):

    #TODO store inside of ooa
    percent_adjust = 0

    def transforms(self, datum):
        return [
            lambda v : v * (1 + self.percent_adjust / 100),
            lambda v : v / (1 + self.percent_adjust / 100),
        ]


