import numpy as np
import math
import pyrosim
import pickle
import constants as c
from aggregate import AGGREGATE
import element
import population

#np.random.seed(0)

elements = population.POPULATION(element.OneWeightPhaseOffset)

apop = population.FIXEDAGGPOP(AGGREGATE, 3)
apop.initialize()
elements.initialize()

sim = pyrosim.Simulator(eval_steps = 1000, play_blind=True, play_paused=False, dt=.01)

f = open("data/3cube/saved_generations/gen200.p", 'rb')
gen = pickle.load(f)
f.close()
co = gen[0]
co.non_MPI_exhaustive()

#print(sim.get_debug_output())
