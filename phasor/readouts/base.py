# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from phasor.utilities.print import print

from declarative.bunch import (
    DeepBunch,
)


class ReadoutViewBase(object):
    def __init__(
            self,
            readout,
            system,
            solver,
            **kwargs
    ):
        super(ReadoutViewBase, self).__init__(**kwargs)
        self.readout = readout
        self.system = system
        self.solver = solver

    def subview_insert(self, subname_tup, view_obj):
        if len(subname_tup) > 1:
            db = DeepBunch()
            setattr(self, subname_tup[0], db)
            subdb = db
            for name in subname_tup[1:-1]:
                subdb = subdb[name]
            subdb[subname_tup[-1]] = view_obj
