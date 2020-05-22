import numpy as np
import math
import pyrosim
import pickle
import constants as c
from aggregate import AGGREGATE
import element
import population
import matplotlib.pyplot as plt

cubes = 5

f = open("data/hillclimber/max_fit/5WPFA/%dcube/run_111/saved_generations/gen200.p"%cubes,'rb')
gen = pickle.load(f)
f.close()
co = gen[0]

fit = 0
beste = None
for e in co.elmts.p:
    if e.fitness > fit:
        fit = e.fitness
        beste = e

fit = 0
besta = None
for a in co.aggrs.p:
    sim = pyrosim.Simulator(eval_steps=1000, dt=.01, play_blind=True, play_paused=False)
    f = a.evaluate(sim, beste)
    if f > fit:
        fit = f
        besta = a
        
sim1 = pyrosim.Simulator(eval_steps=1000, dt=.01, play_blind=False, play_paused=True, use_textures=False)
besta.evaluate(sim1, beste)
"""
colors = ["blue", "red", "green", "orange"]

cubes = 5

f = open("data/hillclimber/agnostic/5WPFA/%dcube/averagemax.p"%cubes,'rb')
agn = pickle.load(f)
f.close()

f = open("data/hillclimber/max_fit/5WPFA/%dcube/averagemax.p"%cubes,'rb')
max = pickle.load(f)
f.close()

x = np.arange(len(agn[0]))
plt.errorbar(x, agn[0], yerr=agn[1], errorevery=15, ecolor="grey", color=colors[0], label="agnostic")
plt.errorbar(x, max[0], yerr=max[1], errorevery=15, ecolor="black", color=colors[1], label="max-fitness")

plt.title("Comparison of Maximum Scores\n%d-cube"%cubes)
plt.legend()
plt.xlabel("Generation")
plt.ylabel("Average Displacement (Cube Lengths per Minute)")
plt.show()

#for cubes in range(2,6):
    
f = open("data/hillclimber/agnostic/1WP/%dcube/average.p"%cubes,'rb')
avg = pickle.load(f)
f.close()
x = np.arange(len(avg[0]))
plt.errorbar(x, avg[0], yerr=avg[1], errorevery=15, ecolor="grey", color=colors[0], label="1-weight")

f = open("data/hillclimber/agnostic/3WPF/%dcube/average.p"%cubes,'rb')
avg = pickle.load(f)
f.close()
x = np.arange(len(avg[0]))
plt.errorbar(x, avg[0], yerr=avg[1], errorevery=15, ecolor="black", color=colors[1], label="3-weight")

f = open("data/hillclimber/agnostic/5WPFA/%dcube/average.p"%cubes,'rb')
avg = pickle.load(f)
f.close()
x = np.arange(len(avg[0]))
plt.errorbar(x, avg[0], yerr=avg[1], errorevery=15, ecolor="black", color=colors[2], label="5-weight")

plt.title("Compared Controller Agnosticism\n%d-cube"%cubes)
plt.legend()
plt.xlabel("Generation")
plt.ylabel("Average Displacement (Cube Lengths per Minute)")
plt.show()

"""
