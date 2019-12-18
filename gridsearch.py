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

num_cubes = 3

phases = np.linspace(-1,1, 20000)
elements = []
    
aggregates = FIXEDAGGPOP(AGGREGATE, num_cubes=num_cubes)
aggregates.initialize()
    
for phase in phases:
    elements.append(element.FixedWeightPhaseOffset(phase))
if not os.path.exists("./%dcube-gridsearch.p"%num_cubes):
    for e in range(len(elements)):
        print(e)
        fit=0
        elm = elements[e]
        for a in range(len(aggregates.p)):
            agg = aggregates.p[a]
            sim = pyrosim.Simulator(eval_steps=1000, play_blind=True, play_paused=False, dt=.01)
            fit += agg.evaluate(sim, elm, idNum=[a,e], debug=False)
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
    e2.append((e.fitness/2 /(.01*1000/60))/c.SCALE)
e3 = []
for e in data3:
    e3.append((e.fitness/5 /(.01*1000/60))/c.SCALE)

x = np.linspace(-1,1, len(data2))

plt.plot(x*math.pi, e2, label="2-Cube controller")
plt.plot(x*math.pi, e3, label="3-Cube controller")
plt.title("Average Fitness of Fixed-Size Polycube Controllers By Phase Offset")
plt.xlabel("Phase Offset")
plt.ylabel("Average Speed (Cube Lengths per Minute)")
plt.legend()
plt.show()
