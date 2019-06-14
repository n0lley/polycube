import numpy as np
import pyrosim
import pickle
import os
import sys
import matplotlib.pyplot as plt

from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT

def try_load_generation(fileName):
    try:
        f=open(fileName, 'rb')
        coevolve = pickle.load(f)
        f.close()
        return coevolve
    except:
        return None

def find_best_fits(coevolve):
    fit = 0
    for j in coevolve.aggrs.p:
        if coevolve.aggrs.p[j].fitness > fit:
            fit = coevolve.aggrs.p[j].fitness
    bestAggt = fit
    fit = 0
    for j in coevolve.elmts.p:
        if coevolve.elmts.p[j].fitness > fit:
            fit = coevolve.elmts.p[j].fitness
    bestElmt = fit

    return bestAggt, bestElmt

assert len(sys.argv) > 1, "Please run as python analyzeBest.py <path/to/saved_gens/>"
pathToSavedGens = sys.argv[1]
if pathToSavedGens[-1] != "/":
    pathToSavedGens += "/"
fileName = "gen%d.p"
currGen = 1
coevolve = None
tmp = try_load_generation(pathToSavedGens+fileName%currGen)

aggtBest = []
elmtBest = []

aggFit, elmtFit = find_best_fits(tmp)

aggtBest.append(aggFit)
elmtBest.append(elmtFit)

while tmp is not None:
    currGen += 1
    tmp = try_load_generation(pathToSavedGens+fileName%currGen)
    if tmp is not None:
        aggFit, elmtFit = find_best_fits(tmp)

        aggtBest.append(aggFit)
        elmtBest.append(elmtFit)

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
for i in range(0, currGen-1):
    ax.scatter(i, aggtBest[i], color=[.3, .7, .4])
    ax.scatter(i, elmtBest[i], color=[.7, .3, .4])

plt.show()
