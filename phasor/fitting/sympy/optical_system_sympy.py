# -*- coding: utf-8 -*-
"""
"""

from __future__ import division, print_function, unicode_literals
#from builtins import zip, range, object
from .optical_system import OpticalSystem
import sympy
import numpy as np

from declarative.bunch import Bunch
import phasor.utilities.numerics.dispatched as dmath
import phasor.utilities.numerics.dispatch_sympy

from .optical_elements import (
    BeamSplitter,
    Mirror,
    PD,
    PDMixer,
    Space,
)

from IPython.display import (
    display,
    display_pretty,
    display_html,
    display_jpeg,
    display_png,
    display_json,
    display_latex,
    display_svg,
    clear_output,
)


var = sympy.var


def var_rp(name):
    return sympy.var(name, real = True, positive = True)


def var_r(name):
    return sympy.var(name, real = True)


class SympyTransmissionReducer(object):

    def sympy_conjugate_reduction(self, expr):
        if sympy.sympify(expr) is not expr:
            return expr
        if sympy.sympify(self.R_hr) is self.R_hr:
            R_hr_temp = var_rp("R_TEMPORARY")
            expr = expr.subs(self.R_hr, R_hr_temp)
            expr = expr.subs(R_hr_temp, self.R_hr)
        return expr


class SympyMirror(SympyTransmissionReducer, Mirror):
    pass


class SympyBeamSplitter(SympyTransmissionReducer, BeamSplitter):
    pass


class SympyViewReduction(object):
    view_cc_folding = True

    def view_simplification(self, expr, substitution = 0):
        self._view_simplifications[expr] = substitution
        return

    def sympy_reduce_solutions(self, expr):
        for sub_expr, subst in list(self._view_simplifications.items()):
            expr = expr.subs(sub_expr, subst)
        for func in self.view_simplification_funcs:
            expr = func(expr)
        return expr

    def sympy_reduce_total(self, expr):
        for func in self.view_total_simplifications:
            expr = func(expr)
        return expr

    @property
    def _view_simplifications(self):
        try:
            return self.__view_simplifications
        except AttributeError:
            self.__view_simplifications = {}
            return self.__view_simplifications

    @property
    def view_simplification_funcs(self):
        try:
            return self.__view_simplification_funcs
        except AttributeError:
            self.__view_simplification_funcs = []
            return self.__view_simplification_funcs

    @property
    def view_total_simplifications(self):
        try:
            return self.__view_total_simplifications
        except AttributeError:
            self.__view_total_simplifications = []
            return self.__view_total_simplifications


class PDSimplifications(SympyViewReduction):
    view_cc_folding = None


class SympyPD(SympyViewReduction, PD):
    pass


class SympyPDMixer(SympyViewReduction, PDMixer):
    pass


class SympySpace(Space):
    def phase_advance(self, system, F):
        return super(SympySpace, self).phase_advance(system, F).simplify()


def prefactor_cplx_split(expr):
    outer_factors = []
    factors = expr.as_ordered_factors()
    cplx_parity = 0
    idx = 0
    while idx < len(factors):
        factor = factors[idx]
        if factor.is_real:
            outer_factors.append(factor)
            factors.pop(idx)
        elif factor.is_imaginary:
            outer_factors.append(factor)
            factors.pop(idx)
            cplx_parity += 1
        else:
            idx += 1
    cplx_sign = (-1) ** ((cplx_parity / 2) % 2)
    cplx_parity = cplx_parity % 2
    prefactor = cplx_sign * sympy.Mul(*outer_factors)
    return cplx_parity, prefactor, sympy.Mul(*factors)


class projectR(sympy.Function):
    is_real = True

    @classmethod
    def eval(cls, arg):
        cplx_parity, prefactor, factor = prefactor_cplx_split(arg)
        if cplx_parity:
            return -prefactor * projectI(factor)
        else:
            if factor == 1:
                return prefactor
            if (not cplx_parity) and prefactor == 1:
                return
            return prefactor * cls(factor)

    def _latex(self, printer):
        pr_args = printer._print(self.args[0])
        return r'\operatorname{Re}\left\{' + pr_args + r'\right\}'


class projectI(sympy.Function):
    is_real = True

    @classmethod
    def eval(cls, arg):
        cplx_parity, prefactor, factor = prefactor_cplx_split(arg)
        if cplx_parity:
            return prefactor * projectR(factor)
        else:
            if factor == 1:
                return sympy.sympify(0)
            if (not cplx_parity) and prefactor == 1:
                return
            return prefactor * cls(factor)

    def _latex(self, printer):
        pr_args = printer._print(self.args[0])
        return r'\operatorname{Im}\left\{' + pr_args + r'\right\}'


#class Abs(sympy.Abs):
#    @classmethod
#    def eval(cls, arg):
#        return super(Abs, cls).eval(arg)
#        factors = arg.as_ordered_factors()
#        idx = 0
#        while idx < len(factors):
#            pe_A = sympy.Wild('pe_A')
#            phasor = sympy.exp(sympy.ps_In * pe_A)
#            if factors[idx].match(phasor):
#                factors.pop(idx)
#            else:
#                idx += 1
#        return super(Abs, cls).eval(sympy.Mul(*factors))
#

def sympy_count_conjugates(expr):
    pe_A = sympy.Wild('pe_A')
    return len(expr.find(sympy.conjugate(pe_A)))


def choose_fewer_conjugates(expr1, expr2):
    return sympy_count_conjugates(expr1) <= sympy_count_conjugates(expr2)


class OpticalSystemSympy(OpticalSystem):
    c_m_s         = sympy.var('c', real = True, positive = True)
    lambda_m      = sympy.var('lambda', real = True, positive = True)
    pi            = sympy.pi
    i             = sympy.ps_In
    math          = sympy
    project_re    = projectR
    project_im    = projectI

    BeamSplitter = SympyBeamSplitter
    Mirror       = SympyMirror
    PD           = SympyPD
    PDMixer      = SympyPDMixer
    Space        = SympySpace
    PDSimplifications = PDSimplifications

    def number(self, num):
        return sympy.sympify(num)

    def solve_system(self):
        rt = sympy.Matrix(self.coupling_matrix_rt.array)
        print("Solving")
        solution_vector_array = rt.solve(self.source_vector.col)
        solution_vector_array = np.asarray(solution_vector_array).reshape(-1)

        #for idx in range(len(solution_vector_array)):
        #    print "Simplifying", idx
        #    expr = solution_vector_array[idx]
        #    solution_vector_array[idx] = sympy.powsimp(expr, deep=True, force=True)
        self.field_spaces.append(self.field_space)
        self.solution_vectors.append(self.source_vector.backmap_vector(solution_vector_array))

        conj = np.vectorize(self.math.conjugate)
        solution_vector_array_conj = conj(solution_vector_array)
        for element in self.elements:
            reducer = getattr(element, 'sympy_conjugate_reduction', None)
            if reducer is not None:
                for idx in range(len(solution_vector_array_conj)):
                    expr = solution_vector_array_conj[idx]
                    expr = reducer(expr)
                    solution_vector_array_conj[idx] = expr
        self.solution_vectors_conj.append(self.source_vector.backmap_vector(solution_vector_array_conj))
        return

    def conjugate(self, expr):
        expr = dmath.conjugate(expr)
        for element in self.elements:
            reducer = getattr(element, 'sympy_conjugate_reduction', None)
            if reducer is not None:
                expr = reducer(expr)
        return expr

    def collapse_field_operator(self, PD, key_field_operator, order, simplifications = None):
        b = declarative.Bunch()
        b.total = 0

        if simplifications is not None:
            if not isinstance(simplifications, (list, tuple)):
                simplifications = [simplifications]
        else:
            simplifications = []
        simplifications = [PD] + simplifications

        coeff_list = []
        value_list_L = []
        value_list_R = []

        reduce_sols_list = []
        def reduce_sols(expr):
            expr = sympy.sympify(expr)
            for pd in reduce_sols_list:
                expr = pd.sympy_reduce_solutions(expr)
            return expr

        reduce_total_list = []
        def reduce_total(expr):
            expr = sympy.sympify(expr)
            for element in self.elements:
                reducer = getattr(element, 'sympy_conjugate_reduction', None)
                if reducer is not None:
                    expr = reducer(expr)
            for pd in reduce_total_list:
                expr = pd.sympy_reduce_total(expr)
            return expr


        view_cc_folding = False
        for pd in simplifications:
            try:
                pd.sympy_reduce_solutions
            except AttributeError:
                pass
            else:
                reduce_sols_list.append(pd)
            try:
                pd.sympy_reduce_total
            except AttributeError:
                pass
            else:
                reduce_total_list.append(pd)
            #use the last simplification to specify for the view_cc_folding
            v = getattr(pd, 'view_cc_folding', None)
            if v is not None:
                view_cc_folding = v

        #construct total and coeff lists, presimplifying multiplied conjugates
        key_field_op_mat = key_field_operator.array
        sol_array = self.solution_vectors[order].array
        sol_array_conj = self.solution_vectors_conj[order].array
        for idx_row, idx_col in np.argwhere(key_field_op_mat != 0):
            if idx_row == idx_col:
                b.total += key_field_op_mat[idx_row, idx_col] * abs(reduce_sols(sol_array[idx_row]))**2
            else:
                value_R = reduce_sols(sol_array[idx_col])
                #value_L = reduce_sols(sol_array_conj[idx_row])
                #TODO Remove these as they shouldn't be necessary when using raising/lowering
                value_L = value_R
                if not sympy.sympify(value_L).is_zero and not sympy.sympify(value_R).is_zero:
                    coeff_list.append(key_field_op_mat[idx_row, idx_col])
                    value_list_L.append(value_L)
                    value_list_R.append(value_R)
                    #print "TERM"
                    #display(coeff_list[-1])
                    #display(value_list_L[-1])
                    #display(value_list_R[-1])

        if view_cc_folding:
            #simplify conjugate pairs
            def c_rewrite(use_ratsimp = False):
                idx_a = 0
                while idx_a < len(coeff_list):
                    value_La = value_list_L[idx_a]
                    value_La_cc = self.conjugate(value_La)
                    idx_b = idx_a + 1
                    while idx_b < len(coeff_list):
                        value_Ra = value_list_R[idx_a]
                        value_Ra_cc = self.conjugate(value_Ra)

                        def tfunc_cc(vlistL, vlistR, sgn1, sgn2):
                            if not use_ratsimp:
                                simpe_1_x0 = sympy.sympify(value_La_cc - sgn1 * vlistR[idx_b]).is_zero
                                simpe_2_x0 = sympy.sympify(value_Ra_cc - sgn2 * vlistL[idx_b]).is_zero
                            else:
                                simpe_1_x0 = sympy.sympify(value_La_cc.expand() - sgn1 * vlistR[idx_b].expand()).is_zero
                                simpe_2_x0 = sympy.sympify(value_Ra_cc.expand() - sgn2 * vlistL[idx_b].expand()).is_zero

                            coeff_b = sgn1*sgn2*coeff_list[idx_b]
                            coeff_a = coeff_list[idx_a]

                            if simpe_1_x0 and simpe_2_x0:
                                coeff_a_cc = self.conjugate(coeff_a)
                                value_a =  value_La * value_Ra
                                value_a_cc = value_Ra_cc * value_La_cc
                                if sympy.sympify(coeff_a - coeff_b).is_zero:
                                    if choose_fewer_conjugates(value_a, value_a_cc):
                                        b.total += 2 * coeff_a * self.project_re(value_a)
                                    else:
                                        b.total += 2 * coeff_a * self.project_re(value_a_cc)
                                    return True
                                elif sympy.sympify(coeff_a + coeff_b).is_zero:
                                    if choose_fewer_conjugates(value_a, value_a_cc):
                                        b.total += 2 * coeff_a * self.i * self.project_im(value_a)
                                    else:
                                        b.total += -2 * coeff_a * self.i * self.project_im(value_a_cc)
                                    return True
                                elif sympy.sympify(coeff_a_cc - coeff_b).is_zero:
                                    if choose_fewer_conjugates(coeff_a * value_a, coeff_a_cc * value_a_cc):
                                        b.total += 2 * self.project_re(coeff_a * value_a)
                                    else:
                                        b.total += 2 * self.project_re(coeff_a_cc * value_a_cc)
                                    return True
                                elif sympy.sympify(coeff_a_cc + coeff_b).is_zero:
                                    if choose_fewer_conjugates(coeff_a * value_a, coeff_a_cc * value_a_cc):
                                        b.total += 2 * self.ps_In * self.project_im(coeff_a * value_a)
                                    else:
                                        b.total += -2 * self.ps_In * self.project_im(coeff_a_cc * value_a_cc)
                                    return True
                                return False

                        if (
                            tfunc_cc(value_list_L, value_list_R, +1, +1) or
                            tfunc_cc(value_list_L, value_list_R, -1, +1) or
                            tfunc_cc(value_list_L, value_list_R, +1, -1) or
                            tfunc_cc(value_list_L, value_list_R, -1, -1) or
                            tfunc_cc(value_list_R, value_list_L, +1, +1) or
                            tfunc_cc(value_list_R, value_list_L, -1, +1) or
                            tfunc_cc(value_list_R, value_list_L, +1, -1) or
                            tfunc_cc(value_list_R, value_list_L, -1, -1)
                        ):
                            #pop idx b first since it is larger
                            coeff_list.pop(idx_b)
                            value_list_L.pop(idx_b)
                            value_list_R.pop(idx_b)
                            value_list_L.pop(idx_a)
                            value_list_R.pop(idx_a)
                            coeff_list.pop(idx_a)
                            break
                        idx_b += 1
                    else:
                        idx_a += 1

            def p_rewrite():
                idx_a = 0
                while idx_a < len(coeff_list):
                    value_La = value_list_L[idx_a]
                    value_La_cc = self.conjugate(value_La)
                    idx_b = idx_a + 1
                    while idx_b < len(coeff_list):
                        value_Ra = value_list_R[idx_a]
                        value_Ra_cc = self.conjugate(value_Ra)

                        def tfunc(vlistL, vlistR, sgn1, sgn2, do_nest = True):
                            simpe_1_x1 = sympy.sympify(value_La    - sgn1 * vlistR[idx_b]).is_zero
                            simpe_2_x1 = sympy.sympify(value_Ra    - sgn2 * vlistL[idx_b]).is_zero

                            coeff_b = sgn1*sgn2*coeff_list[idx_b]
                            coeff_a = coeff_list[idx_a]
                            coeff_a_cc = self.conjugate(coeff_a)

                            if not (simpe_1_x1 or simpe_2_x1):
                                return False

                            if simpe_1_x1 and simpe_2_x1:
                                value_a =  value_La * value_Ra
                                if sympy.sympify(coeff_a + coeff_b).is_zero:
                                    #b.total += 0
                                    return True
                                elif sympy.sympify(coeff_a_cc - coeff_b).is_zero:
                                    b.total += 2*self.project_re(coeff_a) * value_a
                                    return True
                                elif sympy.sympify(coeff_a_cc + coeff_b).is_zero:
                                    b.total += 2*self.i*self.project_im(coeff_a) * value_a
                                    return True
                                else:
                                    b.total += (coeff_a + coeff_b) * value_a
                                    return True
                            elif simpe_1_x1:
                                if do_nest and tfunc(vlistL, vlistR, sgn1, -sgn2, False):
                                    return True
                                if sympy.sympify(coeff_a - coeff_b).is_zero:
                                    #b.total += coeff_a * value_La * (value_Ra + sgn2 * vlistL[idx_b])
                                    coeff_list.append(coeff_a)
                                    vlistL.append(value_La)
                                    vlistR.append((value_Ra + sgn2 * vlistL[idx_b]).simplify(ratio=1))
                                    return True
                                else:
                                    #b.total += value_La * (coeff_a * value_Ra + coeff_b * sgn2 * vlistL[idx_b])
                                    coeff_list.append(sympy.sympify(1))
                                    vlistL.append(value_La)
                                    vlistR.append((coeff_a * value_Ra + coeff_b * sgn2 * vlistL[idx_b]).simplify(ratio=1))
                                    return True
                            else:
                                if do_nest and tfunc(vlistL, vlistR, -sgn1, sgn2, False):
                                    return True
                                if sympy.sympify(coeff_a - coeff_b).is_zero:
                                    #b.total += coeff_a * value_Ra * (value_La + sgn2 * vlistR[idx_b])
                                    coeff_list.append(coeff_a)
                                    vlistL.append(value_Ra)
                                    vlistR.append((value_La + sgn2 * vlistR[idx_b]).simplify(ratio=1))
                                    return True
                                else:
                                    #b.total += value_Ra * (coeff_a * value_La + coeff_b * sgn2 * vlistR[idx_b])
                                    coeff_list.append(sympy.sympify(1))
                                    vlistL.append(value_Ra)
                                    vlistR.append((coeff_a * value_La + coeff_b * sgn2 * vlistR[idx_b]).simplify(ratio=1))
                                    return True
                            return False

                        if (
                            tfunc(value_list_L, value_list_R, +1, +1) or
                            tfunc(value_list_L, value_list_R, -1, +1) or
                            tfunc(value_list_L, value_list_R, +1, -1) or
                            tfunc(value_list_L, value_list_R, -1, -1) or
                            tfunc(value_list_R, value_list_L, +1, +1) or
                            tfunc(value_list_R, value_list_L, -1, +1) or
                            tfunc(value_list_R, value_list_L, +1, -1) or
                            tfunc(value_list_R, value_list_L, -1, -1)
                        ):
                            #pop idx b first since it is larger
                            coeff_list.pop(idx_b)
                            value_list_L.pop(idx_b)
                            value_list_R.pop(idx_b)
                            value_list_L.pop(idx_a)
                            value_list_R.pop(idx_a)
                            coeff_list.pop(idx_a)
                            break
                        idx_b += 1
                    else:
                        idx_a += 1
            c_rewrite()
            p_rewrite()
            c_rewrite(use_ratsimp=False)
        #accumulate remaining
        for coeff, value_L, value_R in zip(coeff_list, value_list_L, value_list_R):
            b.total += value_L * coeff * value_R

        return reduce_total(b.total)

    def collapse_field_operator_old(self, key_field_operator, order):
        #conjugate = np.vectorize(dmath.conjugate)
        @np.vectorize
        def conjugate(val):
            if val != 0:
                return abs(val)**2 / val
            return dmath.conjugate(val)
        return (conjugate(self.solution_vectors[order].row) * key_field_operator.mat * self.solution_vectors[order].col)[0, 0]

