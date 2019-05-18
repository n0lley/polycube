import numpy as np
import math
import pyrosim
import constants as c
from aggregate import AGGREGATE
from element import ELEMENT, TouchSensorUniversalHingeJointElement

np.random.seed(0)
controller = np.random.random((1, 2))

element = TouchSensorUniversalHingeJointElement(controller)
polybot = AGGREGATE(5)

sim = pyrosim.Simulator(eval_steps = 500, play_paused=True, dt=.01)

polybot.send_to_sim(sim, element)

sim.start()
sim.wait_to_finish()
print(sim.get_debug_output())
