# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
import numpy as np
import sys

#from pprint import pprint

import declarative

from .utils import (
    TargetLeft,
    TargetRight,
    TargetIdx,
    np_check_sorted,
)

from .beam import (
    MatrixAtsBase
)

from ..base import (
    RootElement,
    Element,
)

from ..base.autograft import (
    invalidate_auto,
)

from .substrates import substrate_nitrogen
from .system import CSystem

from declarative.bunch import DeepBunchSingleAssign


class CRootSystem(RootElement, CSystem):
    _defer_build = False

    env_principle_target = None
    env_substrate        = substrate_nitrogen
    env_wavelength_nm    = 1064

    _loc_default = ('loc_m', 0)

    @declarative.mproperty
    def env_reversed(self):
        #TODO put this into the environment_query
        arg = bool(self.reversed)
        #arg = self.ctree.setdefault("env_reversed", arg)
        self.ctree.env_reversed = arg
        return self.ctree.env_reversed
        return arg

    @declarative.dproperty
    def measurements(self):
        arg = CMeasurements(
            layout = self,
        )
        return arg

    def print_yaml(self):
        import yaml
        db = DeepBunchSingleAssign()
        db.update_recursive(self.ctree)
        yaml.dump(db._mydict_resolved, sys.stdout)
        return

    def environment_query_local(self, query):
        if query == (MatrixAtsBase, "root"):
            return self
        elif query == (MatrixAtsBase, "principle_target"):
            return self.env_principle_target
        elif query == (MatrixAtsBase, "substrate"):
            return self.env_substrate
        elif query == (MatrixAtsBase, "wavelength_nm"):
            return self.env_wavelength_nm
        return super(CRootSystem, self).environment_query_local(query)


class CMeasurements(Element):
    @declarative.dproperty
    def layout(self, sys):
        return sys

    def matrix_at(self, z_m):
        z_m = np.asarray(z_m)
        fill = np.empty((2, 2) + z_m.shape)
        return self.layout.matrix_target_to_z(TargetLeft, z_m, fill)

    def matrix_at_linsorted(self, z_m):
        fill = np.empty((2, 2) + z_m.shape)
        return self.layout.matrix_target_to_z_linsorted(TargetLeft, z_m, fill)

    def matrix_at_single(self, z_m):
        return self.layout.matrix_target_to_z_single(TargetLeft, z_m)

    def q_at(self, z_m):
        z_m = np.asarray(z_m)
        if len(z_m.shape) == 0:
            mat = self.layout.matrix_target_to_z_single(TargetLeft, z_m)
        elif np_check_sorted(z_m):
            fill = np.empty((2, 2) + z_m.shape)
            mat = self.layout.matrix_target_to_z_linsorted(TargetLeft, z_m, fill)
        else:
            mat = self.matrix_at(z_m)
        q = self.input_q.propagate_matrix(mat)
        return q

    def z_nearest_waist(self, z_orig, ZR_scale = 0):
        q = self.q_target_z(z_orig)
        return z_orig - q.Z + ZR_scale * q.ZR

    def with_inserted(self, obj_list):
        system = self.layout.with_inserted(obj_list)
        #TODO use specified parameters
        return self.__class__(
            system = system,
            principle_target = self.layout.env_principle_target,
        )

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def constraints(self):
        constraints = self.layout.constraints
        additional_constraints = self.q_constraints()
        return constraints + additional_constraints

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def target_classifications(self):
        targets_by_type = {}
        targets_by_tidx = {}
        for tname, tidx_lst in list(self.layout.targets_map.items()):
            for tidx in tidx_lst:
                ttype = tidx[0]
                tmap = targets_by_type.get(ttype, None)
                if tmap is None:
                    tmap = {}
                    targets_by_type[ttype] = tmap
                tmap.setdefault(tname, []).append(tidx)
                tidxmap = targets_by_tidx.get(ttype, None)
                if tidxmap is None:
                    tidxmap = {}
                    targets_by_tidx[ttype] = tidxmap
                keylist = tidxmap.setdefault(tidx, [])
                keylist.append(tname)
        return declarative.Bunch(
            targets_by_type = targets_by_type,
            targets_by_tidx = targets_by_tidx,
        )

    def q_target_z(self, z_m, beam_source = None):
        if beam_source is None:
            if self.layout.env_principle_target is None:
                beam_source = self.beam_targets.tname[0]
            else:
                beam_source = self.layout.env_principle_target

        if not isinstance(beam_source, TargetIdx):
            tidx_beam = self.target_idx(beam_source)
        else:
            tidx_beam = beam_source

        z_m = np.asarray(z_m)
        if len(z_m.shape) == 0:
            mat = self.layout.matrix_target_to_z_single(tidx_beam, z_m)
        elif np_check_sorted(z_m):
            fill = np.empty((2, 2) + z_m.shape)
            mat = self.layout.matrix_target_to_z_linsorted(tidx_beam, z_m, fill)
        else:
            mat = self.matrix_at(z_m)
        target_obj = self.layout.target_obj(tidx_beam)
        q_in = target_obj.beam_q
        q = q_in.propagate_matrix(mat)
        return q

    def mat_target_z(self, tname, z_m):
        tidx = self.target_idx(tname)
        z_m = np.asarray(z_m)
        if len(z_m.shape) == 0:
            mat = self.layout.matrix_target_to_z_single(tidx, z_m)
        elif np_check_sorted(z_m):
            fill = np.empty((2, 2) + z_m.shape)
            mat = self.layout.matrix_target_to_z_linsorted(tidx, z_m, fill)
        return mat

    def mat_target_between(self, tname1, tname2):
        tidx1 = self.target_idx(tname1)
        tidx2 = self.target_idx(tname2)
        mat = self.layout.matrix_between(tidx1, tidx2)
        return mat

    def target_z(self, tname):
        tidx = self.target_idx(tname)
        return self.layout.target_pos(tidx)

    def overlap_seq(self, *tlist):
        tprev = self.beam_targets.tname[0]
        olap = 1
        for tnext in self.beam_targets.tname[1:]:
            tnext = tnext
            if (not tlist) or (tnext in tlist):
                olap *= abs(self.overlap(tprev, tnext))**4
            tprev = tnext
        return olap

    def overlap(self, tname1 = None, tname2 = None):
        if (tname1 is None) and (tname2 is None):
            if len(self.beam_targets.tname) == 2:
                tname1 = self.beam_targets.tname[0]
                tname2 = self.beam_targets.tname[-1]
        tidx1 = self.target_idx(tname1)
        tidx2 = self.target_idx(tname2)
        mat = self.layout.matrix_between(tidx1, tidx2)

        target_obj1 = self.layout.target_obj(tidx1)
        q_in1 = target_obj1.beam_q
        target_obj2 = self.layout.target_obj(tidx2)
        q_in2 = target_obj2.beam_q
        return q_in2.overlap_with(q_in1.propagate_matrix(mat))

    def target_obj(self, tname1):
        tidx1 = self.target_idx(tname1)
        obj = self.layout.target_obj(tidx1)
        return obj

    def target_q(
            self,
            tname1,
            beam_source = None,
    ):
        if beam_source is None:
            if self.layout.env_principle_target is None:
                beam_source = self.beam_targets.tname[0]
            else:
                beam_source = self.layout.env_principle_target

        if not isinstance(beam_source, TargetIdx):
            tidx_beam = self.target_idx(beam_source)
        else:
            tidx_beam = beam_source

        tidx1 = None
        if isinstance(tname1, str):
            tidx1 = self.target_idx(tname1)
            matbs = self.layout.matrix_between(tidx_beam, tidx1)
        elif tname1 in (TargetLeft, TargetRight) or isinstance(tname1, TargetIdx):
            matbs = self.layout.matrix_between(tidx_beam, tname1)
        else:
            matbs = self.layout.matrix_target_to_z_single(tidx_beam, tname1)
        #print(tidx_beam, tname1, matbs)

        beam_obj = self.layout.target_obj(tidx_beam)
        q_start = beam_obj.beam_q
        q_1 = q_start.propagate_matrix(matbs)
        return q_1

    def relative_gouy_phasor(
            self,
            tname1,
            tname2,
            beam_source = None
    ):
        if beam_source is None:
            beam_source = self.beam_targets.tname[0]

        tidx_beam = self.target_idx(beam_source)

        tidx1 = None
        if isinstance(tname1, str):
            tidx1 = self.target_idx(tname1)
            matbs = self.layout.matrix_between(tidx_beam, tidx1)
        else:
            matbs = self.layout.matrix_target_to_z_single(tidx_beam, tname1)

        beam_obj = self.layout.target_obj(tidx_beam)
        q_start = beam_obj.beam_q

        q_1 = q_start.propagate_matrix(matbs)
        #reset phasor to propagate it further
        q_1.gouy_phasor = 1

        if isinstance(tname2, str):
            tidx2 = self.target_idx(tname2)
            if tidx1 is not None:
                mat = self.layout.matrix_between(tidx1, tidx2)
            else:
                mat = self.layout.matrix_target_to_z_single(tidx2, tname1)**(-1)
        else:
            if tidx1 is not None:
                mat = self.layout.matrix_target_to_z_single(tidx1, tname2)
            else:
                mat = self.layout.matrix_target_to_z_single(tidx_beam, tname2) * matbs**(-1)
        q_2 = q_1.propagate_matrix(mat)

        return q_2.gouy_phasor / abs(q_2.gouy_phasor)

    def relative_gouy_ellipticity(
            self,
            tname1,
            tname2,
            beam_source = None
    ):
        gphasor = self.relative_gouy_phasor(
            tname1      = tname1     ,
            tname2      = tname2     ,
            beam_source = beam_source,
        )
        gcossq = abs(gphasor.real)
        return ((1 + gcossq) / (1 - gcossq))**.5

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def beam_targets(self):
        namemap = self.layout.system_data_targets('q_target')
        funcmap_inv = {}
        for tidx, name in list(namemap.items()):
            funcmap_inv[name] = tidx
        #print("TARGETS: ", funcmap_inv)

        z_targets = [(self.target_z(tidx), tname) for tname, tidx in list(funcmap_inv.items())]
        z_targets.sort()
        return declarative.Bunch(
            tname = [tname for t_z, tname in z_targets],
            z = [t_z for t_z, tname in z_targets],
        )

    def _z_q_descmap(self, descmap, beam_source, no_q = False):
        if beam_source is None:
            if self.layout.env_principle_target is None:
                beam_source = self.beam_targets.tname[0]
            else:
                beam_source = self.layout.env_principle_target

        if not isinstance(beam_source, TargetIdx):
            tidx_beam = self.target_idx(beam_source)
        else:
            tidx_beam = beam_source

        for tidx, dfunc in list(descmap.items()):
            #TODO make this more "robust"
            if tidx_beam[::-1] <= tidx[::-1]:
                tlr = TargetLeft
            else:
                tlr = TargetRight

            target = TargetIdx(tlr + tidx)
            z = self.layout.target_pos(target)
            if not no_q:
                q = self.target_q(target, tidx_beam)
            else:
                q = None
            yield z, q, tlr, dfunc
        return

    def q_constraints(self, beam_source = None):
        funcmap = self.layout.system_data_targets('q_constraints')
        constraints = []
        for z, q, target_side, dfunc in self._z_q_descmap(funcmap, beam_source):
            ret = dfunc(z = z, q = q, from_target = target_side)
            if ret is not None:
                constraints.extend(ret)
        return constraints

    def lens_descriptions(self, beam_source = None):
        funcmap = self.layout.system_data_targets('lens_description')
        z_descs = []
        for z, q, target_side, dfunc in self._z_q_descmap(funcmap, beam_source, no_q = True):
            ret = dfunc(z = z, from_target = target_side)
            if ret is not None:
                z_descs.append(ret)
        return z_descs

    def mirror_descriptions(self, beam_source = None):
        funcmap = self.layout.system_data_targets('mirror_description')
        z_descs = []
        for z, q, target_side, dfunc in self._z_q_descmap(funcmap, beam_source, no_q = True):
            ret = dfunc(z = z, from_target = target_side)
            if ret is not None:
                z_descs.append(ret)
        return z_descs

    def mount_descriptions(self, beam_source = None):
        funcmap = self.layout.system_data_targets('mount_description')
        z_descs = []
        for z, q, target_side, dfunc in self._z_q_descmap(funcmap, beam_source):
            ret = dfunc(z = z, q = q, from_target = target_side)
            if ret is not None:
                z_descs.append(ret)
        return z_descs

    def waist_descriptions(self, beam_source = None):
        funcmap = self.layout.system_data_targets('waist_description')
        data = []
        N = len(self.beam_targets.tname)
        for idx in range(N):
            target = self.beam_targets.tname[idx]
            if idx != 0:
                z1 = self.beam_targets.z[idx]
            else:
                z1 = -float('inf')
            if idx + 1 == N:
                z2 = float('inf')
            else:
                z2 = self.beam_targets.z[idx+1]
            for z, q, target_side, dfunc in self._z_q_descmap(funcmap, target):
                if z > z1 and z <= z2:
                    data.append((z, q, target_side, dfunc))

        z_descs = []
        for z, q, target_side, dfunc in data:
            ret = dfunc(z = z, q = q, from_target = target_side)
            if ret is not None:
                z_descs.append(ret)
        return z_descs

    def extra_descriptions(self, beam_source = None):
        funcmap = self.layout.system_data_targets('extra_description')
        z_descs = []
        for z, q, target_side, dfunc in self._z_q_descmap(funcmap, beam_source):
            ret = dfunc(z = z, q = q, from_target = target_side)
            if ret is not None:
                z_descs.append(ret)
        return z_descs

    def target_descriptions(self, beam_source = None):
        funcmap = self.layout.system_data_targets('target_description')
        z_descs = []
        for z, q, target_side, dfunc in self._z_q_descmap(funcmap, beam_source, no_q = True):
            ret = dfunc(z = z)
            if ret is not None:
                z_descs.append(ret)
        return z_descs

    def target_idx(self, tname):
        if isinstance(tname, TargetIdx):
            return tname
        if tname == 'left':
            return TargetLeft
        elif tname == 'right':
            return TargetRight

        namemap = self.layout.system_data_targets('q_target')
        funcmap_inv = {}
        for tidx, name in list(namemap.items()):
            funcmap_inv[name] = tidx
        #TODO, deal with non-uniques
        return funcmap_inv[tname]

