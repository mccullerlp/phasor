
# coding: utf-8

# In[2]:

import sympy
from YALL.utilities.ipynb.displays import *
#from YALL.utilities.ipynb.ipy_sympy import *
import scipy.linalg


import numpy.testing as np_test
import declarative as decl
from declarative.bunch import (
    DeepBunch,
)

#import numpy as np

from BGSF import system
from BGSF import readouts
from BGSF import optics
from BGSF.utilities.print import pprint


# In[2]:

db = DeepBunch()
#db.test.PSLG.power.val = np.linspace(0, .4, 100)
db.test.opo.ktp.N_ode = 10
db.test.include_AC = True
db.test.include_PM = False
db.test.F_PM.frequency.val = 1
db.environment.F_AC.order = 1
db.test.generateF_PM.amplitude = 0#np.linspace(0, .3, 20)
sys = system.BGSystem(
    ooa_params = db,
)
from BGSF.models.SQZ.TestAOMOPO import AOMnOPOTestStand
sys.my.test = AOMnOPOTestStand()
db = sys.ooa_shadow()
db.test.PSLG.power.val
#print(sys.test.ktp.ooa_as_yaml())


# In[3]:

#print(sys.test.DC_R.DC_readout)
db.test.F_PM.frequency.val
#print(sys.test.DC_G.DC_readout)


# In[4]:

axB = mplfigB(Nrows=1)
X = sys.test.PSLG.power_W.val
axB.ax0.plot(X, sys.test.DC_R.DC_readout, color = 'red')
axB.ax0.plot(X, sys.test.DC_G.DC_readout, color = 'green')
axB.ax0.plot(X, sys.test.DC_R.DC_readout + sys.test.DC_G.DC_readout, color = 'black')
#axB.ax0.plot(test.ktp.length_mm.val, 1 * np.tanh(.200 * test.ktp.length_mm.val)**2, ls = '--', color = 'blue')
#axB.ax0.set_xscale('log')
#axB.ax0.set_ylim(0, 1.1)
print(sys.test.opo.DC.DC_readout)


# In[5]:

axB = mplfigB(Nrows=1)
test = sys.test
X = sys.test.opo.ktp.length_mm.val
axB.ax0.plot(X, test.AC_R.AC_CSD_IQ.real[0,0], color = 'red')
axB.ax0.plot(X, test.AC_R.AC_CSD_IQ.real[1,1], color = 'blue')
axB.ax0.plot(X, test.AC_R.AC_CSD_ellipse.max, color = 'orange', ls = '--')
axB.ax0.plot(X, test.AC_R.AC_CSD_ellipse.min, color = 'purple', ls = '--')
axB.ax0.plot(X, test.AC_R.AC_CSD_ellipse.min**.5* test.AC_R.AC_CSD_ellipse.max**.5, color = 'black', ls = '--')
axB.ax0.axhline(1./2.)
#axB.ax0.axvline(.11)
axB.ax0.set_yscale('log')
#axB.ax0.set_ylim(0, 1.1)


# In[ ]:



