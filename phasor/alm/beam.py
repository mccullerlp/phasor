# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from ..utilities.future_from_2 import str
import numpy as np
import declarative

#import phasor.numerics.dispatched as dmath
#import sympy


from ..base.autograft import invalidate_auto
from ..base.bases import Element

from .beam_param import (
    ComplexBeamParam
)

from ..base.multi_unit_args import (
    unitless_refval_attribute,
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

from . import standard_attrs as attrs


