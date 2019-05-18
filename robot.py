import numpy as np
import random
import math
import pyrosim
import constants as c
from aggregate import AGGREGATE
from element import ELEMENT, TouchSensorUniversalHingeJointElement

controller = np.random.random((1, 2))

element = TouchSensorUniversalHingeJointElement(controller)
polybot = AGGREGATE(2)

sim = pyrosim.Simulator(eval_steps=500, dt = .01, play_paused=True, draw_joints=True)

polybot.send_to_sim(sim, element)

sim.start()
sim.wait_to_finish()
