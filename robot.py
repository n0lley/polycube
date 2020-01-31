import numpy as np
import math
import pyrosim
import pickle
import constants as c
from aggregate import AGGREGATE
import element
import population

np.random.seed(111)

f = open("data/afpo/5WPFA/2cube/saved_generations/gen200.p", 'rb')
gen = pickle.load(f)
f.close()
co = gen[0]

fit = 0
beste = None
for e in co.elmts.p:
    if e.fitness > fit:
        fit = e.fitness
        beste = e
        
scores = []
for a in co.aggrs.p:
    sim = pyrosim.Simulator(eval_steps = 1000, play_blind=True, play_paused=False, dt=.01)
    scores.append(a.evaluate(sim, beste, [0,0]))
    print(len(scores))
    
scores.sort()
fpi = math.ceil(len(scores)*.05)
print(scores[0:fpi])
print(beste.scores[0:fpi])
