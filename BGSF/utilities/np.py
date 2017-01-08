"""
.. autofunction:: masked_argsort
"""
import numpy as np
import cmath
from functools import reduce

def domain_sort(X, *Y):
    X = np.asarray(X)
    if not np.all(X[:-1] <= X[1:]):
        sort_idxs = np.argsort(X)
        X = X[sort_idxs]
        output = [X]
        for y in Y:
            if y is None:
                output.append(None)
            else:
                y = np.asarray(y)
                if len(y) == 1:
                    output.append(y)
                else:
                    output.append(y[sort_idxs])
    else:
        output = [X]
        output.extend(Y)
    return output

def interval_limit(X_min, X_max, X, *Y):
    X = np.asarray(X)
    X_idx = np.where((X >= X_min) & (X <= X_max))
    return (X[X_idx],) + tuple(np.asarray(y)[X_idx] for y in Y)

def masked_argsort(m_array):
    """
    Runs argsort on a masked array and only returns the argsort of the unmasked items
    """
    return np.argsort(m_array)[:sum(~m_array.mask)]

def continuous_phase(data, op_idx= 0, sep = (1.01) * np.pi, deg = False, shiftmod = 2):
    raw_angle = np.angle(data)
    diff = np.diff(raw_angle)
    sep = abs(sep)
    where_up = list(np.where(diff > sep)[0])
    where_down = list(np.where(diff < -sep)[0])
    value_mods = []
    shift = 0
    def shift_mod(val):
        return ((shiftmod + val) % (2*shiftmod)) - shiftmod
    while True:
        if where_up and where_down:
            if where_up[-1] > where_down[-1]:
                shift = shift_mod(shift - 1)
                where = where_up.pop()
            else:
                shift = shift_mod(shift + 1)
                where = where_down.pop()
        elif where_up:
            shift = shift_mod(shift - 1)
            where = where_up.pop()
        elif where_down:
            shift = shift_mod(shift + 1)
            where = where_down.pop()
        else:
            break
        value_mods.append((where+1, shift * 2 * np.pi))

    if not value_mods:
        if np.average(raw_angle) < -np.pi/4:
            raw_angle += np.pi * 2
        if deg:
            raw_angle *= 180./np.pi
        return raw_angle

    full_shift = np.empty_like(raw_angle)
    last_where, shift = value_mods.pop()
    full_shift[0:last_where] = shift
    while value_mods:
        new_where, shift = value_mods.pop()
        full_shift[last_where:new_where] = shift
        last_where = new_where
    full_shift[last_where:] = 0

    raw_angle -= full_shift
    raw_angle += full_shift[op_idx]
    while raw_angle[op_idx] < -np.pi:
        raw_angle += 2*np.pi
    while raw_angle[op_idx] > np.pi:
        raw_angle -= 2*np.pi

    median = np.sort(raw_angle)[len(raw_angle)/2]
    if median < -np.pi/4:
        raw_angle += np.pi * 2

    if deg:
        raw_angle *= 180./np.pi
    return raw_angle

def logspaced(lower, upper, n_points):
    """
    Not very smart about preserving the number of points with a discontiguous interval set
    """
    log_lower = np.log(lower)
    log_upper = np.log(upper)
    return np.exp(np.linspace(log_lower, log_upper, n_points))

def common_type(nd_array):
    nd_flat = np.asanyarray(nd_array).flatten()
    return reduce(type_reduce, nd_flat, nd_flat[0].__class__)

def type_reduce(type_A, obj_B):
    if type_A is None or obj_B is None:
        return None
    if isinstance(obj_B, type_A):
        return type_A
    if issubclass(type_A, obj_B.__class__):
        return obj_B.__class__
    return None

def argsort(array):
    """
    Highly efficient argsort for pure python, this is also good for
    arrays where you only want the sort in the first dimesion
    """
    return sorted(list(range(len(array))), key=array.__getitem__)


def mag_phase_signed(v, deg = True):
    ang = (np.angle(v, deg = False) + np.pi * 9./4) % np.pi - np.pi/4.
    mag = v * np.exp(-1j * ang)
    if deg:
        ang = 180 / np.pi * ang
    return np.real(mag), ang

def group_delay(F, data, mult = 3e8):
    dang = np.convolve([1, -1], np.angle(data), mode='valid')
    dang[dang > 1 * np.pi] -= 2*np.pi
    dang[dang < -1 * np.pi] += 2*np.pi
    dF = np.convolve([1, -1], F, mode='valid')
    return F[-len(dang):], mult * dang/dF

def first_non_NaN(arr):
    idx_lower = 0
    idx_upper = len(arr)
    N = 1
    if not cmath.isnan(arr[0]):
        return 0
    while idx_lower + N < idx_upper:
        if not cmath.isnan(arr[idx_lower + N]):
            if N == 1:
                return idx_lower + 1
            else:
                idx_lower = idx_lower + N/2
                idx_upper = idx_lower + N
                N = 1
        else:
            N *= 2
    return idx_upper


def search_local_sorted_orig(arr_x, arr_y, val_x_start, val_y):
    idx_start = np.searchsorted(arr_x, val_x_start)
    dval_y_start = arr_y[idx_start+1] - arr_y[idx_start]
    idx_upper = idx_start
    idx_lower = idx_start
    if dval_y_start > 0:
        prev = arr_y[idx_start]
        while True:
            new = arr_y[idx_upper]
            if new < prev:
                break
            prev = new
            idx_upper += 1
            if idx_upper == len(arr_x):
                break
        prev = arr_y[idx_start]
        while True:
            new = arr_y[idx_lower]
            if new > prev:
                break
            prev = new
            idx_lower -= 1
            if idx_lower == -1:
                break
        idx_lower += 1
        idx_offset = np.searchsorted(arr_y[idx_lower : idx_upper], val_y)
    else:
        prev = arr_y[idx_start]
        while True:
            new = arr_y[idx_upper]
            if new > prev:
                break
            prev = new
            idx_upper += 1
            if idx_upper == len(arr_x):
                break
        prev = arr_y[idx_start]
        while True:
            new = arr_y[idx_lower]
            if new < prev:
                break
            prev = new
            idx_lower -= 1
            if idx_lower == -1:
                break
        idx_lower += 1
        idx_offset = -1 - np.searchsorted(arr_y[idx_lower : idx_upper][::-1], val_y)

    idx = idx_lower + idx_offset
    sub_idx = (val_y - arr_y[idx]) / (arr_y[idx + 1] - arr_y[idx])
    frac_x = arr_x[idx] + sub_idx * (arr_x[idx + 1] - arr_x[idx])
    return frac_x, idx, sub_idx


def search_local_sorted(arr_x, arr_y, val_x_start, val_y):
    idx_start = np.searchsorted(arr_x, val_x_start)
    dval_y = arr_y[1:] > arr_y[:-1]
    ddval_y = dval_y[1:] ^ dval_y[:-1]
    idx_convex = np.concatenate([[0], np.nonzero(ddval_y)[0], [len(arr_x)]])
    idx_split = np.searchsorted(idx_convex, idx_start)
    idx_lower = idx_convex[idx_split-1]
    idx_upper = idx_convex[idx_split]

    if arr_y[idx_upper-1] > arr_y[idx_lower]:
        idx_offset = np.searchsorted(arr_y[idx_lower : idx_upper], val_y)
    else:
        idx_offset = -1 - np.searchsorted(arr_y[idx_lower : idx_upper][::-1], val_y)

    idx = idx_lower + idx_offset
    sub_idx = (val_y - arr_y[idx]) / (arr_y[idx + 1] - arr_y[idx])
    frac_x = arr_x[idx] + sub_idx * (arr_x[idx + 1] - arr_x[idx])
    return frac_x, idx, sub_idx


def generate_sections(
    barray,
    reconnect_length = None
):
    Dbarray = (barray[1:] ^ barray[:-1])
    args = np.argwhere(Dbarray).T[0,:] + 1
    pargs = []
    if barray[0]:
        pargs.append([0])
    pargs.append(args)
    if barray[-1]:
        pargs.append([len(barray)-1])
    if len(pargs) > 1:
        args = np.concatenate(pargs)
    assert(len(args) % 2 == 0)
    sections = list(zip(args[::2], args[1::2]))
    if (len(sections) > 0) and (reconnect_length is not None):
        disconnects = [sections[0][0]]
        for idx in range(1, len(sections)):
            _, eidx = sections[idx - 1]
            sidx, _ = sections[idx]
            if (sidx - eidx) > reconnect_length:
                disconnects.append(eidx)
                disconnects.append(sidx)
        disconnects.append(sections[-1][-1])
        sections = list(zip(disconnects[0::2], disconnects[1::2]))
    return sections

def generate_antisections(idx_start, idx_end, sections):
    if not sections:
        return [(idx_start, idx_end)]
    disconnects = []
    for section in sections:
        disconnects.extend(section)

    if disconnects[0] == idx_start:
        disconnects = disconnects[1:]
    else:
        disconnects.insert(0, idx_start)

    if disconnects[-1] == idx_end:
        disconnects = disconnects[:-1]
    else:
        disconnects.append(idx_end)
    return list(zip(disconnects[0::2], disconnects[1::2]))




