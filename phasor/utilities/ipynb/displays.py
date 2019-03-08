# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import IPython
_ip = IPython.get_ipython()

if _ip is not None:
    _ip.magic("load_ext autoreload")
    _ip.magic("autoreload 2")

    #if this is run from the console then inline can't be found. This hack seems to get around it
    try:
        import ipykernel.pylab.backend_inline
        backend = ipykernel.pylab.backend_inline.InlineBackend.instance()
        backend.rc.clear()

        _ip.magic("matplotlib inline")
        _ip.magic("pylab inline")
    except Exception:
        _ip.magic("matplotlib")
        _ip.magic("pylab")
    #mpl.use('GTK3Cairo')

import numpy as np
import matplotlib as mpl
import matplotlib
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
    display_markdown,
    FileLink,
    Image,
    SVG,
    clear_output,
    Audio,
    Javascript,
    Markdown,
)

from phasor.utilities.np import (
    logspaced,
    first_non_NaN
)

#for more options in mpl
import phasor.utilities.mpl

from phasor.utilities.mpl.utils import (
    indexed_cmap,
)

from phasor.utilities.mpl import (
    AutoPlotSaver,
    mplfigB,
    asavefig,
    generate_stacked_plot_ax,
    style_6p5in,
    style_3p5in,
    style_tex_serif,
    style_serif,
    setup_log_xticks,
)


try:
    import tabulate
except ImportError:
    pass


def setup_auto_savefig(ipynb_name, check_warn = False):
    from os import path
    new =  path.splitext(ipynb_name)[0] + '-ipynb'
    asavefig.org_subfolder = new
