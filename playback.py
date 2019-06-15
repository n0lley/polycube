from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT
from element import TouchSensorUniversalHingeJointElement
from element import TouchAndLightSensorYAxisHingeJointElement
from element import TouchAndLightSensorXAxisHingeJointElement
import pickle
import os
import sys

def try_load_generation(fileName):
    try:
        f = open(fileName, 'rb')
        coevolve = pickle.load(f)
        f.close()
        print(fileName)
        return coevolve
    except Exception as e:
        return None


elementTypes = [TouchSensorUniversalHingeJointElement,
                TouchAndLightSensorYAxisHingeJointElement,
                TouchAndLightSensorXAxisHingeJointElement]

assert len(sys.argv) > 1, "Please run as python playback.py <path/to/saved_gens/>"
pathToSavedGens = sys.argv[1]
if pathToSavedGens[-1] != "/":
    pathToSavedGens += "/"
fileName = "gen%d.p"
currGen = 1
coevolve = None
tmp = try_load_generation(pathToSavedGens+fileName%currGen)

# TODO: switch to use binary search. It will be much faster

while tmp is not None:
    coevolve = tmp
    currGen += 1
    tmp = try_load_generation(pathToSavedGens+fileName%currGen)


coevolve.playback(play_all=True)
