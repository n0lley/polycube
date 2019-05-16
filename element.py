"""
    TODO: Create Element init which specifies the element's properties
    
    Mutate which changes the motor/sensors
"""
import constants as c
import pyrosim

class ELEMENT:

    def __init__(self, controller):
        '''
        Initialize class variables
        '''
    
        self.sensors = {}
    
        self.motors = {}
    
        self.controller = []
        
        self.fitness = 0
    
    def mutate():
        exit

    def send_elements():
        exit

class TouchSensorHingeJointElement(ELEMENT):

    def __init__(self, body):

        self.controller = controller

    def send_element(self, sim, box, parent, coords):

        sim.send
