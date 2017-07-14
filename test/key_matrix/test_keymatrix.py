# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np
import pytest

from phasor.math.key_matrix import keymatrix


@pytest.mark.skip("Need to revisit")
def test_basic():
    group = keymatrix.KVSpace()

    v_a = keymatrix.KeyVector(group['a'])
    v_b = keymatrix.KeyVector(group['b'])
    m_ab = keymatrix.KeyMatrix(group['a'], group['b'])

    v_a['x'] = 1
    v_a['y'] = 2
    v_a['z'] = 3

    v_b['m'] = 2
    v_b['n'] = 2

    group.freeze()

    m_ab['x', 'm'] = 2
    m_ab['y', 'n'] = 1

    assert(np.all(m_ab.array == np.array([[2, 0, 0], [0, 1, 0]])))
    assert(np.all(v_a.array == np.array([1, 2, 3])))
    assert(np.all(v_b.array == np.array([2, 2])))
    assert(np.all(m_ab.array == m_ab.backmap_array(m_ab.array).array))





