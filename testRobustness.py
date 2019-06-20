from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT
from element import TouchSensorUniversalHingeJointCPGElement
import constants as c
import pyrosim
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

def find_best_agg(coevolve):
    """
    find the fitnesses of the most fit aggregate and element in a population
    """
    fit = 0
    agg = None
    for j in coevolve.aggrs.p:
        if j.fitness > fit:
            fit = j.fitness
            agg = j

    return agg

def test_robustness(coevolve):
    
    fits = np.empty((15, 100))
    
    for i in range(0, 100):
        e = TouchSensorUniversalHingeJointCPGElement()
    
        for j in range(len(coevolve.aggrs.p)):
            sim = pyrosim.Simulator(eval_steps=2000, play_blind=True, play_paused=False, dt=.01)
            fit = coevolve.aggrs.p[j].evaluate(sim, e, debug=False)
            fits[j][i] = fit
    
    return fits

#System input should give the directory path to the run, and the generations being compared
assert len(sys.argv) > 4, "Please run as python playback.py <path/to/saved_runs/>, <firstGeneration>, <secondGeneration>"
pathToSavedGens = sys.argv[1]
if pathToSavedGens[-1] is not "/":
    pathToSavedGens += "/"
gen1 = sys.argv[2]
gen2 = sys.argv[3]
newData = "True" == sys.argv[4]
fileName = "gen%s.p"
currGen = 1
coevolve1 = None
coevolve2 = None

coevolve1 = try_load_generation(pathToSavedGens + fileName%gen1)
print("Generation", gen1, "loaded...")
coevolve2 = try_load_generation(pathToSavedGens + fileName%gen2)
print("Generation", gen2, "loaded...")

if newData:
    print("Creating new robustness data...")
    print("Testing generation", gen1)
    gen1fits = test_robustness(coevolve1)

    print("Testing generation", gen2)
    gen2fits = test_robustness(coevolve2)

    path = "robustness_data"
    f1 = open(path + "gen1.p", 'wb')
    pickle.dump(f1, gen1fits)
    f1.close()

    f2 = open(path + "gen2.p", 'wb')
    pickle.dump(f2, gen2fits)
    f2.close()

else:
    f1 = open("robustness_data/gen1.p", 'rb')
    gen1fits = pickle.load(f1)
    f1.close()

    f2 = open("robustness_data/gen2.p", 'rb')
    gen2fits = pickle.load(f2)
    f2.close()

gen1fits = np.mean(gen1fits, axis=1)
gen2fits = np.mean(gen2fits, axis=1)

fig = plt.figure()
ax = fig.add_subplot(1,1,1)

ax.scatterplot(np.arange(15), gen1fits, color = [.7, .3, .4], label = "Generation "+gen1)
ax.scatterplot(np.arange(15), gen2fits, color = [.3, .7, .4], label = "Generation "+gen2)

ax.set_ylabel("Average fitness over 100 elements")
ax.legend()
plt.show()
