"""
"""
import declarative
import numpy as np

from OpenLoop.utilities.mpl import (
    generate_stacked_plot_ax,
    #mplfigB,
)

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









