# -*- coding: utf-8 -*-
"""
===========================
Matplotlib Utility Functions
============================

test code

.. autofunction:: hsv_to_rgb

"""
from __future__ import division, print_function, unicode_literals

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors


import contextlib
from matplotlib.ticker import LogLocator, AutoLocator
from matplotlib.scale import LogScale
from matplotlib import transforms as mtransforms
import math


@contextlib.contextmanager
def savefig(save_name, size_x_in, size_y_in):
    fig = plt.figure()
    yield fig
    fig.set_size_inches(size_x_in, size_y_in)
    fig.savefig(save_name)

def hsva_to_rgba(h,s,v,a=1.):
    """
    Convert h,s,v into rgb using mpl. The converter of mpl is vectorized, so it is not convenient for
    this operation, this is convenient. Furthermore, this will correctly wrap the h value
    """

    s = min(s,1.)
    s = max(s,0.)
    v = min(v,1.)
    v = max(v,0.)
    mpl_formatted = np.array([[[h % 1.,s,v]]])
    rgbarray = mpl.colors.hsv_to_rgb(mpl_formatted)[0,0]
    return np.concatenate([rgbarray, [a]])

def vertical_stack_optional(ax_list, ax_names, fig = None, autofig = True, share_x = False):
    if autofig and all(ax is None for ax in ax_list):
        import matplotlib.pylab as plt
        if fig is None:
            fig = plt.figure()
        for idx in range(len(ax_list)):
            if idx > 0 or (not share_x):
                ax = fig.add_subplot(len(ax_list),1,idx + 1)
            else:
                ax = fig.add_subplot(len(ax_list),1,idx + 1, sharex = ax_list[0])
            ax_list[idx] = ax
    ax_dict = DictTree()
    for name, ax in zip(ax_names, ax_list):
        ax_dict.local_set(name, ax)
    return ax_dict



class LogLocator2(LogLocator):
    """
    Determine the tick locations for log axes
    """

    def view_limits(self, vmin, vmax):
        'Try to choose the view limits intelligently'
        b = self._base

        if vmax < vmin:
            vmin, vmax = vmax, vmin

        if self.axis.axes.name == 'polar':
            vmax = math.ceil(math.log(vmax) / math.log(b))
            vmin = b ** (vmax - self.numdecs)
            return vmin, vmax

        minpos = self.axis.get_minpos()

        if minpos <= 0 or not np.isfinite(minpos):
            raise ValueError(
                "Data has no positive values, and therefore can not be "
                "log-scaled.")

        if vmin <= minpos:
            vmin = minpos
        result = mtransforms.nonsingular(vmin, vmax)
        return result


class AutoLocator2(AutoLocator):
    """
    """
    def tick_values(self, vmin, vmax):
        locs = super(AutoLocator2, self).tick_values(vmin, vmax)
        locs = np.asarray(locs)
        tidx = np.searchsorted(locs, vmax)
        if tidx == len(locs):
            tidx -= 1
        ticksep = (locs[tidx] - locs[tidx - 1])
        tickmax = vmax - ticksep / 2
        locs = locs[locs < tickmax]
        return locs


class LogScale2(LogScale):
    name = 'log_zoom'
    def set_default_locators_and_formatters(self, axis):
        """
        Set the locators and formatters to specialized versions for
        log scaling.
        """
        super(LogScale2, self).set_default_locators_and_formatters(axis)
        axis.set_major_locator(LogLocator2(self.base))
        axis.set_minor_locator(LogLocator2(self.base, self.subs))

mpl.scale.register_scale(LogScale2)



def indexed_cmap(N, cmap = 'hsv', offset = 0):
    '''Returns a function that maps each index in 0, 1, ... N-1 to a distinct
    RGB color.'''
    color_norm  = colors.Normalize(vmin=0, vmax=N)
    scalar_map = cmx.ScalarMappable(norm=color_norm, cmap=cmap)
    def map_index_to_rgb_color(index):
        return scalar_map.to_rgba(index + offset)
    return map_index_to_rgb_color
