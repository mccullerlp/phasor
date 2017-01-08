"""
"""
from __future__ import print_function
from builtins import range, object

import numpy as np
import warnings

from ..math.key_matrix.keymatrix import (
    KVSpace,
    KeyVector,
    KeyMatrix,
    key_matrix_eye,
)

from ..math.key_matrix.dictionary_keys import (
    DictKey,
    FrequencyKey,
)

from ..math.key_matrix.keyed_linear_algebra import (
    ForewardDictMatrix,
)

from BGSF.utilities.progressbar import ProgressBar


class ElectricalSystem(object):
    pi            = np.pi
    i             = 1j
    math          = np

    coupling_matrix        = None
    coupling_matrix_rt     = None
    coupling_matrix_rt_inv = None

    from .elements import (
        Frequency,
        VoltageSource,
        CurrentSource,
        VoltageSourceBalanced,
        CurrentSourceBalanced,
        TerminatorMatched,
        TerminatorOpen,
        TerminatorShorted,
        Connection,
        Cable,
        TerminatorResistor,
        TerminatorCapacitor,
        TerminatorInductor,
        SeriesResistor,
        SeriesCapacitor,
        SeriesInductor,
        OpAmp,
        VAmp,
        SMatrix2PortBase,
        SMatrix1PortBase,
    )

    Z_termination = 50

    def __init__(
        self,
        frequency = None,
        pi       = None,
    ):
        if pi is not None:
            self.pi = pi

        if frequency is not None:
            self.frequency = frequency
            self.frequency_obj = self.Frequency(frequency, name = 'F')
        else:
            self.frequency = None
            self.frequency_obj = None

        self.elements_named        = {}
        self.elements              = set()

    def number(self, num):
        return num

    def setup_system(self, field_space = None, dtype = object):
        if field_space is None:
            field_space = KVSpace('field_ports', dtype = dtype)
        self.field_space = field_space
        self.coupling_matrix = KeyMatrix(field_space, field_space)

        for element in self.elements:
            element.system_setup_coupling(self)

        mat_eye = key_matrix_eye(field_space)
        self.coupling_matrix_rt = mat_eye - self.coupling_matrix
        #self.coupling_matrix_rt = self.coupling_matrix - mat_eye
        return

    def solve_system(self):
        arr = self.coupling_matrix_rt.array.astype(complex)
        rt_inv = np.empty_like(arr)
        if len(arr.shape) == 3:
            for idx in ProgressBar(list(range(arr.shape[2]))):
                rt_inv[:,:,idx] = np.linalg.inv(arr[:,:,idx])
        else:
            rt_inv[:] = np.linalg.inv(arr)

        self.coupling_matrix_rt_inv = self.coupling_matrix_rt.backmap_array_inv(rt_inv)
        return

    def view_transfer(self, vdict_from, vdict_to, F = None, **kwargs):
        total_xfer = 0
        if F is None:
            F = self.freq_key({self.frequency_obj: 1})
        elif isinstance(F, FrequencyKey):
            pass
        elif isinstance(F, dict):
            F = self.freq_key(F)
        else:
            F = self.freq_key({F:1})
        F = DictKey(F = F)
        for kto, val_to in list(vdict_to.items()):
            for kfrom, val_from in list(vdict_from.items()):
                key_to = kto | F
                key_from = kfrom | F
                try:
                    rt_inv_val =  self.coupling_matrix_rt_inv[key_to, key_from]
                except KeyError:
                    rt_inv_val = 0
                #self.dk_validate(key_to)
                #self.dk_validate(key_from)
                total_xfer = total_xfer + val_to * val_from * rt_inv_val
        return total_xfer

    def freq_key(self, f_dict):
        return FrequencyKey(f_dict)

    _F_basis = None
    @property
    def F_basis(self):
        if self._F_basis is not None:
            return self._F_basis
        if self.frequency_obj is not None:
            F_basis = set([self.frequency_obj])
        else:
            F_basis = set()
        for element in self.elements:
            F_basis.update(element.frequencies_needed())
        self._F_basis = F_basis
        return self._F_basis

    _F_key_basis = None
    @property
    def F_key_basis(self):
        if self._F_key_basis is not None:
            return self._F_key_basis
        F_key_basis = [{}]
        for F in self.F_basis:
            F_combinatoric_prev = F_key_basis
            F_key_basis = []
            for fdict in F_combinatoric_prev:
                for idx in range(F.order_min, F.order_max + 1):
                    f_dict_cp = dict(fdict)
                    f_dict_cp[F] = idx
                    F_key_basis.append(f_dict_cp)
        self._F_key_basis = tuple(self.freq_key(fdict) for fdict in F_key_basis)
        return self._F_key_basis

    def dk_validate(self, dk):
        def split(element, port, F):
            return
        split(**dk)
        return dk

    def coupling_matrix_print(self):
        for key_from, key_to, value in self.coupling_matrix:
            print("[{0: <40},{1: <40}]={2}".format(key_from, key_to, value))

    def coupling_matrix_rt_inv_print(self):
        for key_from, key_to, value in self.coupling_matrix_rt_inv:
            print("[{0: <40},{1: <40}]={2}".format(key_from, key_to, value))

    def include(self, element):
        if element in self.elements:
            return
        self.elements.add(element)
        if element.name is not None:
            if element.name in self.elements_named:
                warnings.warn("Multiple elements added with name {0}, may be confusing".format(element.name))
            self.elements_named[element.name] = element
        for sub_element in element.linked_elements():
            self.include(sub_element)

    def __ilshift__(self, element):
        self.include(element)
        return self


