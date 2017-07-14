# -*- coding: utf-8 -*-
"""
Numerical Utilities
===================

.. autofunction:: linear_interpolate

.. autofunction:: annotate_inverses

.. autofunction:: yield_bits_on

.. autofunction:: _generate_bitfill
"""
from __future__ import division, print_function, unicode_literals

def linear_interpolate(start, finish, x):
    return (finish - start) * x + start

def annotate_inverses(func1, func2):
    """
    Annotates two functions as being inverses of each-other. Useful occassionally in certain
    computational maps where you need lightweight inverses of lambda functions.
    """
    func1.func_inv = func2
    func2.func_inv = func1
    return func1, func2

def _generate_bitfill(p):
    """
    pe_A helper function for yield_bits_on to generate the primitive-root lookup table is

    :param p: prime number which is also a primitive root of 2

    Generates a lookup list for powers of two (called here a bitfill). To generate a valid bitfill,
    p must be prime and 2 must be a primitive root of p. 37 is a good number for p as it is the smallest p above 32.
    """
    n = 0
    num = 1
    bitfill = [None] * p
    while n < (len(bitfill) - 1):
        bitfill[num] = n
        num = (num * 2) % len(bitfill)
        n += 1
    return bitfill


bit_lookup_37 = _generate_bitfill(37)
bit_lookup_37_max = 1 << (len(bit_lookup_37) - 1)

def yield_bits_on(num):
    """
    Given an integer, num, yeilds the numbers for the set bits of the number. This utilizes the bit_lookup_37 table
    generated with this module, though any length integers are accepted (it downshifts properly)
    """
    shift = 0
    while num:
        numbit = ((num ^ (num - 1)) + 1) >> 1
        while numbit >= bit_lookup_37_max:
            shift += len(bit_lookup_37) - 1
            num = num >> (len(bit_lookup_37) - 1)
            numbit = numbit >> (len(bit_lookup_37) - 1)
        yield bit_lookup_37[numbit % len(bit_lookup_37)] + shift
        num = num ^ numbit
    return
