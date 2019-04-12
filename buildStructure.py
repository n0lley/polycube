import numpy
import random
import math

#Create a dictionary to store cube location data
#Each cube is represented by a key with its location in 3D space, and a set of values that indicate the locations/keys of its children.
#Until there are as many cubes as needed:
#Pick a random cube
#Compute a random space next to it by randomly adding or subtracting 1 from one of the three coordinates
#Check the new coordinate against the keys. If it is filled, pick a new cube and try again.

polycube = {}

def Add_Cube():

