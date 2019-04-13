import numpy as np
import random
import math
import pyrosim
from aggregate import AGGREGATE

polybot = AGGREGATE(10)
print (polybot.polycube)

sim = pyrosim.Simulator( play_paused=True )

sim.start()

