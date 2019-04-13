import numpy as np
import itertools

print('')
def check_isomorphism(p1, p2):
    """
    Performs all 48 symmetries on polycube2 (p2)
        and checks if it's equal to polycube1 (p1)
    """
    
    #use p1 as the comparison
    fixedCoordinates = set(p1.keys())
    
    #get all coordinates
    coordinateSet = p2.keys()
    
    #get all x coordinates in a list, all y in a list, all z in a list
    coordinatesSplit = list(zip(*coordinateSet))
    
    #offset to reflect each coordinate by 
    reflectPoints = [max(coor) for coor in coordinatesSplit]
    
    coorReflect = list(itertools.product('01', repeat=3))
    
    permutations = list(itertools.permutations('012'))
    
    #check each permutation of the coordinates
    for permute in permutations:
        
        #permutation indices
        i,j,k = permute[0], permute[1], permute[2]
        i = int(i)
        j = int(j)
        k = int(k)
        
        #get reflection args
        a,b,c = reflectPoints[i], reflectPoints[j], reflectPoints[k]
        
        #check each possible reflection of each coordinate
        for reflect in coorReflect:
            
            rX = int(reflect[0])
            rY = int(reflect[1])
            rZ = int(reflect[2])
            
            newCoordSet = set()
            
            for coord in coordinateSet:
                
                #permute the coordinates
                x,y,z = coord[i], coord[j], coord[k]
                
                #reflect the coordinates
                if rX:
                    x = a-x
                if rY:
                    y = b-y
                if rZ:
                    z = c-z
                
                #add new coordinate under the map
                newCoord = (x, y, z)
                newCoordSet.add(newCoord)
            
            #check if mapping equals the comparison set
            if newCoordSet == fixedCoordinates:
                return True
            
    #at this point, none match
    return False
                

d1 = {(0,0,0): 0, 
      (0,0,1): 1,
      (0,1,1): 2,
      (0,1,2): 3,
      (1,1,1): 4,
      (1,1,2): 5}

d2 = {(0,0,0): 0, 
      (0,0,1): 1,
      (0,0,2): 2,
      (0,0,3): 3,
      (0,0,4): 4,
      (0,0,5): 5}

d3 = {(0,0,0): 0, 
      (0,1,0): 1,
      (0,2,0): 2,
      (0,3,0): 3,
      (0,4,0): 4,
      (0,5,0): 5}

d4 = {(0,0,0): 0, 
      (1,0,0): 1,
      (1,1,0): 2,
      (2,1,0): 3,
      (1,1,1): 4,
      (2,1,1): 5}

print(check_isomorphism(d1, d2))
print(check_isomorphism(d1, d3))
print(check_isomorphism(d1, d4))
print(check_isomorphism(d2, d3))
print(check_isomorphism(d2, d4))
print(check_isomorphism(d3, d4))