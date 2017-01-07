%---------------- p r o b e s L 1. m -------------
% 
% Kiwamu's probesC1_00.m for L1 by KK
%
%--------------------------------------------------------
%
%[Description]
%   This function adds the neccessary RFPDs and DCPDs on
%  an interferomter model. In the name of this file, '00' means
% the TEM00 mode and hence these are the probes dedicated only for
% the length sensing and not for angular sensing.
% Example usage : 
%              par = paramC1;
%              opt = optC1(par);
%              opt = probesC1_00(opt, par);
%--------------------------------------------------------
%
% [Notes]
%  This file is a modified version of the eLIGO opticle file
% called probesH1_00.m.
%


function opt = probesL1(opt, par)

% Add attenuators and terminal sinks
% Here the second return value of the addSink function is used.
% This return value is the serial number of the Sink, which is
% can be used in place of its name for linking (with a marginal
% increase in efficiency).

% 3rd addSink argument is power loss, default is 1
% Attenuator set to match what is there in the real IFOs, maybe.
% AS: transmission to the dark port from SR, before the OMC 


% 'Att' stands for 'Attenuation'
opt = addSink(opt, 'AttREFL', 0);
opt = addSink(opt, 'AttAS',   0);
opt = addSink(opt, 'AttPOP',  0);
opt = addSink(opt, 'AttPOX',  0);
opt = addSink(opt, 'AttPOY',  0);



[opt, nREFL] = addSink(opt, 'REFL');
[opt, nAS] = addSink(opt, 'AS');
[opt, nPOP] = addSink(opt, 'POP');
[opt, nPOX] = addSink(opt, 'POX');
[opt, nPOY] = addSink(opt, 'POY');
[opt, nTRX] = addSink(opt, 'TRX');
[opt, nTRY] = addSink(opt, 'TRY');

% Output links, set gouy phases
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Function addReaduotGouy set the gouy phase 90 degrees apart
% NB: Demodulation phases are in degrees, gouy phases in radiants!!
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% REFL
opt = addLink(opt, 'PR', 'bk', 'AttREFL', 'in', 0);
opt = addLink(opt, 'AttREFL', 'out', 'REFL', 'in', 0);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% AS Asymmetric port
opt = addLink(opt, 'SR', 'bk', 'AttAS', 'in', 0);
opt = addLink(opt, 'AttAS', 'out', 'AS', 'in', 0);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% POP
opt = addLink(opt, 'PR2', 'bkB', 'AttPOP', 'in', 0);
opt = addLink(opt, 'AttPOP', 'out', 'POP', 'in', 0);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% POX
opt = addLink(opt, 'IX', 'po', 'AttPOX', 'in', 0);
opt = addLink(opt, 'AttPOX', 'out', 'POX', 'in', 0);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% POY
opt = addLink(opt, 'IY', 'po', 'AttPOY', 'in', 0);
opt = addLink(opt, 'AttPOY', 'out', 'POY', 'in', 0);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% TRX and TRY
opt = addLink(opt, 'EX', 'bk', 'TRX', 'in', 5);
opt = addLink(opt, 'EY', 'bk', 'TRY', 'in', 5);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Add Probes

% demodulation frequencies
f1 = par.Mod.f1;
f2 = par.Mod.f2;

% REFL signals (reflected or symmetric port)
opt = addProbeIn(opt, 'REFL DC', nREFL, 'in',  0, 0);                             % DC
opt = addProbeIn(opt, 'REFL I1', nREFL, 'in', f1, par.phi.phREFL1);               % f1 demod I
opt = addProbeIn(opt, 'REFL Q1', nREFL, 'in', f1, par.phi.phREFL1 + 90);          % f1 demod Q
opt = addProbeIn(opt, 'REFL I2', nREFL, 'in', f2, par.phi.phREFL2);               % f2 demod I
opt = addProbeIn(opt, 'REFL Q2', nREFL, 'in', f2, par.phi.phREFL2 + 90);          % f2 demod Q
opt = addProbeIn(opt, 'REFL 3I1', nREFL, 'in', 3 * f1, par.phi.phREFL31);         % 3f1 demod I
opt = addProbeIn(opt, 'REFL 3Q1', nREFL, 'in', 3 * f1, par.phi.phREFL31 + 90);    % 3f1 demod Q
opt = addProbeIn(opt, 'REFL 3I2', nREFL, 'in', 3 * f2, par.phi.phREFL32);         % 3f2 demod I
opt = addProbeIn(opt, 'REFL 3Q2', nREFL, 'in', 3 * f2, par.phi.phREFL32 + 90);    % 3f2 demod Q

% AS signals (anti-symmetric port before the OMC) 
opt = addProbeIn(opt, 'AS DC', nAS, 'in',  0, 0);                                 % DC
opt = addProbeIn(opt, 'AS I1', nAS, 'in', f1, par.phi.phAS1);                     % f1 demod I
opt = addProbeIn(opt, 'AS Q1', nAS, 'in', f1, par.phi.phAS1 + 90);                % f1 demod Q
opt = addProbeIn(opt, 'AS I2', nAS, 'in', f2, par.phi.phAS2);                     % f2 demod I
opt = addProbeIn(opt, 'AS Q2', nAS, 'in', f2, par.phi.phAS2 + 90);                % f2 demod Q
opt = addProbeIn(opt, 'AS 3I1', nAS, 'in', 3 * f1, par.phi.phAS31);               % 3f1 demod I
opt = addProbeIn(opt, 'AS 3Q1', nAS, 'in', 3 * f1, par.phi.phAS31 + 90);          % 3f1 demod Q
opt = addProbeIn(opt, 'AS 3I2', nAS, 'in', 3 * f2, par.phi.phAS32);               % 3f2 demod I
opt = addProbeIn(opt, 'AS 3Q2', nAS, 'in', 3 * f2, par.phi.phAS32 + 90);          % 3f2 demod Q

% POP signals (IX pick-off)
opt = addProbeIn(opt, 'POP DC', nPOP, 'in',  0, 0);		                          % DC
opt = addProbeIn(opt, 'POP I1', nPOP, 'in', f1, par.phi.phPOP1);	              % f1 demod I
opt = addProbeIn(opt, 'POP Q1', nPOP, 'in', f1, par.phi.phPOP1 + 90);             % f1 demod Q
opt = addProbeIn(opt, 'POP I2', nPOP, 'in', f2, par.phi.phPOP2);                  % f2 demod I
opt = addProbeIn(opt, 'POP Q2', nPOP, 'in', f2, par.phi.phPOP2 + 90);	          % f2 demod Q
opt = addProbeIn(opt, 'POP 3I1', nPOP, 'in', 3 * f1, par.phi.phPOP31);		      % 3f1 demod I
opt = addProbeIn(opt, 'POP 3Q1', nPOP, 'in', 3 * f1, par.phi.phPOP31 + 90);	      % 3f1 demod Q
opt = addProbeIn(opt, 'POP 3I2', nPOP, 'in', 3 * f2, par.phi.phPOP32);		      % 3f2 demod I
opt = addProbeIn(opt, 'POP 3Q2', nPOP, 'in', 3 * f2, par.phi.phPOP32 + 90);	      % 3f2 demod Q


% POX signals (IX pick-off)
opt = addProbeIn(opt, 'POX DC', nPOX, 'in',  0, 0);                               % DC
opt = addProbeIn(opt, 'POX I1', nPOX, 'in', f1, par.phi.phPOX1);		          % f1 demod I
opt = addProbeIn(opt, 'POX Q1', nPOX, 'in', f1, par.phi.phPOX1 + 90);          	  % f1 demod Q
opt = addProbeIn(opt, 'POX I2', nPOX, 'in', f2, par.phi.phPOX2);                  % f2 demod I
opt = addProbeIn(opt, 'POX Q2', nPOX, 'in', f2, par.phi.phPOX2 + 90);             % f2 demod Q
opt = addProbeIn(opt, 'POX 3I1', nPOX, 'in', 3 * f1, par.phi.phPOX31);		      % 3f1 demod I
opt = addProbeIn(opt, 'POX 3Q1', nPOX, 'in', 3 * f1, par.phi.phPOX31 + 90);	      % 3f1 demod Q
opt = addProbeIn(opt, 'POX 3I2', nPOX, 'in', 3 * f2, par.phi.phPOX32);		      % 3f2 demod I
opt = addProbeIn(opt, 'POX 3Q2', nPOX, 'in', 3 * f2, par.phi.phPOX32 + 90);	      % 3f2 demod Q


% Arm Transmitted DC signals
opt = addProbeIn(opt, 'TRX DC', nTRX, 'in', 0, 0);            % DC
opt = addProbeIn(opt, 'TRY DC', nTRY', 'in', 0, 0);           % DC
