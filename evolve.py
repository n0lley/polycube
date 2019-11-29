from coevolve import COEVOLVE
from population import POPULATION, FIXEDAGGPOP
from aggregate import AGGREGATE
from element import ELEMENT
import constants as c
import element

from parallelpy import parallel_evaluate
import numpy as np
import pickle
import os
import sys

from time import time

#Comment out whichever element types are not in use
elementTypes = [
    element.OneWeightPhaseOffset,
    #element.TwoWeightAmplitude,
    #element.FourWeightPhaseOffsetAmplitude,
    ]

N = c.POPSIZE
GENS = c.GENS

assert len(sys.argv) > 3, "Please run as python evolve.py <SEED> <NUM_CUBES> <NAME>"

try:
    seed = int(sys.argv[1])
    np.random.seed(seed)
    
except:
    raise Exception("Please give a seed as an int.")
    
parallel_evaluate.setup(parallel_evaluate.PARALLEL_MODE_MPI_INTER)

def GetNewElement():
    return np.random.choice(elementTypes)
aggregates = FIXEDAGGPOP(AGGREGATE, num_cubes=num_cubes)
elements = POPULATION(GetNewElement(), pop_size=N, unique=True)

aggregates.initialize()
elements.initialize()

coevolve = COEVOLVE(aggregates, elements)

latestGen = 1
print(os.path.exists("./saved_generations/gen%d.p"%latestGen))
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
    print('GENERATION %d' % 0)
    t0 = time()
    coevolve.exhaustive()
    t1 = time()
    print("Simulation took: %.2f" % (t1 - t0))

    coevolve.print_fitness()


    
for g in range(latestGen, GENS+1):
    
    #selection and mutation
    coevolve.selection()

    #resets all fitness values
    coevolve.reset()

    t0 = time()
    #evaluation
    coevolve.exhaustive()
    t1 = time()
    print('GENERATION %d' % g)
    print("Simulation took: %.2f"%(t1-t0))
    
    #report fitness values
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

parallel_evaluate.cleanup()
