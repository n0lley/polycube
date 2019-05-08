import numpy as np
import random
import math
import pyrosim
import constants as c
from aggregate import AGGREGATE
from element import ELEMENT

sensors = {0:0}
motors = {0:0,1:0}
controller = np.random.random((1, 12))

element = ELEMENT(sensors, motors, controller)
polybot = AGGREGATE(30)

sim = pyrosim.Simulator( play_paused=True )

polybot.send_to_sim(sim, [element])

sim.start()
sim.wait_to_finish()
