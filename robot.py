import numpy as np
import random
import math
import pyrosim
import constants as c
from aggregate import AGGREGATE

polybot = AGGREGATE(c.NUMCUBES)
print (polybot.polycube)

sim = pyrosim.Simulator( play_paused=True )

for coord in polybot.polycube:
    sim.send_box(x=coord[0]*c.SCALE, y=coord[1]*c.SCALE, z=(coord[2]+c.NUMCUBES/2)*c.SCALE, length=c.SCALE, width=c.SCALE, height=c.SCALE, r=random.random(), g=random.random(), b=random.random())

sim.start()

sim.wait_to_finish()
