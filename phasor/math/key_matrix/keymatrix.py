"""
"""
from __future__ import division, print_function
#from builtins import range
#from builtins import object
import declarative

import warnings
import numpy as np


class KVSpace(object):
    _key_map_inverse = None
    dtype = np.float64
    name = None

    def __init__(
        self,
        name = None,
        keys = (),
        dtype = None,
        frozen = False,
        contravariant = False,
        _inverse = None,
    ):
        if dtype is not None:
            self.dtype = dtype
        if name is not None:
            self.name = name
        self._key_set = set(keys)
        self.contravariant = contravariant
        self._inverse = _inverse
        if frozen:
            self.freeze()
        return

    def copy(self):
        return self.__class__(
            name = self.name,
            keys = self._key_set,
            dtype = self.dtype,
        )

    def inverse(self):
        if self._inverse is not None:
            return self._inverse
        self.freeze()
        self._inverse = self.__class__(
            name          = self.name,
            keys          = self._key_set,
            dtype         = self.dtype,
            frozen        = True,
            contravariant = not self.contravariant,
            _inverse      = self,
        )
        return self._inverse

    def frozen_is(self):
        return self._key_map_inverse is not None

    def freeze(self):
        if self.frozen_is():
            return
        self._key_set = frozenset(self._key_set)
        keylist = list(self._key_set)
        keylist.sort()
        keymap = dict()
        for idx, key in enumerate(keylist):
            keymap[key] = idx


        self._key_map = keymap
        #the append is to force a 1D array even if all the keys are tuples
        keylist.append(None)
        self._key_map_inverse = np.asarray(keylist, dtype=object)[:-1]
        self._key_map_inverse.setflags(write = False)
        return

    def __len__(self):
        return len(self._key_set)

    def keys_add(self, *args):
        if self.frozen_is():
            for key in args:
                if key not in self._key_set:
                    raise RuntimeError("Cannot add keys ({0}) to frozen key group".format(repr(key)))
        else:
            self._key_set.update(args)
        return

    def __contains__(self, key):
        return key in self._key_set

    def keys_iter(self):
        self.freeze()
        return iter(self._key_set)

    def key_map(self, key):
        self.freeze()
        return self._key_map[key]

    def idx_map(self, idx):
        self.freeze()
        return self._key_map_inverse[idx]

    def idx_map_full(self):
        self.freeze()
        return self._key_map_inverse


class KVObjectSpace(KVSpace):
    dtype = object


class KVFloatSpace(KVSpace):
    dtype = np.float64


class KVComplexSpace(KVSpace):
    dtype = np.complex128


class KeyLinearBase(object):
    def __init__(self, dtype):
        self._memoize_count = 1
        self._must_test_shape = False
        self.dtype = dtype

    def memoize_prevent(self):
        self._memoize_count = float('NaN')

    def _maxshape(self):
        maxshape = np.array([])
        if self.dtype == object:
            return tuple(maxshape)
        if self._must_test_shape:
            for key_pair, value in list(self._data_map.items()):
                shape = np.array(np.asanyarray(value).shape)
                if len(shape) > len(maxshape):
                    maxshape, shape = shape, maxshape
                expand_idx = (shape == 1)
                shape[expand_idx] = maxshape[expand_idx]
                maxshape_reduced = maxshape[:len(shape)]
                expand_idx = (maxshape_reduced == 1)
                maxshape[expand_idx] = shape[expand_idx]
                if any(shape != maxshape_reduced):
                    raise RuntimeError("Matrix contains unbroadcastable shapes! {0} !=> {1}".format(shape, maxshape))
                if len(maxshape) == 0:
                    self._must_test_shape = False
        return tuple(maxshape)


class KeyVectorBase(KeyLinearBase):

    def __init__(
        self,
        vspace,
        _premap = None,
    ):
        super(KeyVectorBase, self).__init__(dtype = vspace.dtype)
        self.vspace = vspace
        if _premap is None:
            self._data_map = {}
        else:
            self._data_map = _premap
            self._must_test_shape = True

    def __getitem__(self, key):
        return self._data_map[key]

    def get(self, key, default):
        return self._data_map.get(key, default)

    def items(self):
        return self._data_map.items()

    def keys(self):
        return self._data_map.keys()

    def __len__(self):
        return len(self._data_map)

    def __setitem__(self, key, value):
        self._memoize_count += 1
        self.vspace.keys_add(key)
        self._data_map[key] = value
        if len(np.asanyarray(value).shape) > 0:
            self._must_test_shape = True

    def add_by(self, key, value):
        self._memoize_count += 1
        self.vspace.keys_add(key)
        try:
            self._data_map[key] += value
        except KeyError:
            self._data_map[key] = value
        if len(np.asanyarray(value).shape) > 0:
            self._must_test_shape = True

    def __delitem__(self, key):
        self._memoize_count += 1
        del self._data_map[key]

    def __iter__(self):
        return iter(list(self._data_map.items()))

    def iterkeys(self):
        return list(self._data_map.keys())


class KeyMatrixBase(KeyLinearBase):

    def __init__(
        self,
        vspace_from,
        vspace_to,
        _premap = None,
    ):
        super(KeyMatrixBase, self).__init__(dtype = np.result_type(vspace_to.dtype, vspace_from.dtype))
        self.vspace_from = vspace_from
        self.vspace_to = vspace_to
        if _premap is None:
            self._data_map = {}
        else:
            self._data_map = _premap
            self._must_test_shape = True

    def __getitem__(self, key_pair):
        return self._data_map[key_pair]

    def get(self, key_from, key_to, default):
        return self._data_map.get((key_from, key_to), default)

    def __len__(self):
        return len(self._data_map)

    def __setitem__(self, key_pair, value):
        self._memoize_count += 1
        key_from, key_to = key_pair
        self.vspace_from.keys_add(key_from)
        self.vspace_to.keys_add(key_to)
        self._data_map[key_pair] = value
        if len(np.asanyarray(value).shape) > 0:
            self._must_test_shape = True

    def multiply_by(self, key_from, key_to, value):
        self._memoize_count += 1
        self.vspace_from.keys_add(key_from)
        self.vspace_to.keys_add(key_to)
        key_pair = key_from, key_to
        try:
            self._data_map[key_pair] *= value
        except KeyError:
            self._data_map[key_pair] = value
        if len(np.asanyarray(value).shape) > 0:
            self._must_test_shape = True

    def __iter__(self):
        for key_pair, value in list(self._data_map.items()):
            key_from, key_to = key_pair
            yield key_from, key_to, value

    def keys(self):
        return self._data_map.keys()

    def items(self):
        return self._data_map.items()

    def set_nullable(self, key_to, key_from, value):
        self._memoize_count += 1
        if not key_to in self.vspace_to or not key_from in self.vspace_from:
            return False
        self._data_map[key_from, key_to] = value
        if len(np.asanyarray(value).shape) > 0:
            self._must_test_shape = True
        return True

    def __delitem__(self, key_pair):
        self._memoize_count += 1
        del self._data_map[key_pair]

    def fill_from_pair_map(self, key_pair_map):
        for key_pair, value in list(key_pair_map.items()):
            self[key_pair] = value

    def fill_from_nested_map(self, from_to_nested_map):
        self._memoize_count += 1
        for key_from, to_nested_map in list(from_to_nested_map.items()):
            self.vspace_from.keys_add(key_from)
            for key_to, value in list(to_nested_map.items()):
                self.vspace_to.keys_add(key_to)
                self._data_map[key_from, key_to] = value


class KeyVector(KeyVectorBase):

    def __init__(self, vspace, **kwargs):
        super(KeyVector, self).__init__(vspace, **kwargs)
        self._memoize_array_count = 0
        self._memoize_array = None

    def params_set(self, **kwargs):
        self.kw_params.update(kwargs)

    @property
    def array(self):
        if self._memoize_array_count != self._memoize_count:
            maxshape = self._maxshape()
            arr = np.zeros(tuple(maxshape) + (len(self.vspace),), dtype = self.dtype)
            for key, value in list(self._data_map.items()):
                arr[..., self.vspace.key_map(key)] = value
            self._memoize_array = arr
            self._memoize_array_count = self._memoize_count
            return arr
        else:
            return self._memoize_array

    @property
    def row(self):
        return np.matrix(self.array)

    @property
    def col(self):
        return np.matrix(self.array).T

    def backmap_vector(self, array):
        array = np.asarray(array)
        nz_idx = array.nonzero()[-1]
        matrix_map = {}
        for idx in nz_idx:
            key = self.vspace.idx_map(idx)
            value = array[..., idx]
            matrix_map[key] = value
        new_keyvec = self.__class__(
            vspace = self.vspace,
            _premap = matrix_map,
        )
        return new_keyvec


class KeyMatrix(KeyMatrixBase):

    def __init__(
        self,
        vspace_from,
        vspace_to,
        **kwargs
    ):
        super(KeyMatrix, self).__init__(vspace_from, vspace_to, **kwargs)
        self._memoize_array_count = 0
        self._memoize_array = None

    def params_set(self, **kwargs):
        self._memoize_count += 1
        self.kw_params.update(kwargs)

    @declarative.mproperty
    def idx_dict(self):
        newmap = dict()
        for (k1, k2), edge in self._data_map.items():
            k1 = self.vspace_from.key_map(k1)
            k2 = self.vspace_to.key_map(k2)
            newmap[k1, k2] = edge
        return newmap

    @property
    def array(self):
        if self._memoize_array_count != self._memoize_count:
            maxshape = self._maxshape()
            arr = np.zeros(tuple(maxshape) + (len(self.vspace_to), len(self.vspace_from)), dtype = self.dtype)
            for key_pair, value in list(self._data_map.items()):
                key_from, key_to = key_pair
                arr[
                    ...,
                    self.vspace_to.key_map(key_to),
                    self.vspace_from.key_map(key_from)
                ] = value
            self._memoize_array = arr
            self._memoize_array_count = self._memoize_count
            return arr
        else:
            return self._memoize_array

    @property
    def array_T(self):
        return self.array.T

    @property
    def mat(self):
        return np.matrix(self.array)

    @property
    def mat_T(self):
        return self.mat.T

    def index_map(self, key_from, key_to):
        idx_from = self.vspace_from.key_map[key_from]
        idx_to = self.vspace_to.key_map[key_to]
        return idx_from, idx_to

    def backmap_array(self, array):
        vspace_from = self.vspace_from
        vspace_to   = self.vspace_to
        array = np.asarray(array)

        if len(array.shape) > 2:
            array_2d = np.any(array, axis = 0)
            while len(array_2d.shape) > 2:
                array_2d = np.any(array_2d, axis = 0)
            nz_idx_from, nz_idx_to = array_2d.nonzero()
        else:
            nz_idx_from, nz_idx_to = array.nonzero()
        matrix_map = {}
        for idx_count in range(len(nz_idx_from)):
            idx_from = nz_idx_from[idx_count]
            idx_to = nz_idx_to[idx_count]
            key_from = vspace_from.idx_map(idx_from)
            key_to = vspace_to.idx_map(idx_to)
            value = array[..., idx_from, idx_to]
            matrix_map[key_from, key_to] = value
        new_keymat = self.__class__(
            vspace_from = vspace_from,
            vspace_to = vspace_to,
            _premap = matrix_map,
        )
        return new_keymat

    def backmap_array_inv(self, array):
        vspace_from = self.vspace_to
        vspace_to   = self.vspace_from
        array = np.asarray(array)
        if len(array.shape) == 3:
            array_2d = np.any(array, axis = 2)
            nz_idx_from, nz_idx_to = array_2d.nonzero()
        else:
            nz_idx_from, nz_idx_to = array.nonzero()
        matrix_map = {}
        for idx_count in range(len(nz_idx_from)):
            idx_from = nz_idx_from[idx_count]
            idx_to = nz_idx_to[idx_count]
            key_from = vspace_from.idx_map(idx_from)
            key_to = vspace_to.idx_map(idx_to)
            value = array[..., idx_from, idx_to]
            matrix_map[key_from, key_to] = value
        new_keymat = self.__class__(
            vspace_from = vspace_from,
            vspace_to = vspace_to,
            _premap = matrix_map,
        )
        return new_keymat

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        assert(self.vspace_to is other.vspace_to)
        assert(self.vspace_from is other.vspace_from)

        #make a copy
        premap = dict(self._data_map)
        for key_pair, value in list(other._data_map.items()):
            try:
                v = premap[key_pair]
                premap[key_pair] = v + value
            except KeyError:
                premap = value
        return KeyMatrix(self.vspace_from, self.vspace_to, _premap = premap)

    def __sub__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        assert(self.vspace_to is other.vspace_to)
        assert(self.vspace_from is other.vspace_from)

        #make a copy
        premap = dict(self._data_map)
        for key_pair, value in list(other._data_map.items()):
            try:
                v = premap[key_pair]
                premap[key_pair] = v - value
            except KeyError:
                premap[key_pair] = -value
        return KeyMatrix(self.vspace_from, self.vspace_to, _premap = premap)


def key_matrix_eye(vspace):
    _premap = {}
    if not vspace.frozen_is():
        warnings.warn("Should only generate an eye matrix from frozen vector space")
    for key in vspace.keys_iter():
        _premap[key, key] = 1
    return KeyMatrix(vspace, vspace, _premap = _premap)



