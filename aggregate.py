import numpy as np
import random
import math
import constants as c

class AGGREGATE:
    
    def __init__(self, numCubes):
        self.tree = {}
        self.tree[(0,0,0)] = []
        
        self.Build_Tree(numCubes)

    #Takes numcubes as an integer argument for the size of the desired polycube
    #Will randomly generate a polycube of desired size recursively
    def Build_Tree(self, numCubes):

        if(numCubes > len(self.tree)):

            #select whether to move + or -
            direction = random.randint(0, 1)*2 - 1

            #coordinate to move in: 0->x, 1->y, 2->z
            coord = random.randint(0,2)

            #pick a random cube from the structure
            parent = random.choice(list(self.tree.keys()))

            #convert parent to a list, change the selected coordinate, and convert back to tuple
            child = list(parent)
            child[coord] += direction
            child = tuple(child)

            #if child's coordinates are already occupied, do that again
            while(child in self.tree.keys()):

                parent = random.choice(list(self.tree.keys()))
                
                child = list(parent)
                child[coord] += direction
                child = tuple(child)
            
            #Point parent to child, add child to the structure
            self.tree[parent].append(child)
            self.tree[child] = []

            self.Build_Tree(numCubes)

    #Construct a body using the provided body tree and randomly choosing block types from the provided list of elements
    def send_to_sim(self, sim, elements):
        
        self.body = {}
        
        #establish what the lowest z-coordinate in the tree is so the robot can be shifted up accordingly
        lowest = 0
        for coord in self.tree:
            if(coord[2] < lowest):
                lowest = coord[2]

        #Iterate over each index of the tree, call Add_Cube to build a block there.
        for coord in self.tree:
            element = random.choice(elements)
            
            #add a block
            self.body[coord] = [self.Add_Cube(sim, element, coord, lowest), element]

        print(self.body)
                
        #add joints, motors, sensors to each box
        for coord in self.tree:
            joints = self.Build_Joints(sim, coord)
            sensors, motors = self.Add_Neurons(sim, coord, joints)
            self.Build_Network(sim, sensors, motors)


    #Create a cube at the specified coordinate, with the specified element's properties
    def Add_Cube(self, sim, element, coord, lowest):
        box = sim.send_box(
                           x=coord[0]*c.SCALE, y=coord[1]*c.SCALE, z=(coord[2] - lowest + .5)*c.SCALE,
                           length = element.size, width=element.size, height=element.size,
                           r=random.random(), g=random.random(), b=random.random()
                           )
        return box

    #use child list from tree and corresponding boxes in body to attach joints
    def Build_Joints(self, sim, coord):

        box = self.body[coord][0]
        children = self.tree[coord]
        
        joints = {}
        
        j = 0
        for child in children:
            #box to be connected
            box2 = self.body[child][0]
            
            #calculate joint's position
            jx = (child[0] - coord[0])/2 + coord[0]
            jy = (child[1] - coord[1])/2 + coord[1]
            jz = (child[2] - coord[2])/2 + coord[2]

            if( coord[0] == child[0] ):
            #same x-coordinates, create joint with normal on x axis
                joints[j] = sim.send_hinge_joint(
                                                first_body_id = box, second_body_id = box2,
                                                 x=jx, y=jy, z=jz,
                                                 n1=1, n2=0, n3=0,
                                                 lo=-1*math.pi/2., hi=math.pi/2.
                                                 )
                j+=1
            
            if( coord[1] == child[1] ):
            #same y-coordinates, create joint with normal on y axis
                joints[j] = sim.send_hinge_joint(
                                                 first_body_id = box, second_body_id = box2,
                                                 x=jx, y=jy, z=jz,
                                                 n1=0, n2=1, n3=0,
                                                 lo=-1*math.pi/2., hi=math.pi/2.
                                                 )
                j+=1
            
            if( coord[2] == child[2] ):
            #same z-coordinates, create joint with normal on y axis
                joints[j] = sim.send_hinge_joint(
                                 first_body_id = box, second_body_id = box2,
                                 x=jx, y=jy, z=jz,
                                 n1=0, n2=0, n3=1,
                                 lo=-1*math.pi/2., hi=math.pi/2.
                                 )
                j+=1

        return joints

    #add sensor and motor neurons per the box's element specifications
    def Add_Neurons(self, sim, coord, joints):
    
        box = self.body[coord][0]
        element = self.body[coord][1]
    
        sensors = {}
        i=0
        for s in element.sensors:
            sensors[i] = s
            i+=1
        #placeholder until specifics of element's sensors are worked out

        motors = {}
        i=0
        for m in element.motors:
            motors[i] = m
            i+=1
        #placeholder until specifics of element's motors are worked out

        return sensors, motors
    
    #build the synapses using the element's Controller
    def Build_Network(self, sim, sensors, motors):

        for s in sensors:
            for m in motors:
                sim.send_synapse(source_neuron_id = sensors[s], target_neuron_id = motors[m])
