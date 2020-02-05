import numpy as np
import math
import pyrosim
import pickle
import constants as c
from aggregate import AGGREGATE
import element
import population

np.random.seed(111)

parallel_evaluate.setup(parallel_evaluate.PARALLEL_MODE_MPI_INTER)

f = open("saved_generations/gen200.p", 'rb')
gen = pickle.load(f)
f.close()
co = gen[0]

co.elmts.Print()

co.reset()

co.exhaustive()

co.elmts.Print()

parallel_evaluate.cleanup()
