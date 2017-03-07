"""
TODO: Add additional data to "ref" for a standard width. Ref can be the center, there can be a width, and val is the true (possibly symbolic) value
"""
from __future__ import division, print_function

from . import simple_units
from . import pint


def generate_refval_attribute(
    desc,
    stems,
    ooa_name,
    preferred_attr,
    prototypes,
    ubunch,
    default_attr = None,
):
    """
    For use inside of a dproperty_adv_group
    """
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
        ooa = self.ooa_params[ooa_name]
        if self.inst_prototype_t in prototypes:
            #TODO make this do the correct thing
            oattr = getattr(self.inst_prototype, preferred_attr[0])
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
                ooa = ooa.useidx('immediate')
                if v is not None:
                    if isinstance(v, simple_units.SimpleUnitfulGroup):
                        ooa.setdefault("ref",   v.ref)
                        ooa.setdefault("val",   v.val)
                        ooa.setdefault("units", pint.mag1_units(v.units))
                    elif isinstance(v, pint.ureg.Quantity):
                        ooa.setdefault("ref",   v.magnitude)
                        ooa.setdefault("val",   v.magnitude)
                        ooa.setdefault("units", pint.mag1_units(v.units))
                    elif isinstance(v, pint.ureg.Unit):
                        ooa.setdefault("units", pint.mag1_units(v))
                        ooa.setdefault("ref",  1)
                        ooa.setdefault("val",  1)
                    else:
                        raise RuntimeError(
                            "Must be either a unitfulgroup, or a pint.Quantity"
                            ", if it already appears to be a pint object, it may need to be created"
                            "from the registry used by the library"
                        )
                        #then it must be a quantity
                else:
                    #TODO not happy with this string conversion
                    ooa.setdefault("units", str(ubunch.principle_unit))
                    ooa.setdefault("ref", None)
                    ooa.setdefault("val", None)
            else:
                #TODO not thrilled about this conversion
                unit = str(ubunch.umap[units[k]])
                #setup defaults
                ooa = ooa.useidx('immediate')
                ooa.setdefault("units", pint.mag1_units(unit))
                ooa.setdefault("ref", v)
                ooa.setdefault("val", ooa.ref)
        return

    if preferred_attr:
        def PREFERRED(
            self,
            storage,
            group,
        ):
            pint_units = pint.ureg[self.ooa_params[ooa_name].units]
            return simple_units.ElementRefValue(
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
        #print("hmm: " ,self.ooa_params[ooa_name].units)

        pint_units = pint.ureg[units]
        return simple_units.ElementRefValue(
            ooa_params = self.ooa_params[ooa_name],
            units      = pint_units,
            ooa_name   = ooa_name,
        )

    for unitname, unitobj in ubunch.umap.items():
        desc.mproperty(VALUE, stem = '{stem}_{units}', units = unitname)
    return


def unitless_refval_attribute(
    desc,
    prototypes,
    ooa_name = None,
    default_attr = None,
):
    """
    for dproperty_adv
    """
    prototypes = frozenset(prototypes)
    if ooa_name is None:
        ooa_name = desc.__name__

    @desc.construct
    def CONSTRUCT(
            self,
            arg,
    ):
        ooa = self.ooa_params[ooa_name]
        if self.inst_prototype_t in prototypes:
            #TODO make this do the correct thing
            oattr = getattr(self.inst_prototype, desc.__name__)
            ooa.ref   = oattr.ref
            ooa.val   = oattr.val
            ooa.units = str(oattr.units)
            #self.ooa_params[ooa_name]["from"] = self.inst_prototype.name_system + "." + preferred_attr
        else:
            ooa = ooa.useidx('immediate')
            if isinstance(arg, simple_units.SimpleUnitfulGroup):
                #TODO check that it is unitless
                ooa.setdefault("ref",   arg.ref)
                ooa.setdefault("val",   arg.val)
                ooa.setdefault("units", pint.mag1_units(arg.units))
            elif isinstance(arg, pint.ureg.Quantity):
                #TODO check that it is unitless
                ooa.setdefault("ref",   arg.magnitude)
                ooa.setdefault("val",   arg.magnitude)
                ooa.setdefault("units", pint.mag1_units(arg.units))
            elif isinstance(arg, pint.ureg.Unit):
                #TODO check that it is unitless
                ooa.setdefault("units", pint.mag1_units(arg))
                ooa.setdefault("ref",  1)
                ooa.setdefault("val",  1)
            else:
                ooa.setdefault("units", 1)
                ooa.setdefault("ref", arg)
                ooa.setdefault("val", ooa.ref)

        pint_units = pint.ureg[ooa.units]
        return simple_units.ElementRefValue(
            ooa_params = ooa,
            units      = pint_units,
            ooa_name   = ooa_name,
        )


def arbunit_refval_attribute(
    desc,
    prototypes,
    ooa_name = None,
    default_attr = None,
):
    """
    For use inside of a dproperty_adv
    """
    prototypes = frozenset(prototypes)
    if ooa_name is None:
        ooa_name = desc.__name__

    @desc.construct
    def CONSTRUCT(
            self,
            arg,
    ):
        ooa = self.ooa_params[ooa_name]
        if self.inst_prototype_t in prototypes:
            #TODO make this do the correct thing
            oattr = getattr(self.inst_prototype, desc.__name__)
            ooa.ref   = oattr.ref
            ooa.val   = oattr.val
            ooa.units = str(oattr.units)
            #self.ooa_params[ooa_name]["from"] = self.inst_prototype.name_system + "." + preferred_attr
        else:
            ooa = ooa.useidx('immediate')
            if isinstance(arg, str):
                #string convert to quantity
                #print('arg', arg)
                arg = pint.ureg[arg]
                #print('arg', arg)
            if isinstance(arg, simple_units.SimpleUnitfulGroup):
                ooa.setdefault("ref",   arg.ref)
                ooa.setdefault("val",   arg.val)
                ooa.setdefault("units", pint.mag1_units(arg.units))
            elif isinstance(arg, pint.ureg.Quantity):
                ooa.setdefault("ref",   arg.magnitude)
                ooa.setdefault("val",   arg.magnitude)
                ooa.setdefault("units", pint.mag1_units(arg.units))
            elif isinstance(arg, pint.ureg.Unit):
                ooa.setdefault("units", pint.mag1_units(arg))
                ooa.setdefault("ref",  1)
                ooa.setdefault("val",  1)
            else:
                raise RuntimeError("Argument must contain units as a py-pint quantity or SimpleUnitfulGroup")

        pint_units = pint.ureg[ooa.units]
        return simple_units.ElementRefValue(
            ooa_params = self.ooa_params[ooa_name],
            units      = pint_units,
            ooa_name   = ooa_name,
        )
