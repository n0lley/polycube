"""
    TODO: Create Element init which specifies the element's properties
    
    Mutate which changes the motor/sensors
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

    def __init__(self, c1=2, c2=2):
        '''
        Initialize class variables
        '''
        self.id = getSeqNumber()
        self.controller = None
        
        self.contDim1 = c1
        self.contDim2 = c2
        
        self.generate_random()
        
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
    
    def generate_random(self):

        self.controller = np.random.random((self.contDim1, self.contDim2))

    def increment_age(self):
        self.age += 1

    def mutate(self):
        '''
        Randomly modify a weight in the element's genome
        '''
        self.id = getSeqNumber()
        row = np.random.randint(0, self.contDim1)
        col = np.random.randint(0, self.contDim2)
        
        gene = self.controller[row, col]
        gene = np.random.normal(gene)
        
        if gene > 1:
            gene = 1
        elif gene < -1:
            gene = -1
        
        self.controller[row, col] = gene

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

class TouchSensorUniversalHingeJointElement(ELEMENT):

    def __init__(self):
        '''
        Create an element. Initialization does not differ from superclass.
        '''
        super().__init__(1, 2)

    def send_element(self, sim, box, parent, coords):
        '''
        Use the current box being modified, the box it's being attached to, and the coordinates of those boxes (in that order) to build class-specific  joints, sensors, motors, etc on box.
        Attach controller to that network.
        '''

        #add hinge joints
        joints = self.build_universal_hinge(sim, box, parent, coords)
        
        actuators = {}
        for j in joints:
            actuators[j] = sim.send_rotary_actuator(joint_id = joints[j])

        #build the sensors
        sensors = {}
        sensors[0] = sim.send_touch_sensor(body_id = box)
        
        self.build_neural_network(sim, sensors, actuators)

class TouchAndLightSensorYAxisHingeJointElement(ELEMENT):

    def __init__(self):
        '''
        Create an element. Initialization does not differ from superclass.
        '''
        super().__init__(2, 1)

    def send_element(self, sim, box, parent, coords):
        '''
        Use the current box being modified, the box it's being attached to, and the coordinates of those boxes (in that order) to build class-specific  joints, sensors, motors, etc on box.
        Attach controller to that network.
        '''

        j = self.find_joint_position(coords[0], coords[1])
        joints = {}

        joints[0] = sim.send_hinge_joint(body1 = box, body2 = parent,
                                         anchor=(j[0],j[1],j[2]),
                                         axis=(0, 1, 0),
                                         joint_range = math.pi/2.)

        actuators = {}
        for j in joints:
            actuators[j] = sim.send_rotary_actuator(joint_id = joints[j])

        sensors = {}
        sensors[0] = sim.send_touch_sensor(body_id = box)
        sensors[1] = sim.send_light_sensor(body_id = box)

        self.build_neural_network(sim, sensors, actuators)

class TouchAndLightSensorXAxisHingeJointElement(ELEMENT):
    
    def __init__(self):
        '''
        Create an element. Initialization does not differ from superclass.
        '''
        super().__init__(2, 1)
    
    def send_element(self, sim, box, parent, coords):
        '''
        Use the current box being modified, the box it's being attached to, and the coordinates of those boxes (in that order) to build class-specific  joints, sensors, motors, etc on box.
        Attach controller to that network.
        '''
        
        j = self.find_joint_position(coords[0], coords[1])
        joints = {}
        
        joints[0] = sim.send_hinge_joint(body1 = box, body2 = parent,
                                         anchor=(j[0],j[1],j[2]),
                                         axis=(1, 0, 0),
                                         joint_range = math.pi/2.)
            
        actuators = {}
        for j in joints:
            actuators[j] = sim.send_rotary_actuator(joint_id = joints[j])
         
        sensors = {}
        sensors[0] = sim.send_touch_sensor(body_id = box)
        sensors[1] = sim.send_light_sensor(body_id = box)
                 
        self.build_neural_network(sim, sensors, actuators)

class TouchSensorUniversalHingeJointCPGElement(ELEMENT):

    def __init__(self):
        '''
        Create an element. Initialization does not differ from superclass.
        '''
        super().__init__(2,2)

    def send_element(self, sim, box, parent, coords):
        '''
        Use the current box being modified, the box it's being attached to, and the coordinates of those boxes (in that order) to build class-specific  joints, sensors, motors, etc on box.
        Attach controller to that network.
        '''

        joints = self.build_universal_hinge(sim, box, parent, coords)

        actuators = {}
        for j in joints:
            actuators[j] = sim.send_rotary_actuator(joint_id = joints[j])

        sensors = {}
        sin = np.linspace(0, 2*math.pi, 100)
        sin = np.sin(sin)
        cpg = sim.send_user_neuron(input_values = sin)
        sensors[0] = sim.send_touch_sensor(body_id = box)

        #manually build network
        #add sensor neurons
        SN = {}
        for s in sensors:
            SN[s] = sim.send_sensor_neuron(sensor_id = sensors[s])
        SN[1] = cpg
        
        #build the motors
        MN = {}
        for a in actuators:
            MN[a] = sim.send_motor_neuron(motor_id=actuators[a], tau=.3)
        
        #add synapses
        for s in SN:
            for m in MN:
                sim.send_synapse(source_neuron_id = SN[s], target_neuron_id=MN[m], weight=self.controller[s,m])

class TouchSensorPistonJointElement(ELEMENT):

    def __init__(self):
        '''
            Create an element. Initialization does not differ from superclass.
            '''
        super().__init__(1,1)

    def send_element(self, sim, box, parent, coords):
        '''
        Use the current box being modified, the box it's being attached to, and the coordinates of those boxes (in that order) to build class-specific  joints, sensors, motors, etc on box.
        Attach controller to that network.
        '''

        j = self.find_joint_position(coords[0], coords[1])
        joints = {}
        
        dx = coords[0][0] - coords[1][0]
        dy = coords[0][1] - coords[1][1]
        dz = coords[0][2] - coords[1][2]

        joints[0] = sim.send_slider_joint(body1 = box, body2 = parent,
                                          axis=(dx, dy, dz),
                                          joint_range = (-1 * c.SCALE*.75, c.SCALE*.01))

        actuators = {}
        for j in joints:
            actuators[j] = sim.send_linear_actuator(joint_id = joints[j])

        sensors = {}
        sensors[0] = sim.send_touch_sensor(body_id = box)

        self.build_neural_network(sim, sensors, actuators)
