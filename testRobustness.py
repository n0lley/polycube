from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT
from element import TouchSensorUniversalHingeJointCPGElement
import pyrosim
import pickle
import sys
import matplotlib.pyplot as plt
import numpy as np
from time import time

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
    find the fitnesses of the most fit aggregate in a population
    """
    fit = 0
    agg = None
    for j in coevolve.aggrs.p:
        if j.fitness > fit:
            fit = j.fitness
            agg = j

    return agg

def test_robustness(inds, tests, coevolve=None, agg=None):
    
    fits = np.empty((inds, tests))
    
    for i in range(0, tests):
        e = TouchSensorUniversalHingeJointCPGElement()
        start = time()
        
        for j in range(inds):
            sim = pyrosim.Simulator(eval_steps=2000, play_blind=True, play_paused=False, dt=.01)
            if coevolve is not None:
                fits[j][i] = coevolve.aggrs.p[j].evaluate(sim, e, debug=False)
            
            elif agg is not None:
                fits[j][i] = agg.evaluate(sim, e, debug=False)
            else:
                print("Error: no evaluation target")
                break
        print("Iteration %d, Time taken: "%i + format((time()-start), '.0f'))
    
    return fits

def whole_pop(path, gen1, gen2, newData):
    coevolve1 = try_load_generation(path%gen1)
    print("Generation", gen1, "loaded...")
    coevolve2 = try_load_generation(path%gen2)
    print("Generation", gen2, "loaded...")

    if newData:
        print("Creating new robustness data...")
        
        print("Testing Gen %s"%gen1)
        gen1fits = test_robustness(15, 100, coevolve = coevolve1)
        
        print("Testing Gen %s"%gen2)
        gen2fits = test_robustness(15, 100, coevolve = coevolve2)
        
        print("Saving data")
        f1 = open("robustness_data/gen1.p", 'wb')
        f2 = open("robustness_data/gen2.p", 'wb')
        pickle.dump(gen1fits, f1)
        pickle.dump(gen2fits, f2)
        f1.close()
        f2.close()

    else:
        print("Loading data")
        f1 = open("robustness_data/gen1.p", 'rb')
        gen1fits = pickle.load(f1)
        f1.close()
        
        f2 = open("robustness_data/gen2.p", 'rb')
        gen2fits = pickle.load(f2)
        f2.close()

    return gen1fits, gen2fits

def use_best(path, gen1, gen2, newData):

    coevolve1 = try_load_generation(path%gen1)
    gen1Best = find_best_agg(coevolve1)
    print("Generation", gen1, "individual loaded...")
    coevolve2 = try_load_generation(path%gen2)
    gen2Best = find_best_agg(coevolve2)
    print("Generation", gen2, "individual loaded...")
    
    if newData:
        print("Testing Gen %s"%gen1)
        gen1fits = test_robustness(1, 500, agg = gen1Best)
        print("Testing Gen %s"%gen2)
        gen2fits = test_robustness(1, 500, agg = gen2Best)
        print("Saving Data")
        f1 = open("robustness_data/gen1Best.p", 'wb')
        f2 = open("robustness_data/gen2Best.p", 'wb')
        pickle.dump(gen1fits, f1)
        pickle.dump(gen2fits, f2)
        f1.close()
        f2.close()
    
    else:
        print("Loading Data")
        f1 = open("robustness_data/gen1Best.p", 'rb')
        gen1fits = pickle.load(f1)
        f1.close()
        
        f2 = open("robustness_data/gen2Best.p", 'rb')
        gen2fits = pickle.load(f2)
        f2.close()

    return gen1fits, gen2fits

#System input should give the directory path to the run, and the generations being compared
assert len(sys.argv) > 5, "Please run as python playback.py <path/to/saved_runs/>, <firstGeneration>, <secondGeneration>, <usingOnlyBest>, <usingNewData>"

pathToSavedGens = sys.argv[1]
if pathToSavedGens[-1] is not "/":
    pathToSavedGens += "/"
gen1 = sys.argv[2]
gen2 = sys.argv[3]
best = sys.argv[4] == "True"
newData = sys.argv[5] == "True"
pathToSavedGens += "gen%s.p"
currGen = 1
coevolve1 = None
coevolve2 = None

if best:
    print("Loading best aggregates...")
    gen1fits, gen2fits = use_best(pathToSavedGens, gen1, gen2, newData)

    gen1fits = gen1fits[0]
    gen2fits = gen2fits[0]

else:
    print("Loading all aggregates...")
    gen1fits, gen2fits = whole_pop(pathToSavedGens, gen1, gen2, newData)

    gen1fits = np.mean(gen1fits, axis=1)
    gen2fits = np.mean(gen2fits, axis=1)

plt.hist(x=(gen1fits, gen2fits), color=([.7,.3,.4],[.3,.7,.4]), label=("Generation "+gen1, "Generation "+gen2))

plt.ylabel("Frequency")
plt.xlabel("Fitnesses")

plt.legend()
plt.show()

