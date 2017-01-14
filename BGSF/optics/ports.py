# -*- coding: utf-8 -*-
from __future__ import (division, print_function)
from builtins import object

import declarative as decl

from ..math.key_matrix import DictKey

from ..base.ports import(
    ElementKey,
    PortKey,
    MechKey,
    ClassicalFreqKey,
    PortHolderInBase,
    PortHolderOutBase,
    PortHolderInOutBase,
    MechanicalPortHolderIn,
    MechanicalPortHolderOut,
)  # NOQA

from ..signals.ports import(
    SignalPortHolderIn,
    SignalPortHolderOut,
)

QuantumKey = u'Ψ'
RAISE = DictKey({QuantumKey: u'↑'})
LOWER = DictKey({QuantumKey: u'↓'})

PolKEY = u'⤱'
PolS = DictKey({PolKEY: 'S'})
PolP = DictKey({PolKEY: 'P'})

OpticalFreqKey = u'F⇝'


class OpticalPortHolderIn(PortHolderInBase):
    def autoterminations(self, port_map):
        #I don't like having to import from here, but what can you do...
        from .vacuum import VacuumTerminator
        port_map[self.i] = (self, VacuumTerminator)


class OpticalPortHolderOut(PortHolderOutBase):
    pass


class OpticalPortHolderInOut(PortHolderInOutBase):
    def autoterminations(self, port_map):
        #I don't like having to import from here, but what can you do...
        from .vacuum import VacuumTerminator
        port_map[self.i] = (self, VacuumTerminator)


class OpticalNonOriented1PortMixin(object):

    def orient_optical_portsEW(self):
        return (self.Fr,)

    def orient_optical_portsNS(self):
        return (self.Fr,)

class OpticalOriented2PortMixin(object):
    @decl.dproperty
    def facing_cardinal(self, val = None):
        val = self.ooa_params.setdefault('facing_cardinal', val)
        assert(val in ['N', 'S', 'E', 'W', None])
        return val

    def orient_optical_portsEW(self):
        if self.facing_cardinal == 'E':
            return (self.Fr, self.Bk)
        elif self.facing_cardinal == 'W':
            return (self.Bk, self.Fr)
        if self.facing_cardinal is None:
            raise RuntimeError(u"Cardinal facing direction not specified for element {0}".format(self))
        else:
            raise RuntimeError(u"Cardinal facing direction for element {0} is '{1}' but should be 'E' or 'W'".format(self, self.facing_cardinal))

    def orient_optical_portsNS(self):
        if self.facing_cardinal == 'N':
            return (self.Fr, self.Bk)
        elif self.facing_cardinal == 'S':
            return (self.Bk, self.Fr)
        if self.facing_cardinal is None:
            raise RuntimeError(u"Cardinal facing direction not specified for element {0}".format(self))
        else:
            raise RuntimeError(u"Cardinal facing direction for element {0} is '{1}' but should be 'N' or 'S'".format(self, self.facing_cardinal))

class OpticalSymmetric2PortMixin(object):
    def orient_optical_portsEW(self):
        return (self.Fr, self.Bk)

    def orient_optical_portsNS(self):
        return (self.Fr, self.Bk)


class OpticalOriented4PortMixin(object):

    @decl.dproperty
    def facing_cardinal(self, val = None):
        val = self.ooa_params.setdefault('facing_cardinal', val)
        assert(val in ['NE', 'NW', 'SE', 'SW', None])
        return val

    def orient_optical_portsEW(self):
        if self.facing_cardinal == 'NW':
            return (self.BkA, self.FrA)
        elif self.facing_cardinal == 'NE':
            return (self.FrA, self.BkA)
        elif self.facing_cardinal == 'SW':
            return (self.BkA, self.FrA)
        elif self.facing_cardinal == 'SE':
            return (self.FrA, self.BkA)
        else:
            raise RuntimeError(u"No Facing Cardinal direction defined")

    def orient_optical_portsNS(self):
        if self.facing_cardinal == 'NW':
            return (self.FrB, self.BkB)
        elif self.facing_cardinal == 'NE':
            return (self.FrB, self.BkB)
        elif self.facing_cardinal == 'SW':
            return (self.BkB, self.FrB)
        elif self.facing_cardinal == 'SE':
            return (self.BkB, self.FrB)
        else:
            raise RuntimeError(u"No Facing Cardinal direction defined")

class OpticalDegenerate4PortMixin(object):

    @decl.dproperty
    def AOI_deg(self, val = 0):
        val = self.ooa_params.setdefault('AOI_deg', val)
        return val

    #@decl.dproperty
    #def facing_cardinal(self, val = None):
    #    val = self.ooa_params.setdefault('facing_cardinal', val)
    #    if self.AOI_deg == 0:
    #        assert(val in ['N', 'S', 'E', 'W', None])
    #    else:
    #        if self.AOI_deg == 45:
    #            assert(val in ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW', None])
    #        else:
    #            assert(val in ['N', 'S', 'E', 'W', None])
    #    return val

    @decl.mproperty
    def is_4_port(self):
        if self.AOI_deg == 0:
            val = False
        else:
            val = True
        return val

    def orient_optical_portsEW(self):
        if self.facing_cardinal == 'E':
            return (self.FrA, self.BkA)
        elif self.facing_cardinal == 'W':
            return (self.BkA, self.FrA)
        elif self.facing_cardinal == 'NW':
            return (self.BkA, self.FrA)
        elif self.facing_cardinal == 'NE':
            return (self.FrA, self.BkA)
        elif self.facing_cardinal == 'SW':
            return (self.BkA, self.FrA)
        elif self.facing_cardinal == 'SE':
            return (self.FrA, self.BkA)
        if self.facing_cardinal is None:
            if self.AOI_deg == 0 or self.AOI_deg == 45:
                raise RuntimeError(u"Cardinal facing direction not specified for mirror {0}".format(self))
            else:
                raise RuntimeError(u"Cardinal Direction only usable with AOI 0 or 45 deg in mirror {0}".format(self, self.facing_cardinal))
        else:
            if self.AOI_deg == 0:
                raise RuntimeError(u"Cardinal facing direction for mirror {0} is '{1}' but should be 'N' or 'S' for 0 AOI".format(self, self.facing_cardinal))
            elif self.AOI_deg == 45:
                raise RuntimeError(u"Cardinal facing direction for mirror {0} is '{1}' but should be 'NE', 'NW', 'SE', or 'SW' for 45 AOI".format(self, self.facing_cardinal))

    def orient_optical_portsNS(self):
        if self.facing_cardinal == 'N':
            return (self.FrA, self.BkA)
        elif self.facing_cardinal == 'S':
            return (self.BkA, self.FrA)
        elif self.facing_cardinal == 'NW':
            return (self.FrB, self.BkB)
        elif self.facing_cardinal == 'NE':
            return (self.FrB, self.BkB)
        elif self.facing_cardinal == 'SW':
            return (self.BkB, self.FrB)
        elif self.facing_cardinal == 'SE':
            return (self.BkB, self.FrB)
        if self.facing_cardinal is None:
            if self.AOI_deg == 0 or self.AOI_deg == 45:
                raise RuntimeError(u"Cardinal facing direction not specified for mirror {0}".format(self))
            else:
                raise RuntimeError(u"Cardinal Direction only usable with AOI 0 or 45 deg in mirror {0}".format(self, self.facing_cardinal))
        else:
            if self.AOI_deg == 0:
                raise RuntimeError(u"Cardinal facing direction for mirror {0} is '{1}' but should be 'N' or 'S' for 0 AOI".format(self, self.facing_cardinal))
            elif self.AOI_deg == 45:
                raise RuntimeError(u"Cardinal facing direction for mirror {0} is '{1}' but should be 'NE', 'NW', 'SE', or 'SW' for 45 AOI".format(self, self.facing_cardinal))

