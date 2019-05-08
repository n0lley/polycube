"""
    TODO: Create Element init which specifies the element's properties
    
    Mutate which changes the motor/sensors
    """
import constants as c
import pyrosim

class ELEMENT:

    def __init__(self, sensors, motors, controller):
    
        self.size = c.SCALE
    
        self.sensors = sensors
    
        self.motors = motors
    
        self.controller = controller
    
    def Mutate():
        exit

class TouchSensorHingeJointElement(ELEMENT):

    def __init__(self, body):

        self.sensors[0] = self.sim.send_touch_sensor(body_id = body)
