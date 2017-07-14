# -*- coding: utf-8 -*-
"""
"""
#from builtins import zip, object
import sympy
from sympy.utilities.lambdify import lambdastr
from phasor.utilities.strings import canonicalize_TQStrings


def iter_group(iter_expr, n, func = lambda x: x):
    source = iter(iter_expr)
    def yield_n():
        idx = 0
        for item in source:
            yield item
            idx += 1
            if idx >= n:
                break
    while True:
        items = tuple(yield_n())
        if not items:
            return
        yield func(items)

def expr_atoms(expr):
    a = expr.atoms()
    syms = set()
    for v in a:
        if isinstance(v, sympy.Symbol):
            syms.add(v)
    return syms


def expr_functions(expr):
    return [a.func for a in expr.atoms(sympy.Function)]


def indent(s, n = 1):
    if not s:
        return s
    indent_space = '    ' * n
    return indent_space + s.replace('\n', '\n' + indent_space)


def indent_line_each(s_list, n = 1):
    if not s_list:
        return ''
    indent_space = '\n' + ('    ' * n)
    return indent_space + indent_space.join(s_list)


METHOD_TEMPLATE = canonicalize_TQStrings(
"""
_{name} = None
@property
def {name}(self):
    if self._{name} is None:
        self._{name} = {py_expr}
    return self._{name}

@{name}.setter
def {name}(self, value):
    self._{name} = value
    self._clear_cache()
    return
"""
)


INIT_TEMPLATE = canonicalize_TQStrings(
"""
def __init__(
    self, {args}
):
{no_defaults_setups}
{with_defaults_setups}
    return
"""
)


CLEAR_CACHE_TEMPLATE = canonicalize_TQStrings(
"""
_cache_variables = ({cache_variables})

def _clear_cache(self):
    for varname in self._cache_variables:
        try:
            delattr(self, varname)
        except AttributeError:
            pass
    return
"""
)


DEFAULT_ARG_SETUP_TEMPLATE = canonicalize_TQStrings(
"""
if {name} is not None:
    self._{name} = {name}
"""
)

NO_DEFAULT_ARG_SETUP_TEMPLATE = canonicalize_TQStrings(
"""
self._{name} = {name}
"""
)


VIEW_TEMPLATE = canonicalize_TQStrings(
"""
@property
def {name}(self):
    return self._{name}

@{name}.setter
def {name}(self, value):
    self._{name} = value
    self._clear_cache()
    return
"""
)

MODULE_TEMPLATE = canonicalize_TQStrings(
"""
from __future__ import division, print_function, unicode_literals
import numpy as np
from numpy import pi

class {classname}(object):
    _m = np
{defaults}

{initmethod}
{expr_methods}
{value_views}
{auto_methods}
{clear_cache_method}
"""
)


class SympyExpressionGenerator(object):

    def __init__(self, classname):
        self.classname = classname
        self.expressions_to_variables = {}
        self.variable_default_values = {}
        self.variable_rename = {}
        self.function_rename = {sympy.Abs.__name__ : 'abs'}
        self.autogen_variable_format = "_x{num}"

    def autogenerate_name_iter(self):
        num = 0
        while True:
            yield sympy.var(self.autogen_variable_format.format(num = num))
            num += 1
        return

    def expression_add(self, name, expr):
        self.expressions_to_variables[name] = sympy.sympify(expr)

    def variable_name_set(self, var, name):
        self.variable_rename[var.name] = name

    def function_name_set(self, var, name):
        self.function_rename[var.__name__] = name

    def variable_default_set(self, var, default_value):
        self.variable_default_values[var.name] = default_value

    def generate(self):
        expr_name_list, expr_list = list(zip(*iter(list(self.expressions_to_variables.items()))))

        expr_vars = set()
        expr_funcs = set()
        for expr in expr_list:
            expr_vars.update(expr.free_symbols)
            expr_funcs.update(expr_functions(expr))

        cse_pair_list, cse_expr_remap = sympy.cse(
            expr_list,
            symbols=self.autogenerate_name_iter(),
            optimizations='basic'
        )
        cse_vars, cse_exprs = list(zip(*cse_pair_list))

        expr_vars_no_default = set()
        expr_vars_default = {}
        expr_vars_to_classname = {}
        expr_vars_to_selfname = {}
        for var in expr_vars:
            name = self.variable_rename.get(var.name, var.name)
            expr_vars_to_classname[var] = name
            expr_vars_to_selfname[var] = "self.{0}".format(name)
            if name not in self.expressions_to_variables:
                default = self.variable_default_values.get(var.name, None)
                if default is None:
                    expr_vars_no_default.add(var)
                else:
                    expr_vars_default[var] = default

        cse_vars_to_classname = {}
        cse_vars_to_selfname = {}
        for var in cse_vars:
            name = var.name
            cse_vars_to_classname[var] = name
            cse_vars_to_selfname[var] = "self.{0}".format(name)

        func_vars_to_selfname = {}
        for func in expr_funcs:
            name = self.function_rename.get(func.__name__, func.__name__)
            #all sympy functions are type-objects, so we have to get their class names
            func_vars_to_selfname[func] = "self._m.{0}".format(name)

        def hypersubs(expr):
            expr = expr.subs(sympy.ps_In, sympy.var('1j'))
            for func, name in list(func_vars_to_selfname.items()):
                expr = expr.replace(func, sympy.var(name))
            for var, name in list(expr_vars_to_selfname.items()):
                expr = expr.subs(var, sympy.var(name))
            for var, name in list(cse_vars_to_selfname.items()):
                expr = expr.subs(var, sympy.var(name))
            for func, name in list(func_vars_to_selfname.items()):
                expr = expr.subs(func, sympy.Function(name))
            return expr

        import re
        re_sqrt = re.compile(r'([^\w\d])sqrt\(')
        def final_transforms(str_expr):
            str_expr = re_sqrt.sub(r'\1self._m.sqrt(', str_expr)
            return str_expr.strip()

        cache_var_names = []
        cse_python_exprs = {}
        for var, expr in zip(cse_vars, cse_exprs):
            classname = cse_vars_to_classname[var]
            cache_var_names.append('_' + classname)
            lstr = lambdastr([], hypersubs(expr))
            cse_python_exprs[classname] = final_transforms(lstr.split(':')[1])

        main_python_exprs = {}
        for classname, expr in zip(expr_name_list, cse_expr_remap):
            cache_var_names.append('_' + classname)
            lstr = lambdastr([], hypersubs(expr))
            main_python_exprs[classname] = final_transforms(lstr.split(':')[1])

        main_methods = []
        for name, py_expr in sorted(main_python_exprs.items()):
            method_str = METHOD_TEMPLATE.format(
                name = name,
                py_expr = py_expr,
            )
            main_methods.append(method_str)

        auto_methods = []
        for name, py_expr in sorted(cse_python_exprs.items()):
            method_str = METHOD_TEMPLATE.format(
                name = name,
                py_expr = py_expr,
            )
            auto_methods.append(method_str)

        with_defaults = []
        no_defaults_args = []
        with_defaults_args = []
        no_defaults_setups = []
        with_defaults_setups = []
        value_views = []

        done = set()
        for var, default in sorted(iter(list(expr_vars_default.items())), key = lambda p: expr_vars_to_classname[p[0]]):
            classname = expr_vars_to_classname[var]
            if classname in done:
                continue
            else:
                done.add(classname)
            with_defaults.append(
                "_{name} = {default}".format(name = classname, default = repr(default))
            )
            with_defaults_args.append(
                "{name} = None,".format(name = classname, default = repr(default))
            )
            with_defaults_setups.append(
                DEFAULT_ARG_SETUP_TEMPLATE.format(name = classname)
            )
            value_views.append(
                VIEW_TEMPLATE.format(name = classname)
            )

        done = set()
        for var in expr_vars_no_default:
            classname = expr_vars_to_classname[var]
            if classname in done:
                continue
            else:
                done.add(classname)
            no_defaults_args.append(
                "{name},".format(name = classname)
            )
            no_defaults_setups.append(
                NO_DEFAULT_ARG_SETUP_TEMPLATE.format(name = classname)
            )
            value_views.append(
                VIEW_TEMPLATE.format(name = classname)
            )


        init_str = INIT_TEMPLATE.format(
            args     = indent_line_each(no_defaults_args + with_defaults_args),
            no_defaults_setups   = indent((''.join(no_defaults_setups))),
            with_defaults_setups = indent((''.join(with_defaults_setups)).strip()),
        )

        def transform_names(varnames):
            for name in varnames:
                if name.startswith('__'):
                    name = '_' + self.classname + name
                yield name
        cache_var_names = ["'{0}'".format(vname) for vname in transform_names(cache_var_names)]
        if len(cache_var_names) == 0:
            cache_variables_str = ''
        elif len(cache_var_names) == 1:
            cache_variables_str = cache_var_names[0] + ','
        else:
            cache_var_names = list(reversed(cache_var_names))
            cache_variables_str = indent('\n' + ',\n'.join(iter_group(cache_var_names, 5, lambda x: ','.join(x))) + ',') + '\n'

        cache_str = CLEAR_CACHE_TEMPLATE.format(
            cache_variables = cache_variables_str,
        )

        return MODULE_TEMPLATE.format(
            classname          = self.classname,
            defaults           = indent('\n'.join(with_defaults)),
            initmethod         = indent(init_str),
            expr_methods       = indent('\n'.join(main_methods)),
            value_views        = indent('\n'.join(value_views)),
            auto_methods       = indent('\n'.join(auto_methods)),
            clear_cache_method = indent(cache_str),
        )


