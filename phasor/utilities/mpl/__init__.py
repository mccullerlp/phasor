# -*- coding: utf-8 -*-
"""
"""

from .utils import *

from .autoniceplot import (
    AutoPlotSaver,
    asavefig,
    mplfigB,
)

from .stacked_plots import (
    generate_stacked_plot_ax,
    generate_ax,
)

from .logticks import (
    setup_log_xticks,
)

style_6p5in = {
    'savefig.dpi' : 100,
    'figure.dpi' :  100,

    'lines.linewidth' :  1.0,

    'axes.facecolor' :  'FFFFFF',
    'figure.facecolor' :  'FFFFFF',
    'figure.figsize' :  [6.5, 3.0],

    'font.family' :  'DejaVu Sans',

    "figure.titlesize"                    : 'large',  # size of the figure title (Figure.suptitle())
    "figure.titleweight"                  : 'normal',  # weight of the figure title
    "pdf.fonttype"                        : 3       ,  # Output Type 3 (Type3) or Type 42 (TrueType)
    "font.size"                           : 10.0    ,
    "axes.grid"                           : False   ,  # display grid or not
    "axes.titlesize"                      : 'large',  # fontsize of the axes title
    "axes.titlepad"                       : 6.0     ,  # pad between axes and title in points
    "axes.labelsize"                      : 'medium' ,  # fontsize of the x any y labels
    "axes.labelpad"                       : 4.0     ,  # space between label and axis
    "axes.formatter.useoffset"            : True    ,  # If True, the tick label formatter
    "axes.formatter.offset_threshold"     : 4       ,  # When useoffset is True, the offset
    "legend.fontsize"                     : 'medium' ,
    "legend.borderpad"                    : 0.4     ,  # border whitespace
    "legend.labelspacing"                 : 0.5     ,  # the vertical space between the legend entries
    "legend.handlelength"                 : 2.0     ,  # the length of the legend lines
    "legend.handleheight"                 : 0.7     ,  # the height of the legend handle
    "legend.handletextpad"                : 0.8     ,  # the space between the legend line and legend text
    "legend.borderaxespad"                : 0.5     ,  # the border between the axes and legend edge
    "legend.columnspacing"                : 2.0     ,  # column separation
}



style_3p5in = {
    'savefig.dpi' : 200,
    'figure.dpi' :  200,

    'lines.linewidth' :  1.0,

    'axes.facecolor' :  'FFFFFF',
    'figure.facecolor' :  'FFFFFF',
    'figure.figsize' :  [3.5, 2.5],

    'font.family' :  'DejaVu Serif',

    "figure.titlesize"                    : 'medium',  # size of the figure title (Figure.suptitle())
    "figure.titleweight"                  : 'normal',  # weight of the figure title
    "pdf.fonttype"                        : 3       ,  # Output Type 3 (Type3) or Type 42 (TrueType)
    "font.size"                           : 10.0    ,
    "axes.grid"                           : False   ,  # display grid or not
    "axes.titlesize"                      : 10,  # fontsize of the axes title
    "axes.titlepad"                       : 6.0     ,  # pad between axes and title in points
    "axes.labelsize"                      : 8,  # fontsize of the x any y labels
    "axes.labelpad"                       : 4.0     ,  # space between label and axis
    "axes.formatter.useoffset"            : True    ,  # If True, the tick label formatter
    "axes.formatter.offset_threshold"     : 4       ,  # When useoffset is True, the offset
    "legend.fontsize"                     : 8 ,
    "legend.borderpad"                    : 0.4     ,  # border whitespace
    "legend.labelspacing"                 : 0.5     ,  # the vertical space between the legend entries
    "legend.handlelength"                 : 2.0     ,  # the length of the legend lines
    "legend.handleheight"                 : 0.7     ,  # the height of the legend handle
    "legend.handletextpad"                : 0.8     ,  # the space between the legend line and legend text
    "legend.borderaxespad"                : 0.5     ,  # the border between the axes and legend edge
    "legend.columnspacing"                : 2.0     ,  # column separation
}

style_tex_serif = {
    "text.latex.preamble" : (r'\usepackage{txfonts}', r'\usepackage{textgreek}', r'\usepackage{textcomp}'),
    "text.latex.unicode" : True,
    "font.family" : 'serif',
    "text.usetex" : True,
}

style_serif = {
    "font.family" : 'serif',
}






