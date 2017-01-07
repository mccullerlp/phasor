from collections import namedtuple

from .dictionary_keys import DictKey
from .optics_bases import ElectricalCouplerBase


ElectricalCableBase = namedtuple('ElectricalCableBase', ('element', 'port_name'))


class ElectricalCableVI(ElectricalCableBase):
    basis = 'VI'

    @property
    def V(self):
        return DictKey(
            optic = self.element,
            port = self.element._port_map[self.port_name, 'V'],
        )

    @property
    def I(self):
        return DictKey(
            optic = self.element,
            port = self.element._port_map[self.port_name, 'I'],
        )


class ElectricalCableScattering(ElectricalCableBase):
    basis = 'S'
    impedance = None

    @property
    def to(self):
        return DictKey(
            optic = self.element,
            port = self.element._port_map[self.port_name, 'to'],
        )

    @property
    def out(self):
        return DictKey(
            optic = self.element,
            port = self.element._port_map[self.port_name, 'out'],
        )


class ElectricalPassiveBase(ElectricalCouplerBase):
    _port_map = {
        ('A', 'V') : 'V_A',
        ('A', 'I') : 'I_A',
        ('B', 'V') : 'V_B',
        ('B', 'I') : 'I_B',
    }

    @property
    def A(self):
        return ElectricalCableVI(self, 'A')

    @property
    def B(self):
        return ElectricalCableVI(self, 'B')


class ElectricalAmpBase(ElectricalCouplerBase):
    _port_map = {
        ('in_p', 'V') : 'in_P_V',
        ('in_p', 'V') : 'in_P_I',
        ('in_n', 'V') : 'in_N_V',
        ('in_n', 'V') : 'in_N_I',
        ('out',  'V') : 'out_V',
        ('out',  'V') : 'out_V',
    }

    @property
    def in_p(self):
        return ElectricalCableVI(self, 'in_p')

    @property
    def in_n(self):
        return ElectricalCableVI(self, 'in_n')

    @property
    def out(self):
        return ElectricalCableVI(self, 'out')


class ElectricalSrcBase(ElectricalCouplerBase):
    _port_map = {
        ('out',  'V') : 'out_V',
        ('out',  'I') : 'out_I',
    }

    @property
    def out(self):
        return ElectricalCableVI(self, 'out')


