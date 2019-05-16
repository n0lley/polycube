import numpy as np
import random
import math
import pyrosim
import constants as c
from aggregate import AGGREGATE
from element import ELEMENT, TouchSensorHingeJointElement

controller = np.random.random((1, 2))

element = TouchSensorHingeJointElement(controller)
polybot = AGGREGATE(30)

sim = pyrosim.Simulator( play_paused=True, eval_time = 300 )

polybot.send_to_sim(sim, element)

sim.start()
sim.wait_to_finish()
