# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import declarative

from .beam_param import (
    ComplexBeamParam
)

from . import standard_attrs as attrs
from . import target
from . import bases

class BeamTargetProjected(target.BeamTargetBase):
    @declarative.dproperty
    def target_original(self, val):
        #reference to other target, should be live and placed
        return val

    #should use mproperty as this uses intermediate knowledge
    @declarative.mproperty(simple_delete = True)
    @bases.invalidate_auto
    def beam_q(self):
        if self.inst_preincarnation is not None:
            return self.inst_preincarnation.beam_q

        q_pre = self.target_original.beam_q
        mat = self.root.matrix_between(
            self.target_original.as_target(),
            self.as_target()
        )
        return q_pre.propagate_matrix(mat)

    _ref_default = ('ref_m', None)
    ref_m = attrs.generate_reference_m()

