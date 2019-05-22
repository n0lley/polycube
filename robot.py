import numpy as np
import math
import pyrosim
import constants as c
from aggregate import AGGREGATE
from element import ELEMENT, TouchSensorUniversalHingeJointElement,                    TouchAndLightSensorYAxisHingeJointElement,                    TouchAndLightSensorXAxisHingeJointElement

#np.random.seed(0)
controller = np.random.random((2, 2))

element = TouchAndLightSensorXAxisHingeJointElement(controller)
polybot = AGGREGATE(25)

sim = pyrosim.Simulator(eval_steps = 1000, play_paused=True, dt=.01)

polybot.send_to_sim(sim, element)

sim.start()
sim.wait_to_finish()
#print(sim.get_debug_output())
