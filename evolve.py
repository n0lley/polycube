from coevolve import COEVOLVE
from population import POPULATION, FIXEDAGGPOP
from aggregate import AGGREGATE
from controller import CONTROLLER
import constants as c
import controller

from parallelpy import parallel_evaluate
import numpy as np
import pickle
import os
import sys
from copy import deepcopy

from time import time

parallel_evaluate.setup(parallel_evaluate.PARALLEL_MODE_MPI_INTER)

#Comment out whichever controller types are not in use
controllerTypes = [
    #controller.OneWeightPhaseOffset
    #controller.ThreeWeightPhaseOffsetFrequency
    controller.FiveWeightPhaseFrequencyAmplitude
    ]

N = c.POPSIZE
GENS = c.GENS
EVO_MODE = c.MODE

assert len(sys.argv) > 3, "Please run as python evolve.py <SEED> <NUM_CUBES> <NAME>"

try:
    seed = int(sys.argv[1])
    np.random.seed(seed)
    print("random seed set to", seed)
    
except:
    raise Exception("Please give a seed as an int.")
    
try:
    num_cubes = int(sys.argv[2])
    
except:
    raise Exception("Please give the polycube size as an int")
    

if EVO_MODE == 1:
    print("evolving for robustness")
else:
    print("evolving for maximum fitness")

def GetNewController():
    return np.random.choice(controllerTypes)
aggregates = FIXEDAGGPOP(AGGREGATE, num_cubes=num_cubes)
controllers = POPULATION(GetNewController(), pop_size=N, unique=True)

aggregates.initialize()
controllers.initialize()

coevolve = COEVOLVE(aggregates, controllers, EVO_MODE, seed)

latestGen = 1
if os.path.exists("./saved_generations/gen%d.p"%latestGen):
    while os.path.exists("./saved_generations/gen%d.p"%latestGen):
        print("Gen", latestGen, "exists")
        latestGen += 1

    f = open("./saved_generations/gen%d.p"%(latestGen-1), 'rb')
    saveState = pickle.load(f)
    coevolve = saveState[0]
    seed = saveState[1]
    np.random.set_state(seed)
    f.close()
    print("Beginning at Generation", latestGen-1)
else:
    print('GENERATION 0')
    t0 = time()
    coevolve.exhaustive()
    #coevolve.non_MPI_exhaustive()
    t1 = time()
    print("Simulation took: %.2f" % (t1 - t0))

    coevolve.print_fitness()

timetotal = time()

for g in range(latestGen, GENS+1):
    
    #create a parent population
    parent = deepcopy(coevolve.contrs)
    
    #reset children's fitness values
    coevolve.reset()
    #mutate child population
    for i in range(len(coevolve.contrs.p)):
        coevolve.contrs.p[i].mutate()
    
    #evaluation
    t0 = time()
    coevolve.exhaustive()
    #coevolve.non_MPI_exhaustive()
    t1 = time()
    
    #Simple hillclimber selection
    coevolve.contrs.hillclimber_selection(parent)
    
    #report fitness values
    print('GENERATION %d' % g)
    print("Simulation took: %.2f"%(t1-t0))
    coevolve.print_fitness()

    try:
        if not os.path.exists('./saved_generations/'):
            os.makedirs('./saved_generations/')
        fileName = './saved_generations/gen'
        f = open(fileName + format(g) + '.p', 'wb')
        saveState = {}
        saveState[0] = coevolve
        saveState[1] = np.random.get_state()
        pickle.dump(saveState, f)
        f.close()
    
    except:
        print ("Error saving generation", g, "to file.")

print("total runtime:", time()-timetotal)

parallel_evaluate.cleanup()
