import numpy as np
import math
import pyrosim
import pickle
import constants as c
from aggregate import AGGREGATE
import element
import population

np.random.seed(111)

f = open("saved_generations/gen200.p", 'rb')
gen = pickle.load(f)
f.close()
co = gen[0]

co.elmts.Print()

co.reset()

co.exhaustive()

co.elmts.Print()
