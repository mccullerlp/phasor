"""
"""
from __future__ import division, print_function
from . import pint

import declarative


def units_map(
    principle,
    **kwargs
):
    umap = dict()

    for name, to in kwargs.items():
        if to is None:
            uobj = pint.ureg.parse_expression(name)
        else:
            if isinstance(to, str):
                uobj = pint.ureg.parse_expression(to)
            else:
                uobj = to
        umap[name] = uobj
    return declarative.Bunch(
        principle_name = principle,
        principle_unit = umap[principle],
        umap           = umap,
    )


lengths_small = units_map(
    principle = 'm',
    m  = None,
    fm = None,
    pm = None,
    nm = None,
    um = None,
    mm = None,
    cm = None,
    km = None,
    ft = None,
    **{'in' : None}  #because 'in' is reserved keyword
    #meter = None,
    #femtometer = None,
    #picometer = None,
    #nanometer = None,
    #micrometer = None,
    #millimeter = None,
    #centimeter = None,
    #kilometer = None,
    #inch = None,
    #foot = None,
    #feet = None,
)

time_small = units_map(
    principle = 's',
    s  = None,
    fs = None,
    ps = None,
    ns = None,
    us = None,
    ms = None,
)

mass_small = units_map(
    principle = 'kg',
    g  = None,
    ag = None,
    fg = None,
    pg = None,
    ng = None,
    ug = None,
    mg = None,
    cg = None,
    kg = None,
    lb = None,
    #gram = None,
    #attogram = None,
    #femtogram = None,
    #picogram = None,
    #nanogram = None,
    #microgram = None,
    #milligram = None,
    #centigram = None,
    #kilogram = None,
    #pound = None,
)

resistance = units_map(
    principle = 'Ohm',
    Ohm  = 'ohm',
    fOhm = 'fohm',
    pOhm = 'pohm',
    nOhm = 'nohm',
    mOhm = 'mohm',
    uOhm = 'uohm',
    cOhm = 'cohm',
    kOhm = 'kohm',
    MOhm = 'Mohm',
    GOhm = 'Gohm',
    #Ohm = None,
    #attoOhm = None,
    #femtoOhm = None,
    #picoOhm = None,
    #nanoOhm = None,
    #microOhm = None,
    #milliOhm = None,
    #centiOhm = None,
    #kiloOhm = None,
    #megaOhm = None,
    #gigaOhm = None,
)

capacitance = units_map(
    principle = "pF",
    F  = None,
    fF = None,
    pF = None,
    nF = None,
    uF = None,
    mF = None,
    cF = None,
    #Farad = None,
    #attoFarad = None,
    #femtoFarad = None,
    #picoFarad = None,
    #nanoFarad = None,
    #microFarad = None,
    #milliFarad = None,
    #centiFarad = None,
)

inductance = units_map(
    principle = "uH",
    H  = None,
    fH = None,
    pH = None,
    nH = None,
    uH = None,
    mH = None,
    cH = None,
    #Henry = None,
    #attoHenry = None,
    #femtoHenry = None,
    #picoHenry = None,
    #nanoHenry = None,
    #microHenry = None,
    #milliHenry = None,
    #centiHenry = None,
)


angle = units_map(
    principle = "rad",
    rad  = None,
    mrad  = None,
    urad  = None,
    deg = None,
)

rotation = angle

angle_deg = units_map(
    principle = "deg",
    rad  = None,
    mrad  = None,
    urad  = None,
    deg = None,
)

rotation_deg = angle_deg

frequency = units_map(
    principle = "Hz",
    Hz = None,
    GHz = None,
    MHz = None,
    kHz = None,
    mHz = None,
    uHz = None,
)

laser_power = units_map(
    principle = "W",
    W  = None,
    fW = None,
    pW = None,
    nW = None,
    uW = None,
    mW = None,
    kW = None,
    MW = None,
    GW = None,
)

dimensionless = units_map(
    principle = "val",
    val = "dimensionless",
)










    
