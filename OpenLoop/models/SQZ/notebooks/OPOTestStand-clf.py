
# coding: utf-8

# In[1]:

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


# In[2]:

db = DeepBunch()
db.test.PSLG.power.val = logspaced(0.0001, .03, 200)
db.test.opo.ktp.N_ode = 10
db.test.include_AC = True
db.test.include_PM = False
db.test.PSLR_clf.power.val = .001
#db.test.PSLG.phase.val = 90
#db.test.PSLG.phase.units = 'degrees'
db.test.PSLR_clf.phase.val = 45
db.test.PSLR_clf.phase.units = 'deg'
db.test.F_PM.frequency.val = 1
db.environment.F_AC.order = 1
db.test.generateF_PM.amplitude = 0#np.linspace(0, .3, 20)
sys = system.BGSystem(
    ooa_params = db,
)
from OpenLoop.models.SQZ.OPO import OPOTestStand
sys.my.test = OPOTestStand()
db = sys.ooa_shadow()
#print(sys.test.ktp.ooa_as_yaml())
val = (sys.test.opo.DC.DC_readout / sys.test.PSLG.power_W.val)


# In[11]:

generate_stacked_plot_ax


# In[29]:

axB = generate_stacked_plot_ax(
    name_use_list = (
        ('ax0', True),
        ('ax1', True),
        ('gInt', True),
    ),
    Nrows=2
)
X = sys.test.PSLG.power_W.val
if axB.ax0:
    axB.ax0.semilogy(X, sys.test.DC_R.DC_readout, color = 'red')
    axB.ax0.set_title('CLF Power at homodyne')
    axB.ax0.set_ylabel('CLF Power\n[W]')
if axB.ax1:
    axB.ax1.plot(X, sys.test.DC_G.DC_readout, color = (.5,.8,0))
    axB.ax1.set_title('Green REFL Power')
    axB.ax1.set_ylabel('Green REFL\nPower [W]')
if axB.gInt:
    axB.gInt.plot(X, sys.test.opo.DC.DC_readout, color = 'green')
    axB.gInt.set_title('Green Cavity Power')
    axB.gInt.set_ylabel('Green Cavity\nPower [W]')
axB.finalize()


# In[4]:

axB = mplfigB(Nrows=3)
X = -10*np.log10(sys.test.AC_R.AC_CSD_ellipse.min)
idx_sqzdb = np.searchsorted(X, 4)
X = sys.test.PSLG.power_W.val
axB.ax0.plot(X, sys.test.DC_CLF.DC_readout, color = 'red')
axB.ax1.plot(X, sys.test.DCI_CLF.DC_readout, color = 'green')
axB.ax1.plot(X, sys.test.DCQ_CLF.DC_readout, color = 'blue', ls = '--')
axB.ax1.plot(
    X, 
    (sys.test.DCI_CLF.DC_readout**2 + 
    sys.test.DCQ_CLF.DC_readout**2)**.5,
    color = 'purple')
angles_clf =  np.angle(sys.test.DCI_CLF.DC_readout + sys.test.DCQ_CLF.DC_readout*1j, deg = True)
phasor_CLF = sys.test.DCI_CLF.DC_readout + sys.test.DCQ_CLF.DC_readout*1j
axB.ax2.plot(
    X,
    angles_clf,
    color = 'red'
)
axB.ax2.axvline(X[idx_sqzdb])
(angles_clf[idx_sqzdb+1] - angles_clf[idx_sqzdb]) / (X[idx_sqzdb+1] - X[idx_sqzdb]) * 1e-3 * np.pi/180
#axB.ax1.set_ylim(-.1,.6)


# In[5]:

axB = mplfigB(Nrows=4)
X = -10*np.log10(sys.test.AC_R.AC_CSD_ellipse.min)
axB.ax0.plot(
    X,
    sys.test.hDCII_CLF.DC_readout,
    color = 'red'
)
axB.ax0.plot(
    X,
    sys.test.hDCIQ_CLF.DC_readout,
    color = 'orange'
)
axB.ax1.plot(
    X,
    sys.test.hDCQI_CLF.DC_readout,
    color = 'blue'
)
axB.ax1.plot(
    X,
    sys.test.hDCQQ_CLF.DC_readout,
    color = 'green'
)
axB.ax2.plot(
    X,
    (sys.test.hDCII_CLF.DC_readout**2 + 
    sys.test.hDCIQ_CLF.DC_readout**2)**.5,
    color = 'red'
)
axB.ax2.plot(
    X,
    (sys.test.hDCQI_CLF.DC_readout**2 + 
    sys.test.hDCQQ_CLF.DC_readout**2)**.5,
    color = 'green'
)

phasorI = sys.test.hDCII_CLF.DC_readout + sys.test.hDCIQ_CLF.DC_readout*1j
angleI = np.angle(sys.test.hDCII_CLF.DC_readout + sys.test.hDCIQ_CLF.DC_readout*1j, deg = True)
axB.ax3.plot(
    X,
    angleI,
    color = 'red'
)
phasorQ = sys.test.hDCQI_CLF.DC_readout + sys.test.hDCQQ_CLF.DC_readout*1j
angleQ = np.angle(sys.test.hDCQI_CLF.DC_readout + sys.test.hDCQQ_CLF.DC_readout*1j, deg = True)
axB.ax3.plot(
    X,
    angleQ,
    color = 'green'
)

#angleI - angleQ

#axB.ax1.set_ylim(-.1,.6)


# In[6]:

axB = mplfigB(Nrows=4)
X = -10*np.log10(sys.test.AC_R.AC_CSD_ellipse.min)
axB.ax0.plot(
    X,
    sys.test.hDCII_CLF.DC_readout,
    color = 'red'
)
axB.ax0.plot(
    X,
    sys.test.hDCQI_CLF.DC_readout,
    color = 'orange'
)
axB.ax1.plot(
    X,
    sys.test.hDCIQ_CLF.DC_readout,
    color = 'blue'
)
axB.ax1.plot(
    X,
    sys.test.hDCQQ_CLF.DC_readout,
    color = 'green'
)
axB.ax2.plot(
    X,
    (sys.test.hDCII_CLF.DC_readout**2 + 
    sys.test.hDCQI_CLF.DC_readout**2)**.5,
    color = 'red'
)
axB.ax2.plot(
    X,
    (sys.test.hDCIQ_CLF.DC_readout**2 + 
    sys.test.hDCQQ_CLF.DC_readout**2)**.5,
    color = 'green'
)

angleI = np.angle(sys.test.hDCII_CLF.DC_readout + sys.test.hDCQI_CLF.DC_readout*1j, deg = True)
axB.ax3.plot(
    X,
    angleI,
    color = 'red'
)
angleQ = np.angle(sys.test.hDCIQ_CLF.DC_readout + sys.test.hDCQQ_CLF.DC_readout*1j, deg = True)
axB.ax3.plot(
    X,
    angleQ,
    color = 'green'
)

angleI[idx_sqzdb]

#axB.ax1.set_ylim(-.1,.6)


# In[7]:

axB = mplfigB(Nrows=3)
X = -10*np.log10(sys.test.AC_R.AC_CSD_ellipse.min)
idx_sqzdb = np.searchsorted(X, 6)
norm_phasor = lambda C : C/abs(C)
CLF_adj = 1/norm_phasor(phasor_CLF / phasor_CLF[idx_sqzdb])
phasorAP = -(CLF_adj*phasorI/norm_phasor(phasorQ[idx_sqzdb])).imag + (CLF_adj*phasorQ/norm_phasor(phasorQ[idx_sqzdb])).imag * 1j
axB.ax0.plot(
    X,
    abs(phasorAP),
    color = 'green'
)
axB.ax0.plot(
    X,
    (phasorAP).real,
    color = 'blue',
    ls = '--',
)
axB.ax0.plot(
    X,
    (phasorAP).imag,
    color = 'red'
)

angleAP = np.angle(phasorAP, deg=True)
axB.ax1.plot(
    X,
    angleAP,
    color = 'red'
)
axB.ax1.axvline(X[idx_sqzdb])
axB.ax1.set_ylim(-40,20)

@np.vectorize
def radSQZ_Grin(SQZDB):
    X = -10*np.log10(sys.test.AC_R.AC_CSD_ellipse.min)
    idx_sqzdb = np.searchsorted(X, SQZDB)
    if idx_sqzdb >= len(X)-1:
        idx_sqzdb = len(X)-2
    norm_phasor = lambda C : C/abs(C)
    CLF_adj = 1/norm_phasor(phasor_CLF / phasor_CLF[idx_sqzdb])
    phasorAP = -(CLF_adj*phasorI/norm_phasor(phasorQ[idx_sqzdb])).imag + (CLF_adj*phasorQ/norm_phasor(phasorQ[idx_sqzdb])).imag * 1j
    angleAP = np.angle(phasorAP, deg=True)
    P_g = sys.test.PSLG.power_W.val
    return  (angleAP[idx_sqzdb+1] - angleAP[idx_sqzdb]) / (P_g[idx_sqzdb+1] - P_g[idx_sqzdb]) * P_g[idx_sqzdb] * np.pi/180

axB.ax2.plot(
    X,
    radSQZ_Grin(X),
    color = 'red'
)
print(radSQZ_Grin(3))
print(radSQZ_Grin(6))
print(radSQZ_Grin(10))
#phasorAP


# In[8]:

axB = mplfigB(Nrows=1)
test = sys.test
X = sys.test.PSLG.power_W.val
x = (sys.test.PSLG.power_W.val / .04)**.5
axB.ax0.semilogy(X, sys.test.DC_R.DC_readout / sys.test.DC_R.DC_readout[0], color = 'red')
axB.ax0.plot(X, test.AC_R.AC_CSD_IQ.real[0,0], color = 'red')
axB.ax0.plot(X, test.AC_R.AC_CSD_IQ.real[1,1], color = 'blue')
axB.ax0.plot(X, test.AC_R.AC_CSD_ellipse.max, color = 'orange', ls = '--')
axB.ax0.plot(X, test.AC_R.AC_CSD_ellipse.min, color = 'purple', ls = '--')
axB.ax0.plot(X, test.AC_R.AC_CSD_ellipse.min**.5* test.AC_R.AC_CSD_ellipse.max**.5, color = 'black', ls = '--')
axB.ax0.semilogy(X, 1 + .96*4*x/(1-x)**2, color = 'cyan')
axB.ax0.semilogy(X, 1 - .96*4*x/(1+x)**2, color = 'cyan')
axB.ax0.axhline(1./2.)
#axB.ax0.axvline(.02)
axB.ax0.set_yscale('log')
axB.ax0.set_xscale('log')
axB.ax0.set_xlabel('G Pump in [W]')
axB.ax0.set_ylabel('shot noise [relative]')
axB.ax0.set_ylim(1e-2,1e3)
#axB.ax0.set_ylim(0, 1.1)


# In[ ]:




# In[ ]:



