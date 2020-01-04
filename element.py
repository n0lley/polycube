"""
Contains controller layouts for simulation. Each subclass should init with the dimensions of its genome as a tuple.
"""

import constants as c
from individual import INDIVIDUAL

import numpy as np
import pyrosim
import math

global sequenceNumber
sequenceNumber = 0

def getSeqNumber():
    global sequenceNumber
    sequenceNumber += 1
    return sequenceNumber

class ELEMENT(INDIVIDUAL):

    def __init__(self, dimensions):
        '''
        Initialize class variables
        '''
        self.id = getSeqNumber()
        
        self.generate_random(dimensions)
        
        self.scores = []
        self.fitness = 0
        self.age = 0

    def __str__(self):
        return "Fit: %.3f, Age: %d" % (self.fitness, self.age)

    def reset(self):
        '''
        reset fitness list
        '''
        
        self.scores = []
    
    def generate_random(self, dimensions):

        self.controller = np.random.random(dimensions)

    def increment_age(self):
        self.age += 1

    def mutate(self):
        '''
        Randomly modify a weight in the element's genome
        '''
        dimensions = self.controller.shape
        index = 0
        genome = self.controller
        while type(genome[0]).__name__ != "float64":
            tmp = np.random.randint(0, dimensions[index])
            index += 1
            genome = genome[tmp]
        
        gene = np.random.choice(genome)
        
        self.id = getSeqNumber()
        
        newgene = np.random.normal(gene)
        
        if newgene > 1:
            newgene = 1
        elif newgene < -1:
            newgene = -1
        
        self.controller = np.where(self.controller == gene, newgene, self.controller)

    def build_elements(self, sim, tree, cubes, lowest):
        '''
        Take the tree and boxes from the aggregate and construct the elements.
        '''
        
        for parent in tree:
            #modify parent coordinates to match real-space
            rparent = parent[:2] + (float(format(parent[2] - lowest + .5, '.2f')),)
            for child in tree[parent]:
                #modify child coordinates to match real-space
                rchild = child[:2]+ (float(format(child[2] - lowest + .5, '.2f')),)
                self.send_element(sim, cubes[rchild], cubes[rparent], [rchild, rparent])

    def send_element(self):
        '''
        
        '''
        raise NotImplementedError("send_element function is not written")

    def find_joint_position(self, coord1, coord2):
        '''
        For subclasses to call when building joints. coord1 is child's coordinates, coord2 is the parent.
        '''

        parent = coord2
        child = coord1
        
        #calculate joint's position
        jx = format(((child[0] - parent[0])/2 + parent[0])*c.SCALE, '.3')
        jy = format(((child[1] - parent[1])/2 + parent[1])*c.SCALE, '.3')
        jz = format(((child[2] - parent[2])/2 + parent[2])*c.SCALE, '.3')

        return [jx, jy, jz]

    def build_neural_network(self, sim, sensors, actuators, hidden=None):
        '''
        For subclasses to call when building their neural networks. Additional functionality for hidden neurons TBA.
        '''
        
        #add sensor neurons
        SN = {}
        for s in sensors:
            SN[s] = sim.send_sensor_neuron(sensor_id = sensors[s])
            
        #build the motors
        MN = {}
        for a in actuators:
            MN[a] = sim.send_motor_neuron(motor_id=actuators[a], tau=.3)

        #add synapses
        if hidden==None:
            for s in SN:
                for m in MN:
                    sim.send_synapse(source_neuron_id = SN[s], target_neuron_id=MN[m], weight=self.controller[s,m])

    def build_universal_hinge(self, sim, box, parent, coords):
        '''
        Creates two joints normal to each other to serve as a universal hinge, with a small
        intermediate box object to allow two joints
        '''

        #get joint position
        j = self.find_joint_position(coords[0], coords[1])
        
        #build intermediate box
        b2 = sim.send_box(position=(j[0], j[1], j[2]),
                          sides=(c.SCALE*.01, c.SCALE*.01, c.SCALE*.01),
                          collision_group = "body")

        #build the joints
        joints = {}
        bodies = {0:box, 1:b2, 2:parent}
        i = 0
        if coords[0][0] == coords[1][0]:
        #Same x-coordinates, create joint with normal on x axis
            joints[i] = sim.send_hinge_joint(body1=bodies[i], body2=bodies[i+1],
                                             anchor=(j[0],j[1],j[2]),
                                             axis=(1, 0, 0),
                                             joint_range = math.pi/2.)
            i+=1
        
        if coords[0][1] == coords[1][1]:
        #Same y-coordinates, create joint with normal on y axis
            joints[i] = sim.send_hinge_joint(body1=bodies[i], body2=bodies[i+1],
                                             anchor=(j[0],j[1],j[2]),
                                             axis=(0, 1, 0),
                                             joint_range = math.pi/2.)
            i+=1
        
        if coords[0][2] == coords[1][2]:
        #Same z-coordinates, create joint with normal on z axis
            joints[i] = sim.send_hinge_joint(body1=bodies[i], body2=bodies[i+1],
                                            anchor=(j[0],j[1],j[2]),
                                            axis=(0, 0, 1),
                                            joint_range = math.pi/2.)
            i+=1

        return joints
        
class TwoWeightAmplitude(ELEMENT):

    def __init__(self):
        '''
        Create an element. Initialization does not differ from superclass.
        '''
        super().__init__((1,2))
    
    def build_elements(self, sim, tree, cubes, lowest):
        '''
        Take the tree and boxes from the aggregate and construct the elements.
        '''
        super().build_elements(sim, tree, cubes, lowest)

    def send_element(self, sim, box, parent, coords):
        '''
        Use the current box being modified, the box it's being attached to, and the coordinates of those boxes (in that order) to build class-specific  joints, sensors, motors, etc on box.
        Attach controller to that network.
        '''

        joints = self.build_universal_hinge(sim, box, parent, coords)

        actuators = {}
        for j in joints:
            actuators[j] = sim.send_rotary_actuator(joint_id = joints[j])

        sin = np.linspace(0, 2*math.pi, 200)
        sin = np.sin(sin)
        cpg = sim.send_user_neuron(input_values = sin)

        #manually build network
        #add sensor neuron
        SN = {}
        SN[0] = cpg
        
        #build the motors
        MN = {}
        for a in actuators:
            MN[a] = sim.send_motor_neuron(motor_id=actuators[a], tau=.3)
        
        #add synapses
        for s in SN:
            for m in MN:
                sim.send_synapse(source_neuron_id = SN[s], target_neuron_id=MN[m], weight=self.controller[s,m])

class FixedWeightPhaseOffset(ELEMENT):

    def __init__(self, weight):
        '''
        Create an element, with its single weight set to a fixed value
        '''
        self.id = getSeqNumber()
        
        self.controller = [weight]
        
        self.scores = []
        self.fitness = 0
        self.age = 0
    
    def build_elements(self, sim, tree, cubes, lowest):
        '''
        Take the tree and boxes from the aggregate and construct the elements.
        '''
        
        super().build_elements(sim, tree, cubes, lowest)

    def send_element(self, sim, box, parent, coords):
        '''
        Use the current box being modified, the box it's being attached to, and the coordinates of those boxes (in that order) to build class-specific  joints, sensors, motors, etc on box.
        Attach controller to that network.
        '''

        joints = self.build_universal_hinge(sim, box, parent, coords)

        actuators = {}
        for j in joints:
            actuators[j] = sim.send_rotary_actuator(joint_id = joints[j])

        sin1 = np.linspace(0 + self.controller[0]*math.pi, 2*math.pi + self.controller[0]*math.pi, 200)
        sin1 = np.sin(sin1)
        sin2 = np.linspace(0, 2*math.pi, 200)
        sin2 = np.sin(sin2)
        cpg1 = sim.send_user_neuron(input_values = sin1)
        cpg2 = sim.send_user_neuron(input_values = sin2)

        #manually build network
        #add input neurons
        SN = {}
        SN[0] = cpg1
        SN[1] = cpg2
        
        #build the motors
        MN = {}
        for a in actuators:
            MN[a] = sim.send_motor_neuron(motor_id=actuators[a], tau=.3)
        
        #add synapses
        for s in SN:
            sim.send_synapse(source_neuron_id = SN[s], target_neuron_id=MN[s], weight=1)

class OneWeightPhaseOffset(ELEMENT):

    def __init__(self):
        '''
        Create an element. Initialization does not differ from superclass.
        '''
        super().__init__((1,1))

    def build_elements(self, sim, tree, cubes, lowest):
        '''
        Take the tree and boxes from the aggregate and construct the elements.
        '''
        
        super().build_elements(sim, tree, cubes, lowest)

    def send_element(self, sim, box, parent, coords):
        '''
        Use the current box being modified, the box it's being attached to, and the coordinates of those boxes (in that order) to build class-specific  joints, sensors, motors, etc on box.
        Attach controller to that network.
        '''

        joints = self.build_universal_hinge(sim, box, parent, coords)

        actuators = {}
        for j in joints:
            actuators[j] = sim.send_rotary_actuator(joint_id = joints[j])

        sin1 = np.linspace(0 + self.controller[0][0]*math.pi, 2*math.pi + self.controller[0][0]*math.pi, 200)
        sin1 = np.sin(sin1)
        sin2 = np.linspace(0, 2*math.pi, 200)
        sin2 = np.sin(sin2)
        cpg1 = sim.send_user_neuron(input_values = sin1)
        cpg2 = sim.send_user_neuron(input_values = sin2)

        #manually build network
        #add input neurons
        SN = {}
        SN[0] = cpg1
        SN[1] = cpg2
        
        #build the motors
        MN = {}
        for a in actuators:
            MN[a] = sim.send_motor_neuron(motor_id=actuators[a], tau=.3)
        
        #add synapses
        for s in SN:
            sim.send_synapse(source_neuron_id = SN[s], target_neuron_id=MN[s], weight=1)

class ThreeWeightPhaseOffsetFrequency(ELEMENT):
    
    def __init__(self):
    
        super().__init__((3,1))
        
    def build_elements(self, sim, tree, cubes, lowest):
    
        super().build_elements(sim, tree, cubes, lowest)
        
    def send_element(self, sim, box, parent, coords):
        
        joints = self.build_universal_hinge(sim, box, parent, coords)

        actuators = {}
        for j in joints:
            actuators[j] = sim.send_rotary_actuator(joint_id = joints[j])

        sin1 = np.linspace(0 + self.controller[0][0]*math.pi, 2*math.pi + self.controller[0][0]*math.pi, 200+(150*self.controller[1][0]))
        sin1 = np.sin(sin1)
        sin2 = np.linspace(0, 2*math.pi, 200+(150*self.controller[2][0]))
        sin2 = np.sin(sin2)
        cpg1 = sim.send_user_neuron(input_values = sin1)
        cpg2 = sim.send_user_neuron(input_values = sin2)

        #manually build network
        #add input neurons
        SN = {}
        SN[0] = cpg1
        SN[1] = cpg2
        
        #build the motors
        MN = {}
        for a in actuators:
            MN[a] = sim.send_motor_neuron(motor_id=actuators[a], tau=.3)
        
        #add synapses
        for s in SN:
            sim.send_synapse(source_neuron_id = SN[s], target_neuron_id=MN[s], weight=1)
