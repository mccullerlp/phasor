# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from BGSF.utilities.print import print

from declarative import (
    mproperty,
)

from ..base.utilities import (
    type_test
)

from ..math.key_matrix.dictionary_keys import (
    DictKey,
    FrequencyKey,
)

from ..base import (
    FrequencyBase,
)

from .bases import (
    OpticalCouplerBase,
    OpticalNoiseBase,
)

from .ports import (
    OpticalPortHolderIn,
    ports.OpticalPortHolderOut,
    ports.OpticalPortHolderInOut,
    ports.MechanicalPortHolderIn,
    ports.MechanicalPortHolderOut,
    SignalPortHolderIn,
    ports.SignalPortHolderOut,
    QuantumKey,
    ports.RAISE, ports.LOWER,
    PolKEY,
    ports.PolS, ports.PolP,
    OpticalFreqKey,
    ClassicalFreqKey,
    ports.OpticalSymmetric2PortMixin,
    ports.OpticalOriented2PortMixin,
    ports.OpticalNonOriented1PortMixin,
)

from .nonlinear_utilities import (
    #symmetric_update,
    ports_fill_2optical_2classical,
    modulations_fill_2optical_2classical,
)


