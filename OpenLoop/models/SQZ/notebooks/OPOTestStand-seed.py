
# coding: utf-8

# In[115]:

import sympy
from YALL.utilities.ipynb.displays import *
from YALL.utilities.ipynb.ipy_sympy import *
import scipy.linalg


import numpy.testing as np_test
import declarative as decl
from declarative.bunch import (
    DeepBunch,
)

#import numpy as np

from OpenLoop import system
from OpenLoop import readouts
from OpenLoop import optics
from OpenLoop.utilities.print import pprint


# In[116]:

db = DeepBunch()
db.test.PSLG.power.val = logspaced(0.0001, .04, 200)
db.test.opo.ktp.N_ode = 10
db.test.include_AC = True
db.test.include_PM = False
#db.test.PSLG.phase.val = 90
#db.test.PSLG.phase.units = 'degrees'
db.test.PSLR_seed.power.val = .0000001
db.test.PSLR_seed.phase.val = 90
db.test.PSLR_seed.phase.units = 'deg'
db.test.F_PM.frequency.val = 1
db.environment.F_AC.order = 1
db.test.generateF_PM.amplitude = 0#np.linspace(0, .3, 20)
sys = system.BGSystem(
    ooa_params = db,
)
from OpenLoop.models.SQZ.OPO import OPOTestStand
sys.my.test = OPOTestStand()
db = sys.ooa_shadow()
solve = sys.test.opo.DC.DC_readout
#print(sys.test.ktp.ooa_as_yaml())
#print(sys.test.opo.DC.DC_readout / sys.test.PSLG.power_W.val)


# In[117]:

axB = mplfigB(Nrows=2)
X = sys.test.PSLG.power_W.val
axB.ax0.semilogy(X, sys.test.DC_R.DC_readout, color = 'red')
axB.ax1.plot(X, sys.test.DC_G.DC_readout, color = 'green')


# In[118]:

db = DeepBunch()
db.test.PSLG.power.val = logspaced(0.0001, .04, 200)
db.test.opo.ktp.N_ode = 10
db.test.include_AC = True
db.test.include_PM = False
db.test.PSLR_seed.power.val = .05
#db.test.PSLG.phase.val = 90
#db.test.PSLG.phase.units = 'degrees'
db.test.PSLR_seed.phase.val = 90
db.test.PSLR_seed.phase.units = 'deg'
db.test.F_PM.frequency.val = 1
db.environment.F_AC.order = 1
db.test.generateF_PM.amplitude = 0#np.linspace(0, .3, 20)
sys2 = system.BGSystem(
    ooa_params = db,
)
from OpenLoop.models.SQZ.OPO import OPOTestStand
sys2.my.test = OPOTestStand()
db = sys2.ooa_shadow()
solve = sys2.test.opo.DC.DC_readout
#print(sys.test.ktp.ooa_as_yaml())
#print(sys.test.opo.DC.DC_readout / sys.test.PSLG.power_W.val)


# In[119]:

axB = mplfigB(Nrows=2)
X = sys2.test.PSLG.power_W.val
axB.ax0.semilogy(X, sys2.test.DC_R.DC_readout, color = 'red')
axB.ax1.plot(X, sys2.test.DC_G.DC_readout, color = 'green')


# In[120]:

axB = mplfigB(Nrows=2)
X = sys.test.PSLG.power_W.val
axB.ax0.semilogy(X, sys.test.DC_R.DC_readout / sys.test.PSLR_seed.power_W.val, color = 'purple')
axB.ax0.semilogy(X, sys2.test.DC_R.DC_readout / sys2.test.PSLR_seed.power_W.val, color = 'red')
axB.ax1.plot(X, sys2.test.DC_G.DC_readout, color = 'green')
axB.ax1.plot(X, sys.test.DC_G.DC_readout, color = 'purple')


# In[121]:

axB = mplfigB(Nrows=2)
test = sys.test
X = sys.test.PSLG.power_W.val
x = (sys.test.PSLG.power_W.val / .040)**.5
axB.ax0.plot(X, test.AC_R.AC_CSD_IQ.real[0,0], color = 'red')
axB.ax0.plot(X, test.AC_R.AC_CSD_IQ.real[1,1], color = 'blue')
axB.ax0.plot(X, test.AC_R.AC_CSD_ellipse.max, color = 'orange', ls = '--')
axB.ax0.plot(X, test.AC_R.AC_CSD_ellipse.min, color = 'purple', ls = '--')
axB.ax0.plot(X, test.AC_R.AC_CSD_ellipse.min**.5* test.AC_R.AC_CSD_ellipse.max**.5, color = 'black', ls = '--')
axB.ax0.semilogy(X, 1 + .96*4*x/(1-x)**2, color = 'cyan')
axB.ax0.semilogy(X, 1 - .96*4*x/(1+x)**2, color = 'cyan')
axB.ax0.axhline(1./2.)
axB.ax0.axvline(.02)
axB.ax0.set_yscale('log')
axB.ax0.set_xscale('log')
axB.ax0.set_xlabel('G Pump in [W]')
axB.ax0.set_ylabel('shot noise [relative]')
axB.ax0.set_ylim(2e-2,1e2)
axB.ax1.semilogy(X, .875 * 1/(1-x)**(2), color = 'green')
axB.ax1.semilogy(X, .875 * 1/(1+x)**(2), color = 'green')

axB.ax1.semilogy(X, sys.test.DC_R.DC_readout / sys.test.DC_R.DC_readout[0], color = 'red')
#axB.ax0.set_ylim(0, 1.1)

