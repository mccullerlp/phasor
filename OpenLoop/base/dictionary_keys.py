# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from ..utilities.future_from_2 import str, object

from collections import Mapping as MappingABC
import declarative


class DictKey(MappingABC):
    __slots__ = ('_dict', 'prev_hash')
    def __init__(self, *args, **kwargs):
        self._dict = kwargs
        if args:
            self._dict.update(args[0])

    def copy_update(self, **kwargs):
        newdict = dict(self._dict)
        newdict.update(**kwargs)
        return self.__class__(**newdict)

    def __hash__(self):
        try:
            return self.prev_hash
        except AttributeError:
            pass
        l = tuple(sorted(self._dict.items()))
        self.prev_hash = hash(l)
        return self.prev_hash

    def __iter__(self):
        return iter(self._dict)

    def __getitem__(self, key):
        return self._dict[key]

    def get(self, key, default = declarative.NOARG):
        if default is declarative.NOARG:
            return self._dict[key]
        return self._dict.get(key, default)

    def __len__(self):
        return len(self._dict)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._dict == other._dict

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return False
        #TODO this is probably megaslow. Should likely use id or hash
        l1 = tuple(sorted(self._dict.items()))
        o1 = tuple(sorted(self._dict.items()))
        return l1 < o1

    def __repr__(self):
        l = tuple(sorted(self._dict.items()))
        #print(unicode(repr(l), 'utf-8'))
        l2 = [u'{0}:{1}'.format(i, j) for i, j in l]
        return u"DK{{{0}}}".format(u'|'.join(l2))

    def __or__(self, other):
        cp = dict(self._dict)
        cp.update(other._dict)
        return self.__class__(cp)

    def iteritems(self):
        return list(self._dict.items())

    def kv_contains(self, k, v):
        v2 = self._dict.get(k, declarative.NOARG)
        return v == v2

    def __and__(self, other):
        if len(self) > len(other):
            larger = self
            smaller = other
        else:
            larger = other
            smaller = self
        newdict = dict()
        for k, v in list(smaller.items()):
            if larger.kv_contains(k, v):
                newdict[k] = v
        return self.__class__(**newdict)

    def contains(self, other):
        for k, v in list(other.items()):
            if not self.kv_contains(k, v):
                return False
        return True

    def without_keys(self, *keys):
        cp = dict(self._dict)
        for key in keys:
            del cp[key]
        return self.__class__(**cp)

    def purge_keys(self, *keys):
        cp = dict(self._dict)
        for key in keys:
            try:
                del cp[key]
            except KeyError:
                pass
        return self.__class__(**cp)

    def replace_keys(self, key_dict, *more_key_dicts):
        cp = dict(self._dict)
        for key, val in list(key_dict.items()):
            cp[key] = val
        if more_key_dicts:
            for key_dict in more_key_dicts:
                for key, val in list(key_dict.items()):
                    cp[key] = val
        return self.__class__(**cp)

    def subkey_has(self, other):
        try:
            for k, v in list(other.items()):
                v2 = self._dict[k]
                if v != v2:
                    return False
        except KeyError:
            return False
        return True

    def __sub__(self, other):
        cp = dict(self._dict)
        for k, v in list(other._dict.items()):
            assert(cp[k] == v)
            del cp[k]
        return self.__class__(cp)

    def __deepcopy__(self, memo):
        #by the immutibility of this object and anything it stores, it is OK to return the same thing
        return self

    def __copy__(self):
        #by the immutibility of this object and anything it stores, it is OK to return the same thing
        return self


class FrequencyKey(object):
    __slots__ = ('F_dict', 'prev_hash', 'prev_tup')
    def __init__(self, F_dict):
        self.F_dict = F_dict

    def DC_is(self):
        return not self.F_dict

    def __hash__(self):
        try:
            return self.prev_hash
        except AttributeError:
            pass
        self.prev_hash = hash(self.hash_tuple())
        return self.prev_hash

    def hash_tuple(self):
        try:
            return self.prev_tup
        except AttributeError:
            pass
        self.prev_tup = tuple(sorted((f, n) for f, n in list(self.F_dict.items()) if n != 0))
        return self.prev_tup

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.F_dict == other.F_dict

    def __getitem__(self, F):
        return self.F_dict[F]

    def frequency(self):
        F_sum = 0
        for F, n in list(self.F_dict.items()):
            if n != 0:
                #TODO maybe move the .val somewhere else
                F_sum += F.F_Hz.val * n
        return F_sum

    def __repr__(self):
        l = tuple(sorted(((F.name, n) for F, n in list(self.F_dict.items()))))
        flist = []
        for Fname, n in l:
            if n == 1:
                flist.append(u'+' + Fname)
            elif n == -1:
                flist.append(u'-' + Fname)
            elif n > 1:
                flist.append(u'+' + str(n) + Fname)
            elif n < -1:
                flist.append(str(n) + Fname)
        if not flist:
            flist.append('0')
        return ''.join(flist)

    def __add__(self, other):
        F_dict = dict(self.F_dict)
        for F, n in list(other.F_dict.items()):
            current_idx = self.F_dict.get(F, 0)
            new_idx = current_idx + n
            if new_idx == 0 and F in F_dict:
                del F_dict[F]
            else:
                F_dict[F] = new_idx
        return self.__class__(F_dict)

    def __sub__(self, other):
        F_dict = dict(self.F_dict)
        for F, n in list(other.F_dict.items()):
            current_idx = self.F_dict.get(F, 0)
            new_idx = current_idx - n
            if new_idx == 0 and F in F_dict:
                del F_dict[F]
            else:
                F_dict[F] = new_idx
        return self.__class__(F_dict)

    def __rmul__(self, other):
        F_dict = dict()
        for F, n in list(self.F_dict.items()):
            F_dict[F] = other * n
        return self.__class__(F_dict)

    def __neg__(self):
        F_dict = dict()
        for F, n in list(self.F_dict.items()):
            current_idx = self.F_dict[F]
            F_dict[F] = -current_idx
        return self.__class__(F_dict)

