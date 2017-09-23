# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from ..utilities.future_from_2 import str
import numpy as np
import declarative

from .beam_param import (
    ComplexBeamParam
)

from .utils import (
    TargetLeft,
    TargetRight,
    TargetIdx,
    eigen_q,
)

from . import bases


class BeamTargetBase(bases.NoP):
    def target_description(self, z):
        beam_q = self.beam_q
        return declarative.Bunch(
            z = z,
            q = beam_q,
            type = 'target',
            str = u'{name} {q}'.format(name = self.name, q = str(beam_q)),
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


class BeamTarget(BeamTargetBase):
    q_raw = None
    gouy_phasor = 1

    @declarative.dproperty
    def q_system(self, arg = declarative.NOARG):
        if arg is declarative.NOARG:
            arg = None
        return arg

    @declarative.dproperty
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

    @declarative.mproperty
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


