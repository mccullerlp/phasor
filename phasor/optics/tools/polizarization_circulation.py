from __future__ import division
from __future__ import print_function
from past.utils import old_div
import numpy as np

def normalize(v):
    return old_div(v, np.dot(v, v)**.5)

def project_away(v, N):
    #project away N from v, assumes N normalized
    return v - N * np.dot(v, N)

def reflect_through(v, N):
    #reflect v through N, assumes N normalized
    #output preserves the norm of v
    return v - 2 * N * np.dot(v, N)


def polarization_circulation(pos_xyx_list):
    p_s = np.array(pos_xyx_list)

    #generate beam pointing vectors from list of positions
    p_prev = p_s[-1]
    v_s = []
    for p in p_s:
        v = p - p_prev
        v = normalize(v)
        v_s.append(v)
        p_prev = p
    v_s = np.array(v_s)
    v_s = np.roll(v_s, -1, axis = 0)

    #generate mirror normals from beam pointings
    v_prev = v_s[-1]
    N_s = []
    for v in v_s:
        N = v - v_prev
        N = normalize(N)
        N_s.append(N)
        v_prev = v
    N_s = np.array(N_s)

    #use the first two beam pointings to generate canonical p polarization
    pol_p = project_away(v_s[-1], v_s[0])
    pol_p = normalize(pol_p)
    #and an s polarization that is orthogonal
    pol_s = np.cross(pol_p, v_s[0])
    pol_s = normalize(pol_s)

    #now reflect p and s through all of the normals
    pol_p_new = pol_p
    pol_s_new = pol_s
    for N in np.roll(N_s, -1, axis = 0):
        pol_p_new = reflect_through(pol_p_new, N)
        pol_s_new = reflect_through(pol_s_new, N)

    pp = np.dot(pol_p_new, pol_p)
    ps = np.dot(pol_p_new, pol_s)
    sp = np.dot(pol_s_new, pol_p)
    ss = np.dot(pol_s_new, pol_s)

    circular_jones_ps = np.array([[pp, ps], [sp, ss]])
    return circular_jones_ps

if __name__ == '__main__':
    up_down = .002
    #square of mirrors alternating
    p_s = [
        (0, 0, +up_down),
        (1, 0, -up_down),
        (1, 1, +up_down),
        (0, 1, -up_down),
    ]
    jones = polarization_circulation(p_s)
    print('Jones Matrix: ')
    print(jones)
    print('Polarization Defect: ', 1 - jones[0,0]**2)
