# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import numpy as np
import scipy.optimize
import declarative

from .beam_param import (
    ComplexBeamParam
)

from phasor.utilities.mpl.autoniceplot import (
    #AutoPlotSaver,
    mplfigB,
    #asavefig,
)

from .beam import BeamTargetBase
from . import utils
from . import standard_attrs as attrs

class QFitBeamTarget(BeamTargetBase):
    @declarative.dproperty
    def qfit(self, val):
        return val

    @declarative.dproperty
    def beam_q(self):
        if self.ref_m.val is None:
            q_value = self.qfit.q_fit
        else:
            q_value = self.qfit.q_fit.propagate_distance(self.loc_m.val - self.ref_m.val)
        if self.env_reversed:
            q_value = q_value.reversed()
        return q_value

    _ref_default = ('ref_m', None)
    ref_m = attrs.generate_reference_m()


class QFit(declarative.OverridableObject):
    @declarative.dproperty
    def wavelen_nm(self, val):
        return val

    def as_target(self, **kwargs):
        return QFitBeamTarget(
            qfit = self,
            **kwargs
        )

    m2 = 1.00

    @declarative.mproperty
    def D_um(self, arg):
        arg = np.array(arg)
        return arg

    @declarative.mproperty
    def R_m(self, arg = declarative.NOARG):
        if arg is declarative.NOARG:
            arg = self.D_um * 1e-6 / 2
        else:
            arg = np.array(arg)
        return arg

    @declarative.mproperty
    def Z_in(self, arg):
        arg = np.array(arg)
        return arg

    @declarative.mproperty
    def Z_m(self, arg = declarative.NOARG):
        if arg is declarative.NOARG:
            arg = self.Z_in * .0254
        else:
            arg = np.array(arg)
        return arg

    @declarative.mproperty
    def Z0_ZR_init(self, arg = declarative.NOARG):
        if arg is declarative.NOARG:
            idx_W0 = np.argsort(self.R_m)
            W0 = self.R_m[idx_W0[0]]  * 1

            ZR = np.pi*W0**2/(self.wavelen_nm * 1e-9)
            Z0 = -np.mean(self.Z_m[idx_W0[:4]])
            arg = (Z0, ZR)
        return arg

    def waist_func(self, z, z_0, z_R):
        return (self.m2 * self.wavelen_nm * 1e-9 / (np.pi * z_R) * ((z + z_0)**2 + z_R**2))**.5

    def waist_func_fit(self, z):
        return self.waist_func(z, *self.Z0_ZR_fit)

    no_prefit = False
    @declarative.mproperty
    def Z0_ZR_fit(self):
        idx_W0 = np.argmin(self.R_m)
        init = self.Z0_ZR_init
        #do a prefit to try and find tiny waists using a subset of the data
        if idx_W0 > 1 and idx_W0 < len(self.R_m) - 1 and not self.no_prefit and len(self.R_m) > 3:
            #don't include the point
            if idx_W0 < len(self.R_m) / 2:
                idx_W0 += 1
                #ignore the actual point itself as it may be across a gap
                init, hess = scipy.optimize.curve_fit(
                    self.waist_func,
                    self.Z_m[idx_W0:],
                    self.R_m[idx_W0:],
                    p0 = self.Z0_ZR_init
                )
            else:
                init, hess = scipy.optimize.curve_fit(
                    self.waist_func,
                    self.Z_m[:idx_W0],
                    self.R_m[:idx_W0],
                    p0 = self.Z0_ZR_init
                )
        (z0, zR), hess = scipy.optimize.curve_fit(self.waist_func, self.Z_m, self.R_m, p0 = init)
        return (z0, zR)

    @declarative.mproperty
    def q_fit(self):
        return ComplexBeamParam.from_Z_ZR(
            self.Z0_ZR_fit[0],
            self.Z0_ZR_fit[1],
            wavelen = self.wavelen_nm * 1e-9,
        )

    @declarative.mproperty
    def q_init(self, initval = None):
        if initval is None:
            return ComplexBeamParam.from_Z_ZR(
                self.Z0_ZR_init[0],
                self.Z0_ZR_init[1],
                wavelen = self.wavelen_nm * 1e-9,
            )
        else:
            return initval

    def rep(self, place_in = 0):
        print(self.Z0_ZR_fit)
        try:
            print ("ComplexBeamParam.from_Z_ZR({0}, {1}, wavelen = {2})".format(
                self.Z0_ZR_fit[0] + place_in * .0254,
                self.Z0_ZR_fit[1],
                self.wavelen_nm * 1e-9,
            ))
        except Exception as e:
            print(e)

    def plot(
        self,
        init = False,
    ):
        F = mplfigB()
        diff = max(self.Z_m) - min(self.Z_m)
        Z_pts = np.linspace(min(self.Z_m) - diff/4, max(self.Z_m) + diff/4, 100)

        if int(self.wavelen_nm) == 1064:
            color_pts = 'red'
            color_fit = 'orange'
            color_init = 'purple'
        elif int(self.wavelen_nm) == 532:
            color_pts = 'blue'
            color_fit = 'green'
            color_init = 'purple'
        else:
            color_pts = 'blue'
            color_fit = 'black'
            color_init = 'purple'


        F.ax0.scatter(
            self.Z_in,
            self.D_um,
            color = color_pts,
            label = 'data',
        )

        fit_label = (u"Fit: waist {Zm} = {Zin:.1f}in\nZR={ZR}\nW0={W0}\nD0={D0}".format(
            Zm      = utils.str_m(-self.q_fit.Z, d = 3),
            Zin     = -self.q_fit.Z / .0254,
            ZR      = utils.str_m(self.q_fit.ZR, d = 4),
            W0      = utils.str_m(self.q_fit.W0, d = 4),
            D0      = utils.str_m(2 * self.q_fit.W0, d = 4),
        ))

        F.ax0.plot(
            Z_pts / .0254,
            2 * 1e6 * self.q_fit.propagate_distance(Z_pts).W,
            color = color_fit,
            label = fit_label,
        )
        if init:
            F.ax0.plot(
                Z_pts / .0254,
                2 * 1e6 * self.q_init.propagate_distance(Z_pts).W,
                color = color_init,
                label = 'Initial',
            )
        F.ax0.set_xlabel('Inches from reference')
        F.ax0.set_ylabel('2σ intensity\ndiameter[μm]')
        F.ax0.set_title('Beam Parameter Fit (at {0:.0f}nm)'.format(self.wavelen_nm))
        F.ax0.legend(loc = 'best')
        return F


class BFitPlotter(declarative.OverridableObject):
    sys       = None
    fname     = None
    z         = None
    N_points  = 300
    padding_m = None
    padding_rel = .05

    _overridable_object_save_kwargs = True
    _overridable_object_kwargs = None

    def regenerate(self, **kwargs):
        usekwargs = dict(self._overridable_object_kwargs)
        usekwargs.update(kwargs)
        return self.__class__(
            **usekwargs
        )

    def __call__(self, *args, **kwargs):
        self.plot(*args, **kwargs)

    def plot(
            self,
            fname       = None,
            sys         = None,
            z           = None,
            annotate    = 'full',
            use_in      = True,
            padding_m   = None,
            padding_rel = None,
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
            fB.width.plot(z_unit * z_sub, 2 * 1e3 * qs1.W, label = tname)
            fB.iROC.plot(z_unit * z_sub, qs1.R_inv, label = tname)
            #fB.iROC.plot(z_unit * z_sub, qs1.W * qs1.R_inv, label = tname)
            #fB.iROC.plot(z_unit * z_sub, qs1.divergence_rad/2, label = tname)
            phase = np.unwrap(np.angle(qs1.gouy_phasor))
            zp_idx = np.searchsorted(z_sub, last_zsub)
            if zp_idx >= len(z_sub):
                zp_idx = -1
            phase = phase - phase[zp_idx] + last_phase
            last_phase = phase[-1]
            last_zsub = z_sub[-1]
            fB.Gouy.plot(z_unit * z_sub, 180 / np.pi * phase, label = tname)
        legend = fB.Gouy.legend(
            loc = 'upper left',
            ncol = 2,
            fontsize='medium',
        )
        if legend is not None:
            legend.get_frame().set_alpha(.9)

        fB.iROC.set_ylabel('iROC [1/m]')
        fB.Gouy.set_ylabel("Gouy Phase [deg]")

        fB.ax_bottom.set_xlim(z_unit * min(z), z_unit * max(z))
        fB.ax_tope_2 = fB.ax_top.twiny()
        fB.ax_tope_2.set_xlim(z_unit_top * min(z), z_unit_top * max(z))

        if use_in:
            l = fB.ax_bottom.set_xlabel('Path [in]')
            l2 = fB.ax_tope_2.set_xlabel('Path [m]')
        else:
            l = fB.ax_bottom.set_xlabel('Path [m]')
            l2 = fB.ax_tope_2.set_xlabel('Path [in]')
        l.set_horizontalalignment('right')
        l.set_position((0.9, 0))
        l2.set_horizontalalignment('left')
        l2.set_position((0.1, 0))

        if annotate:
            self.annotate(sys, fB, use_in = use_in, annotate = annotate)
        fB.finalize()
        if fname is not None:
            fB.save(fname)
        return fB

    bbox_args = dict(boxstyle="round", fc="0.8")
    bbox_args = dict()
    arrow_args = dict(
        arrowstyle="->",
        connectionstyle="angle,angleB=90,angleA=180,rad=3",
        linewidth = .5,
    )

    def annotate(self, sys, F, use_in = False, annotate = 'full'):
        all_desc_by_z = []
        if use_in:
            z_unit = 1/.0254
        else:
            z_unit = 1

        for wdesc in sys.waist_descriptions():
            all_desc_by_z.append((
                wdesc.z, None,
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
                    wdesc.z, wdesc.get('width_m', None),
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
            all_desc_by_z.append((
                wdesc.z, wdesc.get('width_m', None),
                wdesc.str,
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
                wdesc.z, wdesc.get('width_m', None),
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
                wdesc.z, -float('inf'),
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
                wdesc.z, wdesc.get('width_m', None),
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

        none_to_zero = lambda v : v if v is not None else 0
        all_desc_by_z.sort(key = lambda v: tuple(none_to_zero(x) for x in v[:2]))

        zs = np.array([tup[0] for tup in all_desc_by_z])
        xlow, xhigh = F.ax_top.get_xlim()
        xmid = (xlow + xhigh)/2
        idx_mid = np.searchsorted(z_unit * zs, xmid)

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
                    xy=(z_unit * z, 1), xycoords=F.ax_top.get_xaxis_transform(),
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
        return

