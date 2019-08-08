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

elementTypes = [TouchSensorUniversalHingeJointCPGElement]


EXHAUSTIVE_EVALUATION_MODE = 0
RANDOM_SUBSET_EVALUATION_MODE = 1
HYBRID_EVALUATION_MODE = 2

N = 50
GENS = 500
EVALUATION_MODE = EXHAUSTIVE_EVALUATION_MODE # Default

assert len(sys.argv) > 2, "Please run as python evolve.py <SEED> <NAME>"
try:
    seed = int(sys.argv[1])
    np.random.seed(seed)
    random.seed(seed)
except:
    raise Exception("Please give a seed as an int.")



# how to give fitness to individuals?
if "RAND_EVAL" in sys.argv[2]:
    EVALUATION_MODE = RANDOM_SUBSET_EVALUATION_MODE
    N = 30
elif "EXHAUSTIVE_EVAL" in sys.argv[2]:
    EVALUATION_MODE = EXHAUSTIVE_EVALUATION_MODE
elif "HYBRID_EVAL" in sys.argv[2]:
    EVALUATION_MODE = HYBRID_EVALUATION_MODE


parallel_evaluate.setup(parallel_evaluate.PARALLEL_MODE_MPI_INTER)

def GetNewElement():
    return random.choice(elementTypes)()
aggregates = POPULATION(AGGREGATE, pop_size=N, unique=True)
elements = POPULATION(GetNewElement, pop_size=N, unique=True)

aggregates.initialize()
elements.initialize()

# what evolution mode are we running in?
if "COOPERATIVE" in sys.argv[2]:
    coevolve = COEVOLVE(aggregates, elements, evolution_mode=COEVOLVE.COOPERATIVE_MODE)
    print("Evolving in Cooperative Mode.")

elif "COMPETITIVE" in sys.argv[2]:
    coevolve = COEVOLVE(aggregates, elements, evolution_mode=COEVOLVE.COMPETITIVE_MODE)
    print("Evolving in Competative Mode.")

else:
    coevolve = COEVOLVE(aggregates, elements)
    print("Evolution mode not understood. Using default.")

latestGen = 1
print(os.path.exists("./saved_generations/gen%d.p"%latestGen))
if os.path.exists("./saved_generations/gen%d.p"%latestGen):
    while os.path.exists("./saved_generations/gen%d.p"%latestGen):
        print("Gen", latestGen, "exists")
        latestGen += 1

    f = open("./saved_generations/gen%d.p"%(latestGen-1), 'rb')
    coevolve = pickle.load(f)
    f.close()
    print("Beginning at Generation", latestGen-1)

else:
    print('GENERATION %d' % 0)
    t0 = time()
    if EVALUATION_MODE == EXHAUSTIVE_EVALUATION_MODE:
        coevolve.exhaustive()
    elif EVALUATION_MODE == RANDOM_SUBSET_EVALUATION_MODE:
        coevolve.random_subset()
    elif EVALUATION_MODE == HYBRID_EVALUATION_MODE:
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
    if EVALUATION_MODE  == EXHAUSTIVE_EVALUATION_MODE:
        coevolve.exhaustive()
    elif EVALUATION_MODE == RANDOM_SUBSET_EVALUATION_MODE:
        coevolve.random_subset()
    elif EVALUATION_MODE == HYBRID_EVALUATION_MODE:
        if (g%10 == 0):
            coevolve.exhaustive()
        else:
            coevolve.random_subset()
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
