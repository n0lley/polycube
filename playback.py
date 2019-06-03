from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT
from element import TouchSensorUniversalHingeJointElement
from element import TouchAndLightSensorYAxisHingeJointElement
from element import TouchAndLightSensorXAxisHingeJointElement
import pickle
import os

elementTypes = [TouchSensorUniversalHingeJointElement,
                TouchAndLightSensorYAxisHingeJointElement,
                TouchAndLightSensorXAxisHingeJointElement]

g = 99

    #try:
fileName = './saved_generations/gen'
f = open(fileName + format(g) + '.p', 'rb')
coevolve = pickle.load(f)
f.close()
coevolve.playback()

'''
except:
    print ("Error loading generation", g)
'''
