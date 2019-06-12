from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT
from element import TouchSensorUniversalHingeJointElement
from element import TouchAndLightSensorYAxisHingeJointElement
from element import TouchAndLightSensorXAxisHingeJointElement
from element import TouchSensorUniversalHingeJointCPGElement

from parallelpy import parallel_evaluate
import numpy as np
import random
import pickle
import os
import sys

from time import time

elementTypes = [TouchSensorUniversalHingeJointElement,
                TouchAndLightSensorYAxisHingeJointElement,
                TouchAndLightSensorXAxisHingeJointElement,
                TouchSensorUniversalHingeJointCPGElement]

N = 10
GENS = 100

assert len(sys.argv) > 1, "Please run as python evolve.py <SEED>"
try:
    seed = int(sys.argv[1])
    np.random.seed(seed)
    random.seed(seed)
except:
    raise Exception("Please give a seed as an int.")

parallel_evaluate.setup(parallel_evaluate.PARALLEL_MODE_MPI_INTER)

aggregates = POPULATION(AGGREGATE, pop_size=N, unique=True)
elements = POPULATION(ELEMENT, pop_size=N, unique=True)

aggregates.initialize()
elements.initialize()

for i in range(N):
    elements.p[i] = elementTypes[i%len(elementTypes)]()
    
coevolve = COEVOLVE(aggregates, elements)

print('GENERATION %d' % 0)
t0 = time()
coevolve.exhaustive()
t1 = time()
print("Simulation took: %.2f" % (t1 - t0))

coevolve.print_fitness()

for g in range(1, GENS+1):
    
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
        pickle.dump(coevolve, f)
        f.close()
        
    except:
        print ("Error saving generation", g, "to file.")

parallel_evaluate.cleanup()