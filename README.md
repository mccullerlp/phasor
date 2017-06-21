# python-phasor

Frequency-Domain Bond Graph modeling for OptoMechaTronics with control feedback, signal propagation and noise analysis. The noise
analysis include quantum noise and squeezing for optical systems. 

Iteratively solves linear systems of equations to simulate optical modulations and electrical mixers. Stops upon convergence (or specified order). Uses many frequency indexes to
determine all coherent signals.

Has test cases to check physical validity.

Noise modeling can occur across physical domains, with closed optical/mechanical/signal/electrical feedback.

After reading the features, it is easiest to dive in to some examples before consulting dry documentation.

## Features

### General
 * Numerical values are duck-typed. This allows numpy broadcasting. ps_In particular this allows simulating many parameters simultaneously by using a an array for the parameter value. These parameters could be things like the sideband frequency for noise analysis, the nonlinear gain in a crystal. 2d array parameter sweeps are also possible.
 
 * Configuration management! Using the declarative library, all (in principle) configurable parameters are stored in a heirarchical dictionary. This allows easy modification of even deep components. It also hooks into the fitting system and can be used to archive simulations by parameters for comparison (see declarative.HDFDeepBunch).
 
 * Uses internal matrix solver optimized for smallest-arrays-first and fewest-connections-first as it solves the linear system.

 * NOTE: currently the Gaussian elimination algorithm with heuristics can be unstable for large systems. pe_A QR factorization step is needed to behave better. The output is obviously bad when unstable, but the iterative solver can take many iterations when poor loop reduction ordering occurs.
 
 * The system object can store global settings and debug flags. These are easy to hook into and can be adjusted through the configuration management system.

### Optical
 * Single-mode Mirrors, Lasers, Polarization optics, Faraday Isolators, Multiple laser frequencies and harmonics can be simulated and propagate simultaneously. Currently biased for 1064nm lasers, but no code intrinsically assumes any optical wavelength.

 * Simulation indexed using lowering/raising operators and frequency. This allows more obvious correspondence with quantum optics. Computing with both (typically the states are conjugates of one-another) removes the distinctions of other simulators between driven and sideband fields (DC vs. AC analysis).

 * Simulation of ODE's within nonlinear optical crystals. Still a bit slow, but functional for optical parametric oscillation/second-harmonic generation and related effects. Also works for simulation of Acousto-Optic modulators. This is further enabled by the inclusion of both raising and lowering states.
 
 * Photodiodes transduce from optical to signal, allowing immediate use in feedback.
 
 * Homodyne detection implemented with outputs in Watts, root-Watts (field amplitude of differential signal) and in root-quanta of differential signal (normalizes standard shot-noise to PSD of 1/Hz for any optical wavelength).
 
 * Code for nonlinear signal mixing of AM/PM modulators, mirror phases, mirror radiation pressure force and photodiode readout all uses the _same code_. This helps the reliability of physical processes.

### Electrical
 * Passive components work in 1-port or 2-port forms. (1-port is a connection to ground via passive component)

 * Johnson-Nyquist noise automatically computed

 * Uses only scattering parameter form. All components are converted into equivalent scattering matrix forms. 
 
 * Op-Amps fully configurable to add data-sheet parameters as python function (open-loop gain and phase, voltage noise and current noise).
 
 * Multi-bonding allowed and interpreted as a solder-joint between components.
 

### Mechanical 
 * 1d bond modeling for transducers and resonances.

 * 3d bond modeling for suspensions with moments of inertia.

 * Mechanical loss appears automatically as Johnson noise terms.
 
 * Uses the "mobility analogy" to convert to electrical system, then uses scattering parameter form.

 * Multi-bonding allowed and interpreted as a rigid connection between points (solder-joint in mobility analogy)
 
### Signal
 * Mixers, RMS detectors included
 
 * Multi-bonding allowed for convenience, interpreted as distribution (unit-gain in or out).
 
### Mode Matching
 * bonus! Python code for paraxial approximation mode matching similar to the a-la-mode matlab code. Call it _Py a la mode_.
 
 * can use thin-lens approximation for quick quotes
 
 * Uses substrate types and radius of curvature for thick-lens computations. These often are different at the 1% level from vendor quotes!
 
 * Using substrates, index of refraction changes the focal length
 
 * Excellent plotter to know the beam profile across your layout.
 
 * Fitting is fast and can/(should) support parameter variations during the fits.
 
 * Can implement resonant mode systems to get the cavity eigenmode. Advanced: if done using substrate copies (see documentation for phasor.base.autograft), then parameter variation will affect event the cavity eigenmodes.

## Generation Stages

## Missing/Intended Features

 * DC/steady-state point lock solving. Only AC solutions currently found. Often simulation has infinite gain at DC in loops. This requires alternate solution strategy for convergence.
 
 * Saving input/output fields between computations for speed.

 * Optical Higher-Order-Modes at least HG01-HG10 angular modes for alignment sensing.

 * Scicos or Simulink graphical modeling import

## TODO
#### code
 * first fitting! needs just a few unit-tests
 
 * split outputs of mirrors for eventual modal computations
 * make the port algorithm split into in-out flows (more efficient for the above)
 
