# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import declarative
import collections


def figure_callthrough(data, figure):
    if isinstance(data, collections.Callable):
        return data(figure)
    return data


class MPLSetupAxes(declarative.OverridableObject):
    title      = None
    ylim       = None
    yscale     = None
    ylabel     = None
    xlim       = None
    xscale     = None
    xlabel     = None
    legend     = True
    legend_loc = 'best'
    grid       = True
    aspect     = None

    def finalize(
        self,
        ax,
        title      = None,
        ylim       = None,
        yscale     = None,
        ylabel     = None,
        xlim       = None,
        xscale     = None,
        xlabel     = None,
        legend     = None,
        legend_loc = None,
        grid       = None,
        aspect     = None,
    ):
        title      = declarative.first_non_none(title, self.title)
        if title is not None:
            ax.set_title(title)

        grid      = declarative.first_non_none(grid, self.grid)
        if grid is not None:
            ax.grid(b = grid)

        ylim       = declarative.first_non_none(ylim, self.ylim)
        if ylim is not None:
            ax.set_ylim(ylim)

        yscale     = declarative.first_non_none(yscale, self.yscale)
        if yscale is not None:
            ax.set_yscale(yscale)

        ylabel       = declarative.first_non_none(ylabel, self.ylabel)
        if ylabel is not None:
            ax.set_ylabel(ylabel)

        xlim       = declarative.first_non_none(xlim, self.xlim)
        if xlim is not None:
            ax.set_xlim(xlim)

        xscale     = declarative.first_non_none(xscale, self.xscale)
        if xscale is not None:
            ax.set_xscale(xscale)

        xlabel       = declarative.first_non_none(xlabel, self.xlabel)
        if xlabel is not None:
            ax.set_xlabel(xlabel)

        legend     = declarative.first_non_none(legend, self.legend)
        legend_loc = declarative.first_non_none(legend_loc, self.legend_loc)
        if legend:
            leg_kw = dict(loc = legend_loc)
            if isinstance(legend, dict):
                leg_kw.update(legend)
            ax.legend(**leg_kw)

        aspect      = declarative.first_non_none(aspect, self.aspect)
        if aspect is not None:
            ax.set_aspect(aspect)

        return declarative.Bunch(locals())


class MPLLayoutBase(declarative.OverridableObject):
    facecolor              = (.9, .9, .9)

    @mproperty
    def fig(self, f = declarative.NOARG):
        if f is declarative.NOARG:
            f = plt.figure(facecolor = self.facecolor)
        return f

    grid_vh = (1, 1)
    size_inches_wh_base = (14, 8)
    size_inches_wh_scaling = (4, 3)
    @mproperty
    def size_inches(self, si = declarative.NOARG):
        if si is declarative.NOARG:
            si = (
                self.size_inches_wh_base[0] + self.size_inches_wh_scaling[0] * (self.grid_vh[1]-1),
                self.size_inches_wh_base[1] + self.size_inches_wh_scaling[1] * (self.grid_vh[0]-1)
            )
        return si

    @mproperty
    def gridspec(self):
        return gridspec(self.grid)

    @mproperty
    def ax_list(self):
        """
        Should be overridden if gridspec is to be used
        """
        spl_list = []
        for idx in range(self.grid_vh[0] * self.grid_vh[1]):
            spl_list.append(self.fig.add_subplot(self.grid_vh[0], self.grid_vh[1], idx + 1))
        return spl_list


class MPLAnnotations(declarative.OverridableObject):
    title                  = None

    facecolor              = (.9, .9, .9)
    size_inches            = None
    size_inches_wh_base    = None
    size_inches_wh_scaling = None

    fname                  = None
    fsize_inches           = None
    save_key               = 'save_figures'

    t_layout_suggest       = None
    t_layout               = None
    layout_kw              = dict()

    @mproperty
    def layout(self, l_out = declarative.NOARG):
        if l_out is declarative.NOARG:
            kw = dict(self.layout_kw)
            kw.update(
                facecolor              = self.facecolor,
                size_inches            = self.size_inches,
                size_inches_wh_base    = self.size_inches_wh_base,
                size_inches_wh_scaling = self.size_inches_wh_scaling,
            )
            kw = dict((k, w) for k, w in kw.items() if w is not None)
            t_layout = self.t_layout
            if t_layout is None:
                t_layout = self.t_layout_suggest
            l_out = t_layout(**kw)
        return l_out

    def layout_finalizer(self, fcall):
        self._layout_finalizers.append(fcall)
        return

    @mproperty
    def _layout_finalizers(self):
        return []

    def finalize(self, layout):
        for finalizer in self._layout_finalizers:
            finalizer(layout)

        if self.title is not None:
            layout.fig.suptitle(self.title)

        fig = getattr(layout, 'fig', None)
        if fig is not None:
            if self.fname is not None:
                if self.save_key is not None:
                    can_save = globals().get(self.save_key, False)
                else:
                    can_save = False
                if can_save:
                    if self.fsize_inches is not None:
                        fig.set_size_inches(*self.fsize_inches)
                fig.savefig(self.fname, facecolor = self.facecolor)

            if layout.size_inches is not None:
                fig.set_size_inches(*layout.size_inches)
        return

    @classmethod
    def build(cls, *args, **kwargs):
        self = cls(**kwargs)
        for arg_call in args:
            arg_call(layout = self.layout, annotations = self)
        self.finalize(self.layout)
        return self



global save_figures
save_figures = True



