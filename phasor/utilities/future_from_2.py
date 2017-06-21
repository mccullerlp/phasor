"""
Pulls in the future library requirement if running on python2
"""

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
