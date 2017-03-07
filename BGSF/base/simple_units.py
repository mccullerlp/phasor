"""
TODO: Add additional data to "ref" for a standard width. Ref can be the center, there can be a width, and val is the true (possibly symbolic) value
"""
from __future__ import division, print_function
import declarative

from declarative.substrate import Element

from . import pint


class SimpleUnitfulGroup(declarative.OverridableObject):
    @declarative.dproperty
    def units(self, val):
        if isinstance(val, str):
            val = pint.ureg[val]
        return val

    @declarative.dproperty
    def ref(self, val):
        return val

    @declarative.dproperty
    def val(self, val):
        return val

    @declarative.mproperty
    def refQ(self, val):
        return val * self.units

    @declarative.mproperty
    def valQ(self, val):
        return val * self.units

    def __add__(self, other):
        units_to = self.units
        units_from = other.units
        rescale = units_from / units_to
        assert(rescale.unitless)
        rescale = rescale.to(pint.ureg.dimensionless).magnitude
        #rescale = rescale.m_as(pint.ureg.dimensionless)
        return SimpleUnitfulGroup(
            val = self.val + other.val * rescale,
            ref = self.ref + other.ref * rescale,
            units = self.units,
        )

    def __sub__(self, other):
        units_to = self.units
        units_from = other.units
        rescale = units_from / units_to
        assert(rescale.unitless)
        rescale = rescale.to(pint.ureg.dimensionless).magnitude
        #rescale = rescale.m_as(pint.ureg.dimensionless)
        return SimpleUnitfulGroup(
            val = self.val - other.val * rescale,
            ref = self.ref - other.ref * rescale,
            units = self.units,
        )

    def __mul__(self, other):
        return SimpleUnitfulGroup(
            val = self.val * other,
            ref = self.ref * other,
            units = self.units,
        )

    def __neg__(self):
        return SimpleUnitfulGroup(
            val = -self.val,
            ref = -self.ref,
            units = self.units,
        )

    def __rmul__(self, other):
        return SimpleUnitfulGroup(
            val = other * self.val,
            ref = other * self.ref,
            units = self.units,
        )

    def __div__(self, other):
        return SimpleUnitfulGroup(
            val = self.val / other,
            ref = self.ref / other,
            units = self.units,
        )


class ElementRefValue(SimpleUnitfulGroup, Element):
    ##Inherited from SimpleUnitfulGroup
    #@declarative.dproperty
    #def units(self, val):
    #    print(self, " units: ", val, type(val))
    #    return val

    #TODO integrate or name this better
    @declarative.mproperty
    def ooa_name(self, val):
        return val

    @declarative.dproperty
    def ooa_units_scale(self):
        units_to = self.units
        units_from = pint.ureg[self.ooa_params.units]
        rescale = units_from / units_to
        assert(rescale.unitless)
        #TODO check these methods (only seem present on newer pint)
        #return rescale.m_as(pint.ureg.dimensionless)
        rescale.to(pint.ureg.dimensionless).magnitude
        return rescale.to(pint.ureg.dimensionless).magnitude

    @declarative.dproperty
    def ref(self):
        val = self.ooa_params.ref
        if val is not None:
            return val * self.ooa_units_scale
        else:
            return None

    @declarative.dproperty
    def val(self):
        val = self.ooa_params.val
        if val is not None:
            return val * self.ooa_units_scale
        else:
            return None

    @declarative.mproperty
    def fitter_parameter(self):
        root = self.root
        names = [self.ooa_name]
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


