# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
from builtins import object


class FactorCouplingBase(object):
    __slots__ = ()

    #this is a dictionary from (pkfrom, pkto) into a func(sol_vector, sB) that returns the new edge coupling
    edges_pkpk_dict = {}
    edges_NZ_pkset_dict = {}

    @property
    def edges_req_pkset_dict(self):
        return self.edges_NZ_pkset_dict

    #this is a dictionary from pksrc into a func(sol_vector, sB) that returns the new edge coupling
    sources_pk_dict = {}
    sources_NZ_pkset_dict = {}

    @property
    def sources_req_pkset_dict(self):
        return self.sources_NZ_pkset_dict

    AC_ins_pk  = ()
    AC_outs_pk = ()


class ConstantEdgeCoupling(FactorCouplingBase):
    __slots__ = (
        'pkfrom',
        'pkto',
        'cplg',
        'edges_pkpk_dict',
        'edges_NZ_pkset_dict',
    )

    def __init__(self, pkfrom, pkto, cplg):
        self.pkfrom = pkfrom
        self.pkto   = pkto
        self.cplg   = cplg

        self.edges_pkpk_dict = {
            (self.pkfrom, self.pkto) : self.edge_func,
        }
        self.edges_NZ_pkset_dict = {
            (self.pkfrom, self.pkto) : frozenset(),
        }

    def edge_func(self, sol_vector, sB):
        return self.cplg


class ConstantSourceCoupling(FactorCouplingBase):
    __slots__ = (
        'pksrc',
        'cplg',
        'sources_pk_dict',
        'sources_NZ_pkset_dict',
    )

    def __init__(self, pksrc, cplg):
        self.pksrc = pksrc
        self.cplg   = cplg

        self.sources_pk_dict = {
            self.pksrc : self.source_func,
        }
        self.sources_NZ_pkset_dict = {
            self.pksrc : frozenset(),
        }

    def source_func(self, sol_vector, sb):
        return self.cplg


class MultiplicativeEdgeCoupling(FactorCouplingBase):
    __slots__ = (
        'pkfrom',
        'pkto',
        'cplg',
        'pksrc_list',
        'edges_pkpk_dict',
        'edges_NZ_pkset_dict',
    )

    def __init__(self, pkfrom, pkto, cplg, pksrc_list):
        self.pkfrom     = pkfrom
        self.pkto       = pkto
        self.cplg       = cplg
        self.pksrc_list = pksrc_list

        self.edges_pkpk_dict = {
            (self.pkfrom, self.pkto) : self.edge_func,
        }
        self.edges_NZ_pkset_dict = {
            (self.pkfrom, self.pkto) : frozenset(pksrc_list),
        }

    def edge_func(self, sol_vector, sB):
        val = self.cplg
        for pksrc in self.pksrc_list:
            sval = sol_vector.get(pksrc, 0)
            val = val * sval
        return val


class MultiplicativeSourceCoupling(FactorCouplingBase):
    __slots__ = (
        'pksrc',
        'cplg',
        'pksrc_list',
        'sources_pk_dict',
        'sources_NZ_pkset_dict',
    )

    def __init__(self, pksrc, cplg, pksrc_list):
        self.pksrc                  = pksrc
        self.cplg                   = cplg
        self.pksrc_list             = pksrc_list

        self.sources_pk_dict = {
            self.pksrc : self.source_func,
        }
        self.sources_NZ_pkset_dict = {
            self.pksrc : frozenset(pksrc_list),
        }

    def source_func(self, sol_vector, sb):
        val = self.cplg
        for pksrc in self.pksrc_list:
            sval = sol_vector.get(pksrc, 0)
            val = val * sval
        return val


class TripletCoupling(FactorCouplingBase):
    __slots__ = (
        'pkfrom1',
        'pkfrom2',
        'pkto',
        'cplg',
        'edges_pkpk_dict',
        'edges_NZ_pkset_dict',
        'sources_pk_dict',
        'sources_NZ_pkset_dict',
    )

    def __init__(
            self,
            pkfrom1,
            pkfrom2,
            pkto,
            cplg,
    ):
        self.pkfrom1    = pkfrom1
        self.pkfrom2    = pkfrom2
        self.pkto       = pkto
        self.cplg       = cplg

        self.sources_pk_dict = {
            self.pkto : self.source_func
        }
        self.sources_NZ_pkset_dict = {
            self.pkto : frozenset([self.pkfrom1, self.pkfrom2]),
        }
        self.edges_pkpk_dict = {
            (self.pkfrom1, self.pkto) : self.edge1_func,
            (self.pkfrom2, self.pkto) : self.edge2_func,
        }
        self.edges_NZ_pkset_dict = {
            (self.pkfrom1, self.pkto) : frozenset([self.pkfrom2]),
            (self.pkfrom2, self.pkto) : frozenset([self.pkfrom1]),
        }

    def edge1_func(self, sol_vector, sB):
        val = self.cplg * sol_vector.get(self.pkfrom2, 0)
        return val

    def edge2_func(self, sol_vector, sB):
        val = self.cplg * sol_vector.get(self.pkfrom1, 0)
        return val

    def source_func(self, sol_vector, sB):
        val = -self.cplg
        val = val * sol_vector.get(self.pkfrom1, 0)
        val = val * sol_vector.get(self.pkfrom2, 0)
        return val


