# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from matplotlib import pyplot
from matplotlib import gridspec
import numpy as np

from phasor.utilities.mpl import (
    generate_stacked_plot_ax,
    #mplfigB,
)


def plot_loop(F, h, inv = True, full = True):
    if inv:
        h = -h
    fig = pyplot.figure()
    fig.set_size_inches(10, 4)
    gs = gridspec.GridSpec(
        1, 2,
        wspace = .2
    )
    axF = generate_stacked_plot_ax(
        fig = fig,
        gs_base = gs[0],
        name_use_list = [
            ('OLG', True),
            ('OLG_zoom', True),
            ('OLG_phase', True),
        ],
        height_ratios = {
            'OLG': 1,
            'OLG_zoom': .5,
            'OLG_phase': 1,
            'CLG': 1,
            'CLG_zoom': .8,
            'CLG_phase': .5,
        },
        xscales = 'log_zoom',
        hspace = .4
    )
    if full:
        axF2 = generate_stacked_plot_ax(
            fig = fig,
            gs_base = gs[1],
            name_use_list = [
                ('CLG', full),
                ('CLG_zoom', full),
                #('CLG_phase', full),
            ],
            height_ratios = {
                'CLG': 1,
                'CLG_zoom': .8,
                #'CLG_phase': .5,
            },
            xscales = 'log_zoom',
            hspace = .4
        )

    UGFs = []
    abs_OLG = abs(h)
    OLG_sides = (abs_OLG > 1)
    OLG_crossings = (OLG_sides[1:] ^ OLG_sides[:-1])
    ugf_idx = None

    for idx in np.argwhere(OLG_crossings):
        ugf_idx = idx
        F_ugf = F[ugf_idx]
        UGFs.append(F_ugf)


    OLG_color = 'blue'
    CLG_color = 'red'
    SNIG_color = 'purple'

    axF.OLG.plot(F, abs(h), color = OLG_color)
    axF.OLG.set_yscale('log_zoom')
    axF.OLG_zoom.plot(F, abs(h), color = OLG_color)
    axF.OLG_zoom.set_yscale('log_zoom')
    axF.OLG_zoom.set_ylim(.5, 2)
    axF.OLG_phase.plot(F, np.angle(-h, deg = True), color = OLG_color)

    if full:
        clg = 1/(1 + h)
        clg_up = 1/(1 + 1.1 * h)
        clg_dn = 1/(1 + .9 * h)

        snig = h/(1 + h)
        snig_up = 1.1 * h/(1 + 1.1 * h)
        snig_dn = 0.9 * h/(1 + .9 * h)

        CLG_ud_ls = (0, (2, 2))


        axF2.CLG.plot(F, abs(clg), color = CLG_color)
        axF2.CLG_zoom.plot(F, abs(clg), color = CLG_color)
        #axF2.CLG_phase.plot(F, np.angle(clg, deg = True), CLG_color)

        axF2.CLG.plot(F, abs(clg_up), color = CLG_color, ls = CLG_ud_ls)
        axF2.CLG_zoom.plot(F, abs(clg_up), color = CLG_color, ls = CLG_ud_ls)
        #axF2.CLG_phase.plot(F, np.angle(clg_up, deg = True), CLG_color, ls = CLG_ud_ls)

        axF2.CLG.plot(F, abs(clg_dn), color = CLG_color, ls = CLG_ud_ls)
        axF2.CLG_zoom.plot(F, abs(clg_dn), color = CLG_color, ls = CLG_ud_ls)
        #axF2.CLG_phase.plot(F, np.angle(clg_dn, deg = True), CLG_color, ls = CLG_ud_ls)

        axF2.CLG.plot(F, abs(snig), color = SNIG_color)
        axF2.CLG_zoom.plot(F, abs(snig), color = SNIG_color)
        #axF2.CLG_phase.plot(F, np.angle(snig, deg = True), SNIG_color)

        axF2.CLG.plot(F, abs(snig_up), color = SNIG_color, ls = CLG_ud_ls)
        axF2.CLG_zoom.plot(F, abs(snig_up), color = SNIG_color, ls = CLG_ud_ls)
        #axF2.CLG_phase.plot(F, np.angle(snig_up, deg = True), SNIG_color, ls = CLG_ud_ls)

        axF2.CLG.plot(F, abs(snig_dn), color = SNIG_color, ls = CLG_ud_ls)
        axF2.CLG_zoom.plot(F, abs(snig_dn), color = SNIG_color, ls = CLG_ud_ls)
        #axF2.CLG_phase.plot(F, np.angle(snig_dn, deg = True), SNIG_color, ls = CLG_ud_ls)

        axF2.CLG.set_title("CLTF Gain (Red.) Sensing Injection (Purp.)")
        axF2.CLG_zoom.set_title("CLTF Gain (zoomed)")
        #axF2.CLG_phase.set_title("CLTF Phase")

        axF2.CLG.set_ylabel("Gain")
        axF2.CLG_zoom.set_ylabel("Gain")
        #axF2.CLG_phase.set_ylabel("Phase [deg]")
        axF2.CLG.set_yscale('log_zoom')
        #ax2F.CLG_zoom.set_yscale('log_zoom')
        #axF2.CLG_zoom.set_ylim(.5, 2)

    axF.OLG.set_title("OLTF Gain")
    axF.OLG_zoom.set_title("OLTF Gain (zoomed)")
    axF.OLG_phase.set_title("OLTF Phase")

    axF.OLG.set_ylabel("Gain")
    axF.OLG_zoom.set_ylabel("Gain")
    axF.OLG_phase.set_ylabel("Phase [deg]")

    axF.ax_bottom.set_xlabel('Frequency [Hz]')
    axF.ax_bottom.set_xscale('log_zoom')
    axF.finalize()

    if full:
        axF2.ax_bottom.set_xlabel('Frequency [Hz]')
        axF2.ax_bottom.set_xscale('log_zoom')

        axF2.finalize()

    for UGF in UGFs:
        for ax in axF.ax_list:
            ax.axvline(UGF, ls = ':', color = 'blue')
        if full:
            for ax in axF2.ax_list:
                ax.axvline(UGF, ls = ':', color = 'blue')
    return axF


def plot_xfer(
        F,
        h,
        phase_crossings = [-60, -30, 30, 60],
        inv = False,
        xscale = 'log_zoom',
):
    if inv:
        h = -h
    fig = pyplot.figure()
    fig.set_size_inches(10, 4)
    gs = gridspec.GridSpec(
        1, 2,
        wspace = .2
    )
    axF = generate_stacked_plot_ax(
        fig = fig,
        gs_base = gs[0],
        name_use_list = [
            ('OLG', True),
            ('OLG_zoom', True),
            ('OLG_phase', True),
        ],
        height_ratios = {
            'OLG': 1,
            'OLG_zoom': .5,
            'OLG_phase': 1,
        },
        xscales = 'log_zoom',
        hspace = .4
    )

    crossings = []
    #abs_OLG = abs(h)
    phase_OLG = np.angle(h, deg = True)
    cross_blocks = (phase_OLG > phase_crossings[0])
    for phase in phase_crossings[1:]:
        cross_blocks = cross_blocks ^ (phase_OLG > phase)
    cross_blocks = (cross_blocks[1:] ^ cross_blocks[:-1])
    ugf_idx = None

    for idx in np.argwhere(cross_blocks):
        ugf_idx = idx
        F_ugf = F[ugf_idx]
        crossings.append(F_ugf)

    OLG_color = 'blue'

    axF.OLG.plot(F, abs(h), color = OLG_color)
    axF.OLG.set_yscale('log_zoom')
    axF.OLG_zoom.plot(F, abs(h), color = OLG_color)
    axF.OLG_zoom.set_yscale('log_zoom')
    axF.OLG_zoom.set_ylim(.5, 2)
    axF.OLG_phase.plot(F, np.angle(h, deg = True), color = OLG_color)

    axF.OLG.set_title("OLTF Gain")
    axF.OLG_zoom.set_title("OLTF Gain (zoomed)")
    axF.OLG_phase.set_title("OLTF Phase")

    axF.OLG.set_ylabel("Gain")
    axF.OLG_zoom.set_ylabel("Gain")
    axF.OLG_phase.set_ylabel("Phase [deg]")

    axF.ax_bottom.set_xlabel('Frequency [Hz]')
    axF.finalize()

    axF.ax_bottom.set_xscale(xscale)
    for cross_F in crossings:
        for ax in axF.ax_list:
            ax.axvline(cross_F, ls = ':', color = 'blue')
    for phase in phase_crossings:
        axF.OLG_phase.axhline(phase)
    return axF
