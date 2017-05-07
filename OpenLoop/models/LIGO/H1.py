
#---------------- p a r a m H 1 . m ---------------------
# parameters shown in LIGO-T0900043, non-folded
# Originally written by Kiwamu, and modified for L1 by KK
#
# need to update with H1 params
#--------------------------------------------------------
# In the current setting PR3, SR2 and SR3 are omitted for simplicity.
# However PR2 is included as a high reflective beam splitter so that
# the POP2 (light coming from BS to PRM) signal can be obtained.
# 



# basic constants
lambda = 1064e-9;   # Can't we get inherit these somehow?
c = 299792458;

################################################################
# Detector Geometry (distances in meters)
#
# 
lPRC  = 57.656;   # PRCL: lPRC = lPR + (lIX + lIY) / 2
lSRC  = 56.008;   # SRCL: lSRC = lSR + (lIX + lIY) / 2  
lasy  = 0.0504;   # Schnupp Asy: lasy = lIX - lIY
lmean = 4.8298;   # (lIX + lIY) / 2
#--------------

# optics.Mirror curvatures (all dimensions in meters)
Ri = 1934;             # radius of curvature of input mirrors (IX and IY)
Re = 2245;           # radius of curvature of end mirrors (EX and EY)
Rpr = -10.997;          # radius of curvature of power recycling mirrors
Rpr2 = -4.555;
Rsr = -5.6938;      	# radius of curvature of signal recycling mirrors


# Put together all the length parameters into 'par'
par.Length.IX = lmean + lasy / 2;  # distance [m] from BS to IX
par.Length.IY = lmean - lasy / 2;  # distance [m] from BS to IY
par.Length.EX = 3994.50;           # length [m] of the X arm
par.Length.EY = 3994.50;           # length [m] of the Y armlplp
par.Length.PR = lPRC - lmean;      # distance from PR to BS
par.Length.SR = lSRC - lmean;      # distance from SR to BS
par.Length.PR_PR2 = 16.6037;           # distance from PR to PR2
par.Length.PR2_BS = par.Length.PR - par.Length.PR_PR2;           # distance from PR2 to BS

# Put together all the Radius of Curvature [1/m] 
par.IX.ROC = 1 / Ri;
par.IY.ROC = 1 / Ri;
par.EX.ROC = 1 / Re;
par.EY.ROC = 1 / Re;
par.BS.ROC = 0;
par.PR.ROC = 1 / Rpr;
par.SR.ROC = 1 / Rsr;
par.PR2.ROC = 1/Rpr2; # 40m doesn't use curved mirrors for PRC folding

# Microscopic length offsets
dETM = 0;            # DARM offset, for DC readout - leave this as zero
par.IX.pos = 0;
par.IY.pos = 0;
par.EX.pos = 0;      # Set DARMoffset in your own scripts, not here.
par.EY.pos = 0;
par.BS.pos = 0;
par.PR.pos = 0;
par.SR.pos = lambda/4; # pos = lambda/4 for signal recycling
par.PR2.pos = 0;


################################################################
# optics.Mirror Parameters

# HR Transmissivities 
par.IX.T = 0.014;     # T = 1.4# for ITMX
par.IY.T = 0.014;     # T = 1.4# for ITMY
par.BS.T = 0.5;       # T = 50 # for BS, may have +- 0.003 RT imbalance

par.EX.T = 5e-6;     # T = 1 for DRMI (T = 5ppm for ALIGO)
par.EY.T = 5e-6;     # T = 1 for DRMI (T = 5ppm for ALIGO)

par.PR.T = 0.03;     # T = 3# for PRM
par.SR.T = 0.35;      # T = 35# for SRM
par.PR2.T = 250e-6;  # 250ppm

# Power reflectivity on AR Surfaces
# Using 40m parameters ...
#
par.IX.Rar = 0;  # designed value is 500 ppm
par.IY.Rar = 0;  # designed value is 500 ppm
par.EX.Rar = 0;  # designed value is less than 300 ppm
par.EY.Rar = 0;  # designed value is less than 300 ppm
par.BS.Rar = 0;       # designed value is less than 600 ppm 
par.PR.Rar = 0;       # designed value is less than 300 ppm
par.SR.Rar = 0;       # designed value is less than 300 ppm
par.PR2.Rar = 0;

# HR Losses (75 ppm round trip, 50 ppm assumed in 40m)
par.IX.L = 0;
par.IY.L = 0;
par.EX.L = 100e-6;
par.EY.L = 100e-6;
par.BS.L = 37.5e-6;
par.PR.L = 37.5e-6;
par.SR.L = 1; #37.5e-6;
par.PR2.L = 37.5e-6;

# mechanical parameters
par.w = 2 * pi * 0.45;      # resonance frequency of the mirror (rad/s)
par.mass  = 40;		    # mass of the test mass mirrors (kg)
par.w_pit = 2 * pi * 0.6;   # pitch mode resonance frequency


################################################################
# Input Beam Parameters
par.Pin = 1;            # input power (W)
f1 = 9099471;          # first modulation frequency
f2 = 5*f1;            # second modulation frequency

Nmod1 = 2;              # first modulation order
Nmod2 = 2;              # second modulation order

# construct modulation vectors 
n1 = (-Nmod1:Nmod1)';
n2 = (-Nmod2:Nmod2)';
vMod1 = n1*f1;
vMod2 = n2*f2;
  
# # make sidebands of sidebands
#  for i=1:length(n1)                        # run through all the f1 components
#      for j=1:length(n2)                    # run through all the f2 components
#            index = j + (i-1)*length(n1);   # index for new arrays
#            vFrf(index) = vMod1(i)+vMod2(j);    # frequency of sidebands and carrier
#      end
#  end
# vFrf = sortrows(vFrf');

# input amplitude is only carrier and zero ampliutde in sidebands.
# because two RF modulators are placed after the laser source
nCarrier = find(vFrf == 0, 1);
vArf = zeros(size(vFrf));
vArf(nCarrier) = sqrt(par.Pin);

par.Laser.vFrf = vFrf; 
par.Laser.vArf = vArf;
par.Laser.Power = par.Pin;
par.Laser.Wavelength = lambda;

par.Mod.f1 = f1;
par.Mod.f2 = f2;
par.Mod.g1 = 0.1; #  first modulation depth (radians)
par.Mod.g2 = 0.1; # second modulation depth (radians)

par.Mod.AM1 = 0;
par.Mod.AM2 = 0;
par.Mod.a1 = 0;
par.Mod.a2 = 0;

################################################################
# Adjustment of demodulation phase 
# Demodulation Phases -- tuned with getDemodPhases

par.phi.phREFL1  = 0;          # f1 : adjusted for CARM, I-phase
par.phi.phREFL2  = 5;             # f2 : adjusted for CARM, I-phase
par.phi.phREFL31 = 0;            # 3*f1: adjusted for PRCL, I-phase
par.phi.phREFL32 = 0;         # 3*f2: adjusted for SRCL, I-phase

par.phi.phAS1    = 0;       # f1 : adjusted for DARM, Q-pjase
par.phi.phAS2    = 0;      # f2 : adjusted for DARM, Q-phase
par.phi.phAS31   = 0;        # 3f1: adjusted for MICH, Q-phase
par.phi.phAS32   = 0;

par.phi.phPOP1 = 0;             # f1 : adjusted for PRCL, I-phase
par.phi.phPOP2 = 0;            # f2 : adjusted for SRCL, I-phase
par.phi.phPOP31 = 0;           # 3f1: adjusted for PRCL, I-phase
par.phi.phPOP32 = 0;            # 3f2: adjusted for SRCL, I-phase

par.phi.phPOX1 = 0;            # f1 : adjusted for PRCL, I-phase
par.phi.phPOX2 = 0;        # f2 : adjusted for MICH, Q-phase
par.phi.phPOX31 = 0;           # 3f1: adjusted for PRCL, I-phase
par.phi.phPOX32 = 0;      # 3f2: adjusted for MICH, Q-phase

par.phi.phPOY1 = 0;
par.phi.phPOY2 = 0;
par.phi.phPOY31 = 0;
par.phi.phPOY32 = 0;


################################################################

# Create an Optickle model of H1
#--------------------------------------------------------
# In the current setting PR3, SR2 and SR3 are omitted for simplicity.
# However PR2 is included as a high reflective beam splitter so that
# the POP2 (light coming from BS to PRM) signal can be obtained.
# 
#--------------------------------------------------------
# par = parameter struct returned from paramC1 -- par = parmC1
# opt = optC1(par)

function opt = optH1(par)

################################################################
# Add a Field Source

# create an empty model, with frequencies specified
opt = Optickle(par.Laser.vFrf);

# add a source, with RF amplitudes specified
opt = addSource(opt, 'optics.Laser', par.Laser.vArf);

# add modulators for optics.Laser amplitude and phase noise
opt = addModulator(opt, 'AM', 1);
opt = addModulator(opt, 'PM', i);

# link, output of optics.Laser is PM->out
opt = addLink(opt, 'optics.Laser', 'out', 'AM', 'in', 0);
opt = addLink(opt, 'AM', 'out', 'PM', 'in', 0);

################################################################
# Add Input Optics
# The argument list for addMirror is:
# [opt, sn] = addMirror(opt, name, aio, Chr, Thr, Lhr, Rar, Lmd)
# type "help addMirror" for more information


# Modulators
opt = addRFmodulator(opt, 'Mod1', par.Mod.f1, i * par.Mod.g1);
opt = addRFmodulator(opt, 'Mod2', par.Mod.f2, i * par.Mod.g2);
#-#
opt = addRFmodulator(opt, 'AMmod1', par.Mod.AM1, 1*par.Mod.a1);
opt = addRFmodulator(opt, 'AMmod2', par.Mod.AM2, 1*par.Mod.a2);
#-#

# link, No MZ
opt = addLink(opt, 'PM', 'out', 'Mod1', 'in', 5);
opt = addLink(opt, 'Mod1', 'out', 'Mod2', 'in',0);# 0.05);
#-#
opt = addLink(opt, 'Mod2', 'out','AMmod1','in',0);
opt = addLink(opt, 'AMmod1','out','AMmod2','in',0);
#-#

################################################################
# Add Core Optics
#
# The parameter struct must contain parameters the following
# for each mirror: T, L, Rar, mechTF, pos, ROC

listMirror = {'PR','SR', 'BS', 'IX', 'IY', 'EX', 'EY', 'PR2'};

for n = 1:length(listMirror)
  name = listMirror{n};
  p = par.(name);

  # add mirror
  if strmatch(name, 'BS')
    opt = addBeamSplitter(opt, name, 45, 1 / p.ROC, p.T, p.L, p.Rar, 0);
  elseif strmatch('PR2', name)
    opt = addBeamSplitter(opt, name, 10, 1 / p.ROC, p.T, p.L, p.Rar, 0);
  else
    opt = addMirror(opt, name, 0, 1 / p.ROC, p.T, p.L, p.Rar, 0);
  end

  # set mechanical transfer-functions and mirror position offsets
  opt = setPosOffset(opt, name, p.pos);
end

dampRes = [-0.1 + 1i, -0.1 - 1i];
opt = setMechTF(opt, 'IX', zpk([], par.w * dampRes, 1 / par.mass));
opt = setMechTF(opt, 'EX', zpk([], par.w * dampRes, 1 / par.mass));
opt = setMechTF(opt, 'IY', zpk([], par.w * dampRes, 1 / par.mass));
opt = setMechTF(opt, 'EY', zpk([], par.w * dampRes, 1 / par.mass));
opt = setMechTF(opt, 'PR', zpk([], par.w * dampRes, 1 / par.mass));
opt = setMechTF(opt, 'SR', zpk([], par.w * dampRes, 1 / par.mass));
opt = setMechTF(opt, 'BS', zpk([], par.w * dampRes, 1 / par.mass));


# link Modulators output to PR back input (no input Mode Cleaner)
#opt = addLink(opt, 'Mod2', 'out', 'PR', 'bk', 0.2);#35);
#-#
opt = addLink(opt, 'AMmod2', 'out', 'PR', 'bk', 0.2);#35);
#-#

# link PR front output -> PR2 A-side fron input
opt = addLink(opt, 'PR', 'fr', 'PR2', 'frA', par.Length.PR_PR2);

# link BS A-side inputs to PR2 A-side and SR front outputs
opt = addLink(opt, 'PR2', 'frA', 'BS', 'frA', par.Length.PR2_BS);
opt = addLink(opt, 'SR', 'fr', 'BS', 'bkA', par.Length.SR);

# link BS A-side outputs to and IX and IY back inputs
opt = addLink(opt, 'BS', 'frA', 'IY', 'bk', par.Length.IY);
opt = addLink(opt, 'BS', 'bkA', 'IX', 'bk', par.Length.IX);

# link BS B-side inputs to and IX and IY back outputs
opt = addLink(opt, 'IY', 'bk', 'BS', 'frB', par.Length.IY);
opt = addLink(opt, 'IX', 'bk', 'BS', 'bkB', par.Length.IX);

# link BS B-side outputs to PR2 B-side and SR front inputs
opt = addLink(opt, 'BS', 'frB', 'PR2', 'frB', par.Length.PR2_BS);
opt = addLink(opt, 'BS', 'bkB', 'SR', 'fr', par.Length.SR);

# link PR2 B-side front output to PR fron input
opt = addLink(opt, 'PR2', 'frB', 'PR', 'fr', par.Length.PR_PR2);

# link the arms
opt = addLink(opt, 'IX', 'fr', 'EX', 'fr', par.Length.EX);
opt = addLink(opt, 'EX', 'fr', 'IX', 'fr', par.Length.EX);

opt = addLink(opt, 'IY', 'fr', 'EY', 'fr', par.Length.EY);
opt = addLink(opt, 'EY', 'fr', 'IY', 'fr', par.Length.EY);


# tell Optickle to use this cavity basis
opt = setCavityBasis(opt, 'IX', 'EX');
opt = setCavityBasis(opt, 'IY', 'EY');

################################################################
