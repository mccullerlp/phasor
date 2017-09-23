# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np
import declarative


from .utils import (
    TargetIdx,
    TargetLeft,
    TargetRight,
)

from . import substrates
from . import standard_attrs as attrs
from . import bases


class MountBase(
        bases.MatrixAtsBase,
        declarative.OverridableObject
):
    _target_type = None

    @declarative.mproperty
    def subsystem(self, ssys = declarative.NOARG):
        if ssys is declarative.NOARG:
            raise RuntimeError("Must Specify")
        return ssys

    @declarative.mproperty
    def width_m(self):
        return self.subsystem.width_m

    def mount_desc_dfunct(self, z, q, from_target):
        return declarative.Bunch(
            q = q,
            gouy_phasor = q.gouy_phasor,
            z = z,
            type = self._target_type,
            str = '{0} gouy = {1:.1f}deg'.format(self._target_type, np.angle(q.gouy_phasor, deg = True)),
        )

    def system_data_targets(self, typename):
        dmap = {}
        if typename == 'mount_description':
            dmap[TargetIdx()] = self.mount_desc_dfunct
        for tidx, dfunc in list(self.subsystem.system_data_targets(typename).items()):
            dmap[TargetIdx(tidx + (1,))] = dfunc
        return dmap

    def target_obj(self, tidx1):
        tidx1_outer = tidx1[-1]
        tidx1_inner = tidx1[:-1]
        if tidx1_outer == 0:
            assert(tidx1_inner[0] == self._target_type)
            return self
        else:
            return self.subsystem.target_obj(tidx1_inner)

    def target_pos(self, tidx1):
        if tidx1 == TargetLeft:
            return 0
        elif tidx1 == TargetRight:
            return self.width_m
        tidx1_outer = tidx1[-1]
        tidx1_inner = tidx1[:-1]
        if tidx1_outer == 0:
            assert(tidx1_inner[0] == self._target_type)
            return 0
        else:
            return self.subsystem.target_pos(tidx1_inner)

    def matrix_detune_left(self, inverse = False):
        return np.matrix([
            [1, 0],
            [0, 1],
        ])

    def matrix_detune_right(self, inverse = False):
        return np.matrix([
            [1, 0],
            [0, 1],
        ])

    @declarative.mproperty
    def matrix(self):
        return self.matrix_detune_right() * self.subsystem.matrix * self.matrix_detune_left()

    @declarative.mproperty
    def matrix_inv(self):
        return self.matrix_detune_left(inverse = True) * self.subsystem.matrix_inv * self.matrix_detune_right(inverse = True)

    def matrix_between(self, tidx1, tidx2):
        if tidx1 == TargetLeft:
            if tidx2 == TargetLeft:
                return np.eye(2)
            elif tidx2 == TargetRight:
                return self.matrix
            else:
                tidx2_outer = tidx2[-1]
                if tidx2_outer != 0:
                    tidx2_inner = TargetIdx(tidx2[:-1])
                    return self.subsystem.matrix_between(TargetLeft, tidx2_inner) * self.matrix_detune_left()
                else:
                    return self.matrix_detune_left()
        elif tidx1 == TargetRight:
            if tidx2 == TargetLeft:
                return self.matrix_inv
            elif tidx2 == TargetRight:
                return np.eye(2)
            else:
                tidx2_outer = tidx2[-1]
                if tidx2_outer != 0:
                    tidx2_inner = TargetIdx(tidx2[:-1])
                    return self.subsystem.matrix_between(TargetRight, tidx2_inner) * self.matrix_detune_right(inverse = True)
                else:
                    return self.matrix_detune_right(inverse = True)
        else:
            tidx1_outer = tidx1[-1]
            if tidx1_outer != 0:
                tidx1_inner = TargetIdx(tidx1[:-1])
                if tidx2 == TargetLeft:
                    return self.matrix_detune_left(inverse = True) * self.subsystem.matrix_between(tidx1_inner, TargetLeft)
                elif tidx2 == TargetRight:
                    return self.matrix_detune_right() * self.subsystem.matrix_between(tidx1_inner, TargetRight)
                else:
                    tidx2_outer = tidx2[-1]
                    if tidx1_outer != 0:
                        tidx2_inner = TargetIdx(tidx2[:-1])
                        return self.subsystem.matrix_between(tidx1_inner, tidx2_inner)
                    else:
                        raise NotImplementedError()
            else:
                if tidx2 == TargetLeft:
                    return self.matrix_detune_left(inverse = True)
                elif tidx2 == TargetRight:
                    return self.matrix_detune_right()
                else:
                    raise NotImplementedError()

    def matrix_target_to_z_single(
            self,
            tidx1,
            z_m,
            invert = False,
    ):
        if tidx1 == TargetLeft:
            return self.subsystem.matrix_target_to_z_single(
                TargetLeft,
                z_m,
                invert = invert,
            ) * self.matrix_detune_left()
        elif tidx1 == TargetRight:
            return self.subsystem.matrix_target_to_z_single(
                TargetRight,
                z_m,
                invert = invert,
            ) * self.matrix_detune_right(inverse = True)
        else:
            tidx1_outer = tidx1[-1]
            if tidx1_outer != 0:
                tidx1_inner = TargetIdx(tidx1[:-1])
                return self.subsystem.matrix_target_to_z_single(
                    tidx1_inner,
                    z_m,
                    invert = invert,
                )
            else:
                raise NotImplementedError()

    @declarative.mproperty
    def constraints(self):
        return self.subsystem.constraints

class LensMount(MountBase):
    _target_type = 'lens_mount'
    substrate = substrates.substrate_environment

    detune_m = attrs.generate_detune_m()

    def matrix_detune_left(self, inverse = False):
        n = self.substrate.n()
        if not inverse:
            return np.matrix([
                [1, self.detune_m / n],
                [0, 1],
            ])
        else:
            return np.matrix([
                [1, -self.detune_m / n],
                [0, 1],
            ])

    def matrix_detune_right(self, inverse = False):
        n = self.substrate.n()
        if not inverse:
            return np.matrix([
                [1, -self.detune_m / n],
                [0, 1],
            ])
        else:
            return np.matrix([
                [1, self.detune_m / n],
                [0, 1],
            ])


class MirrorMount(MountBase):
    _target_type = 'mirror_mount'
    subsystem    = bases.NoP()
    substrate = substrates.substrate_environment

    detune_m = attrs.generate_detune_m()

    def matrix_detune_left(self, inverse = False):
        n = self.substrate.n()
        if not inverse:
            return np.matrix([
                [1, self.detune_m / n],
                [0, 1],
            ])
        else:
            return np.matrix([
                [1, -self.detune_m / n],
                [0, 1],
            ])

    def matrix_detune_right(self, inverse = False):
        n = self.substrate.n()
        if not inverse:
            return np.matrix([
                [1, self.detune_m / n],
                [0, 1],
            ])
        else:
            return np.matrix([
                [1, -self.detune_m / n],
                [0, 1],
            ])


class TargetMount(MountBase):
    _target_type = 'target_mount'

    @declarative.dproperty
    def subsystem(self):
        return bases.NoP()


class ConjMirrorMount(MountBase):
    _target_type = 'mirror_mount'
    subsystem    = bases.NoP()
    substrate = substrates.substrate_environment

    detune_m = attrs.generate_detune_m()

    def matrix_detune_left(self, inverse = False):
        n = self.substrate.n()
        if not inverse:
            return np.matrix([
                [1, self.detune_m / n],
                [0, 1],
            ])
        else:
            return np.matrix([
                [1, -self.detune_m / n],
                [0, 1],
            ])

    def matrix_detune_right(self, inverse = False):
        n = self.substrate.n()
        if not inverse:
            return np.matrix([
                [-1, self.detune_m / n],
                [0, -1],
            ])
        else:
            return np.matrix([
                [-1, -self.detune_m / n],
                [0, -1],
            ])

