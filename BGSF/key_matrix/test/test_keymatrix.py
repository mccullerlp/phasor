import numpy as np
from keymatrix import (
    KVSpaceGroup,
    KeyVector,
    KeyMatrix
)

group = KVSpaceGroup()

v_a = KeyVector(group['a'])
v_b = KeyVector(group['b'])
m_ab = KeyMatrix(group['a'], group['b'])


v_a['x'] = 1
v_a['y'] = 2
v_a['z'] = 3

v_b['m'] = 2
v_b['n'] = 2

group.freeze()

m_ab['x', 'm'] = 2
m_ab['y', 'n'] = 1

assert(np.all(m_ab.array == np.array([[2,0,0],[0,1,0]])))
assert(np.all(v_a.array == np.array([1,2,3])))
assert(np.all(v_b.array == np.array([2,2])))
assert(np.all(m_ab.array == m_ab.backmap_array(m_ab.array).array))





