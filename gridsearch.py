from population import POPULATION, FIXEDAGGPOP
from aggregate import AGGREGATE
import element
import pyrosim
import constants as c

import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
import math

"""
This code takes a custom OneWeightPhaseOffset element designed to initialize at a set starting weight and initializes it at 20000 separate points evenly spaced along its genome's range. It then evaluates each of those elements against every aggregate of size num_cubes (line 17) and saves those performances before plotting them along with the performances from other aggregate sizes.
"""

num_cubes = 2

phases = np.linspace(-1,1, 20000)
elements = []
    
aggregates = FIXEDAGGPOP(AGGREGATE, num_cubes=num_cubes)
aggregates.initialize()
    
for phase in phases:
    elements.append(element.FixedWeightPhaseOffset(phase))
if not os.path.exists("./%dcube-gridsearch.p"%num_cubes):
    for e in range(len(elements)):
        print(e)
        fits = []
        elm = elements[e]
        for a in range(len(aggregates.p)):
            agg = aggregates.p[a]
            sim = pyrosim.Simulator(eval_steps=1000, play_blind=True, play_paused=False, dt=.01)
            fits.append(agg.evaluate(sim, elm, idNum=[a,e], debug=False))
        
        fits.sort()
        fpi = math.ceil(len(fits)*.05)
        fit = sum(fits[0:fpi])
        if (np.isnan(fit) or np.isinf(fit)):
            fit = 0
        elements[e].fitness = fit

    f = open("%dcube-gridsearch.p"%num_cubes, 'wb')
    pickle.dump(elements, f)
    f.close()


f = open("2cube-gridsearch.p", 'rb')
data2 = pickle.load(f)
f.close()
f = open("3cube-gridsearch.p", 'rb')
data3 = pickle.load(f)
f.close()

e2 = []
for e in data2:
    e.fitness/=(.01*1000/60)
    e.fitness/=c.SCALE
    e2.append(e.fitness)
e3 = []
for e in data3:
    e.fitness/=(.01*1000/60)
    e.fitness/=c.SCALE
    e3.append(e.fitness)

x = np.linspace(-1,1, len(data2))

plt.plot(x*math.pi, e2, label="2-Cube controller")
plt.plot(x*math.pi, e3, label="3-Cube controller")
plt.title("Fifth Percentile Speed of Fixed-Size Polycube Controllers By Phase Offset")
plt.xlabel("Phase Offset")
plt.ylabel("Speed (Cube Lengths per Minute)")
plt.legend()
plt.show()
