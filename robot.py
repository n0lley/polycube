import numpy as np
import random
import math
import pyrosim
import constants as c
from aggregate import AGGREGATE
from element import ELEMENT

sim = pyrosim.Simulator( play_paused=True )

sensors = {}
motors = {}
controller = np.random.random((1, 12))

element = ELEMENT(sensors, motors, controller)
polybot = AGGREGATE(30)
polybot.send_to_sim(sim, [element])

sim.start()
sim.wait_to_finish()
