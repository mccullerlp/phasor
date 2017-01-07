"""
TODO: Add additional data to "ref" for a standard width. Ref can be the center, there can be a width, and val is the true (possibly symbolic) value
"""
from __future__ import division, print_function

from declarative import (
    OverridableObject,
    dproperty,
    mproperty,
    FrozenBunch,
    NOARG,
)

from declarative.substrate import Element

from .units import (
    units_lookup,
    units_lookup_dim,
)


class SimpleUnitfulGroup(OverridableObject):
    @dproperty
    def units(self, val):
        return val

    @dproperty
    def ref(self, val):
        return val

    @dproperty
    def val(self, val):
        return val

    def __add__(self, other):
        units_to = self.units
        type_to = units_lookup[units_to]
        units_from = other.units
        type_from = units_lookup[units_from]
        assert(type_to.dim == type_from.dim)
        rescale = type_from.scale / type_to.scale
        return SimpleUnitfulGroup(
            val = self.val + other.val * rescale,
            ref = self.ref + other.ref * rescale,
            units = self.units,
        )

    def __sub__(self, other):
        units_to = self.units
        type_to = units_lookup[units_to]
        units_from = other.units
        type_from = units_lookup[units_from]
        assert(type_to.dim == type_from.dim)
        rescale = type_from.scale / type_to.scale
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
    @dproperty
    def units(self, val):
        return val

    #TODO integrate or name this better
    @mproperty
    def pname(self, val):
        return val

    @dproperty
    def ooa_units_scale(self):
        units_to = self.units
        type_to = units_lookup[units_to]
        units_from = self.ooa_params.units
        type_from = units_lookup[units_from]
        assert(type_to.dim == type_from.dim)
        return type_from.scale / type_to.scale

    @dproperty
    def ref(self):
        val = self.ooa_params.ref
        if val is not None:
            return val * self.ooa_units_scale
        else:
            return None

    @dproperty
    def val(self):
        val = self.ooa_params.val
        if val is not None:
            return val * self.ooa_units_scale
        else:
            return None

    @mproperty
    def fitter_parameter(self):
        root = self.root
        names = [self.pname]
        current = self.parent
        while current is not root:
            names.append(current.name_child)
            current = current.parent
        return tuple(names[::-1])

    @mproperty
    def fitter_data(self):
        def fitter_inject(ooa, value, ivalue):
            for key in self.fitter_parameter:
                ooa = ooa[key]
            ooa.val   = value
            ooa.ref   = ivalue
            ooa.units = self.units

        def fitter_reinject(ooa, value):
            for key in self.fitter_parameter:
                ooa = ooa[key]
            ooa.val = value
            ooa.ref = value
            ooa.units = self.units

        def fitter_initial(ooa):
            for key in self.fitter_parameter:
                ooa = ooa[key]
            val = ooa.get('ref', NOARG)
            if val is NOARG:
                val = ooa.get('val', None)
            return val

        return [FrozenBunch(
            parameter_key = self.fitter_parameter,
            units         = self.units,
            name          = self.name_system,
            name_global   = self.name_system,
            initial       = fitter_initial,
            inject        = fitter_inject,
            reinject      = fitter_reinject,
        )]


def generate_refval_attribute(
    desc,
    stems,
    pname,
    preferred_attr,
    prototypes,
    units,
    default_attr = None,
):
    desc.stems(*stems)
    prototypes = frozenset(prototypes)

    @desc.setup
    def SETUP(
        self,
        sources,
        group,
        units,
    ):
        if self.inst_prototype_t in prototypes:
            #TODO make this do the correct thing
            oattr = getattr(self.inst_prototype, preferred_attr)
            ooa = self.ooa_params[pname]
            ooa.units = oattr.units
            ooa.ref   = oattr.ref
            ooa.val   = oattr.val
            #self.ooa_params[pname]["from"] = self.inst_prototype.name_system + "." + preferred_attr
            sources.clear()
        else:
            if len(sources) > 1:
                raise RuntimeError("Must Provide only one in: {0}".format(group.keys()))
            elif len(sources) == 0:
                if default_attr is None:
                    default = None
                else:
                    default = getattr(self, default_attr)
                if default is None:
                    raise RuntimeError("Must Provide one in: {0}".format(group.keys()))
                else:
                    k, v = default
            else:
                k, v = sources.popitem()

            if preferred_attr is not None and k == preferred_attr:
                ooa = self.ooa_params[pname].useidx('immediate')
                if v is not None:
                    ooa.setdefault("units", v.units)
                    ooa.setdefault("ref", v.ref)
                    ooa.setdefault("val", v.val)
                else:
                    ooa.setdefault("units", "m")
                    ooa.setdefault("ref", None)
                    ooa.setdefault("val", None)
            else:
                unit = units[k]
                #setup defaults
                ooa = self.ooa_params[pname].useidx('immediate')
                ooa.setdefault("units", unit)
                ooa.setdefault("ref", v)
                ooa.setdefault("val", ooa.ref)
        return

    if preferred_attr is not None:
        @desc.mproperty(name = preferred_attr)
        def PREFERRED(
            self,
            storage,
            group,
        ):
            return ElementRefValue(
                ooa_params = self.ooa_params[pname],
                units = self.ooa_params[pname].units,
                pname = pname,
            )

    def VALUE(
        self,
        storage,
        group,
        units,
    ):
        #could get value with
        #k, v = storage.iteritems().next()
        units = units
        return ElementRefValue(
            ooa_params = self.ooa_params[pname],
            units = units,
            pname = pname,
        )

    for unitb in units_lookup_dim[units]:
        desc.mproperty(VALUE, stem = '{stem}_{units}', units = unitb.short)
    return

"""
class LocMixin(OverridableObject):
    _loc_default = None

    @group_dproperty
    def loc_m(desc):
        return generate_refval_attribute(
            desc,
            stems = ['loc',],
            pname = 'location',
            units = 'length',
            default_attr = '_loc_default',
            preferred_attr = 'loc_preferred',
            prototypes = ['full'],
        )

"""
#decorator




