# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from ..utilities.future_from_2 import str
import numpy as np
import declarative

#import phasor.numerics.dispatched as dmath
#import sympy

from .utils import (
    TargetLeft,
    TargetRight,
    TargetIdx,
    str_m,
)

from .substrates import (
    substrate_environment,
)

from . import standard_attrs as attrs
from . import bases


class Space(bases.MatrixAtsBase, declarative.OverridableObject):
    substrate = substrate_environment

    L_m = attrs.generate_L_m()

    _loc_default = ('loc_m', None)
    loc_m = attrs.generate_loc_m()

    annotate_extra = None

    @declarative.mproperty
    def width_m(self):
        return self.L_m.val

    @declarative.mproperty
    def matrix(self):
        n = self.substrate.n(self)
        return np.matrix([
            [1, self.L_m.val / n],
            [0, 1],
        ])

    @declarative.mproperty
    def matrix_inv(self):
        n = self.substrate.n(self)
        return np.matrix([
            [1, -self.L_m.val / n],
            [0, 1],
        ])

    def matrix_target_to_z_single(self, tidx1, z_m, invert = False):
        if z_m < 0 or z_m > self.L_m.val:
            print(self.__class__)
            print(z_m, self.L_m.val)
            raise RuntimeError("Outside of size of space")

        #invert if viewing from the right
        if tidx1 == TargetRight:
            invert = not invert

        n = self.substrate.n(self)
        if not invert:
            return np.matrix([
                [1, z_m / n],
                [0, 1],
            ])
        else:
            return np.matrix([
                [1, (z_m - self.L_m.val) / n],
                [0, 1],
            ])

    def matrix_target_to_z(self, tidx1, z_m, fill, invert = False):
        return self.matrix_target_to_z_linsorted(self, z_m, fill, invert = invert)

    def matrix_target_to_z_linsorted(self, tidx1, z_m, fill, invert = False):
        if not all(z_m == 0):
            raise RuntimeError("Only located at 0")

        #invert if viewing from the right
        if tidx1 == TargetRight:
            invert = not invert

        n = self.root.env_substrate.n(self)
        fill[0, 0, ...] = 1
        fill[1, 1, ...] = 1
        fill[1, 0, ...] = 0
        if not invert:
            fill[0, 1, ...] = z_m / n
        else:
            fill[0, 1, ...] = (z_m - self.L_m.val) / n
        return

    def target_pos(self, tidx1):
        if tidx1 == TargetLeft:
            return 0
        if tidx1 == TargetRight:
            return self.L_m.val
        raise RuntimeError(tidx1)
        return

    min_spacing = 0*2 * .0254
    @declarative.mproperty
    def constraints(self):
        return [(self.L_m.val, self.min_spacing, +float('inf'))]

    def waist_description(self, z, q, from_target):
        has_waist = False
        n = self.substrate.n(self)
        #print("N: ", n)
        qZ = q.Z * n
        zw = z - qZ
        if from_target == TargetLeft:
            if -qZ > -1e-16 and -qZ < self.L_m.val:
                has_waist = True
        elif from_target == TargetRight:
            if qZ > -1e-16 and qZ < self.L_m.val:
                has_waist = True
        if has_waist:
            return declarative.Bunch(
                z = zw,
                ZR = q.ZR,
                str = u'waist ZR = {0}, W = {1}'.format(str_m(q.ZR, 2), str_m(q.W0, 2)),
            )
        return None

    def extra_description(self, z, q, from_target):
        return self.annotate_extra(
            self,
            z = z,
            q = q,
            target = from_target,
        )

    def system_data_targets(self, typename):
        dmap = {}
        if typename == 'waist_description':
            dmap[TargetIdx()] = self.waist_description
        elif typename == 'extra_description':
            if self.annotate_extra:
                dmap[TargetIdx()] = self.extra_description
        return dmap


