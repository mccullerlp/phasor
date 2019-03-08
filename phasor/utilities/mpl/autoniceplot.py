# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import warnings
import os
import contextlib
from os import path

import declarative
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np

from .colors import color_array

try:
    org_mode
except NameError:
    org_mode = False


def save_figure_MP(fig, fname, *args, **kwargs):
    """
    After pickling to a subprocess, the canvas is destroyed due to matplotlib bullshit, so make a new one as it apparently doesn't
    do this for you
    """
    if fig.canvas is None:
        canvas = FigureCanvas(fig)
        fig.set_canvas(canvas)
    return fig.savefig(fname, *args, **kwargs)


class SaveToken(declarative.OverridableObject):
    aps = None
    fbasename = None
    kwargs = {}

    def __lshift__(self, other):
        self.aps(self.fbasename, fig_or_fbunch = other, **self.kwargs)
        return other
    def __rlshift__(self, other):
        self.aps(self.fbasename, fig_or_fbunch = other, **self.kwargs)
        return other
    def __rshift__(self, other):
        self.aps(self.fbasename, fig_or_fbunch = other, **self.kwargs)
        return other
    def __rrshift__(self, other):
        self.aps(self.fbasename, fig_or_fbunch = other, **self.kwargs)
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
    formats.pdf.use          = True
    formats.jpg.use          = False
    formats.jpg.dpi          = 200
    formats.jpg.facecolorize = True
    formats.png.use          = False

    embed     = False
    save_show = True
    fixname   = True
    _pool     = None

    _last_async_result = None

    @contextlib.contextmanager
    def pool(self, workers = 4):
        """
        runs the plot save in a contextmanager and waits for the plotting to be done simultaneously
        """
        import multiprocessing
        wasnone = False
        if self._pool is None:
            if workers > 1:
                asavefig._pool = multiprocessing.Pool(workers)
                asavefig._last_async_result = []
            wasnone = True
        yield
        if asavefig._last_async_result is not None:
            for result in asavefig._last_async_result:
                result.get()
            asavefig._last_async_result = []
        if wasnone:
            if asavefig._pool is not None:
                asavefig._pool.close()
                asavefig._pool.join()
                asavefig._pool = None
            asavefig._last_async_result = None

    def __call__(
            self,
            fbasename,
            fig_or_fbunch = None,
            fixname = None,
    ):

        if fig_or_fbunch is None:
            return SaveToken(
                aps = self,
                fbasename = fbasename,
                kwargs = dict(
                    fixname = fixname,
                ),
            )

        fixname = fixname if fixname is not None else self.fixname

        try:
            fig = fig_or_fbunch.fig

            formats = fig_or_fbunch.get("formats", None)
            #the "get" method unwraps the deepbunch
            formats = declarative.DeepBunch(formats)
            if not formats:
                formats = self.formats

            save_show    = fig_or_fbunch.get("save_show", None)
            #and needed since show may be empty DeepBunch
            if not save_show and save_show is not False:
                save_show = self.save_show

        except AttributeError:
            fig = fig_or_fbunch
            save_show = self.save_show
            formats = self.formats
        w, h = fig.get_size_inches()
        if self.max_width_in is not None and w > self.max_width_in:
            new_w = self.max_width_in
            new_h = float(h)/float(w) * new_w
            fig.set_size_inches(new_w, new_h)

        #this silly bit reduces the formats to only the one specified
        fbase, fext = path.splitext(fbasename)
        if fext:
            fbasename = fbase
            #cut off the dot
            fext = fext[1:]
            single_formats = declarative.DeepBunch()
            #apply any settings stored in this object or the plot itself
            single_formats[fext].update_recursive(self.formats[fext])
            single_formats[fext].update_recursive(formats[fext])
            #force usage of this single format!
            single_formats[fext].use = True
            formats = single_formats

        if self.rasterize_auto:
            mpl_autorasterize(fig)

        subfolder = ''
        if self.org_subfolder:
            subfolder = self.org_subfolder

        fbasepath, fbasefname = path.split(fbasename)
        if '_' in fbasefname and fixname:
            warnings.warn("Image name contains '_' which will be changed to '-' to fix nbsphinx export")
            fbasefname = fbasefname.replace('_', '-')
            fbasename = path.join(fbasepath, fbasename)

        fbasename = path.join(subfolder, fbasename)
        dirname = path.dirname(fbasename)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

        global org_mode
        used_png = False
        for fmt, fB in formats.items():
            if fmt == 'png' and (org_mode or self.org_subfolder):
                #to avoide the elif
                pass
            elif not fB.use:
                continue
            if fmt == 'png':
                used_png = True
            if fB.dpi:
                dpi = fB.dpi
            else:
                dpi = self.save_dpi
            kwargs = dict()
            if fB.facecolorize:
                kwargs['facecolor'] = fig.get_facecolor()
            if self._pool is None:
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
            else:
                mydir = os.getcwd()
                self._last_async_result.append(
                    self._pool.apply_async(
                        save_figure_MP,
                        args          = (
                            fig,
                            os.path.join(mydir, fbasename + '.' + fmt),
                        ),
                        kwds = dict(
                            dpi           = dpi,
                            bbox_inches   = 'tight',
                            pad_inches    = 0.05,
                            transparent   = True,
                            quality       = 50,
                            #tight_layout =True,
                            **kwargs
                        ),
                    )
                )

        if used_png:
            fname = fbasename + '.png'
            if org_mode:
                print("figure: {0}".format(fname))
                print("[[file:{0}]]".format(fname))
            if not self.embed:
                if save_show:
                    try:
                        import IPython.display
                        import time
                        #IPython.display.display(IPython.display.Image(filename=fname, embed=False))
                        #html_bit = '<img src="{1}/../{0}?{1}">'.format(fname, int(time.time()))
                        #IPython.display.display(IPython.display.HTML(html_bit))
                        ftype_md = []
                        for fmt, fB in formats.items():
                            if fB.use or fmt == 'png':
                                md = "[{ftype}]({fbasename}.{ftype})".format(
                                    ftype = fmt,
                                    fbasename = fbasename
                                )
                                ftype_md.append(md)
                        markdown_bit = '![{fbasename}]({0}?{1} "{fbasename}")'.format(
                            fname,
                            int(time.time()),
                            fbasename = fbasename,
                        )
                        IPython.display.display(IPython.display.Markdown(markdown_bit + "\n" + ",  ".join(ftype_md)))
                        plt.close(fig)
                    except ImportError:
                        pass
                else:
                    plt.close(fig)
            else:
                if save_show:
                    try:
                        import IPython.display
                        import time
                        IPython.display.display(IPython.display.Image("{0}".format(fname)))
                        plt.close(fig)
                    except ImportError:
                        pass
                else:
                    plt.close(fig)
        fig.set_dpi(mpl.rcParams['figure.dpi'])
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
        size_in       = (None, None),
        size_in_base  = (None, None),
        size_in_dW_dH = (3, 1),
        x_by_col      = False,
        prop_cycle    = color_array,
):
    if isinstance(Nrows, (list, tuple)):
        rownames = Nrows
        Nrows = len(rownames)
    else:
        rownames = None

    width_in, height_in = size_in
    size_in_base_W, size_in_base_H = size_in_base

    if size_in_base_W is None:
        size_in_base_W = mpl.rcParams['figure.figsize'][0]

    if size_in_base_H is None:
        size_in_base_H = mpl.rcParams['figure.figsize'][1]

    if width_in is None:
        width_in = size_in_base_W + Ncols * size_in_dW_dH[0]

    if height_in is None:
        height_in = size_in_base_H + Nrows * size_in_dW_dH[1]

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
            if prop_cycle is not None:
                ax.set_prop_cycle(
                    color = prop_cycle
                )
            #patch_axes(ax)
            ax_list.append(ax)
            ax.grid(b=True)
            ax.grid(b=True, which = 'minor', color = (.9, .9, .9), lw = .5)
            axB.ax_grid_colrow[idx_col].append(ax)
            axB["ax{0}_{1}".format(idx_row, idx_col)] = ax
            axB["ax{0}".format(N)] = ax

            if rownames is not None:
                axB[rownames[N]] = ax

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
