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
    ureg,
)

def mag1_units(pint_quantity):
    if isinstance(pint_quantity, ureg.Quantity):
        if pint_quantity.m == 1:
            return str(pint_quantity.units)
    return str(pint_quantity)


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

    @mproperty
    def refQ(self, val):
        return val * self.units

    @mproperty
    def valQ(self, val):
        return val * self.units

    def __add__(self, other):
        units_to = self.units
        type_to = ureg[units_to]
        units_from = other.units
        type_from = ureg[units_from]
        rescale = type_from / type_to
        assert(rescale.unitless)
        rescale = rescale.m_as(ureg.dimensionless)
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
        rescale = rescale.m_as(ureg.dimensionless)
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
    def ooa_name(self, val):
        return val

    @dproperty
    def ooa_units_scale(self):
        units_to = self.units
        units_from = ureg[self.ooa_params.units]
        rescale = units_from / units_to
        assert(rescale.unitless)
        return rescale.m_as(ureg.dimensionless)

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
        names = [self.ooa_name]
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
    ooa_name,
    preferred_attr,
    prototypes,
    ubunch,
    default_attr = None,
):
    desc.stems(*stems)
    prototypes = frozenset(prototypes)

    if preferred_attr is None:
        preferred_attr = ()
    elif isinstance(preferred_attr, str):
        preferred_attr = (preferred_attr,)
    else:
        preferred_attr = tuple(preferred_attr)

    @desc.setup
    def SETUP(
        self,
        sources,
        group,
        units,
    ):
        if self.inst_prototype_t in prototypes:
            #TODO make this do the correct thing
            oattr = getattr(self.inst_prototype, preferred_attr[0])
            ooa = self.ooa_params[ooa_name]
            ooa.ref   = oattr.ref
            ooa.val   = oattr.val
            ooa.units = str(oattr.units)
            #self.ooa_params[ooa_name]["from"] = self.inst_prototype.name_system + "." + preferred_attr
            sources.clear()
        else:
            if len(sources) > 1:
                raise RuntimeError("Must Provide only one in: {0}".format(list(group.keys())))
            elif len(sources) == 0:
                if default_attr is None:
                    default = None
                else:
                    default = getattr(self, default_attr)
                if default is None:
                    raise RuntimeError("Must Provide one in: {0}".format(list(group.keys())))
                else:
                    k, v = default
            else:
                k, v = sources.popitem()

            if k in preferred_attr:
                ooa = self.ooa_params[ooa_name].useidx('immediate')
                if v is not None:
                    if isinstance(v, SimpleUnitfulGroup):
                        ooa.setdefault("ref",   v.ref)
                        ooa.setdefault("val",   v.val)
                        ooa.setdefault("units", mag1_units(v.units))
                    elif isinstance(v, ureg.Quantity):
                        ooa.setdefault("ref",   v.magnitude)
                        ooa.setdefault("val",   v.magnitude)
                        ooa.setdefault("units", mag1_units(v.units))
                    elif isinstance(v, ureg.Unit):
                        ooa.setdefault("units", mag1_units(v))
                        ooa.setdefault("ref",  1)
                        ooa.setdefault("val",  1)
                    else:
                        raise RuntimeError("Must be either a unitfulgroup, or a pint.Quantity"
                        ", if it already appears to be a pint object, it may need to be created"
                        "from the registry used by the library")
                        #then it must be a quantity
                else:
                    ooa.setdefault("units", ubunch.principle_name)
                    ooa.setdefault("ref", None)
                    ooa.setdefault("val", None)
            else:
                unit = units[k]
                #setup defaults
                ooa = self.ooa_params[ooa_name].useidx('immediate')
                ooa.setdefault("units", unit)
                ooa.setdefault("ref", v)
                ooa.setdefault("val", ooa.ref)
        return

    if preferred_attr:
        def PREFERRED(
            self,
            storage,
            group,
        ):
            pint_units = ureg[self.ooa_params[ooa_name].units]
            return ElementRefValue(
                ooa_params = self.ooa_params[ooa_name],
                units = pint_units,
                ooa_name = ooa_name,
            )
        for pattr in preferred_attr:
            desc.mproperty(PREFERRED, name = pattr)

    def VALUE(
        self,
        storage,
        group,
        units,
    ):
        #could get value with
        #k, v = storage.items().next()
        print("hmm: " ,self.ooa_params[ooa_name].units)
        pint_units = ureg[self.ooa_params[ooa_name].units]
        return ElementRefValue(
            ooa_params = self.ooa_params[ooa_name],
            units      = pint_units,
            ooa_name   = ooa_name,
        )

    for unitname, unitobj in ubunch.umap.items():
        desc.mproperty(VALUE, stem = '{stem}_{units}', units = unitname)
    return

