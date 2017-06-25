"""
"""
import declarative
import numpy as np

from phasor.utilities.mpl import (
    generate_stacked_plot_ax,
    mplfigB,
)


def angle(
        Y,
        center_idx = None,
        unwrap = True,
        deg = True
):
    if not np.asarray(Y).shape:
        return np.angle(Y, deg = deg)
    if unwrap:
        uw = np.unwrap(np.angle(Y))
        if center_idx is None:
            if np.max(uw) > np.pi and np.min(uw) > 0:
                uw = uw - 2*np.pi
            if np.min(uw) > .95 * np.pi:
                uw = uw - 2*np.pi
            if np.min(uw) < 2*np.pi:
                uw = uw + 2*np.pi
            if np.max(uw) > 2*np.pi:
                uw = uw - 2*np.pi
        else:
            uw -= (2 * np.pi) * (uw[center_idx] // (2 * np.pi))
    else:
        uw = np.angle(Y)
    if deg:
        return 180 / np.pi * uw
    else:
        return uw


class ACReadoutPlots(declarative.OverridableObject):
    sys = None
    deg = True

    @declarative.mproperty
    def X(self, val = None):
        if val is None or val == 'FHz':
            val = declarative.Bunch(
                val = self.X_FHz,
                label = 'Frequency [Hz]'
            )
        return val

    @declarative.mproperty
    def X_FHz(self):
        return self.sys.environment.F_AC.F_Hz.val

    def readout_loop_xfer(
            self,
            readout,
            ax_mag        = None,
            ax_phase      = None,
            color_OLG     = 'orange',
            color_CLG     = 'red',
            color_plant   = 'blue',
            label_plant   = 'Plant',
            unwrap        = False,
            ugf_line      = True,
            preferred_UGF = None,
    ):
        if ugf_line and np.asarray(readout.OLG).shape:
            abs_OLG = abs(readout.OLG)
            OLG_sides = (abs_OLG > 1)
            OLG_crossings = (OLG_sides[1:] ^ OLG_sides[:-1])
            ugf_idx = None
            for idx in np.argwhere(OLG_crossings):
                if ax_mag:
                    ax_mag.axvline(
                        self.X.val[idx + 1],
                        color = color_OLG,
                        ls = '--'
                    )
                if ax_phase:
                    ax_phase.axvline(
                        self.X.val[idx + 1],
                        color = color_OLG,
                        ls = '--'
                    )
                ugf_idx = idx

        ax_mag.set_ylabel("Gain")
        ax_mag.loglog(
            self.X.val,
            abs(readout.GPlant),
            color = color_plant,
        )
        ax_phase.semilogx(
            self.X.val,
            angle(
                readout.GPlant,
                center_idx = ugf_idx,
                unwrap = unwrap,
                deg = self.deg
            ),
            color = color_plant,
            label = label_plant,
        )
        ax_mag.loglog(
            self.X.val,
            abs(readout.CLG),
            color = color_CLG,
        )
        ax_phase.semilogx(
            self.X.val,
            angle(
                readout.CLG,
                center_idx = ugf_idx,
                unwrap = unwrap,
                deg = self.deg
            ),
            color = color_CLG,
            label = 'CLG'
        )
        ax_mag.loglog(
            self.X.val,
            abs(readout.OLG),
            color = color_OLG,
        )
        ax_phase.semilogx(
            self.X.val,
            angle(
                readout.OLG,
                center_idx = ugf_idx,
                unwrap = unwrap,
                deg = self.deg
            ),
            color = color_OLG,
            label = 'OLG'
        )

        ax_phase.legend(loc = 'upper right', fontsize = 6)
        if preferred_UGF is not None and np.asarray(readout.OLG).shape:
            print(
                "UGF at {0}Hz needs {1} more gain".format(
                    preferred_UGF,
                    1/abs(readout.OLG)[np.searchsorted(self.X.val, preferred_UGF)]
                )
            )
        return

    def readout_AC(
            self,
            readout,
            ax_mag        = None,
            ax_phase      = None,
            **kwargs
    ):

        ax_mag.loglog(
            self.X.val,
            abs(readout.AC_sensitivity),
            **kwargs
        )
        ax_phase.semilogx(
            self.X.val,
            angle(readout.AC_sensitivity, deg = self.deg),
            **kwargs
        )
        return

    def readout_budget(
        self,
        readout,
        ax,
        limit = 2e-8,
    ):
        ax.loglog(
            self.X.val,
            abs(readout.AC_ASD),
            color = 'black',
            label = 'total'
        )

        sgroups = []
        for source, psd in readout.AC_PSD_by_source.items():
            ratio = psd / readout.AC_PSD
            mratio = np.max(ratio)
            mpsd = np.max(psd)
            #print(source.name_noise, mratio, mpsd)
            if mratio > limit:
                sgroups.append((mpsd, str(source), source, psd))
        sgroups.sort()

        prev_mpsd = 0
        prev_psd = 0
        for mpsd, sname, source, psd in reversed(sgroups):
            kw = dict()
            r_psd = prev_psd / psd
            N_nearby = np.count_nonzero((r_psd < 1.2) & (r_psd > .8))
            if N_nearby / len(psd) > .3:
                kw['ls'] = (0, (2, 1))
            ax.loglog(
                self.X.val,
                abs(psd)**.5,
                label = (source.name_noise),
                **kw,
            )
            prev_mpsd = mpsd
            prev_psd  = psd

        ax.set_ylim(np.min(readout.AC_ASD) * 1e-3, np.max(readout.AC_ASD) * 3)
        ax.legend(fontsize = 6)
        return
