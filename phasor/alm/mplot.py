# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
#from ..utilities.future_from_2 import str, object, repr_compat
import numpy as np
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

from pprint import pprint
from matplotlib.text import OffsetFrom
import declarative

from .utils import (
    str_m,
)

#from phasor.utilities.mpl.autoniceplot import (
#    AutoPlotSaver,
#    mplfigB,
#    asavefig,
#)

from phasor.utilities.mpl.stacked_plots import (
    generate_stacked_plot_ax,
)


class MPlotter(declarative.OverridableObject):
    sys       = None
    fname     = None
    z         = None
    N_points  = 300
    padding_m = None
    padding_rel = .05

    bbox_args = dict(boxstyle="round", fc="0.8")
    bbox_args = dict()
    arrow_args = dict(
        arrowstyle="->",
        connectionstyle="angle,angleB=90,angleA=180,rad=3",
        linewidth = .5,
    )

    _overridable_object_save_kwargs = True
    _overridable_object_kwargs = None

    def regenerate(self, **kwargs):
        usekwargs = dict(self._overridable_object_kwargs)
        usekwargs.update(kwargs)
        return self.__class__(
            **usekwargs
        )

    def __call__(self, *args, **kwargs):
        return self.plot(*args, **kwargs)

    def plot(
            self,
            fname       = None,
            sys         = None,
            z           = None,
            annotate    = 'full',
            use_in      = True,
            padding_m   = None,
            padding_rel = None,
            object_0    = None,
            **kwargs
    ):
        fname = declarative.first_non_none(fname, self.fname)
        if fname is None:
            raise RuntimeError("Must specify fname")

        if use_in:
            z_unit = 1/.0254
            z_unit_top = 1
        else:
            z_unit = 1
            z_unit_top = 1/.0254

        sys         = declarative.first_non_none(sys, self.sys)
        z           = declarative.first_non_none(z, self.z)
        padding_m   = declarative.first_non_none(padding_m, self.padding_m)
        padding_rel = declarative.first_non_none(padding_rel, self.padding_rel)

        if object_0 is not None:
            z0 = sys.object_z(object_0)
        else:
            z0 = 0

        if sys is None:
            raise RuntimeError("Must Provide a system to plot")

        if z is None:
            if padding_m is None:
                padding_m = sys.layout.width_m * padding_rel
            z = np.linspace(-padding_m, float(sys.layout.width_m) + padding_m, self.N_points)

        #fB = mplfigB(Nrows = 3)
        fB = generate_stacked_plot_ax(
            name_use_list = [
                ('width', True),
                ('iROC', True),
                ('Gouy', True),
            ],
            width_phys_in = 10,
            heights_phys_in_default = 1.5,
            hspace = .08,
        )
        fB.width.set_ylabel(u'2σ intensity\ndiameter[mm]')

        beam_zs = [sys.target_z(t) for t in sys.beam_targets.tname]
        last_phase = 0
        last_zsub = 0
        for idx, tname in enumerate(sys.beam_targets.tname):
            z_sub = z
            if idx > 0:
                z_from = beam_zs[idx - 1]
                z_sub = z_sub[z_sub > z_from]
            if idx < len(beam_zs) - 1:
                z_to = beam_zs[idx + 1]
                z_sub = z_sub[z_sub < z_to]
            qs1 = sys.q_target_z(z_sub, tname)
            fB.width.plot(z_unit * (z_sub - z0), 2 * 1e3 * qs1.W, label = tname)
            fB.iROC.plot(z_unit * (z_sub - z0), qs1.R_inv, label = tname)
            #fB.iROC.plot(z_unit * z_sub, qs1.W * qs1.R_inv, label = tname)
            #fB.iROC.plot(z_unit * z_sub, qs1.divergence_rad/2, label = tname)
            #phase = np.unwrap(np.angle(qs1.gouy_phasor))
            phase = np.unwrap(np.angle(qs1.gouy_phasor))
            zp_idx = np.searchsorted(z_sub, last_zsub)
            if zp_idx >= len(z_sub):
                zp_idx = -1
            phase = phase - phase[zp_idx] + last_phase
            last_phase = phase[-1]
            last_zsub = z_sub[-1]
            fB.Gouy.plot(z_unit * (z_sub - z0), 180 / np.pi * phase, label = tname)
        legend = fB.Gouy.legend(
            loc = 'upper left',
            ncol = 2,
            fontsize='medium',
        )
        if legend is not None:
            legend.get_frame().set_alpha(.9)

        fB.iROC.set_ylabel('iROC [1/m]')
        fB.Gouy.set_ylabel("Gouy Phase [deg]")

        fB.ax_bottom.set_xlim(z_unit * min(z - z0), z_unit * max(z - z0))
        fB.ax_top_2 = fB.ax_top.twiny()
        fB.ax_top_2.set_xlim(z_unit_top * min(z - z0), z_unit_top * max(z - z0))

        if use_in:
            l = fB.ax_bottom.set_xlabel('Path [in]')
            l2 = fB.ax_top_2.set_xlabel('Path [m]')
        else:
            l = fB.ax_bottom.set_xlabel('Path [m]')
            l2 = fB.ax_top_2.set_xlabel('Path [in]')
        l.set_horizontalalignment('right')
        l.set_position((0.9, 0))
        l2.set_horizontalalignment('left')
        l2.set_position((0.1, 0))

        if annotate:
            self.annotate(
                sys,
                fB,
                use_in = use_in,
                annotate = annotate,
                z0 = z0,
                **kwargs
            )
        fB.finalize()
        fB.ax_bottom.minorticks_on()
        fB.ax_top_2.minorticks_on()
        fB.width.minorticks_on()
        fB.iROC.minorticks_on()
        fB.Gouy.minorticks_on()

        fB.width.grid(which='minor', linewidth = 0.5, ls = ':')
        fB.iROC.grid(which='minor', linewidth = 0.5, ls = ':')
        fB.Gouy.grid(which='minor', linewidth = 0.5, ls = ':')

        fB.width.grid(which = 'major', linewidth = 1)
        fB.iROC.grid(which = 'major', linewidth = 1)
        fB.Gouy.grid(which = 'major', linewidth = 1)

        if fname is not None:
            fB.save(fname)
        return declarative.Bunch(locals())

    def annotate(
            self,
            sys,
            F,
            use_in = False,
            annotate = 'full',
            z0 = 0,
            include_detuning = False,
    ):
        all_desc_by_z = []
        if use_in:
            z_unit = 1/.0254
        else:
            z_unit = 1

        for wdesc in sys.waist_descriptions():
            all_desc_by_z.append((
                wdesc.z - z0,
                None,
                wdesc.str,
                dict(
                    color = 'green',
                    ls = '--',
                    lw = .5,
                ),
                dict(
                    color = 'green',
                    lw = .5,
                ),
            ))

        for wdesc in sys.mount_descriptions():
            if wdesc.type == 'mirror_mount':
                all_desc_by_z.append((
                    wdesc.z - z0,
                    wdesc.get('width_m', None),
                    wdesc.str,
                    dict(
                        color = 'red',
                        ls = '--',
                        lw = .5,
                    ),
                    dict(
                        color = 'red',
                        lw = .5,
                    ),
                ))

        for wdesc in sys.lens_descriptions():
            str_tag = ''
            obj = wdesc.get('obj', None)
            if obj is not None and hasattr(obj, 'DCC'):
                str_tag = '[{}] '.format(obj.DCC)
            all_desc_by_z.append((
                wdesc.z - z0,
                wdesc.get('width_m', None),
                str_tag + wdesc.str,
                dict(
                    color = 'blue',
                    ls = '--',
                    lw = .5,
                ),
                dict(
                    color = 'blue',
                    lw = .5,
                ),
            ))

        for wdesc in sys.mirror_descriptions():
            all_desc_by_z.append((
                wdesc.z - z0,
                wdesc.get('width_m', None),
                wdesc.str,
                dict(
                    color = 'red',
                    ls = '--',
                    lw = .5,
                ),
                dict(
                    color = 'red',
                    lw = .5,
                ),
            ))

        for wdesc in sys.target_descriptions():
            all_desc_by_z.append((
                wdesc.z - z0,
                -float('inf'),
                wdesc.str,
                dict(
                    color = 'orange',
                    #ls = '--',
                    lw = .5,
                ),
                dict(
                    color = 'orange',
                    lw = .5,
                ),
            ))
        for wdesc in sys.extra_descriptions():
            all_desc_by_z.append((
                wdesc.z - z0,
                wdesc.get('width_m', None),
                wdesc.str,
                dict(
                    color = wdesc.get('color', ),
                    #ls = '--',
                    lw = .5,
                ),
                dict(
                    color = wdesc.get('color', 'brown'),
                    lw = .5,
                ),
            ))

        if include_detuning:
            for wdesc in sys.detune_descriptions():
                all_desc_by_z.append((
                    wdesc.z - z0,
                    wdesc.get('width_m', None),
                    "02 detuning: {0:.1f}/m , {1:.1f}deg".format(wdesc.mag, wdesc.deg),
                    dict(
                        color = wdesc.get('color', 'cyan'),
                        ls = '--',
                        lw = .5,
                    ),
                    dict(
                        color = wdesc.get('color', 'cyan'),
                        lw = .5,
                    ),
                ))

        none_to_zero = lambda v : v if v is not None else 0
        all_desc_by_z.sort(key = lambda v: tuple(none_to_zero(x) for x in v[:2]))

        zs = np.array([tup[0] for tup in all_desc_by_z])
        xlow, xhigh = F.ax_top.get_xlim()
        xmid = (xlow + xhigh)/2
        idx_mid = np.searchsorted(z_unit * (zs), xmid)

        left_list = all_desc_by_z[:idx_mid]
        right_list = all_desc_by_z[idx_mid:]
        fsize_sep = 15

        if use_in:
            def desc_format(z, desc):
                desc = u"{0:.2f}in: {desc}".format(z * 100 / 2.54, desc = desc)
                return desc
        else:
            def desc_format(z, desc):
                desc = u"{0}: {desc}".format(str_m(z, 3), desc = desc)
                return desc
        for idx, (z, width, desc, lkw, akw) in enumerate(reversed(left_list)):
            desc = desc_format(z, desc)
            #top elements
            arrowkw = dict(self.arrow_args)
            arrowkw.update(akw)
            if annotate == 'full':
                an = F.ax_top.annotate(
                    desc, #'',
                    xy=(z_unit * (z), 1), xycoords=F.ax_top.get_xaxis_transform(),
                    xytext=(0, 15 + fsize_sep*idx), textcoords=OffsetFrom(F.ax_top.bbox, (1, 1), "points"),
                    ha = "right", va = "bottom",
                    bbox = self.bbox_args,
                    arrowprops = arrowkw,
                )
            #F.ax_top.annotate(
            #    desc,
            #    #'',
            #    xy=(0.0, 2), xytext=(0.0, 2),
            #    textcoords=OffsetFrom(an, (1, 1), "points"),
            #    ha="right", va="bottom",
            #    bbox=self.bbox_args,
            #)
            if width is not None and abs(width) > .001:
                an = F.ax_top.annotate(
                    desc,
                    xy=(z_unit * (z + width), 1), xycoords=F.ax_top.get_xaxis_transform(),
                    xytext=(0, 15 + fsize_sep*idx), textcoords=OffsetFrom(F.ax_top.bbox, (1, 1), "points"),
                    ha = "right", va = "bottom",
                    bbox = self.bbox_args,
                    arrowprops = arrowkw,
                    alpha = 0,
                )
                F.width.axvline(z_unit * float(z), **lkw)
                F.width.axvline(z_unit * float(z + width), **lkw)
                F.iROC.axvline(z_unit * float(z), **lkw)
                F.iROC.axvline(z_unit * float(z + width), **lkw)
                F.Gouy.axvline(z_unit * float(z), **lkw)
                F.Gouy.axvline(z_unit * float(z + width), **lkw)
            else:
                F.width.axvline(z_unit * float(z), **lkw)
                F.iROC.axvline(z_unit * float(z), **lkw)
                F.Gouy.axvline(z_unit * float(z), **lkw)

        for idx, (z, width, desc, lkw, akw) in enumerate(right_list):
            desc = desc_format(z, desc)
            #bottom elements
            arrowkw = dict(self.arrow_args)
            arrowkw.update(akw)
            if annotate == 'full':
                an = F.ax_top.annotate(
                    desc, #'',
                    xy=(z_unit * z, -.12), xycoords=F.ax_bottom.get_xaxis_transform(),
                    xytext=(0, -34 - fsize_sep*idx), textcoords=OffsetFrom(F.ax_bottom.bbox, (0, 0), "points"),
                    ha="left", va="bottom",
                    bbox=self.bbox_args,
                    arrowprops = arrowkw,
                )
            #F.ax_top.annotate(
            #    '',#desc,
            #    xy=(0.0, 2),
            #    xytext=(0.0, 2),
            #    textcoords=OffsetFrom(an, (0, 0), "points"),
            #    ha="left", va="bottom",
            #    bbox=self.bbox_args,
            #)
            if width is not None and abs(width) > .001:
                F.width.axvline(z_unit * float(z), **lkw)
                F.width.axvline(z_unit * float(z + width), **lkw)
                F.iROC.axvline(z_unit * float(z), **lkw)
                F.iROC.axvline(z_unit * float(z + width), **lkw)
                F.Gouy.axvline(z_unit * float(z), **lkw)
                F.Gouy.axvline(z_unit * float(z + width), **lkw)
                an = F.ax_top.annotate(
                    desc,
                    xy=(z_unit * (z + width), -.12), xycoords=F.ax_bottom.get_xaxis_transform(),
                    xytext=(0, -34 - fsize_sep*idx), textcoords=OffsetFrom(F.ax_bottom.bbox, (0, 0), "points"),
                    ha="left", va="bottom",
                    bbox=self.bbox_args,
                    arrowprops = arrowkw,
                    alpha = 0,
                )
            else:
                F.width.axvline(z_unit * float(z), **lkw)
                F.iROC.axvline(z_unit * float(z), **lkw)
                F.Gouy.axvline(z_unit * float(z), **lkw)
        F.width.set_ylim(0, None)
        return


