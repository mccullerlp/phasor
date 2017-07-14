# -*- coding: utf-8 -*-
"""
TODO: Add additional data to "ref" for a standard width. Ref can be the center, there can be a width, and val is the true (possibly symbolic) value
"""
from __future__ import division, print_function, unicode_literals
import declarative

from ..base.autograft import Element

#from . import pint


class PolarizationCPLG(declarative.OverridableObject):
    @declarative.dproperty
    def Scplg(self, val):
        return val

    @declarative.dproperty
    def ScplgC(self):
        return self.Scplg.conjugate()

    @declarative.dproperty
    def Pcplg(self, val):
        return val

    @declarative.dproperty
    def PcplgC(self):
        return self.Pcplg.conjugate()


class ComplexCplg(declarative.OverridableObject):
    @declarative.dproperty
    def cplg(self, val):
        return val

    @declarative.dproperty
    def cplgC(self):
        return self.cplg.conjugate()


class TransLRT(declarative.OverridableObject):
    @declarative.dproperty
    def L(self, val):
        return val

    @declarative.dproperty
    def R(self, val):
        return val

    @declarative.dproperty
    def T(self, val):
        return val


class TransLRTInner(Element):
    ##Inherited from SimpleUnitfulGroup
    #@declarative.dproperty
    #def units(self, val):
    #    print(self, " units: ", val, type(val))
    #    return val

    #TODO integrate or name this better
    @declarative.mproperty
    def ctree_name(self, val):
        return val

    @declarative.dproperty
    def ref(self):
        val = self.ctree.ref
        if val is not None:
            return val * self.ctree_units_scale
        else:
            return None

    @declarative.dproperty
    def val(self):
        val = self.ctree.val
        if val is not None:
            return val * self.ctree_units_scale
        else:
            return None

    @declarative.mproperty
    def fitter_parameter(self):
        root = self.root
        names = [self.ctree_name]
        current = self.parent
        while current is not root:
            names.append(current.name_child)
            current = current.parent
        return tuple(names[::-1])

    @declarative.mproperty
    def fitter_data(self):
        #TODO: provide real units rather than the str version
        def fitter_inject(ooa, value, ivalue):
            for key in self.fitter_parameter:
                ooa = ooa[key]
            ooa.val   = value
            ooa.ref   = ivalue
            ooa.units = str(self.units)

        def fitter_reinject(ooa, value):
            for key in self.fitter_parameter:
                ooa = ooa[key]
            ooa.val = value
            ooa.ref = value
            ooa.units = str(self.units)

        def fitter_initial(ooa):
            for key in self.fitter_parameter:
                ooa = ooa[key]
            val = ooa.get('ref', declarative.NOARG)
            if val is declarative.NOARG:
                val = ooa.get('val', None)
            return val

        #TODO: fix name vs. name_global
        return [declarative.FrozenBunch(
            parameter_key = self.fitter_parameter,
            units         = str(self.units),
            name          = self.name_system,
            name_global   = self.name_system,
            initial       = fitter_initial,
            inject        = fitter_inject,
            reinject      = fitter_reinject,
        )]


