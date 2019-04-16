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

element = ELEMENT(sensors, motors)
polybot = AGGREGATE(sim, [element], 15)
print (polybot.tree)

sim.start()
sim.wait_to_finish()
"""
joints1 = {}
joints2 = {}
joints3 = {}
for coord in polybot.polycube:
    for neighbor in polybot.polycube[coord]:
        joints1[coord] = {}
        joints2[coord] = {}
        joints3[coord] = {}
        xdif = (coord[0] - neighbor[0])/2
        ydif = (coord[1] - neighbor[1])/2
        zdif = (coord[2] - neighbor[2])/2
        
        if(xdif == 0):
            joints1[coord][neighbor] = sim.send_hinge_joint(
                        first_body_id = cubes[coord], second_body_id = cubes[neighbor],
                        x=(xdif + coord[0])*c.SCALE, y=(ydif + coord[1])*c.SCALE, z=(zdif + coord[2])*c.SCALE,
                        n1=1, n2=0, n3=0,
                        lo=-math.pi/2., hi=math.pi/2.
                        )
        if(ydif == 0):
            joints2[coord][neighbor] = sim.send_hinge_joint(
                        first_body_id = cubes[coord], second_body_id = cubes[neighbor],
                        x=(xdif + coord[0])*c.SCALE, y=(ydif + coord[1])*c.SCALE, z=(zdif + coord[2])*c.SCALE,
                        n1=0, n2=1, n3=0,
                        lo=-math.pi/2., hi=math.pi/2.
                        )

        if(zdif == 0):
            joints3[coord][neighbor] = sim.send_hinge_joint(
                        first_body_id = cubes[coord], second_body_id = cubes[neighbor],
                        x=(xdif + coord[0])*c.SCALE, y=(ydif + coord[1])*c.SCALE, z=(zdif + coord[2])*c.SCALE,
                        n1=0, n2=0, n3=1,
                        lo=-math.pi/2., hi=math.pi/2.
                        )
"""
