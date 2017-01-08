"""
"""
from __future__ import division, print_function
from . import visitors as VISIT
import casadi

from declarative import (
    mproperty,
    group_dproperty,
)

from ...base.multi_unit_args import (
    generate_refval_attribute,
)

from declarative.bunch import Bunch

from .base import (
    FitterBase,
)


class FitterSym(FitterBase):

    @mproperty
    def _parameter_symbols(self):
        if self.inst_preincarnation is not None:
            return dict(self.inst_preincarnation._parameter_symbols)
        else:
            return dict()

    @mproperty
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
            system = pvalue.root
            sysname = self.root.object_roots_inv[system]
            self.root.parameter_add(system, fdatum)
            self._parameter_sysnames[fdatum] = sysname
            self._parameter_symbols[fdatum] = casadi.MX.sym(fdatum.name)
        return

    def targets_list(self, typename):
        #TODO, opt out of these if not carrying parameters
        if typename == VISIT.ooa_inject:
            return self.ooa_inject
        elif typename == VISIT.symbol_map:
            return self.fitter_symbol_map
        elif typename == VISIT.ooa_reinject:
            return self.ooa_reinject
        elif typename == VISIT.constraints:
            return self.constraints
        else:
            return super(FitterSym, self).targets_list(typename)

    def ooa_inject(self, meta_ooa):
        for datum, symbol in list(self._parameter_symbols.items()):
            sysname = self._parameter_sysnames[datum]
            ival = datum.initial(self.root.meta_ooa[sysname])
            datum.inject(meta_ooa[sysname], symbol, ival)
        return

    def ooa_reinject(self, meta_ooa, param_map):
        for datum, sysname in list(self._parameter_sysnames.items()):
            nval = param_map[datum]
            datum.reinject(meta_ooa[sysname], nval)
        return

    def transforms(self, datum):
        return []

    def fitter_symbol_map(self):
        symbol_map = []
        for datum, symbol in list(self._parameter_symbols.items()):
            sysname = self._parameter_sysnames[datum]
            ival = datum.initial(self.root.meta_ooa[sysname])
            symbol_map.append(
                Bunch(
                    datum         = datum,
                    symbol        = symbol,
                    initial_value = ival,
                    upper_bound   = float('inf'),
                    lower_bound   = -float('inf'),
                    transforms    = self.transforms(datum),
                    units         = datum.units,
                )
            )
        return symbol_map

class FitterSymJitterPlacement(FitterSym):

    @group_dproperty
    def shift_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['shift', ],
            pname = 'shift',
            preferred_attr = 'shift_preferred',
            default_attr = '_shift_default',
            prototypes = ['full'],
        )

    def transforms(self, datum):
        return [
            lambda v : v + self.shift_m,
            lambda v : v - self.shift_m,
        ]

class FitterSymJitterRelative(FitterSym):

    #TODO store inside of ooa
    percent_adjust = 0

    def transforms(self, datum):
        return [
            lambda v : v * (1 + self.percent_adjust / 100),
            lambda v : v / (1 + self.percent_adjust / 100),
        ]


