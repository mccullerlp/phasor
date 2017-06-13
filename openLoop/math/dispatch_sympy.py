from . import dispatched
import sympy

sympy_mods = [sympy, sympy.functions]
dispatched.module_by_type[sympy.var('x').__class__] = sympy_mods
dispatched.module_by_type[sympy.numbers.Zero] = sympy_mods
dispatched.module_by_type[sympy.numbers.One] = sympy_mods
dispatched.module_by_type[sympy.Mul] = sympy_mods
dispatched.module_by_type[sympy.Add] = sympy_mods

def zero_check_heuristic(arg):
    return arg == 0

