# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

#from declarative import (
#    declarative.dproperty,
#)


from .beam_param import ComplexBeamParam

from .utils import (
    TargetLeft,
    TargetRight,
    TargetIdx,
    #matrix_space,
    matrix_focus,
    eigen_q,
    np_check_sorted,
    #matrix_array_invert,
    #targets_map_fill,
    str_m,
)

from .measurements import (
    substrate_environment,
)

from .beam import NoP



class WaistLocation(NoP):

    ZR_minimum = None
    ZR_maximum = None
    W0_minimum = None
    W0_maximum = None

    def q_constraints(self, z, q, from_target):
        constraints = [
            (q.Z, 0, 0),
        ]
        if self.ZR_maximum is not None or self.ZR_minimum is not None:
            constraints.append((q.ZR, self.ZR_minimum, self.ZR_maximum))
        if self.W0_maximum is not None or self.W0_minimum is not None:
            constraints.append((q.W0, self.W0_minimum, self.W0_maximum))
        return constraints

    def system_data_targets(self, typename):
        dmap = {}
        if typename == "q_constraints":
            dmap[TargetIdx()] = self.q_constraints
        return dmap


class BeamApertureConstraint(NoP):
    W_minimum = None
    W_maximum = None

    def q_constraints(self, z, q, from_target):
        constraints = []
        if self.W_minimum is not None or self.W_maximum is not None:
            constraints.append((q.W, self.W_minimum, self.ZR_maximum))
        return constraints

    def system_data_targets(self, typename):
        dmap = {}
        if typename == "q_constraints":
            dmap[TargetIdx()] = self.q_constraints
        return dmap

