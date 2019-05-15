import numpy as np
import random
import math
import constants as c

class AGGREGATE:
    
    def __init__(self, numCubes):
        
        self.tree = {}
        self.tree[(0,0,0)] = []
        self.body = {}
        
        self.build_tree(numCubes)

    def build_tree(self, numCubes):
        '''
        Takes numcubes as an integer argument for the size of the desired polycube
        Will randomly generate a polycube of desired size
        '''

        while numCubes > len(self.tree):

            #select whether to move + or -
            direction = np.random.choice([-1, 1])

            #coordinate to move in: 0->x, 1->y, 2->z
            coord = np.random.choice([0, 1, 2])

            #pick a random cube from the structure
            keys = list(self.tree.keys())
            index = np.random.choice(len(keys))
            parent = keys[index]
            
            #convert parent to a list, change the selected coordinate, and convert back to tuple
            child = list(parent)
            child[coord] += direction
            child = tuple(child)

            #if child's coordinates are already occupied, do that again
            while child in self.tree.keys():

                index = np.random.choice(len(keys))
                parent = keys[index]
                
                child = list(parent)
                child[coord] += direction
                child = tuple(child)
            
            #Point parent to child, add child to the structure
            self.tree[parent].append(child)
            self.tree[child] = []

    def send_to_sim(self, sim, elements):
        '''
        Construct a body using the provided body tree and randomly choosing 
            block types from the provided list of elements
        '''
        
        #establish what the lowest z-coordinate in the tree is so the robot can be shifted up accordingly
        lowest = 0
        for coord in self.tree:
            if coord[2] < lowest:
                lowest = coord[2]

        if len(self.body) == 0:
            #Iterate over each index of the tree, call add_cube to build a block there.
            for coord in self.tree:
                element = np.random.choice(elements)
                
                #add a block
                self.body[coord] = [self.add_cube(sim, element, coord, lowest), element]

        else:
            #draw existing values from self.body
            for coord in self.body:
                element = self.body[coord][1]
                self.add_cube(sim, element, coord, lowest)
                
        #add joints, motors, sensors to each box
        for parent in self.tree:
            for child in self.tree[parent]:
                joints = self.build_joints(sim, parent, child)
                #sensors, motors = self.add_neurons(sim, child, joints)
                #self.build_network(sim, child, sensors, motors)


    def add_cube(self, sim, element, coord, lowest):
        '''
        Create a cube at the specified coordinate, with the specified element's properties
        '''
        
        colors = np.random.random(size=3)
        
        box = sim.send_box(x=coord[0]*c.SCALE, y=coord[1]*c.SCALE, z=(coord[2] - lowest + .5)*c.SCALE,
                           length = element.size, width=element.size, height=element.size,
                           r=colors[0], g=colors[1], b=colors[2])
        
        return box

    
    def build_joints(self, sim, parent, child):
        '''
        Use child list from tree and corresponding boxes in body to attach joints
        attach joint from child to parent, using child's specifications. Child's nn is attached to that joint
        '''
        
        root = self.body[parent][0]
        leaf = self.body[child][0]
        
        #calculate joint's position
        jx = (child[0] - parent[0])/2 + parent[0]
        jy = (child[1] - parent[1])/2 + parent[1]
        jz = (child[2] - parent[2])/2 + parent[2]

        joints = {}
        
        j=0
        if parent[0] == child[0]:
            #same x-coordinates, create joint with normal on x axis
            joints[j] = sim.send_hinge_joint(
                                            first_body_id=leaf, second_body_id=root,
                                             x=jx, y=jy, z=jz,
                                             n1=1, n2=0, n3=0,
                                             lo=-1*math.pi/2., hi=math.pi/2.
                                             )
            j+=1
        
        if parent[1] == child[1]:
            #same y-coordinates, create joint with normal on y axis
            joints[j] = sim.send_hinge_joint(
                                             first_body_id = leaf, second_body_id = root,
                                             x=jx, y=jy, z=jz,
                                             n1=0, n2=1, n3=0,
                                             lo=-1*math.pi/2., hi=math.pi/2.
                                             )
            j+=1
        
        if parent[2] == child[2]:
            #same z-coordinates, create joint with normal on y axis
            joints[j] = sim.send_hinge_joint(
                             first_body_id=leaf, second_body_id=root,
                             x=jx, y=jy, z=jz,
                             n1=0, n2=0, n3=1,
                             lo=-1*math.pi/2., hi=math.pi/2.
                             )
            j+=1

        return joints

    def add_neurons(self, sim, coord, joints):
        '''
        add sensor and motor neurons per the box's element specifications
        '''
        
        box = self.body[coord][0]
        element = self.body[coord][1]
    
        sensors = {}
        i=0
        for s in element.sensors:
            sensors[i] = sim.send_touch_sensor(body_id=box)
            i+=1
        #placeholder until specifics of element's sensors are worked out

        motors = {}
        i=0
        for m in element.motors:
            motors[i] = sim.send_motor_neuron(joint_id=joints[m])
            i+=1
        #placeholder until specifics of element's motors are worked out

        return sensors, motors
    
    def build_network(self, sim, coord, sensors, motors):
        '''
        build the synapses using the element's Controller
        '''

        element = self.body[coord][1]
        
        for s in sensors:
            for m in motors:
                sim.send_synapse(source_neuron_id=sensors[s], target_neuron_id=motors[m], weight=element.controller[s,m])

    def check_connections(self):
        '''
        prints distance matrix
        if '1' is in each row/column, the tree is valid
        '''
        
        cubes = list(self.tree.keys())
        N = len(cubes)
        dMatrix = np.zeros((N, N), dtype='int')
        
        for i in range(N):
            for j in range(N):
                x1, y1, z1 = cubes[i]
                x2, y2, z2 = cubes[j]
                dist = (x1-x2) + (y1-y2) + (z1-z2)
                dMatrix[i, j] = dist
        
        dMatrix = np.abs(dMatrix)
        cond = True
        for i in range(N):
            cond = cond and np.isin(1, dMatrix[i])
        
        print('Valid Tree:', cond)
        
        
        
        
        
        
                