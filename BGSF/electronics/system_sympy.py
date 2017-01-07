from system import ElectricalSystem
import sympy
import numpy as np

from YALL.utilities.bunch import Bunch
import YALL.utilities.numerics.dispatched as dmath
import YALL.utilities.numerics.dispatch_sympy

var = sympy.var

var_c = sympy.var

def var_rp(name):
    return sympy.var(name, real = True, positive = True)


def var_r(name):
    return sympy.var(name, real = True)


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



class ElectricalSystemSympy(ElectricalSystem):
    pi            = sympy.pi
    i             = sympy.I
    math          = sympy
    project_re    = projectR
    project_im    = projectI

    Z_termination = var_r('Z_0')

    def number(self, num):
        return sympy.sympify(num)

    def solve_system(self, sympy_matrix_inverse = None):
        rt = sympy.Matrix(self.coupling_matrix_rt.array)
        print("Solving")
        if sympy_matrix_inverse is None:
            rt_inv = rt.inverse_GE(simplify = simplify)
        else:
            rt_inv = sympy_matrix_inverse(rt)
        self.coupling_matrix_rt_inv = self.coupling_matrix_rt.backmap_array_inv(rt_inv)
        return

def sympy_sage_maxima_inv(M):
    m_list = []
    for v in M:
        if not sympify(v).is_number:
            m_list.append(v._sage_())
        else:
            m_list.append(v)

    m = matrix(SR, M.shape[0], M.shape[1], m_list)
    m_maxima = m._maxima_()
    m_maxima_inv = m_maxima.invert().ratsimp()
    m_inv = m_maxima_inv._sage_()
    m_sympy_inv = [[v._sympy_() for v in col] for col in m_inv.rows()]
    return m_sympy_inv
