# -*- coding: utf-8 -*-
"""
Pulls in the future library requirement if running on python2
"""
from __future__ import division, print_function, unicode_literals

import sys

if sys.version_info < (3, 0, 0):
    #requires the future library
    from builtins import (
        super,
        object,
        ascii,
        bytes,
        chr,
        dict,
        filter,
        hex,
        input,
        int,
        map,
        next,
        oct,
        open,
        pow,
        range,
        round,
        str,
        zip,
    )

    from future.standard_library import install_aliases
    install_aliases()

    #decode any unicode repr functions as py27 cannot handle them
    def repr_compat(func):
        def __repr__(self, *args, **kwargs):
            return repr(func(self, *args, **kwargs).encode('utf-8').decode('utf-8'))
        #wrap it
        __repr__.__name__ = func.__name__
        __repr__.__doc__ = func.__doc__
        return __repr__
else:
    super  = super
    object = object
    ascii  = ascii
    bytes  = bytes
    chr    = chr
    dict   = dict
    filter = filter
    hex    = hex
    input  = input
    int    = int
    map    = map
    next   = next
    oct    = oct
    open   = open
    pow    = pow
    range  = range
    round  = round
    str    = str
    zip    = zip

    def repr_compat(func):
        return func
