# -*- coding: utf-8 -*-
"""
TODO: Add additional data to "ref" for a standard width. Ref can be the center, there can be a width, and val is the true (possibly symbolic) value
"""
from __future__ import division, print_function, unicode_literals
from ..utilities.future_from_2 import str
import collections
import declarative

from . import simple_units
from . import pint


def generate_refval_attribute(
    desc,
    stems,
    ctree_name,
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
        ooa = self.ctree[ctree_name]
        if self.inst_prototype_t in prototypes:
            #TODO make this do the correct thing
            oattr = getattr(self.inst_prototype, preferred_attr[0])
            ooa.val   = oattr.val
            if ooa.ref is not ooa.val:
                ooa.ref   = oattr.ref
            ooa.units = str(oattr.units)
            #self.ctree[ctree_name]["from"] = self.inst_prototype.name_system + "." + preferred_attr
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

            #print("FINAL: ", k, v)
            if k in preferred_attr:
                ooa = ooa.useidx('immediate')
                if v is not None:
                    if isinstance(v, simple_units.SimpleUnitfulGroup):
                        ooa.setdefault("val",   v.val)
                        if v.val is not v.ref:
                            ooa.setdefault("ref",   v.ref)
                        ooa.setdefault("units", pint.mag1_units(v.units))
                    elif isinstance(v, pint.ureg.Quantity):
                        ooa.setdefault("val",   v.magnitude)
                        if v.val is not v.ref:
                            ooa.setdefault("ref",   v.ref)
                        ooa.setdefault("units", pint.mag1_units(v.units))
                    elif isinstance(v, pint.ureg.Unit):
                        ooa.setdefault("units", pint.mag1_units(v))
                        ooa.setdefault("val",  1)
                        #ooa.setdefault("ref",  1)
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
                    ooa.setdefault("val", None)
                    #ooa.setdefault("ref", None)
            else:
                #TODO not thrilled about this conversion
                unit = ubunch.umap[units[k]]
                #setup defaults
                ooa = ooa.useidx('immediate')
                ooa.setdefault("units", pint.mag1_units(unit))
                ooa.setdefault("val", v)
                #ooa.setdefault("ref", ooa.val)
        return

    if preferred_attr:
        def PREFERRED(
            self,
            storage,
            group,
        ):
            pint_units = pint.ureg.parse_expression(self.ctree[ctree_name].units)
            return simple_units.ElementRefValue(
                ctree = self.ctree[ctree_name],
                units = pint_units,
                ctree_name = ctree_name,
            )
        for pattr in preferred_attr:
            desc.mproperty(PREFERRED, name = pattr)
        #desc.default(PREFERRED)

    def VALUE(
        self,
        storage,
        group,
        units,
    ):
        #could get value with
        #k, v = storage.items().next()
        #print("hmm: " ,self.ctree[ctree_name].units)

        pint_units = pint.ureg.parse_expression(units)
        return simple_units.ElementRefValue(
            ctree = self.ctree[ctree_name],
            units      = pint_units,
            ctree_name   = ctree_name,
        )

    for unitname, unitobj in ubunch.umap.items():
        desc.mproperty(VALUE, stem = '{stem}_{units}', units = unitname)
    return


def unitless_refval_attribute(
    desc,
    prototypes    = ['full', 'base'],
    ctree_name      = None,
    default_attr  = None,
    allow_fitting = True,
):
    """
    for dproperty_adv
    """
    prototypes = frozenset(prototypes)
    if ctree_name is None:
        ctree_name = desc.__name__

    @desc.construct
    def CONSTRUCT(
            self,
            arg = declarative.NOARG,
    ):
        if self.inst_prototype_t in prototypes:
            #TODO make this do the correct thing
            oattr = getattr(self.inst_prototype, desc.__name__)
            ooa = self.ctree[ctree_name]
            if isinstance(ooa, collections.Mapping):
                #the ooa may or may not be specified, if it is, then it is a map type
                if 'ref' not in ooa and 'val' not in ooa:
                    if oattr.ref is oattr.val:
                        #set the single value
                        self.ctree[ctree_name] = oattr.val
                    else:
                        ooa.setdefault('ref', oattr.ref)
                        ooa.setdefault('val', oattr.val)
                else:
                    ooa.setdefault('ref', oattr.ref)
                    ooa.setdefault('val', oattr.val)
            else:
                #the ooa must already be specified
                pass
            #self.ctree[ctree_name]["from"] = self.inst_prototype.name_system + "." + preferred_attr
        else:
            if arg is declarative.NOARG:
                if default_attr is None:
                    default = declarative.NOARG
                else:
                    default = getattr(self, default_attr)
                if default is declarative.NOARG:
                    raise RuntimeError("Must specify attribute: ".format(desc.__name__))
                else:
                    arg = default

            if isinstance(arg, simple_units.SimpleUnitfulGroup):
                #TODO check that it is unitless
                if arg.ref is arg.val:
                    self.ctree.useidx('immediate')[ctree_name] = arg.val
                else:
                    ooa = self.ctree[ctree_name].useidx('immediate')
                    ooa.setdefault("ref",   arg.ref)
                    ooa.setdefault("val",   arg.val)
            else:
                ooa = self.ctree.useidx('immediate')
                if not ctree_name in ooa:
                    ooa[ctree_name] = arg
                else:
                    #TODO maybe should do something here?
                    pass

        return simple_units.UnitlessElementRefValue(
            ctree         = self.ctree[ctree_name],
            ctree_name    = ctree_name,
            allow_fitting = allow_fitting,
        )


def arbunit_refval_attribute(
    desc,
    prototypes,
    ctree_name = None,
    default_attr = None,
):
    """
    For use inside of a dproperty_adv
    """
    prototypes = frozenset(prototypes)
    if ctree_name is None:
        ctree_name = desc.__name__

    @desc.construct
    def CONSTRUCT(
            self,
            arg,
    ):
        ooa = self.ctree[ctree_name]
        if self.inst_prototype_t in prototypes:
            #TODO make this do the correct thing
            oattr = getattr(self.inst_prototype, desc.__name__)
            ooa.val   = oattr.val
            if ooa.ref is not ooa.val:
                ooa.ref   = oattr.ref
            ooa.units = str(oattr.units)
            #self.ctree[ctree_name]["from"] = self.inst_prototype.name_system + "." + preferred_attr
        else:
            ooa = ooa.useidx('immediate')
            if isinstance(arg, str):
                #string convert to quantity
                #print('arg', arg)
                arg = pint.ureg.parse_expression(arg)
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

        pint_units = pint.ureg.parse_expression(ooa.units)
        return simple_units.ElementRefValue(
            ctree = self.ctree[ctree_name],
            units      = pint_units,
            ctree_name   = ctree_name,
        )
