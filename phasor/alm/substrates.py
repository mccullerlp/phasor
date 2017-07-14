# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import declarative


class Substrate(declarative.OverridableObject):
    n_by_lambda_nm = {}

    def n(self, obj):
        return self.n_by_lambda_nm[obj.root.env_wavelength_nm]


class SubstrateEnvironment(declarative.OverridableObject):
    def n(self, obj):
        return obj.root.env_substrate.n(obj)


substrate_environment = SubstrateEnvironment()


substrate_fused_silica = Substrate(
    n_by_lambda_nm = {
        1064 : 1.4496,
        532  : 1.4607,
    }
)

substrate_BK7 = Substrate(
    n_by_lambda_nm = {
        1064 : 1.5066,
        532  : 1.5195,
    }
)

substrate_vacuum = Substrate(
    n_by_lambda_nm = {
        1064 : 1.,
        532  : 1.,
    }
)

substrate_nitrogen = Substrate(
    n_by_lambda_nm = {
        1064 : 1.0002952,
        532  : 1.0002994,
    }
)

substrate_PPKTP = Substrate(
    n_by_lambda_nm = {
        1064 : 1.8302,
        532  : 1.7779,
    }
)

