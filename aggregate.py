import numpy as np
import random
import math
import constants as c

class AGGREGATE:
    
    def __init__(self, sim, elements, numCubes, no_sim=False):
        self.tree = {}
        self.tree[(0,0,0)] = []
        
        self.Build_Tree(numCubes)

        if not no_sim:
            self.body = {}
            self.Build_Body(sim, elements)

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
    def Build_Body(self, sim, elements):

        #establish what the lowest z-coordinate in the tree is so the robot can be shifted up accordingly
        lowest = 0
        for coord in self.tree:
            if(coord[2] < lowest):
                lowest = coord[2]

        #Iterate over each index of the tree, call Add_Cube to build a block there.
        for coord in self.tree:
            element = random.choice(elements)
            
            self.Add_Cube(sim, element, coord)

            

    #Create a cube at the specified coordinate, with the specified element's properties
    def Add_Cube(self, sim, element, coord):
        box = sim.send_box(
                           x=coord[0]*c.SCALE, y=coord[1]*c.SCALE, z=(coord[2] - lowest + .5)*c.SCALE,
                           length = element.size, width=element.size, height=element.size,
                           r=random.random(), g=random.random(), b=random.random()
                           )
