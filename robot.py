import numpy as np
import random
import math
import pyrosim
import constants as c
from aggregate import AGGREGATE

polybot = AGGREGATE(50)
print (polybot.polycube)

sim = pyrosim.Simulator( play_paused=True )

lowest = 0
for coord in polybot.polycube:
    if(coord[2] < lowest):
        lowest = coord[2]

cubes = {}

for coord in polybot.polycube:
    cubes[coord] = sim.send_box(
                 x=coord[0]*c.SCALE, y=coord[1]*c.SCALE, z=(coord[2] - lowest + .5)*c.SCALE,
                 length=c.SCALE, width=c.SCALE, height=c.SCALE,
                 r=random.random(), g=random.random(), b=random.random()
                 )

joints = {}
j=0
for coord in polybot.polycube:
    for neighbor in polybot.polycube[coord]:
        xloc = (coord[0] - neighbor[0])/2
        yloc = (coord[1] - neighbor[1])/2
        zloc = (coord[2] - neighbor[2])/2
        joints[j] = sim.send_hinge_joint(
                    first_body_id = cubes[coord], second_body_id = cubes[neighbor],
                    x=xloc*c.SCALE, y=yloc*c.SCALE, z=zloc*c.SCALE,
                    n1=0, n2=0, n3=1,
                    lo=-.0001, hi=.0001
    )

sim.start()

sim.wait_to_finish()
