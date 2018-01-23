# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np
import declarative

#import phasor.numerics.dispatched as dmath
#import sympy


from ..utilities.future_from_2 import super
from ..base.autograft import invalidate_auto
from ..base.bases import Element

from ..base.multi_unit_args import (
    unitless_refval_attribute,
)

from .utils import (
    TargetLeft,
    TargetRight,
    TargetIdx,
    matrix_focus,
    np_check_sorted,
    str_m,
)

from .substrates import (
    substrate_environment,
)

from . import standard_attrs as attrs


class MatrixAtsBase(Element):
    #TODO report in ctree

    @declarative.dproperty
    def reversed(self, arg = declarative.NOARG):
        elname = "reversed"
        if arg is declarative.NOARG:
            arg = False

        ooa = self.ctree
        if self.inst_prototype_t in ["full"]:
            #TODO make this do the correct thing
            arg = getattr(self.inst_prototype, elname)
        else:
            ooa = self.ctree.useidx('immediate')

        ooa[elname] = arg
        #arg = ooa.setdefault(elname, arg)
        return ooa[elname]

    @declarative.mproperty
    def env_reversed(self):
        #TODO put this into the environment_query
        #print("PREV: ", self.parent.env_reversed, " ME: ", self.reversed)
        p_env_reversed = self.parent.environment_query((MatrixAtsBase, "reversed"))
        arg = bool(p_env_reversed) ^ bool(self.reversed)
        #arg = self.ctree.setdefault("env_reversed", arg)
        self.ctree.env_reversed = arg
        return self.ctree.env_reversed

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def matrix_inv(self):
        #print(self.__class__)
        #print(self.matrix)
        return self.matrix**(-1)

    def matrix_between(self, tidx1, tidx2):
        if tidx1 == TargetLeft:
            if tidx2 == TargetLeft:
                return np.eye(2)
            elif tidx2 == TargetRight:
                return self.matrix
            else:
                raise RuntimeError("Unknown Target {0}".format(tidx1))
        elif tidx1 == TargetRight:
            if tidx2 == TargetLeft:
                return self.matrix_inv
            elif tidx2 == TargetRight:
                return np.eye(2)
            else:
                raise RuntimeError("Unknown Target {0}".format(tidx1))
        else:
            print(self.__class__)
            raise RuntimeError("Unknown Target {0}".format(tidx1))

    def matrix_target_to_z_single(self, tidx1, z_m, invert = False):
        raise NotImplementedError()

    def matrix_target_to_z(self, tidx1, z_m, fill, invert = False):
        z_m = np.asarray(z_m)
        if len(z_m.shape) > 0:
            if len(z_m.shape) == 1 and np_check_sorted(z_m):
                return self.matrix_target_to_z_linsorted(tidx1, z_m, fill, invert = invert)

            fill_reshape = fill.reshape(2, 2, -1)
            idx_remux = np.indices(z_m.shape)
            idx_remux = idx_remux.reshape(len(z_m.shape), -1)
            z_m = z_m.reshape(-1)
            sidx = np.argsort(z_m)
            z_m = z_m[sidx]
            idx_remux = idx_remux[:, sidx]
            self.matrix_target_to_z_linsorted(tidx1, z_m, fill_reshape, invert = invert)
            fill = fill_reshape[(slice(None), slice(None)) + tuple(idx_remux[i] for i in range(idx_remux.shape[0]))]
            return
        else:
            return self.matrix_target_to_z_single(z_m)

    def matrix_target_to_z_linsorted(self, tidx1, z_m, fill, invert = False):
        it = np.nditer(z_m, flags = ['multi_index'])
        while not it.finished:
            fill[(slice(None), slice(None)) + it.multi_index] = self.matrix_target_to_z_single(tidx1, it.value)
            it.iternext()
        return fill

    @declarative.mproperty
    def constraints(self):
        return []

    def as_target(self, direction = 'left'):
        sub_target = self.parent._target_to_child(self)
        if direction == 'left':
            return TargetIdx(TargetLeft + sub_target)
        elif direction == 'right':
            return TargetIdx(TargetRight + sub_target)
        else:
            return None

    def environment_query_local(self, query):
        if query == (MatrixAtsBase, "reversed"):
            return self.env_reversed
        return super().environment_query_local(query)

    @declarative.dproperty
    def root(self):
        return self.environment_query((MatrixAtsBase, "root"))


class MatrixAtsCompositeBase(MatrixAtsBase):
    pass


class ThinBase(MatrixAtsBase, declarative.OverridableObject):
    width_m      = 0

    _loc_default = ('loc_m', None)
    loc_m = attrs.generate_loc_m()

    def matrix_target_to_z_single(self, tidx1, z_m, invert = False):
        if z_m != 0:
            raise RuntimeError("Only located at 0")

        #invert if viewing from the right
        if tidx1 == TargetRight:
            invert = not invert

        if not invert:
            return self.matrix
        else:
            return self.matrix_inv

    def matrix_target_to_z(self, tidx1, z_m, fill, invert = False):
        return self.matrix_target_to_z_linsorted(self, z_m, fill, invert = invert)

    def matrix_target_to_z_linsorted(self, tidx1, z_m, fill, invert = False):
        if not all(z_m == 0):
            raise RuntimeError("Only located at 0")

        #invert if viewing from the right
        if tidx1 == TargetRight:
            invert = not invert

        if not invert:
            fill[:, :, ...] = self.matrix
        else:
            fill[:, :, ...] = self.matrix_inv
        return

    def target_pos(self, target):
        return 0

    def system_data_targets(self, typename):
        dmap = {}
        return dmap


class NoP(ThinBase):
    @declarative.mproperty
    def matrix(self):
        return np.matrix([[1, 0], [0, 1]])

    @declarative.mproperty(simple_delete = True)
    def matrix_inv(self):
        return np.matrix([[1, 0], [0, 1]])


class ThinLens(ThinBase):

    f_m = attrs.generate_f_m()

    @declarative.mproperty
    def matrix(self):
        mat = matrix_focus(f_m = self.f_m.val)
        return mat

    @declarative.mproperty
    def matrix_inv(self):
        mat = matrix_focus(f_m = -self.f_m.val)
        return mat

    def lens_description(self, z, from_target):
        return declarative.Bunch(
            f_m = self.f_m.val,
            z = z,
            type = 'lens',
            str = 'thin lens f_m = {f_m}'.format(f_m = str_m(self.f_m.val)),
        )

    def detune_description(self, z, q_left):
        q_right = q_left.propagate_matrix(self.matrix)
        cplg02 = q_right.cplg02 - q_left.cplg02
        return declarative.Bunch(
            cplg02   = cplg02,
            type    = 'lens',
            q       = q_left,
            obj     = self,
        )

    def system_data_targets(self, typename):
        dmap = {}
        if typename == 'lens_description':
            dmap[TargetIdx()] = self.lens_description
        elif typename == 'detune_description':
            dmap[TargetIdx()] = self.detune_description
        return dmap


class LensInterface(ThinBase):
    substrate_from = substrate_environment
    substrate_to   = substrate_environment

    R_m = attrs.generate_R_m()

    @declarative.mproperty
    def matrix(self):
        n_from = self.substrate_from.n(self)
        n_to   = self.substrate_to.n(self)
        if self.R_m.val is not None:
            if not self.env_reversed:
                mat = np.matrix([
                    [1, 0],
                    [(n_from/n_to - 1)/self.R_m.val, n_from / n_to],
                ])
            else:
                mat = np.matrix([
                    [1, 0],
                    [(n_to/n_from - 1)/-self.R_m.val, n_to / n_from],
                ])
        else:
            if not self.env_reversed:
                mat = np.matrix([
                    [1 , 0],
                    [0 , n_from / n_to],
                ])
            else:
                mat = np.matrix([
                    [1 , 0],
                    [0 , n_to / n_from],
                ])
        return mat

    @declarative.mproperty
    def matrix_inv(self):
        n_to = self.substrate_from.n(self)
        n_from = self.substrate_to.n(self)
        if self.R_m.val is not None:
            if not self.env_reversed:
                mat = np.matrix([
                    [1, 0],
                    [(n_from/n_to - 1)/self.R_m.val, n_from / n_to],
                ])
            else:
                mat = np.matrix([
                    [1, 0],
                    [(n_to/n_from - 1)/-self.R_m.val, n_to / n_from],
                ])
        else:
            if not self.env_reversed:
                mat = np.matrix([
                    [1 , 0],
                    [0 , n_from / n_to],
                ])
            else:
                mat = np.matrix([
                    [1 , 0],
                    [0 , n_to / n_from],
                ])
        return mat


class Mirror(ThinBase):
    R_m = attrs.generate_R_m()

    @declarative.mproperty
    def matrix(self):
        if self.R_m.val is not None:
            mat = np.matrix([
                [1,      0],
                [-2/self.R_m.val, 1],
            ])
        else:
            mat = np.matrix([
                [1 , 0],
                [0 , 1],
            ])
        return mat

    def mirror_description(self, z, from_target):
        if self.R_m.val is not None:
            f_m = -1/self.matrix[1, 0]
            return declarative.Bunch(
                R_m = self.R_m.val,
                f_m = f_m,
                z = z,
                type = 'mirror',
                str = 'Mirror, R_m = {R_m}, f_m = {R_m}'.format(R_m = str_m(self.R_m.val), f_m = str_m(f_m)),
            )
        else:
            return declarative.Bunch(
                R_m = self.R_m.val,
                z = z,
                type = 'mirror',
                str = 'Mirror, flat',
            )

    def detune_description(self, z, q_left):
        q_right = q_left.propagate_matrix(self.matrix)
        cplg02 = q_right.cplg02 + q_left.cplg02
        return declarative.Bunch(
            cplg02   = cplg02,
            type    = 'mirror',
            q       = q_left,
            obj     = self,
        )

    def system_data_targets(self, typename):
        dmap = {}
        if typename == 'mirror_description':
            dmap[TargetIdx()] = self.mirror_description
        elif typename == 'detune_description':
            dmap[TargetIdx()] = self.detune_description
        return dmap


class ABCDGeneric(ThinBase):
    _A_default = 1
    @declarative.dproperty_adv
    def A(desc):
        return unitless_refval_attribute(
            desc,
            prototypes    = ['full', 'base'],
            default_attr  = '_A_default',
            allow_fitting = True,
        )

    _B_default = 0
    @declarative.dproperty_adv
    def B(desc):
        return unitless_refval_attribute(
            desc,
            prototypes    = ['full', 'base'],
            default_attr  = '_B_default',
            allow_fitting = True,
        )

    _C_default = 0
    @declarative.dproperty_adv
    def C(desc):
        return unitless_refval_attribute(
            desc,
            prototypes    = ['full', 'base'],
            default_attr  = '_C_default',
            allow_fitting = True,
        )

    @declarative.dproperty
    def D(self):
        return (self.C.val * self.B.val + 1)/self.A.val

    @declarative.mproperty
    def matrix(self):
        return np.matrix([[self.A.val, self.B.val], [self.C.val, self.D]])

