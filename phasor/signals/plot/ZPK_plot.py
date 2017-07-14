# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np
import math

from matplotlib.text import OffsetFrom
import declarative

def eng_string(x, format='%.3f', si=False):
    '''
    Returns float/int value <x> formatted in a simplified engineering format -
    using an exponent that is a multiple of 3.

    format: printf-style string used to format the value before the exponent.

    si: if true, use SI suffix for exponent, e.g. k instead of e3, n instead of
    e-9 etc.

    E.g. with format='%.2f':
        1.23e-08 => 12.30e-9
             123 => 123.00
          1230.0 => 1.23e3
      -1230000.0 => -1.23e6

    and with si=True:
          1230.0 => 1.23k
      -1230000.0 => -1.23M
    '''
    sign = ''
    if x < 0:
        x = -x
        sign = '-'
    exp = int(math.floor(math.log10(x)))
    expe_3 = exp - (exp % 3)
    x3 = x / (10 ** expe_3)

    if si and expe_3 >= -24 and expe_3 <= 24 and expe_3 != 0:
        expe_3_text = 'yzafpnum kMGTPEZY'[(expe_3 - (-24)) / 3]
    elif expe_3 == 0:
        expe_3_text = ''
    else:
        expe_3_text = 'e%s' % expe_3

    return ('%s'+format+'%s') % (sign, x3, expe_3_text)


class ZPKAnnotator(declarative.OverridableObject):
    bbox_args = dict(boxstyle="round", fc="0.8")
    bbox_args = dict()
    arrow_args = dict(
        arrowstyle="->",
        connectionstyle="angle,angleB=90,angleA=180,rad=3",
        linewidth = .5,
    )

    style   = dict(
        ls = '--',
        lw = .5,
    )
    style_vline    = dict()
    style_annotate = dict()
    style_poles    = dict()
    style_zeros    = dict()
    style_real     = dict()
    style_cplx     = dict()
    style_poles_r  = dict()
    style_zeros_r  = dict()
    style_poles_c  = dict()
    style_zeros_c  = dict()

    def annolist(
        self,
        poles_r        = (),
        poles_c        = (),
        zeros_r        = (),
        zeros_c        = (),
        style          = None,
        style_vline    = None,
        style_annotate = None,
        style_poles    = None,
        style_zeros    = None,
        style_real     = None,
        style_cplx     = None,
        style_poles_r  = None,
        style_zeros_r  = None,
        style_poles_c  = None,
        style_zeros_c  = None,
    ):
        desc_by_x = []
        style          = declarative.first_non_none(style         , self.style         )
        style_vline    = declarative.first_non_none(style_vline   , self.style_vline   )
        style_annotate = declarative.first_non_none(style_annotate, self.style_annotate)
        style_poles    = declarative.first_non_none(style_poles   , self.style_poles   )
        style_zeros    = declarative.first_non_none(style_zeros   , self.style_zeros   )
        style_real     = declarative.first_non_none(style_real    , self.style_real    )
        style_cplx     = declarative.first_non_none(style_cplx    , self.style_cplx    )
        style_poles_r  = declarative.first_non_none(style_poles_r , self.style_poles_r )
        style_zeros_r  = declarative.first_non_none(style_zeros_r , self.style_zeros_r )
        style_poles_c  = declarative.first_non_none(style_poles_c , self.style_poles_c )
        style_zeros_c  = declarative.first_non_none(style_zeros_c , self.style_zeros_c )

        for root in poles_r:
            desc = "Pole:{0}Hz".format(eng_string(root))
            lkw = dict(style)
            loc = abs(root)
            lkw.update(style_vline)
            lkw.update(style_poles)
            lkw.update(style_real)
            lkw.update(style_poles_r)
            akw = dict(style)
            akw.update(style_annotate)
            akw.update(style_poles)
            akw.update(style_real)
            akw.update(style_poles_r)
            desc_by_x.append((loc, desc, lkw, akw))

        for root in zeros_r:
            desc = "Zero:{0}Hz".format(eng_string(root))
            lkw = dict(style)
            loc = abs(root)
            lkw.update(style_vline)
            lkw.update(style_zeros)
            lkw.update(style_real)
            lkw.update(style_zeros_r)
            akw = dict(style)
            akw.update(style_annotate)
            akw.update(style_zeros)
            akw.update(style_real)
            akw.update(style_zeros_r)
            desc_by_x.append((loc, desc, lkw, akw))

        for root in poles_c:
            desc = "CPole:{0}+{1}i [Hz]".format(eng_string(root.real), eng_string(root.imag))
            loc = abs(root.real) if abs(root.real) > abs(root.imag) else abs(root.imag)
            lkw = dict(style)
            lkw.update(style_vline)
            lkw.update(style_poles)
            lkw.update(style_cplx)
            lkw.update(style_poles_c)
            akw = dict(style)
            akw.update(style_annotate)
            akw.update(style_poles)
            akw.update(style_cplx)
            akw.update(style_poles_c)
            desc_by_x.append((loc, desc, lkw, akw))

        for root in zeros_c:
            desc = "CZero:{0}+{1}i [Hz]".format(eng_string(root.real), eng_string(root.imag))
            loc = abs(root.real) if abs(root.real) > abs(root.imag) else abs(root.imag)
            lkw = dict(style)
            lkw.update(style_vline)
            lkw.update(style_zeros)
            lkw.update(style_cplx)
            lkw.update(style_zeros_c)
            akw = dict(style)
            akw.update(style_annotate)
            akw.update(style_zeros)
            akw.update(style_cplx)
            akw.update(style_zeros_c)
            desc_by_x.append((loc, desc, lkw, akw))
        return desc_by_x

    def annotate(
        self,
        fB,
        desc_by_x = None,
        **kwargs
    ):
        if desc_by_x is None:
            desc_by_x = self.annolist(**kwargs)
        desc_by_x.sort()

        zs = np.array([tup[0] for tup in desc_by_x])
        xlow, xhigh = fB.ax_top.get_xlim()
        if fB.ax_bottom.get_xscale().find('log') != -1:
            xmid = np.exp((np.log(xlow) + np.log(xhigh))/2)
        else:
            xmid = (xlow + xhigh)/2
        idx_mid = np.searchsorted(zs, xmid)

        left_list = desc_by_x[:idx_mid]
        right_list = desc_by_x[idx_mid:]
        fsize_sep = 15

        for idx, (z, desc, lkw, akw) in enumerate(reversed(left_list)):
            #top elements
            if z < xlow:
                z = xlow
            arrowkw = dict(self.arrow_args)
            arrowkw.update(akw)
            an = fB.ax_top.annotate(
                desc,
                xy=(z, 1), xycoords=fB.ax_top.get_xaxis_transform(),
                xytext=(0, 15 + fsize_sep * idx), textcoords=OffsetFrom(fB.ax_top.bbox, (1, 1), "points"),
                ha = "right", va = "bottom",
                bbox = self.bbox_args,
                arrowprops = arrowkw,
            )
            for ax in fB.ax_list:
                ax.axvline(float(z), **lkw)

        for idx, (z, desc, lkw, akw) in enumerate(right_list):
            #bottom elements
            if z > xhigh:
                z = xhigh
            arrowkw = dict(self.arrow_args)
            arrowkw.update(akw)
            an = fB.ax_bottom.annotate(
                desc,
                xy=(z, -.12), xycoords=fB.ax_bottom.get_xaxis_transform(),
                xytext=(0, -34 - fsize_sep * idx), textcoords=OffsetFrom(fB.ax_bottom.bbox, (0, 0), "points"),
                ha="left", va="bottom",
                bbox=self.bbox_args,
                arrowprops = arrowkw,
            )
            for ax in fB.ax_list:
                ax.axvline(float(z), **lkw)
        return


