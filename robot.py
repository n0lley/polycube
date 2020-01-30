import numpy as np
import math
import pyrosim
import pickle
import constants as c
from aggregate import AGGREGATE
import element
import population

f = open("data/hillclimber/5WPFA/3cube/saved_generations/gen200.p",'rb')
g = pickle.load(f)
f.close()
co = g[0]

fit = 0
beste = None
for e in co.elmts.p:
    if e.fitness > fit:
        beste = e
        fit = e.fitness
        
print(beste.scores)
