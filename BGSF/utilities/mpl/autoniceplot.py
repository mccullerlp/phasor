#!/usr/bin/env python2
"""
"""

import os
from os import path
import matplotlib as mpl
import declarative as decl


try:
    org_mode
except NameError:
    org_mode = False


class SaveToken(decl.OverridableObject):
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
            continue
        except AttributeError:
            pass

        try:
            paths = child.get_paths()
            for p in paths:
                if len(p.vertices) > 100:
                    child.set_rasterized(True)
                    print(child, len(xdat))
        except AttributeError:
            pass


class AutoPlotSaver(decl.OverridableObject):
    max_width_in = None
    max_height_in = None
    save_dpi = 400

    org_dpi = 100
    org_subfolder = None

    rasterize_auto = True

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

        fig.savefig(
            fbasename + '.pdf',
            dpi = self.save_dpi,
            bbox_inches = 'tight',
            #tight_layout=True,
            pad_inches = 0.05,
            transparent=True,
        )

        global org_mode
        if org_mode or self.org_subfolder:
            fname = fbasename + '.png'
            fig.savefig(
                fname,
                dpi = self.org_dpi,
                bbox_inches = 'tight',
                #tight_layout=True,
                pad_inches = 0.05,
                transparent=False,
            )
            print("figure: {0}".format(fname))
            print("[[file:{0}]]".format(fname))
            try:
                import IPython.display
                import time
                #IPython.display.display(IPython.display.Image(filename=fname, embed=False))
                html_bit = '<img src="{1}/../{0}?{1}">'.format(fname, int(time.time()))
                IPython.display.display(IPython.display.HTML(html_bit))
                import matplotlib.pyplot as plt
                plt.close(fig)
            except ImportError:
                pass

        fig.set_dpi(144)
        return


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

    axB = decl.Bunch()
    axB.fig = mpl.figure()
    axB.fig.set_size_inches(width_in, height_in)

    global asavefig
    def save(rootname, **kwargs):
        axB << asavefig(rootname, **kwargs)
    axB.save = save

    N = 0
    axB.ax_grid_colrow = []
    for idx_col in range(Ncols):
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
    return axB


asavefig = AutoPlotSaver()
