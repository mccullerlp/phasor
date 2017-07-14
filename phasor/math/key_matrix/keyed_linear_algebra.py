# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from builtins import object
import numbers

from .dictionary_keys import (
    DictKey,
)


class ForewardDictMatrix(object):
    def __init__(self, vdict = None, _premap = None):
        if _premap is not None:
            self.from_to_map = _premap
        else:
            self.from_to_map = {}

        if vdict is not None:
            for key_pair, value in list(vdict.items()):
                from_key, to_key = key_pair
                self[from_key, to_key] = value

    def __getitem__(self, key):
        from_key, to_key = key
        to_map = self.from_to_map[from_key]
        return to_map[to_key]

    def __setitem__(self, key, value):
        from_key, to_key = key
        to_map = self.from_to_map.setdefault(from_key, {})
        to_map[to_key] = value
        return

    def __delitem__(self, key):
        from_key, to_key = key
        to_map = self.from_to_map.get(from_key, None)
        if to_map is None:
            raise KeyError()
        del to_map[to_key]
        if not to_map:
            del self.from_to_map[from_key]
        return

    def __iter__(self):
        for from_key, to_map in list(self.from_to_map.items()):
            for to_key, value in list(to_map.items()):
                yield from_key, to_key, value
        return

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            from_to_map_new = {}
            for from_key, to_map in list(self.from_to_map.items()):
                to_map_new = {}
                from_to_map_new[from_key] = to_map_new
                for to_key, value in list(to_map.items()):
                    try:
                        other_to_map = other.from_to_map[to_key]
                    except KeyError:
                        pass
                    else: #runs only if other_to_map was defined
                        for other_to_key, other_value in list(other_to_map.items()):
                            try:
                                to_map_new[other_to_key] += value * other_value
                            except KeyError:
                                to_map_new[other_to_key] = value * other_value
            return self.__class__(_premap = from_to_map_new)
        elif isinstance(other, numbers.Number):
            from_to_map_new = {}
            for from_key, to_map in list(self.from_to_map.items()):
                to_map_new = {}
                from_to_map_new[from_key] = to_map_new
                for to_key, value in list(to_map.items()):
                    to_map_new[to_key] =  value * other
            return self.__class__(_premap = from_to_map_new)
        return NotImplemented

    def __rmul__(self, other):
        return NotImplemented
        if isinstance(other, numbers.Number):
            from_to_map_new = {}
            for from_key, to_map in list(self.from_to_map.items()):
                to_map_new = {}
                from_to_map_new[from_key] = to_map_new
                for to_key, value in list(to_map.items()):
                    to_map_new[to_key] =  other * value
            return self.__class__(_premap = from_to_map_new)
        return NotImplemented

    def data_print(self):
        for from_key, to_map in list(self.from_to_map.items()):
            for to_key, value in list(to_map.items()):
                print("{0: <20}:{1: <20}={2}".format(from_key, to_key, value))

    def tensor_product(
        self,
        other,
        into = None,
        validate = None,
    ):
        #insert tensor product
        if into is None:
            into = ForewardDictMatrix()
        for s_A, s_B, s_Val in self:
            for o_A, o_B, o_Val in other:
                key1 = o_A | s_A
                key2 = o_B | s_B
                if validate is not None:
                    validate(key1)
                    validate(key2)
                into[key1, key2] = s_Val * o_Val
        return into

    def insert(
        self,
        into = None,
        validate = None,
    ):
        #insert tensor product
        if into is None:
            into = ForewardDictMatrix()
        for s_A, s_B, s_Val in self:
            if validate is not None:
                validate(s_A)
                validate(s_B)
            into[s_A, s_B] = s_Val
        return into

