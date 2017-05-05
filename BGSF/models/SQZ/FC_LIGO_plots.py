"""
"""
import declarative
import numpy as np

from BGSF.utilities.mpl import (
    generate_stacked_plot_ax,
    #mplfigB,
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


class OPOPlotGroup(declarative.OverridableObject):
    sys = None
    sys_bigclf = None

    @declarative.mproperty
    def X(self, val = None):
        if val is None or val == 'GPWR':
            val = declarative.Bunch(
                val = self.X_GPWR * 1e3,
                label = 'Green Power on M1 [mW]'
            )
        elif val == 'SQZDB':
            val = declarative.Bunch(
                val = self.X_SQZSB,
                label = 'Raw Squeezing Level [db]'
            )
        elif val == 'RPHASE':
            val = declarative.Bunch(
                val = self.X_RPHASE,
                label = 'Red phase detuning [deg]'
            )
        return val

    @declarative.mproperty
    def X_GPWR(self):
        return self.sys.test.PSLG.power_W.val

    @declarative.mproperty
    def X_RPHASE(self):
        return self.sys.test.opo.M1.mirror_H1.phase_deg.val

    @declarative.mproperty
    def X_SQZSB(self):
        return -10*np.log10(self.sys.test.AC_R.AC_CSD_ellipse.min)

    def SQZ(
        self,
        ax,
        color_sqz = 'blue',
        color_asqz = 'red',
        **kw
    ):
        if not ax: return
        ax.plot(
            self.X.val,
            10*np.log10(self.sys.test.AC_R.AC_CSD_ellipse.min),
            color = color_sqz,
            label = 'Squeezing [db]',
            **kw
        )
        ax.plot(
            self.X.val,
            10*np.log10(self.sys.test.AC_R.AC_CSD_ellipse.max),
            color = color_asqz,
            label = 'AntiSqueezing [db]',
            **kw
        )
        ax.set_title(
            'Squeezing Level',
        )
        ax.legend(
            fontsize = 8,
            loc = 'best',
        )
        ax.set_ylabel('shotnoise relative\npower spectrum [db]')
        return ax

    def CLF_hdyne_PWR(
        self,
        ax,
        color = 'red',
        **kw
    ):
        if not ax: return
        ax.semilogy(
            self.X.val,
            self.sys.test.DC_R.DC_readout,
            color = color,
            label = '({0:.2f}mW at M2)'.format(self.sys.test.PSLR_clf.power_mW.val),
            **kw
        )
        ax.set_title(
            'CLF Power at homodyne',
        )
        ax.legend(
            fontsize = 8,
            loc = 'best',
        )
        ax.set_ylabel('CLF Power\n[W]')
        return ax

    def GREFL_PWR(
        self,
        ax,
        color = (.5, .8, 0),
        **kw
    ):
        if not ax: return
        ax.plot(
            self.X.val,
            self.sys.test.DC_G.DC_readout,
            color = color,
            **kw
        )
        ax.set_title('Green REFL Power')
        ax.set_ylabel('Green REFL\nPower [W]')
        return

    def GCAV_PWR(
        self,
        ax,
        color = (.5, .8, 0),
        **kw
    ):
        if not ax: return
        ax.plot(
            self.X.val,
            self.sys.test.opo.DC.DC_readout,
            color = color,
            **kw
        )
        ax.set_title('Green Cavity Power')
        ax.set_ylabel('Green Cavity\nPower [W]')

    def initial_CLF_perf(self):
        axB = generate_stacked_plot_ax(
            name_use_list = (
                (self.CLF_hdyne_PWR, dict()),
                (self.GREFL_PWR, dict()),
                (self.GCAV_PWR, dict()),
                (self.SQZ, dict()),
            ),
            Nrows=2
        )
        axB.ax_bottom.set_xlabel(self.X.label)
        axB.finalize()
        return axB

    def CLF_DC(self, ax, color = 'red', **kw):
        if not ax: return
        ax.plot(
            self.X.val,
            self.sys.test.DC_CLF.DC_readout,
            label = '({0:.2f}mW at M2)'.format(self.sys.test.PSLR_clf.power_mW.val),
            color = color,
            **kw
        )
        ax.legend(
            fontsize = 8,
            loc = 'best',
        )
        ax.set_title('CLF PD Power')
        ax.set_ylabel('CLF PD Power')
        return

    @declarative.mproperty
    def CLF_2x_phasor(self):
        return self.sys.test.DCI_CLF.DC_readout + self.sys.test.DCQ_CLF.DC_readout*1j

    def CLF_2x_IQ_mag(
            self,
            ax,
            color_re = 'red',
            color_im = 'blue',
            color_mag = 'purple',
            **kw
    ):
        if color_re:
            ax.plot(
                self.X.val,
                1e6 * self.CLF_2x_phasor.real,
                color = color_re,
                label = 'CLF I',
                **kw
            )
        if color_im:
            ax.plot(
                self.X.val,
                1e6 * self.CLF_2x_phasor.imag,
                color = color_im,
                label = 'CLF Q',
                **kw
            )
        if color_mag:
            ax.plot(
                self.X.val,
                1e6 * abs(self.CLF_2x_phasor),
                color = color_mag,
                label = 'CLF MAG',
                **kw
            )
        ax.legend(
            fontsize = 8,
            loc = 'best',
        )
        ax.set_title('CLF PD 2x demod')
        ax.set_ylabel('Demod Power [uW]')

    def CLF_2x_IQ_phase(
            self,
            ax,
            color = 'purple',
            deg = True,
            **kw
    ):
        angles_clf = np.angle(self.CLF_2x_phasor, deg = deg)
        ax.plot(
            self.X.val,
            angles_clf,
            color = color,
            **kw
        )
        ax.set_title('CLF PD 2x demod phase')
        if deg:
            ax.set_ylabel('angle [deg]')
        else:
            ax.set_ylabel('angle [rad]')

    def CLF_PD_demod(self):
        axB = generate_stacked_plot_ax(
            name_use_list = (
                (self.CLF_2x_IQ_mag, dict()),
                (self.CLF_2x_IQ_phase, dict()),
            ),
            Nrows=2
        )
        axB.ax_bottom.set_xlabel(self.X.label)
        axB.finalize()
        return axB

    def CLF_2x_IQ_mag_div(
            self,
            ax,
            color = 'red',
            **kw
    ):
        div_sig = abs(self.CLF_2x_phasor) / self.sys.test.DC_CLF.DC_readout
        ax.plot(
            self.X.val,
            div_sig,
            color = color,
            label = 'CLF demod / div',
            **kw
        )
        #ax.legend(
        #    fontsize = 8,
        #    loc = 'best',
        #)
        ax.set_ylim(0, max(div_sig))
        ax.set_xlim(0, max(self.X.val))
        ax.set_title('CLF PD 2x demod / DC')
        ax.set_ylabel('Demod/DC\n[W/W]')

    def CLF_PD_demod_div(self):
        axB = generate_stacked_plot_ax(
            name_use_list = (
                (self.CLF_2x_IQ_mag_div, dict()),
            ),
            Nrows=2
        )
        axB.ax_bottom.set_xlabel(self.X.label)
        axB.finalize()
        return axB

    @declarative.mproperty
    def CLF_hdyne_phasor_Amp(self):
        return self.sys.test.hDCAmpI_CLF.DC_readout + self.sys.test.hDCAmpQ_CLF.DC_readout*1j

    @declarative.mproperty
    def CLF_hdyne_phasor_Phase(self):
        return self.sys.test.hDCPhaseI_CLF.DC_readout + self.sys.test.hDCPhaseQ_CLF.DC_readout*1j

    def CLF_hdyne_Amp(
            self,
            ax,
            **kw
    ):
        ax.plot(
            self.X,
            self.sys.test.CLF_hdyne_phasor_Amp.real,
            color = 'purple'
        )
        ax.plot(
            self.X,
            self.sys.test.CLF_hdyne_phasor_Amp.imag,
            color = 'orange'
        )
        ax.plot(
            self.X,
            abs(self.sys.test.CLF_hdyne_phasor_Amp),
            color = 'red'
        )
    def CLF_hdyne_Phase(
            self,
            ax,
            **kw
    ):
        ax.plot(
            self.X,
            self.sys.test.CLF_hdyne_phasor_Phase.real,
            color = 'blue'
        )
        ax.plot(
            self.X,
            self.sys.test.CLF_hdyne_phasor_Phase.imag,
            color = 'cyan'
        )
        ax.plot(
            self.X,
            abs(self.sys.test.CLF_hdyne_phasor_Phase.imag),
            color = 'green'
        )

    def CLF_hdyne_Angles(
            self,
            ax,
            deg = True,
            **kw
    ):
        angleAmp = np.angle(
            self.CLF_hdyne_phasor_Amp,
            deg = deg,
        )
        ax.plot(
            self.X,
            angleAmp,
            color = 'red'
        )
        anglePhase = np.angle(
            self.CLF_hdyne_phasor_Phase,
            deg = deg,
        )
        ax.plot(
            self.X,
            anglePhase,
            color = 'green'
        )
        return



class ACReadoutPlots(declarative.OverridableObject):
    sys = None
    deg = True

    @declarative.mproperty
    def X(self, val = None):
        if val is None or val == 'FHz':
            val = declarative.Bunch(
                val = self.X_FHz,
                label = 'Frequency [Hz]',
                xscale = 'log_zoom',
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
            unwrap        = True,
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
            if mratio > 2e-8 and mpsd > 1e-2:
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

    def SQZ(
        self,
        ax,
        readout,
        color_in_quad = 'green',
        color_sqz     = 'blue',
        color_asqz    = 'red',
        **kw
    ):
        if not ax: return
        ax.plot(
            self.X.val,
            10*np.log10(readout.AC_PSD),
            color = color_in_quad,
            label = 'Readout Quadrature',
            **kw
        )
        ax.plot(
            self.X.val,
            10*np.log10(readout.AC_CSD_ellipse.min),
            color = color_sqz,
            label = 'Squeezing [db]',
            ls = '--',
            **kw
        )
        ax.plot(
            self.X.val,
            10*np.log10(readout.AC_CSD_ellipse.max),
            color = color_asqz,
            label = 'AntiSqueezing [db]',
            ls = '--',
            **kw
        )
        ax.set_title(
            'Squeezing Level',
        )
        ax.set_xscale
        ax.legend(
            fontsize = 8,
            loc = 'best',
        )
        ax.set_ylabel('SN rel.\nPSD [db]')
        return ax

    def SQZ_angle(
        self,
        ax,
        readout,
        color = 'black',
        **kw
    ):
        if not ax: return
        ax.plot(
            self.X.val,
            readout.AC_CSD_ellipse.deg % 180,
            color = color,
            label = 'Squeeze angle [deg]',
            **kw
        )
        ax.set_title(
            'Squeezing Angle',
        )
        #ax.set_xscale
        ax.legend(
            fontsize = 8,
            loc = 'best',
        )
        ax.set_ylabel('Angle [deg]')
        return ax

    def readout_angle(
        self,
        ax,
        readout,
        color = 'black',
        **kw
    ):
        if not ax: return
        ax.plot(
            self.X.val,
            readout.AC_optimal_readout_deg % 180,
            color = color,
            label = 'Readout angle [deg]',
            **kw
        )
        ax.set_title(
            'Readout Angle',
        )
        #ax.set_xscale
        ax.legend(
            fontsize = 8,
            loc = 'best',
        )
        ax.set_ylabel('Angle [deg]')
        return ax
