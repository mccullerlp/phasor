# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from builtins import object


class FactorCouplingBase(object):
    __slots__ = ()

    #this is a dictionary from (pkfrom, pkto) into a func(sol_vector, sB) that returns the new edge coupling
    edges_pkpk_dict = {}
    edges_NZ_pkset_dict = {}

    #this is a dict from (pkfrom, pkto) edges into collections of pk nodes that need to be included in the
    #solution vector
    @property
    def edges_req_pkset_dict(self):
        return self.edges_NZ_pkset_dict

    #this is a dictionary from pksrc into a func(sol_vector, sB) that returns the new edge coupling
    sources_pk_dict = {}
    sources_NZ_pkset_dict = {}

    #this is a (pk) source nodes into collections of pk nodes that need to be included in the
    #solution vector
    @property
    def sources_req_pkset_dict(self):
        return self.sources_NZ_pkset_dict


    #just a list of direct source node requirements.
    floating_req_set = None
    #holds a list of 3-tuples, each one carrying an in-set, out-set, and coupling-func
    #it behaves as though all in-set is connected to out-set for requirements analysis
    #but then during coupling matrix construction, only the edges returned from coupling-func
    #will be used
    floating_in_out_func_pairs = None

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

        if self.pkfrom1 != self.pkfrom2:
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
        else:
            #if the sources are identical, then the combinatorics change.
            #these dictionaries cannot double count the edges, so we don't need to compensate with a source
            self.sources_pk_dict = {}
            self.sources_NZ_pkset_dict = {}
            self.edges_pkpk_dict = {
                (self.pkfrom1, self.pkto) : self.edge1_func,
            }
            self.edges_NZ_pkset_dict = {
                (self.pkfrom1, self.pkto) : frozenset([self.pkfrom2]),
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


class TripletNormCoupling(FactorCouplingBase):
    __slots__ = (
        'pkfrom1',
        'pkfrom2',
        'pkto',
        'pknorm',
        'pknorm_func',
        'cplg',
        'edges_pkpk_dict',
        'edges_NZ_pkset_dict',
        'edges_req_pkset_dict',
        'sources_pk_dict',
        'sources_NZ_pkset_dict',
        'sources_req_pkset_dict',
    )

    def __init__(
            self,
            pkfrom1,
            pkfrom2,
            pkto,
            pknorm,
            cplg,
            pknorm_func = lambda val : val,
    ):
        self.pkfrom1     = pkfrom1
        self.pkfrom2     = pkfrom2
        self.pkto        = pkto
        self.cplg        = cplg
        self.pknorm      = pknorm
        self.pknorm_func = pknorm_func

        if self.pkfrom1 != self.pkfrom2:
            self.sources_pk_dict = {
                self.pkto : self.source_func
            }
            self.sources_NZ_pkset_dict = {
                self.pkto : frozenset([self.pkfrom1, self.pkfrom2]),
            }
            self.sources_req_pkset_dict = {
                self.pkto : frozenset([self.pkfrom1, self.pkfrom2, self.pknorm]),
            }
            self.edges_pkpk_dict = {
                (self.pkfrom1, self.pkto) : self.edge1_func,
                (self.pkfrom2, self.pkto) : self.edge2_func,
            }
            self.edges_NZ_pkset_dict = {
                (self.pkfrom1, self.pkto) : frozenset([self.pkfrom2]),
                (self.pkfrom2, self.pkto) : frozenset([self.pkfrom1]),
            }
            self.edges_req_pkset_dict = {
                (self.pkfrom1, self.pkto) : frozenset([self.pkfrom2, self.pknorm]),
                (self.pkfrom2, self.pkto) : frozenset([self.pkfrom1, self.pknorm]),
            }
        else:
            #if the sources are identical, then the combinatorics change.
            #these dictionaries cannot double count the edges, so we don't need to compensate with a source
            self.sources_pk_dict = {}
            self.sources_NZ_pkset_dict = {}
            self.sources_req_pkset_dict = {}

            self.edges_pkpk_dict = {
                (self.pkfrom1, self.pkto) : self.edge1_func,
            }
            self.edges_NZ_pkset_dict = {
                (self.pkfrom1, self.pkto) : frozenset([self.pkfrom2]),
            }
            self.edges_req_pkset_dict = {
                (self.pkfrom1, self.pkto) : frozenset([self.pkfrom2, self.pknorm]),
            }

    def edge1_func(self, sol_vector, sB):
        val = self.cplg * sol_vector.get(self.pkfrom2, 0) / self.pknorm_func(sol_vector.get(self.pknorm, 1e12))
        return val

    def edge2_func(self, sol_vector, sB):
        val = self.cplg * sol_vector.get(self.pkfrom1, 0) / self.pknorm_func(sol_vector.get(self.pknorm, 1e12))
        return val

    def source_func(self, sol_vector, sB):
        val = -self.cplg
        val = val * sol_vector.get(self.pkfrom1, 0)
        val = val * sol_vector.get(self.pkfrom2, 0)
        denom = sol_vector.get(self.pknorm, 1e12) + 1e-30
        val = val / self.pknorm_func(denom)
        return val



class TripletNormsCoupling(FactorCouplingBase):
    __slots__ = (
        'pkfrom1',
        'pkfrom2',
        'pkto',
        'pknorms',
        'pknorms_func',
        'cplg',
        'edges_pkpk_dict',
        'edges_NZ_pkset_dict',
        'edges_req_pkset_dict',
        'sources_pk_dict',
        'sources_NZ_pkset_dict',
        'sources_req_pkset_dict',
    )

    def __init__(
            self,
            pkfrom1,
            pkfrom2,
            pkto,
            pknorms,
            cplg,
            pknorms_func,
    ):
        self.pkfrom1     = pkfrom1
        self.pkfrom2     = pkfrom2
        self.pkto        = pkto
        self.cplg        = cplg
        self.pknorms     = list(pknorms)
        self.pknorms_func = pknorms_func

        if self.pkfrom1 != self.pkfrom2:
            self.sources_pk_dict = {
                self.pkto : self.source_func
            }
            self.sources_NZ_pkset_dict = {
                self.pkto : frozenset([self.pkfrom1, self.pkfrom2]),
            }
            self.sources_req_pkset_dict = {
                self.pkto : frozenset([self.pkfrom1, self.pkfrom2] + self.pknorms),
            }
            self.edges_pkpk_dict = {
                (self.pkfrom1, self.pkto) : self.edge1_func,
                (self.pkfrom2, self.pkto) : self.edge2_func,
            }
            self.edges_NZ_pkset_dict = {
                (self.pkfrom1, self.pkto) : frozenset([self.pkfrom2]),
                (self.pkfrom2, self.pkto) : frozenset([self.pkfrom1]),
            }
            self.edges_req_pkset_dict = {
                (self.pkfrom1, self.pkto) : frozenset([self.pkfrom2] + self.pknorms),
                (self.pkfrom2, self.pkto) : frozenset([self.pkfrom1] + self.pknorms),
            }
        else:
            #if the sources are identical, then the combinatorics change.
            #these dictionaries cannot double count the edges, so we don't need to compensate with a source
            self.sources_pk_dict = {}
            self.sources_NZ_pkset_dict = {}
            self.sources_req_pkset_dict = {}

            self.edges_pkpk_dict = {
                (self.pkfrom1, self.pkto) : self.edge1_func,
            }
            self.edges_NZ_pkset_dict = {
                (self.pkfrom1, self.pkto) : frozenset([self.pkfrom2]),
            }
            self.edges_req_pkset_dict = {
                (self.pkfrom1, self.pkto) : frozenset([self.pkfrom2] + self.pknorms),
            }

    def edge1_func(self, sol_vector, sB):
        sols = [sol_vector.get(pknorm, 1e12) for pknorm in self.pknorms]
        val = self.cplg * sol_vector.get(self.pkfrom2, 0) / self.pknorms_func(*sols)
        return val

    def edge2_func(self, sol_vector, sB):
        sols = [sol_vector.get(pknorm, 1e12) for pknorm in self.pknorms]
        val = self.cplg * sol_vector.get(self.pkfrom1, 0) / self.pknorms_func(*sols)
        return val

    def source_func(self, sol_vector, sB):
        val = -self.cplg
        val = val * sol_vector.get(self.pkfrom1, 0)
        val = val * sol_vector.get(self.pkfrom2, 0)
        sols = [sol_vector.get(pknorm, 1e12) for pknorm in self.pknorms]
        val = val / self.pknorms_func(*sols)
        return val

