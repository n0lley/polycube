import numpy as np
import random
import math

class AGGREGATE:
    
    def __init__(self, numCubes):
        self.polycube = {}
        self.polycube[(0,0,0)] = []
        self.Build_Structure(numCubes)

    #Takes numcubes as an integer argument for the size of the desired polycube
    #Will randomly generate a polycube of desired size recursively
    def Build_Structure(self, numCubes):

        if(numCubes > len(self.polycube)):

            #select whether to move + or -
            direction = random.randint(0, 1)*2 - 1

            #coordinate to move in: 0->x, 1->y, 2->z
            coord = random.randint(0,2)

            #pick a random cube from the structure
            parent = random.choice(list(self.polycube.keys()))

            #convert parent to a list, change the selected coordinate, and convert back to tuple
            child = list(parent)
            child[coord] += direction
            child = tuple(child)

            #if child's coordinates are already occupied, do that again
            while(child in self.polycube.keys()):

                parent = random.choice(list(self.polycube.keys()))
                
                child = list(parent)
                child[coord] += direction
                child = tuple(child)
            
            #Point parent to child, add child to the structure
            self.polycube[parent].append(child)
            self.polycube[child] = []

            self.Build_Structure(numCubes)

#Add_Cube(30)
# print(self.polycube)
