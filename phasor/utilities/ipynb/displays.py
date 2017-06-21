"""
"""

import IPython
_ip = IPython.get_ipython()

_ip.magic("load_ext phasor.utilities.ipynb.autoreload")
_ip.magic("autoreload 2")

#if this is run from the console then inline can't be found. This hack seems to get around it
try:
    _ip.magic("matplotlib inline")
    _ip.magic("pylab inline")
except Exception:
    _ip.magic("matplotlib")
    _ip.magic("pylab")
#mpl.use('GTK3Cairo')

import numpy as np
import matplotlib as mpl
from matplotlib import gridspec
import matplotlib.pyplot as plt

from IPython.display import (
    display,
    display_pretty,
    display_html,
    display_jpeg,
    display_png,
    display_json,
    display_latex,
    display_svg,
    display_javascript,
    FileLink,
    Image,
    SVG,
    clear_output,
    Audio,
)

#for more options in mpl
import phasor.utilities.mpl
from phasor.utilities.mpl.utils import indexed_cmap
from phasor.utilities.np import logspaced, first_non_NaN

#_ip.magic("load_ext utilities.ipynb.diagmagic")
#try:
#    _ip.magic("load_ext utilities.ipynb.hierarchymagic")
#except ImportError:
#    pass

from phasor.utilities.mpl.autoniceplot import (
    AutoPlotSaver,
    mplfigB,
    asavefig
)

from phasor.utilities.mpl.stacked_plots import (
    generate_stacked_plot_ax,
)
import matplotlib
matplotlib.rcParams['savefig.dpi'] = 144

mpl.rcParams['axes.facecolor'] = 'FFFFFF'
mpl.rcParams['figure.facecolor'] = 'FFFFFF'
mpl.rcParams['figure.dpi'] = 130
mpl.rcParams['savefig.dpi'] = 92
mpl.rcParams['figure.figsize'] = [7.0, 3.0]

