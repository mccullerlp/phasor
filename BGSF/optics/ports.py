# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print

from ..key_matrix import DictKey

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

from .bases import (
    OOA_ASSIGN,
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
    def __init__(
        self,
        facing_cardinal = None,
        **kwargs
    ):
        super(OpticalOriented2PortMixin, self).__init__(**kwargs)
        assert(facing_cardinal in ['N', 'S', 'E', 'W', None])
        self.facing_cardinal = facing_cardinal

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
    def __init__(
        self,
        facing_cardinal = None,
        **kwargs
    ):
        super(OpticalOriented2PortMixin, self).__init__(**kwargs)
        OOA_ASSIGN(self).facing_cardinal = facing_cardinal
        assert(self.facing_cardinal in ['NE', 'NW', 'SE', 'SW', None])

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
    def __init__(
        self,
        facing_cardinal = None,
        AOI_deg         = 0,
        **kwargs
    ):
        super(OpticalDegenerate4PortMixin, self).__init__(**kwargs)
        OOA_ASSIGN(self).AOI_deg = AOI_deg
        OOA_ASSIGN(self).facing_cardinal = facing_cardinal

        if self.AOI_deg == 0:
            assert(self.facing_cardinal in ['N', 'S', 'E', 'W', None])
            self.is_4_port = False
        else:
            if self.AOI_deg == 45:
                assert(self.facing_cardinal in ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW', None])
            else:
                assert(self.facing_cardinal in ['N', 'S', 'E', 'W', None])
            self.is_4_port = True

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

