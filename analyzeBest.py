from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT
import pickle
import os
import sys
import matplotlib.pyplot as plt
import numpy as np

def try_load_generation(fileName, debug=False):
    try:
        f = open(fileName, 'rb')
        coevolve = pickle.load(f)
        f.close()
        if debug: print(fileName)
        return coevolve
    except Exception as e:
        if debug:
            print(e)
        return None

def GetNewElement():
    raise NotImplementedError

def find_best_fits(coevolve):
    """
    find the fitnesses of the most fit aggregate and element in a population
    """
    fit = 0
    for j in coevolve.aggrs.p:
        if j.fitness > fit:
            fit = j.fitness
    bestAggt = fit
    fit = 0
    for j in coevolve.elmts.p:
        if j.fitness > fit:
            fit = j.fitness
    bestElmt = fit

    return bestAggt, bestElmt

def coallate_best_fits(r=''):
    """
    Open up run r, return the highest fitnesses of each generation as a pair of lists
    """

    currGen = 1
    runNumber = "run_%d"
    coevolve = None
    
    tmp = try_load_generation(pathToSavedGens + runNumber%(r) + "/saved_generations/" + fileName%currGen)
    
    aggtBest = []
    elmtBest = []
    
    if tmp is not None:
        aggFit, elmtFit = find_best_fits(tmp)
    
        aggtBest.append(aggFit)
        elmtBest.append(elmtFit)
    
    while tmp is not None:
        currGen += 1
        tmp = try_load_generation(pathToSavedGens + runNumber%(r) + "/saved_generations/" + fileName%currGen)
        
        if tmp is not None:
            
            aggFit, elmtFit = find_best_fits(tmp)
            
            aggtBest.append(aggFit)
            elmtBest.append(elmtFit)

    return aggtBest, elmtBest

#System input should give the directory storing the run folders. Provided they're organized in the same manner as previous runs, it should work from there.
assert len(sys.argv) > 1, "Please run as python playback.py <path/to/saved_runs/>"
pathToSavedGens = sys.argv[1]
fileName = "gen%d.p"
currGen = 1
coevolve = None

aggtBest, elmtBest = coallate_best_fits(1)

fig = plt.figure()
x = np.arange(len(aggtBest))
ax = fig.add_subplot(1,1,1)
ax.plot(x, aggtBest, color=[.3, .7, .4], label = "Aggregates")
ax.plot(x, elmtBest, color=[.7, .3, .4], label = "Elements")

for i in range(2,11):
    
    agg, elm = coallate_best_fits(i)
    x = np.arange(len(agg))
    ax.plot(x, agg, color=[.3, .7, .4])
    ax.plot(x, elm, color=[.7, .3, .4])

ax.legend()
plt.show()

