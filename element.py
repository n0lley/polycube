"""
    TODO: Create Element init which specifies the element's properties
    
    Mutate which changes the motor/sensors
"""
import constants as c
import numpy as np
import pyrosim
import math

class ELEMENT:

    def __init__(self, c1=2, c2=2):
        '''
        Initialize class variables
        '''
    
        self.controller = None
        
        self.contDim1 = c1
        self.contDim2 = c2
        
        self.generate_random()
        
        self.scores = []
        self.fitness = 0
    
    def reset(self):
        '''
        reset fitness list
        '''
        
        self.scores = []
    
    def generate_random(self):
        
        self.controller = np.random.random((self.contDim1, self.contDim2))
    
    def mutate(self):
        '''
        Randomly modify a weight in the element's genome
        '''
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
        jx = format(((child[0] - parent[0])/2 + parent[0])*c.SCALE, '.2')
        jy = format(((child[1] - parent[1])/2 + parent[1])*c.SCALE, '.2')
        jz = format(((child[2] - parent[2])/2 + parent[2])*c.SCALE, '.2')

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

        #add hinge joints. Adds a very small intermediate block to make 2 joints
        
        #joint's position
        j = self.find_joint_position(coords[0], coords[1])
        
        b2 = sim.send_box(position=(j[0], j[1], j[2]),
                          sides=(c.SCALE*.01, c.SCALE*.01, c.SCALE*.01))
        
        #build the joints
        joints = {}
        actuators = {}
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
