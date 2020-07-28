from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from controller import CONTROLLER
import constants as c
import math
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
    
def find_best_avg(coevolve):
    """
    find the fitnesses of the most fit aggregate and controller in a population
    """
    fit = 0
    beste = None
    for j in coevolve.elmts.p:
        if j.fitness > fit:
            fit = j.fitness
            beste = j
            
    avg = sum(beste.scores)/len(beste.scores)

    return avg
    
def find_best_score(coevolve):
    """
    find the fitnesses of the most fit aggregate and controller in a population
    """
    fit = 0
    bestc = None
    for j in coevolve.contrs.p:
        if j.fitness > fit:
            fit = j.fitness
            bestc = j
            
    bestc.scores.sort()
    high = bestc.scores[-1]

    return high

def find_best_agn(coevolve):
    """
    find the fitnesses of the most fit aggregate and controller in a population
    """
    fit = 0
    bestc = None
    for j in coevolve.contrs.p:
        if j.fitness > fit:
            fit = j.fitness
            bestc = j
            
    fpi = math.ceil(len(bestc.scores)*.05)
    bestc.scores.sort()
    fpi_avg = sum(bestc.scores[0:fpi])
    fpi_avg/=fpi

    return fpi_avg

def coallate_best_fits(path, r=None):
    """
    Open up run r, return the highest fitnesses of each generation as a pair of lists
    """
    #print(path)

    currGen = 1
    runNumber = "run_%s"
    coevolve = None
    tmp = try_load_generation(path + "/saved_generations/" + fileName%currGen)
    #print (path + "/saved_generations/" + fileName%currGen)
    x = find_best_agn(tmp[0])
    #x = find_best_avg(tmp[0])
    #x = find_best_score(tmp[0])
    best = np.array([x])
    
    while tmp is not None:
        currGen += 1
        tmp = try_load_generation(path + "/saved_generations/" + fileName%currGen)
        if tmp is not None:
            x = find_best_agn(tmp[0])
            #x = find_best_avg(tmp[0])
            #x = find_best_score(tmp[0])
            best = np.append(best, [x], axis=0)
            time = tmp[0].DT * tmp[0].TIME_STEPS / 60

    return best, time

def evaluate_runs(path):
    evalBest = []
    tmp, time = coallate_best_fits(path)
    evalBest = tmp

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
plt.title("Controller Agnosticism in Polycubes Size n = 5\n Agnostic (More Data Pending)")

colors = ["red", "blue", "green", "purple", "black"]

i=0
for eval in best:
    x = np.arange(len(best[eval]))
    best[eval] = best[eval]/times[eval]
    best[eval] = best[eval]/c.SCALE
    if i==0:
        tmpeval = eval
        ax.plot(x, best[eval], color=colors[1], alpha=.4, label="Individual Run Fitnesses")
    else:
        ax.plot(x, best[eval], color=colors[1], alpha=.4)
    i += 1
    avgs = [0]*len(x)
    err = [0]*len(x)
    
for eval in best:
    for j in range(len(best[eval])):
        avgs[j] += best[eval][j]

for j in range(len(avgs)):
    avgs[j] = avgs[j]/i

for j in range(len(avgs)):
    tmperr = 0
    for eval in best:
        tmp = best[eval][j] - avgs[j]
        tmperr += tmp**2
    tmperr /= (i - 1)
    err[j] = tmperr**.5


f = open(datapath+"/average.p",'wb')
pickle.dump((avgs, err), f)
f.close()

ax.errorbar(x, avgs, yerr=err, color=colors[0], ecolor="black", label="Average Fitness", errorevery=15)

ax.set_ylabel("Displacement (cube lengths per minute)")
ax.set_xlabel("Generation")
ax.legend()
plt.show()
