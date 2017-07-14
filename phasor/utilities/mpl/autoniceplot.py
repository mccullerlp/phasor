# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import os
from os import path

import declarative
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from .colors import color_array

try:
    org_mode
except NameError:
    org_mode = False


class SaveToken(declarative.OverridableObject):
    aps = None
    fbasename = None

    def __lshift__(self, other):
        self.aps(self.fbasename, fig_or_fbunch = other)
        return other
    def __rlshift__(self, other):
        self.aps(self.fbasename, fig_or_fbunch = other)
        return other
    def __rshift__(self, other):
        self.aps(self.fbasename, fig_or_fbunch = other)
        return other
    def __rrshift__(self, other):
        self.aps(self.fbasename, fig_or_fbunch = other)
        return other

def mpl_autorasterize(fig):
    children_current = fig.get_children()
    children_ever = set()
    while children_current:
        child = children_current.pop()
        if child in children_ever:
            continue
        else:
            children_ever.add(child)

        try:
            more_children = child.get_children()
        except AttributeError:
            pass
        else:
            children_current.extend(more_children)

        try:
            xdat = child.get_xdata()
            if len(xdat) > 100:
                child.set_rasterized(True)
                child.set_antialiased(True)
            continue
        except AttributeError:
            pass

        try:
            paths = child.get_paths()
            for p in paths:
                if len(p.vertices) > 100:
                    child.set_rasterized(True)
                    child.set_antialiased(True)
                    #print(child, len(xdat))
        except AttributeError:
            pass


class AutoPlotSaver(declarative.OverridableObject):
    max_width_in = None
    max_height_in = None
    save_dpi = 400

    org_dpi = 100
    org_subfolder = None

    rasterize_auto = True
    formats = declarative.DeepBunch()
    formats.pdf.use = True
    formats.jpg.use = False
    formats.jpg.dpi = 200
    formats.jpg.facecolorize = True
    formats.png.use = False

    embed = False

    def __call__(self, fbasename, fig_or_fbunch = None):
        if fig_or_fbunch is None:
            return SaveToken(
                aps = self,
                fbasename = fbasename,
            )
        try:
            fig = fig_or_fbunch.fig
        except AttributeError:
            fig = fig_or_fbunch
        w, h = fig.get_size_inches()
        if self.max_width_in is not None and w > self.max_width_in:
            new_w = self.max_width_in
            new_h = float(h)/float(w) * new_w
            fig.set_size_inches(new_w, new_h)

        if self.rasterize_auto:
            mpl_autorasterize(fig)

        subfolder = ''
        if self.org_subfolder:
            subfolder = self.org_subfolder
        fbasename = path.join(subfolder, fbasename)
        dirname = path.dirname(fbasename)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

        global org_mode
        for fmt, fB in self.formats.items():
            if fmt == 'png' and (org_mode or self.org_subfolder):
                pass
            elif not fB.use:
                continue
            if fB.dpi:
                dpi = fB.dpi
            else:
                dpi = self.save_dpi
            kwargs = dict()
            if fB.facecolorize:
                kwargs['facecolor'] = fig.get_facecolor()
            fig.savefig(
                fbasename + '.' + fmt,
                dpi = dpi,
                bbox_inches = 'tight',
                #tight_layout=True,
                pad_inches = 0.05,
                transparent=True,
                quality = 50,
                **kwargs
            )

        if org_mode or self.org_subfolder:
            fname = fbasename + '.png'
            print("figure: {0}".format(fname))
            print("[[file:{0}]]".format(fname))
            if not self.embed:
                try:
                    import IPython.display
                    import time
                    #IPython.display.display(IPython.display.Image(filename=fname, embed=False))
                    html_bit = '<img src="{1}/../{0}?{1}">'.format(fname, int(time.time()))
                    IPython.display.display(IPython.display.HTML(html_bit))
                    plt.close(fig)
                except ImportError:
                    pass
            else:
                try:
                    import IPython.display
                    import time
                    IPython.display.display(IPython.display.Image("{0}".format(fname)))
                    plt.close(fig)
                except ImportError:
                    pass

        fig.set_dpi(144)
        return

asavefig = AutoPlotSaver()

def patchify_axes(ax, plotname, check_log_Y = False):
    oldplot = getattr(ax, plotname)

    def plot(X, Y, *args, **kwargs):
        Y = np.asarray(Y)
        b = np.broadcast(X, Y)

        if check_log_Y and np.all(Y <= 0):
            return

        if b.shape != Y.shape:
            Y = np.ones(X.shape) * Y
        return oldplot(X, Y, *args, **kwargs)
    plot.__name__ = oldplot.__name__
    plot.__doc__  = oldplot.__doc__
    setattr(ax, plotname, plot)

def patch_axes(ax):
    patchify_axes(ax, 'plot')
    patchify_axes(ax, 'loglog', check_log_Y = True)
    patchify_axes(ax, 'semilogy', check_log_Y = True)
    patchify_axes(ax, 'semilogx')

def mplfigB(
        Nrows         = 1,
        Ncols         = 1,
        size_in       = None,
        size_in_base  = (6, 2),
        size_in_dW_dH = (3, 1),
        x_by_col      = False,
):
    if size_in:
        width_in = size_in[0]
        height_in = size_in[1]
    else:
        width_in = size_in_base[0] + Ncols * size_in_dW_dH[0]
        height_in = size_in_base[1] + Nrows * size_in_dW_dH[1]

    axB = declarative.Bunch()
    axB.fig = plt.figure()
    axB.fig.set_size_inches(width_in, height_in)

    global asavefig
    def save(rootname, **kwargs):
        axB << asavefig(rootname, **kwargs)
    axB.save = save

    N = 0
    axB.ax_grid_colrow = []
    for idx_col in range(Ncols):
        ax_list = []
        axB.ax_grid_colrow.append([])
        for idx_row in range(Nrows):
            if x_by_col:
                if idx_row != 0:
                    sharex = axB.ax_grid_colrow[idx_col][0]
                else:
                    sharex = None
            else:
                sharex = None
            ax = axB.fig.add_subplot(Nrows, Ncols, idx_row + idx_col*Nrows + 1, sharex = sharex)
            ax.set_prop_cycle(
                color = color_array
            )
            patch_axes(ax)
            ax_list.append(ax)
            ax.grid(b=True)
            axB.ax_grid_colrow[idx_col].append(ax)
            axB["ax{0}_{1}".format(idx_row, idx_col)] = ax
            axB["ax{0}".format(N)] = ax
            N += 1
            if idx_col == 0:
                if idx_row == 0:
                    axB.ax_top = ax
                if idx_row == Nrows-1:
                    axB.ax_bottom = ax
                axB['ax_list']   = ax_list
        axB['ax_list_{0}'.format(idx_col)]    = ax_list
    return axB


asavefig = AutoPlotSaver()
