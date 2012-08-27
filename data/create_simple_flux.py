import numpy as np

import time
import math
import sys

def frange(startValue, endValue, steps):
    incrementValue = (float(endValue) - startValue) / steps
    for i in range(steps):
        yield float(startValue) + i*incrementValue

polarization = 0.0
pi = 3.1415
parent_energy = 3.8 # GeV 

E_min = 0.10  # GeV
E_max = 5.0
E_steps = 500

mass_muon = 0.1056 # GeV

stored_muons = 1e17

theta = 0

distance = 1 # km, GLoBES normalization

flux_file_e = open('flux_file_e.dat', 'w') # electron
flux_file_mu = open('flux_file_m.dat', 'w') # muon
flux_file_flat = open('flux_file_f.dat', 'w') # flat

for E in frange (E_min, E_max, E_steps):
    cos_theta = 1
    y = float(E) / parent_energy
    beta = math.sqrt(1 - mass_muon**2 / parent_energy**2)

    N = stored_muons
    N /= pi * distance**2 * mass_muon**6
    N *= parent_energy**4 * y**2 * (1 - beta * math.cos(theta))

    flux_mu = 4 * N * (3 * mass_muon**2 - 4 * parent_energy**2 * y * (1 - beta * math.cos(theta)))
    flux_e = 24 * N * (1 * mass_muon**2 - 2 * parent_energy**2 * y * (1 - beta * math.cos(theta)))
    
    
    flux_e  *= (2*pi) / parent_energy  # solid angle -> cos(theta), y -> E
    flux_mu *= (2*pi) / parent_energy  # solid angle -> cos(theta), y -> E  

    if E > parent_energy:
        flux_e = 0.0
        flux_mu = 0.0

    flux_file_e.write('%0.9g %0.9g\n' % (E, flux_e))
    flux_file_mu.write('%0.9g %0.9g\n' % (E, flux_mu))
    flux_file_flat.write('%0.9g %0.9g\n' % (E, 1.0))


flux_file_e.close()
flux_file_mu.close()
flux_file_flat.close()

