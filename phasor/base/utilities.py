# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

def type_test(obj, types):
    if not isinstance(obj, types):
        if not isinstance(types, tuple):
            types = (types, )
        example_names = []
        for t in types:
            for oname, obj in list(globals().items()):
                try:
                    if isinstance(obj, t) or issubclass(obj, t):
                        if obj is not t:
                            example_names.append(oname)
                except TypeError:
                    pass
        raise RuntimeError("Argument Must be an object such as: {0}".format(example_names))
    return

