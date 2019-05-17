"""
    TODO: Create Element init which specifies the element's properties
    
    Mutate which changes the motor/sensors
"""
import constants as c
import pyrosim
import math

class ELEMENT:

    def __init__(self, controller):
        '''
        Initialize class variables
        '''
    
        self.controller = controller
        
        self.fitness = 0
    
    def mutate():
        exit

    def send_element():
        exit

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

class TouchSensorHingeJointElement(ELEMENT):

    def __init__(self, controller):
        '''
        Create an element. Initialization does not differ from superclass.
        '''
        super().__init__(controller)

    def send_element(self, sim, box, parent, coords):
        '''
        Use the current box being modified, the box it's being attached to, and the coordinates of those boxes (in that order) to build class-specific  joints, sensors, motors, etc on box.
        Attach controller to that network.
        '''

        #add hinge joints. Adds a very small intermediate block to make 2 joints
        
        #joint's position
        j = self.find_joint_position(coords[0], coords[1])
        
        #intermediate block
        jointBox = sim.send_box(x=j[0], y=j[1], z=j[2],
                     length=c.SCALE*.001, width=c.SCALE*.001, height=c.SCALE*.001)

        #build the joints
        boxes = {0:box, 1:jointBox, 2:parent}
        joints = {}
        i=0
        if coords[0][0] == coords[1][0]:
            #same x-coordinates, create joint with normal on x axis
            joints[i] = sim.send_hinge_joint(
                                             first_body_id=boxes[i], second_body_id=boxes[i+1],
                                             x=j[0], y=j[1], z=j[2],
                                             n1=1, n2=0, n3=0,
                                             lo=-1*math.pi/2., hi=math.pi/2.
                                             )
            i+=1

        if coords[0][1] == coords[1][1]:
            #same y-coordinates, create joint with normal on y axis
            joints[i] = sim.send_hinge_joint(
                                             first_body_id = boxes[i], second_body_id = boxes[i+1],
                                             x=j[0], y=j[1], z=j[2],
                                             n1=0, n2=1, n3=0,
                                             lo=-1*math.pi/2., hi=math.pi/2.
                                             )
            i+=1

        if coords[0][2] == coords[1][2]:
            #same z-coordinates, create joint with normal on z axis
            joints[i] = sim.send_hinge_joint(
                                             first_body_id = boxes[i], second_body_id = boxes[i+1],
                                             x=j[0], y=j[1], z=j[2],
                                             n1=0, n2=0, n3=1,
                                             lo=-1*math.pi/2., hi=math.pi/2.
                                             )
            i+=1

        #build the sensors
        sensors = {}
        sensors[0] = sim.send_touch_sensor(body_id = box)

        #build the motors
        motors = {}
        for joint in joints:
            motors[joint] = sim.send_motor_neuron(joint_id=joints[joint], tau=5)

        #add synapses
        for s in sensors:
            for m in motors:
                sim.send_synapse(source_neuron_id = sensors[s], target_neuron_id=motors[m], weight=self.controller[s,m])
