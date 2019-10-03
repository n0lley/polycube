import numpy as np
import math
import pyrosim
import constants as c
from aggregate import AGGREGATE
from element import ELEMENT, UniversalHingeJointCPGChildBasedElement

#np.random.seed(0)

element = UniversalHingeJointCPGChildBasedElement()

polybot = AGGREGATE()

sim = pyrosim.Simulator(eval_steps = 1000, play_blind=False, play_paused=True, dt=.01)

fit = polybot.evaluate(sim, element, debug=True)

print(fit)

#print(sim.get_debug_output())
