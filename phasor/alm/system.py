# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np

#import phasor.numerics.dispatched as dmath
#import sympy

import declarative

from ..base.autograft import (
    invalidate_auto,
    Element,
)

from .utils import (
    TargetLeft,
    TargetRight,
    TargetIdx,
    matrix_space,
)

from . import bases
from . import space

from . import standard_attrs as attrs

class System(
    bases.MatrixAtsCompositeBase,
):
    @declarative.mproperty
    def _internal(self):
        return Element()

    _loc_default = ('loc_m', None)
    loc_m = attrs.generate_loc_m()

    _boundary_left_default = ('boundary_left_m', None)
    boundary_left = attrs.generate_boundary_left_m()

    _boundary_right_default = ('boundary_right_m', None)
    boundary_right = attrs.generate_boundary_right_m()

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def offset_m(self, arg = declarative.NOARG):
        return 0
        if arg is declarative.NOARG:
            if self.component_pos_pairings.any_abs_pos:
                arg = self.positions_list[0]
            else:
                arg = None
        return arg

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def width_m(self):
        return self.positions_list[-1] - self.positions_list[0]

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def components(self, comp_list = declarative.NOARG):
        if comp_list is not declarative.NOARG:
            for component in comp_list:
                if isinstance(component, declarative.PropertyTransforming):
                    with self.building:
                        self.insert(component)
                else:
                    with self.building:
                        self.insert(
                            obj  = component.replica_generate(),
                            name = component.name_child,
                        )
        self.root._complete()
        loc_ch_list = []
        for name, ch in list(self._registry_children.items()):
            if isinstance(ch, bases.MatrixAtsBase):
                if ch.loc_m.ref is not None:
                    loc_ch_list.append((ch.loc_m.ref, ch))
        loc_ch_list.sort()
        #print(loc_ch_list)
        clist = [ch for loc, ch in loc_ch_list]
        return clist

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def component_pos_pairings(self):
        with self.building:
            try:
                del self.ctree['_internal']
            except KeyError:
                pass
            components_pos = []
            components_filled = []
            loc_m = 0
            loc_m_prev = None
            pos_list = []

            if self.boundary_left_m.ref is not None:
                for idx, comp in enumerate(self.components):
                    if comp.loc_m.ref >= self.boundary_left_m.ref:
                        lslice = idx
                        break
                    else:
                        if comp.loc_m.ref + comp.width_m >= self.boundary_left_m.ref:
                            raise NotImplementedError("currently does not support system truncation that cuts objects (including subsystems)")
                else:
                    #if all of the components are behind the truncation, then index outside the component list
                    lslice = idx + 1
            else:
                lslice = None

            if self.boundary_right_m.ref is not None:
                for idx, comp in enumerate(reversed(self.components)):
                    if comp.loc_m.ref <= self.boundary_right_m.ref:
                        if comp.loc_m.ref + comp.width_m >= self.boundary_right_m.ref:
                            raise NotImplementedError("currently does not support system truncation that cuts objects (including subsystems)")
                        #this gives the actual (non reversed) index + 1
                        rslice = len(self.components) - idx
                        break
                else:
                    #if all of the components are behind the truncation, then index outside the component list
                    rslice = 0
            else:
                rslice = None

            if not self.env_reversed:
                comp_iter = iter(self.components[slice(lslice, rslice)])
            else:
                comp_iter = iter(reversed(self.components[slice(lslice, rslice)]))

            for idx, comp in enumerate(comp_iter):
                loc_m = None
                if comp.loc_m.val is not None:
                    #builds using negative indices when reversed
                    if not self.env_reversed:
                        loc_m = comp.loc_m.val
                    else:
                        loc_m = -comp.width_m - comp.loc_m.val
                    #TODO make this typesafe for casadi MX 
                    #if idx != 0 and loc_m < loc_m_prev:
                    #    print("OUT OF SEQ: ", comp, loc_m, loc_m_prev)
                    #    raise RuntimeError("Objects stacked out of sequence. Maybe you meant to insert objects into an inner system.")
                #TODO
                if loc_m is not None:
                    #put in a space to make up the gap
                    if idx != 0:
                        pos_list.append(loc_m_prev)
                        name = 'auto_space{0}'.format(idx)
                        components_filled.append(
                            self._internal.insert(
                                obj = space.Space(
                                    L_m = loc_m - loc_m_prev,
                                    loc_m = loc_m,
                                    #ctree = self.ctree['internal'][name],
                                ),
                                name = name,
                                invalidate = False,
                            )
                        )
                    elif (
                            (lslice is not None and not self.env_reversed) or
                            (rslice is not None and self.env_reversed)
                    ) :
                        #put in a space for the gap the truncation edge
                        if self.env_reversed:
                            loc_m_prev = -self.boundary_right_m.val
                        else:
                            loc_m_prev = self.boundary_left_m.val
                        pos_list.append(loc_m_prev)
                        name = 'auto_space{0}'.format(idx)
                        components_filled.append(
                            self._internal.insert(
                                obj = space.Space(
                                    L_m = loc_m - loc_m_prev,
                                    loc_m = loc_m,
                                    #ctree = self.ctree['internal'][name],
                                ),
                                name = name,
                                invalidate = False,
                            )
                        )
                else:
                    loc_m = loc_m_prev

                pos_list.append(loc_m)
                components_pos.append(loc_m)
                components_filled.append(comp)
                #print comp, loc_m
                loc_m += comp.width_m
                loc_m_prev = loc_m

            #now add the final space if there is a truncation
            if (
                    (rslice is not None and not self.env_reversed) or
                    (lslice is not None and self.env_reversed)
            ) :
                #put in a space for the gap the truncation edge
                if self.env_reversed:
                    loc_m = -self.boundary_left_m.val
                else:
                    loc_m = self.boundary_right_m.val

                pos_list.append(loc_m_prev)
                name = 'auto_space{0}'.format(idx + 1)
                components_filled.append(
                    self._internal.insert(
                        obj = space.Space(
                            L_m = loc_m - loc_m_prev,
                            loc_m = loc_m,
                            #ctree = self.ctree['internal'][name],
                        ),
                        name = name,
                        invalidate = False,
                    )
                )
            pos_list.append(loc_m)
            pos_list = np.asarray(pos_list) - pos_list[0]
            return declarative.Bunch(
                positions   = pos_list,
                filled      = components_filled,
                components_pos = components_pos,
            )

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def positions_list(self):
        return self.component_pos_pairings.positions

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def filled_list(self):
        return self.component_pos_pairings.filled

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def component_matrix_list(self):
        mat = np.eye(2)
        mat_list = [mat]
        for comp in self.filled_list:
            mat = comp.matrix * mat
            mat_list.append(mat)
        return mat_list

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def matrix(self):
        return self.component_matrix_list[-1]

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def matrix_inv(self):
        mat = np.eye(2)
        for comp in reversed(self.filled_list):
            #print comp.matrix * comp.matrix_inv
            #print comp
            mat = comp.matrix_inv * mat
        return mat

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def _matrix_between_memomap(self):
        return {}

    def matrix_between(self, tidx1, tidx2):
        result = self._matrix_between_memomap.get((tidx1, tidx2), None)
        if result is not None:
            return result
        if tidx1 == TargetLeft:
            if tidx2 == TargetLeft:
                mat = np.eye(2)
            elif tidx2 == TargetRight:
                mat = self.matrix
            else:
                tidx2_outer = tidx2[-1]
                tidx2_inner = TargetIdx(tidx2[:-1])
                mat = np.eye(2)
                for comp in self.filled_list[:tidx2_outer]:
                    mat = comp.matrix * mat
                mat = self.filled_list[tidx2_outer].matrix_between(TargetLeft, tidx2_inner) * mat
        elif tidx1 == TargetRight:
            if tidx2 == TargetLeft:
                mat = self.matrix**(-1)
            elif tidx2 == TargetRight:
                mat = np.eye(2)
            else:
                tidx2_outer = tidx2[-1]
                tidx2_inner = TargetIdx(tidx2[:-1])
                mat = np.eye(2)
                for comp in reversed(self.filled_list[tidx2_outer+1:]):
                    mat = comp.matrix_inv * mat
                mat = self.filled_list[tidx2_outer].matrix_between(TargetRight, tidx2_inner) * mat
        else:
            tidx1_outer = tidx1[-1]
            tidx1_inner = TargetIdx(tidx1[:-1])
            if tidx2 == TargetRight:
                mat = self.filled_list[tidx1_outer].matrix_between(tidx1_inner, TargetRight)
                for comp in self.filled_list[tidx1_outer + 1:]:
                    mat = comp.matrix * mat
            elif tidx2 == TargetLeft:
                mat = self.filled_list[tidx1_outer].matrix_between(tidx1_inner, TargetLeft)
                for comp in reversed(self.filled_list[:tidx1_outer]):
                    mat = comp.matrix_inv * mat
            else:
                tidx2_outer = tidx2[-1]
                tidx2_inner = TargetIdx(tidx2[:-1])
                if tidx2_outer == tidx1_outer:
                    mat = self.filled_list[tidx1_outer].matrix_between(tidx1_inner, tidx2_inner)
                elif tidx2_outer > tidx1_outer:
                    mat = self.filled_list[tidx1_outer].matrix_between(tidx1_inner, TargetRight)
                    for comp in self.filled_list[tidx1_outer + 1:tidx2_outer]:
                        mat = comp.matrix * mat
                    mat = self.filled_list[tidx2_outer].matrix_between(TargetLeft, tidx2_inner) * mat
                else:
                    mat = self.filled_list[tidx1_outer].matrix_between(tidx1_inner, TargetLeft)
                    for comp in reversed(self.filled_list[tidx2_outer+1:tidx1_outer]):
                        mat = comp.matrix_inv * mat
                    mat = self.filled_list[tidx2_outer].matrix_between(TargetRight, tidx2_inner) * mat
        #memoize result
        self._matrix_between_memomap[(tidx1, tidx2)] = mat
        return mat

    def matrix_target_to_z_single(self, tidx1, z_m, invert = False):
        if tidx1 == TargetLeft:
            mat = self.matrix_at_single(z_m)
            if invert:
                mat = mat**(-1)
            return mat
        elif tidx1 == TargetRight:
            #not nice numerically
            mat = self.matrix_at_single(z_m)
            mat_full = self.matrix
            if not invert:
                return mat * mat_full**(-1)
            else:
                return mat**(-1) * mat_full
        else:
            tidx1_outer = tidx1[-1]
            tidx1_inner = TargetIdx(tidx1[:-1])
            comp = self.filled_list[tidx1_outer]
            pos_L = self.positions_list[tidx1_outer]
            pos_R = self.positions_list[tidx1_outer+1]
            if z_m < pos_L:
                mat = comp.matrix_between(tidx1_inner, TargetLeft)
                #print z_m, self.positions_list
                idx_z_comp = np.searchsorted(
                    self.positions_list,
                    z_m, side = 'left',
                ) - 1
                if idx_z_comp >= 0:
                    for subcomp in reversed(self.filled_list[idx_z_comp+1:tidx1_outer]):
                        mat = subcomp.matrix_inv * mat
                    mat = self.filled_list[idx_z_comp].matrix_target_to_z_single(TargetRight, z_m - self.positions_list[idx_z_comp]) * mat
                else:
                    for subcomp in reversed(self.filled_list[:tidx1_outer]):
                        mat = subcomp.matrix_inv * mat
                    mat = matrix_space((z_m - self.positions_list[0])) * mat
            elif z_m > pos_R:
                mat = comp.matrix_between(tidx1_inner, TargetRight)
                idx_z_comp = np.searchsorted(
                    self.positions_list,
                    z_m, side = 'right',
                ) - 1
                if idx_z_comp < len(self.filled_list):
                    for subcomp in self.filled_list[tidx1_outer+1:idx_z_comp]:
                        mat = subcomp.matrix * mat
                    mat = self.filled_list[idx_z_comp].matrix_target_to_z_single(
                        TargetLeft,
                        z_m - self.positions_list[idx_z_comp],
                    ) * mat
                else:
                    for subcomp in self.filled_list[tidx1_outer+1:]:
                        mat = subcomp.matrix * mat
                    mat = matrix_space(z_m - self.positions_list[-1]) * mat
            else:
                return comp.matrix_target_to_z_single(tidx1_inner, z_m - pos_L, invert = invert)
            return mat

    def target_obj(self, tidx1):
        tidx1_outer = tidx1[-1]
        tidx1_inner = TargetIdx(tidx1[:-1])
        return self.filled_list[tidx1_outer].target_obj(tidx1_inner)

    def target_pos(self, tidx1):
        if tidx1 == TargetLeft:
            return 0
        elif tidx1 == TargetRight:
            return self.width_m
        tidx1_outer = tidx1[-1]
        tidx1_inner = TargetIdx(tidx1[:-1])
        poffset_m = self.positions_list[tidx1_outer]
        return poffset_m + self.filled_list[tidx1_outer].target_pos(tidx1_inner)

    def matrix_at_single(self, z_m):
        if self.offset_m is not None:
            z_m = z_m + self.offset_m

        mat_list = self.component_matrix_list
        idx_m = np.searchsorted(
            self.positions_list,
            z_m, side = 'right',
        ) - 1
        if idx_m < 0:
            mat = matrix_space(L_m = z_m)
        elif idx_m < len(self.filled_list):
            mat = mat_list[idx_m]
            comp = self.filled_list[idx_m]
            mat = comp.matrix_target_to_z_single(TargetLeft, z_m - self.positions_list[idx_m]) * mat
        else:
            mat = matrix_space(z_m - self.positions_list[-1]) * self.matrix
        return mat

    def system_data_targets(self, typename):
        dmap = {}
        for subidx, comp in enumerate(self.filled_list):
            for tidx, dfunc in list(comp.system_data_targets(typename).items()):
                dmap[TargetIdx(tidx + (subidx,))] = dfunc
        return dmap

    def _target_to_child(self, sub):
        sub_target = self.parent._target_to_child(self)
        subidx = self.filled_list.index(sub)
        return TargetIdx((subidx, ) + sub_target )

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def constraints(self):
        constraints = []
        for idx, comp in enumerate(self.filled_list):
            try:
                sub_constraints = comp.constraints
            except AttributeError:
                pass
            else:
                constraints.extend(sub_constraints)
        return constraints

class SystemStack(System):
    @declarative.mproperty(simple_delete = True)
    def components(self, comp_list):
        components = []
        for component in comp_list:
            if isinstance(component, Element):
                if component.parent is not self:
                    with self.building:
                        obj = self.insert(
                            obj  = component.replica_generate(),
                            name = component.name_child,
                        )
                else:
                    obj = component
            if isinstance(component, declarative.PropertyTransforming):
                with self.building:
                    obj = self.insert(component)
            #print(obj)
            components.append(obj)
        self.root._complete()
        return components

    @declarative.mproperty(simple_delete = True)
    @invalidate_auto
    def component_pos_pairings(self):
        try:
            with self.building:
                try:
                    del self.ctree['_internal']
                except KeyError:
                    pass
                components_pos = []
                components_filled = []
                loc_m = 0
                pos_list = []
                if not self.env_reversed:
                    comp_iter = iter(self.components)
                else:
                    comp_iter = iter(reversed(self.components))
                for idx, comp in enumerate(comp_iter):
                    pos_list.append(loc_m)
                    components_pos.append(loc_m)
                    components_filled.append(comp)
                    #print comp, loc_m
                    loc_m += comp.width_m
                pos_list.append(loc_m)
                pos_list = np.asarray(pos_list) - pos_list[0]
                return declarative.Bunch(
                    positions   = pos_list,
                    filled      = components_filled,
                    components_pos = components_pos,
                )
        except Exception as E:
            print("inside components_pos_pairings")
            print(E)
            raise


