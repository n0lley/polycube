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
    best = fit

    return best

def coallate_best_fits(path, r=None):
    """
    Open up run r, return the highest fitnesses of each generation as a pair of lists
    """

    currGen = 1
    runNumber = "run_%s"
    coevolve = None
    
    tmp = try_load_generation(path + runNumber%(r) + "/saved_generations/" + fileName%currGen)
    
    if tmp is not None:
        elmtFit = find_best_fits(tmp)
        best = np.array([elmtFit])
    
    while tmp is not None:
        currGen += 1
        tmp = try_load_generation(path + runNumber%(r) + "/saved_generations/" + fileName%currGen)
        
        if tmp is not None:
            elmtFit = find_best_fits(tmp)
            best = np.append(best, [elmtFit], axis=0)
            time = tmp.DT * tmp.TIME_STEPS / 60

    return best, time

def evaluate_runs(path):
    evalBest = {}
    for run in os.listdir(path):
        if os.path.isdir(os.path.join(path, run)):
            tmp, time = coallate_best_fits(path+"/", run.split("_")[1])
            evalBest[int(run.split("_")[1])] = tmp

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

colors = [np.random.random(size=3), np.random.random(size=3), np.random.random(size=3)]
avs = {}

i=0
for eval in best:
    avs[eval] = np.empty((15, len(best[eval][111])))
    x = np.arange(len(best[eval][111]))
    ax.plot(x, best[eval][111]/c.SCALE/times[eval], alpha=.1, color=colors[i])
    avs[eval][0] = best[eval][111]

for i in range(112,126):
    
    q = 0
    for eval in best:
        x = np.arange(len(best[eval][i]))
        ax.plot(x, (best[eval][i]/c.SCALE)/times[eval], color=colors[q], alpha=.1)
        avs[eval][i-111] = best[eval][i]
        q += 1

i=0
for eval in best:
    avs[eval] = np.mean(avs[eval], axis=0)
    x = np.arange(len(avs[eval]))
    ax.plot(x, (avs[eval]/c.SCALE)/times[eval], color=colors[i], label=eval)
    i+=1

ax.set_ylabel("Displacement (cube lengths per minute)")
ax.set_xlabel("Generations")
ax.legend()
plt.show()

