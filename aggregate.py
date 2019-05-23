import numpy as np
import random
import math
import constants as c

class AGGREGATE:
    
    def __init__(self, numCubes):
        
        self.tree = {}
        self.tree[(0,0,0)] = []
        self.body = {}
        
        self.fitness = 0
        
        self.generate_random(numCubes)

    def generate_random(self, numCubes):
        '''
        Takes numcubes as an integer argument for the size of the desired polycube
        Will randomly generate a polycube of desired size
        '''

        while numCubes > len(self.tree):
            
            #np.random.seed(0)

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

    def send_to_sim(self, sim, element):
        '''
        Construct a body using the provided body tree. Call the element's build function to add joints, neurons, and synapses.
        '''
        
        #establish what the lowest z-coordinate in the tree is so the robot can be shifted up accordingly
        lowest = 0
        for coord in self.tree:
            if coord[2] < lowest:
                lowest = coord[2]

        if len(self.body) == 0:
            #Iterate over each index of the tree, call add_cube to build a block there. Store that cube mapped to its real-space coordinates (modified z)
            for coord in self.tree:
                box, z = self.add_cube(sim, coord, lowest)
                newCoord = coord[:2] + (z,)
                self.body[newCoord] = box
    
        else:
            for coord in self.tree:
                self.add_cube(sim, coord, lowest)
        #Using the element's specifications, build the joints, neurons, and synapses
        for parent in self.tree:
            #modify parent coordinates to match real-space
            rparent = parent[:2] + (parent[2] - lowest + .5,)
            for child in self.tree[parent]:
                #modify child coordinates to match real-space
                rchild = child[:2]+ (child[2] - lowest + .5,)
                element.send_element(sim, self.body[rchild], self.body[rparent], [rchild, rparent])
    def add_cube(self, sim, coord, lowest):
        '''
        Create a cube at the specified coordinate, with the specified element's properties
        '''
        
        colors = np.random.random(size=3)
        
        box = sim.send_box(position=(coord[0]*c.SCALE, coord[1]*c.SCALE, (coord[2] - lowest + .5)*c.SCALE),
                 sides=(c.SCALE, c.SCALE, c.SCALE),
                 color=(colors[0], colors[1], colors[2]))
        
        return box, coord[2] - lowest + .5

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
        
        
        
        
        
        
                
