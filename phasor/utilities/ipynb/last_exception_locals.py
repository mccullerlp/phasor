# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import functools
from declarative.bunch import Bunch


class LocalsExceptionWrapper(object):
    def __init__(self, call):
        self.call = call
    def __enter__(self):
        return
    def __exit__(self, exc_type, exc_value, traceback):
        if traceback is not None:
            self.call.last_tb = traceback
            self.call.last_locals = Bunch(traceback.tb_next.tb_frame.f_locals)
        return


def last_exception_locals(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        with LocalsExceptionWrapper(wrap):
            return func(*args, **kwargs)
    return wrap
