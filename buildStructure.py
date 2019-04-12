import numpy as np
import random
import math

polycube = {}
polycube[(0,0,0)] = []

#Takes numcubes as an integer argument for the size of the desired polycube
#Will randomly generate a polycube of desired size recursively
def Add_Cube(numCubes):

    if(numCubes > len(polycube)):

        #select whether to move + or -
        direction = random.randint(0, 1)*2 - 1

        #coordinate to move in: 0->x, 1->y, 2->z
        coord = random.randint(0,2)

        #pick a random cube from the structure
        parent = random.choice(list(polycube.keys()))

        #convert parent to a list, change the selected coordinate, and convert back to tuple
        child = list(parent)
        child[coord] += direction
        child = tuple(child)

        #if child's coordinates are already occupied, do that again
        while(child in polycube.keys()):

            parent = random.choice(list(polycube.keys()))
            
            child = list(parent)
            child[coord] += direction
            child = tuple(child)
        
        #Point parent to child, add child to the structure
        polycube[parent].append(child)
        polycube[child] = []

        Add_Cube(numCubes)

Add_Cube(10)
print(polycube)
