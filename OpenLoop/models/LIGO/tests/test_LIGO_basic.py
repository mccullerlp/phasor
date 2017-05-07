"""
"""
from __future__ import print_function, division

import declarative
from OpenLoop import optics
from OpenLoop import base
from OpenLoop import signals
from OpenLoop import system
from OpenLoop import readouts
from OpenLoop.models.LIGO import ligo_sled


def test_LIGO_basic():
    sys = system.BGSystem(
        freq_order_max_default = 1,
    )
    sys.my.det = ligo_sled.LIGOBasicOperation()
    sys.solution


if __name__ == '__main__':
    test_LIGO_basic()
