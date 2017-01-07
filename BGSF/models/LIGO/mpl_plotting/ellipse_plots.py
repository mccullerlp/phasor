# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import print_function

import numpy as np

import matplotlib.patches as mplpatch
import matplotlib.transforms as mpltrans
import matplotlib.collections as mplcollect

from declarative.bunch import (
    Bunch,
)
from declarative import (
    OverridableObject,
    mproperty,
)

from YALL.utilities.np import logspaced

def first_non_none(*args):
    for arg in args:
        if arg is not None:
            return arg
    return None

def plot_ellipses(
    readout,
    ellipse_bunch,
    scale         = .1,
    use_logellipt = False,
    vfrac         = .85,
    ax            = None,
    **kwargs
):
    ellipse_freqs = logspaced(ax.get_xlim()[0], ax.get_xlim()[1], 12)[1:-1]

    idx = np.searchsorted(readout.F_Hz, ellipse_freqs)
    ellipse_Hz = readout.F_Hz

    #ax.set_xscale('log')
    trans = mpltrans.composite_transform_factory(
        ax.transData,
        ax.transAxes.inverted(),
    )

    inslocs = np.vstack([
        np.array(ellipse_Hz[idx]),
        np.ones(idx.shape),
    ])
    xlocs = trans.transform(inslocs.T.flatten()).reshape(-1, 2)[:, 0]

    if not use_logellipt:
        heights = scale * ellipse_bunch.min[idx],
        widths = scale * ellipse_bunch.max[idx],
    else:
        ellipt = (ellipse_bunch.max[idx] / ellipse_bunch.min[idx])**.5
        logellipt = 1 + np.log(ellipt)
        heights = scale / logellipt
        widths = scale * logellipt
    col = mplcollect.EllipseCollection(
        widths = heights,
        heights = widths,
        angles = ellipse_bunch.deg[idx],
        units = 'y',
        offsets = np.vstack([xlocs, vfrac * np.ones_like(xlocs)]).T,
        transOffset = ax.transAxes,
        **kwargs
    )
    ax.add_collection(col)


class EllipsePlotter(OverridableObject):
    use_logellipt = False
    color_signal  = 'black'
    color_noise   = 'blue'
    vfrac         = .85
    scale         = .1
    sig_relscale  = 1.5
    use_baseline  = True

    def plot_readout_ellipse(
        self,
        readout,
        ax            = None,
        ax_direct     = False,
        use_logellipt = None,
        color_noise   = None,
        color_signal  = None,
        vfrac         = None,
    ):
        if not ax_direct:
            ax = ax.twinx()
            ax.get_yaxis().set_visible(False)

        if self.use_baseline:
            #TODO
            ebunch = Bunch(
                max = np.ones_like(readout.AC_CSD_ellipse_norm.max),
                min = np.ones_like(readout.AC_CSD_ellipse_norm.min),
                deg = readout.AC_CSD_ellipse_norm.deg,
                rad = readout.AC_CSD_ellipse_norm.rad,
            )
            plot_ellipses(
                readout       = readout,
                ellipse_bunch = ebunch,
                use_logellipt = first_non_none(use_logellipt, self.use_logellipt, False),
                linewidths    = .5,
                alpha         = 1,
                vfrac         = first_non_none(vfrac, self.vfrac, .45),
                edgecolors    = 'gray',
                linestyle     = ':',
                facecolors    = 'none',
                scale         = self.scale,
                ax            = ax,
            )

        plot_ellipses(
            readout       = readout,
            ellipse_bunch = readout.AC_CSD_ellipse_norm,
            use_logellipt = first_non_none(use_logellipt, self.use_logellipt, False),
            color         = first_non_none(color_noise, self.color_noise, 'blue'),
            linewidths    = .5,
            alpha         = .3,
            vfrac         = first_non_none(vfrac, self.vfrac, .45),
            scale         = self.scale,
            ax            = ax,
        )

        plot_ellipses(
            readout       = readout,
            ellipse_bunch = readout.AC_signal_ellipse_norm,
            color         = first_non_none(color_signal, self.color_signal, 'black'),
            scale         = self.sig_relscale * self.scale,
            vfrac         = first_non_none(vfrac, self.vfrac, .45),
            ax            = ax,
        )


