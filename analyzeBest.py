from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT
import constants as c
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
    for j in coevolve.elmts.p:
        if j.fitness > fit:
            fit = j.fitness
            print(j.scores)
    best = fit

    return best

def coallate_best_fits(path, r=None):
    """
    Open up run r, return the highest fitnesses of each generation as a pair of lists
    """
    print(path)

    currGen = 1
    runNumber = "run_%s"
    coevolve = None
    tmp = try_load_generation(path + "/saved_generations/" + fileName%currGen)
    
    if tmp is not None:
        elmtFit = find_best_fits(tmp[0])
        best = np.array([elmtFit])
    
    while tmp is not None:
        currGen += 1
        tmp = try_load_generation(path + "/saved_generations/" + fileName%currGen)
        if tmp is not None:
            elmtFit = find_best_fits(tmp[0])
            best = np.append(best, [elmtFit], axis=0)
            time = tmp[0].DT * tmp[0].TIME_STEPS / 60

    return best, time

def evaluate_runs(path):
    evalBest = {}
    tmp, time = coallate_best_fits(path)
    evalBest[111] = tmp

    return evalBest, time

def analyze_data(path):
    
    best = {}
    times = {}
    
    for eval in os.listdir(path):
        if os.path.isdir(os.path.join(path, eval)):
            tmp, time = evaluate_runs(path + "/" + eval)
            best[eval] = tmp
            times[eval] = time

    return best, times

#System input should give the directory storing the run folders. Provided they're organized in the same manner as previous runs, it should work from there.
assert len(sys.argv) > 1, "Please run as python playback.py <path/to/saved_runs/>"
datapath = sys.argv[1]
fileName = "gen%d.p"
currGen = 1
coevolve = None

best, times = analyze_data(datapath)

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
plt.title("Fitness of Controllers for Fixed-Size Polycubes")

colors = ["red", "blue", "green", "purple"]

i=0
for eval in best:
    print(eval)
    x = np.arange(len(best[eval][111]))
    print(best[eval][111][-1])
    best[eval][111]/=times[eval]
    print(best[eval][111][-1])
    best[eval][111]/=c.SCALE
    print(best[eval][111][-1])
    ax.plot(x, best[eval][111], color=colors[i], label=eval)
    i += 1

ax.set_ylabel("Displacement (cube lengths per minute)")
ax.set_xlabel("Generations")
ax.legend()
plt.show()
