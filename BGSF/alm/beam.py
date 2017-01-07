"""
"""
from __future__ import division, print_function
import numpy as np

#import BGSF.numerics.dispatched as dmath
#import sympy

from declarative import (
    OverridableObject,
    mproperty,
    dproperty,
    NOARG,
    Bunch,
)

from declarative.properties import (
    group_dproperty,
    #group_mproperty,
)

from .beam_param import (
    ComplexBeamParam
)

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

from .substrates import (
    substrate_environment,
)

from .bases import (
    Element,
    invalidate_auto
)

from .multi_unit_args import (
    generate_refval_attribute,
)


class MatrixAtsBase(Element):
    #TODO report in ooa_params

    #@dproperty_adv
    #def reversed(desc):
    #    @desc.construct
    #    def VALUE(self, arg = NOARG):
    #        elname = desc.__name__
    #        if arg is NOARG:
    #            arg = False

    #        ooa = self.ooa_params
    #        if self.inst_prototype_t in ["full"]:
    #            #TODO make this do the correct thing
    #            arg = getattr(self.inst_prototype, elname)
    #        else:
    #            ooa = self.ooa_params.useidx('immediate')
    #        arg = ooa.setdefault(elname, arg)
    #        return arg
    #    return

    @dproperty
    def reversed(self, arg = NOARG):
        elname = "reversed"
        if arg is NOARG:
            arg = False

        ooa = self.ooa_params
        if self.inst_prototype_t in ["full"]:
            #TODO make this do the correct thing
            arg = getattr(self.inst_prototype, elname)
        else:
            ooa = self.ooa_params.useidx('immediate')

        ooa[elname] = arg
        #arg = ooa.setdefault(elname, arg)
        return ooa[elname]

    @mproperty
    def env_reversed(self):
        #TODO put this into the environment_query
        #print("PREV: ", self.parent.env_reversed, " ME: ", self.reversed)
        p_env_reversed = self.environment_query((MatrixAtsBase, "reversed"))
        arg = bool(p_env_reversed) ^ bool(self.reversed)
        #arg = self.ooa_params.setdefault("env_reversed", arg)
        self.ooa_params.env_reversed = arg
        return self.ooa_params.env_reversed

    @mproperty
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

    @mproperty
    def constraints(self):
        return []

    def environment_query_local(self, query):
        if query == (MatrixAtsBase, "reversed"):
            return self.env_reversed
        return super(MatrixAtsBase, self).environment_query_local(query)

    @dproperty
    def root(self):
        return self.environment_query((MatrixAtsBase, "root"))


class MatrixAtsCompositeBase(MatrixAtsBase):
    pass


class CThinBase(MatrixAtsBase, OverridableObject):
    width_m      = 0

    _loc_default = ('loc_m', None)
    @group_dproperty
    def loc_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['loc', ],
            pname = 'location',
            preferred_attr = 'loc_preferred',
            default_attr = '_loc_default',
            prototypes = ['full'],
        )

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


class CNoP(CThinBase):
    @mproperty
    def matrix(self):
        return np.matrix([[1, 0], [0, 1]])

    @mproperty
    def matrix_inv(self):
        return np.matrix([[1, 0], [0, 1]])


class BeamTarget(CNoP):
    q_raw = None
    gouy_phasor = 1

    @dproperty
    def q_system(self, arg = NOARG):
        if arg is NOARG:
            arg = None
        return arg

    @dproperty
    def _check_q(self):
        if self.q_raw is None:
            if self.q_system is None:
                raise RuntimeError("Must specify q_raw or q_system")
            else:
                return None
        else:
            if self.q_system is not None:
                raise RuntimeError("Must specify only on of q_raw or q_system")
            else:
                q_item = self.q_raw
                if isinstance(q_item, ComplexBeamParam):
                    q_item = q_item.value
                return q_item

    @mproperty
    def beam_q(self):
        wavelen = self.root.env_wavelength_nm * 1e-9

        if self._check_q is None:
            q = eigen_q(self.q_system.matrix)
        else:
            q = self._check_q
        q_obj = ComplexBeamParam(
            value = q,
            wavelen = wavelen,
            gouy_phasor = self.gouy_phasor,
        )
        if self._check_q is not None and self.env_reversed:
            q_obj = q_obj.reversed()
        return q_obj

    _overridable_object_save_kwargs = True

    def target_description(self, z):
        beam_q = self.beam_q
        return Bunch(
            z = z,
            q = beam_q,
            type = 'target',
            str = u'{name} {q}'.format(name = self.name, q = unicode(beam_q)),
        )

    def system_data_targets(self, typename):
        dmap = {}
        if typename == 'target_description':
            dmap[TargetIdx()] = self.target_description
        if typename == 'q_target':
            dmap[TargetIdx(('q_target',))] = self.name
        return dmap

    def target_obj(self, tidx1):
        return self

    def target_pos(self, tidx1):
        return 0

    def draw_lines_mpl(self, ax, offset):
        ax.axvline(offset, color = 'orange', ls ='--')

    def matrix_between(self, tidx1, tidx2):
        if tidx1 == TargetLeft:
            pass
        elif tidx1 == TargetRight:
            pass
        elif tidx1 == TargetIdx(['q_target']):
            pass
        else:
            raise RuntimeError("Unknown Target {0}".format(tidx1))
        if tidx2 == TargetLeft:
            pass
        elif tidx2 == TargetRight:
            pass
        elif tidx2 == TargetIdx(['q_target']):
            pass
        else:
            raise RuntimeError("Unknown Target {0}".format(tidx1))
        return np.eye(2)


class CThinLens(CThinBase):

    @group_dproperty
    def f_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['f'],
            pname = 'focal_length',
            preferred_attr = 'f_preferred',
            prototypes = ['full', 'base'],
        )

    @mproperty
    def matrix(self):
        mat = matrix_focus(f_m = self.f_m.val)
        return mat

    @mproperty
    def matrix_inv(self):
        mat = matrix_focus(f_m = -self.f_m.val)
        return mat

    def lens_description(self, z, from_target):
        return Bunch(
            f_m = self.f_m.val,
            z = z,
            type = 'lens',
            str = 'thin lens f_m = {f_m}'.format(f_m = str_m(self.f_m.val)),
        )

    def system_data_targets(self, typename):
        dmap = {}
        if typename == 'lens_description':
            dmap[TargetIdx()] = self.lens_description
        return dmap


class CSpace(MatrixAtsBase, OverridableObject):
    substrate = substrate_environment

    @group_dproperty
    def L_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['L', 'length'],
            pname = 'length',
            preferred_attr = 'L_preferred',
            prototypes = ['full', 'base'],
        )

    _loc_default = ('loc_m', None)
    @group_dproperty
    def loc_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['loc', ],
            pname = 'location',
            preferred_attr = 'loc_preferred',
            default_attr = '_loc_default',
            prototypes = ['full'],
        )

    @mproperty
    def width_m(self):
        return self.L_m.val

    @mproperty
    def matrix(self):
        n = self.substrate.n(self)
        return np.matrix([
            [1, self.L_m.val / n],
            [0, 1],
        ])

    @mproperty
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
    @mproperty
    def constraints(self):
        return [(self.L_m.val, self.min_spacing, +float('inf'))]

    def waist_description(self, z, q, from_target):
        zw = z - q.Z
        has_waist = False
        if from_target == TargetLeft:
            if -q.Z > -1e-16 and -q.Z < self.L_m.val:
                has_waist = True
        elif from_target == TargetRight:
            if q.Z > -1e-16 and q.Z < self.L_m.val:
                has_waist = True
        if has_waist:
            return Bunch(
                z = zw,
                ZR = q.ZR,
                str = u'waist ZR = {0}, W = {1}'.format(str_m(q.ZR, 2), str_m(q.W0, 2)),
            )
        return None

    def system_data_targets(self, typename):
        dmap = {}
        if typename == 'waist_description':
            dmap[TargetIdx()] = self.waist_description
        return dmap


class CLensInterface(CThinBase):
    substrate_from = substrate_environment
    substrate_to   = substrate_environment

    @group_dproperty
    def R_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['R', 'ROC'],
            pname = 'ROC',
            preferred_attr = 'ROC_preferred',
            prototypes = ['full', 'base'],
        )

    @mproperty
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

    @mproperty
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


class CMirror(CThinBase):
    @group_dproperty
    def R_m(desc):
        return generate_refval_attribute(
            desc,
            units = 'length',
            stems = ['R', 'ROC'],
            pname = 'ROC',
            preferred_attr = 'ROC_preferred',
            prototypes = ['full', 'base'],
        )

    @mproperty
    def matrix(self):
        if self.R_m.val is not None:
            mat = np.matrix([
                [1,      0],
                [-2/self.R_m.val, 1],
            ])
        else:
            mat = np.matrix([
                [1 ,     0],
                [2/self.R_m.val , 1],
            ])
        return mat

    def mirror_description(self, z, from_target):
        f_m = -1/self.matrix[1, 0]
        return Bunch(
            R_m = self.R_m.val,
            f_m = f_m,
            z = z,
            type = 'mirror',
            str = 'Mirror, R_m = {R_m}, f_m = {R_m}'.format(R_m = str_m(self.R_m), f_m = str_m(f_m)),
        )

    def system_data_targets(self, typename):
        dmap = {}
        if typename == 'mirror_description':
            dmap[TargetIdx()] = self.mirror_description
        return dmap


