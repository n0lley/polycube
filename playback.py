from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT
import element
import math
import pickle
import os
import sys

def GetNewElement():
    raise NotImplementedError

def try_load_generation(fileName, debug=False):
    try:
        f = open(fileName, 'rb')
        coevolve = pickle.load(f)
        f.close()
        if debug: print(fileName)
        return coevolve
    except Exception as e:
        if debug:
            print(e)
        return None

def load_last_gen(pathToSavedGens, fileName, lGen=0, uGen=1, expand=True):
    if expand:
        if (try_load_generation(pathToSavedGens + fileName%uGen) is not None):
            return load_last_gen(pathToSavedGens, fileName, lGen=lGen, uGen=uGen*2)
        else:
            return load_last_gen(pathToSavedGens, fileName, lGen=lGen, uGen=uGen, expand=False)
    else:
        midGen = (uGen + lGen)//2
        if (lGen == uGen):
            print("Loading Gen %d" %lGen)
            return try_load_generation(pathToSavedGens+fileName%lGen), lGen
        if (try_load_generation(pathToSavedGens + fileName%midGen) is not None):
            if (midGen == lGen):
                print("Loading Gen %d" %lGen)
                return try_load_generation(pathToSavedGens+fileName%lGen), lGen
            return load_last_gen(pathToSavedGens, fileName, lGen=midGen, uGen=uGen, expand=False)
        else:
            return load_last_gen(pathToSavedGens, fileName, lGen=lGen, uGen=midGen, expand=False)

def main():
    assert len(sys.argv) > 1, "Please run as playback.py <path/to/saved_gens>"
    pathToSavedGens = sys.argv[1]
    if pathToSavedGens[-1] != "/":
        pathToSavedGens += "/"
    fileName = "gen%d.p"
    currGen = 1
    coevolve = None
    tmp = try_load_generation(pathToSavedGens+fileName%currGen)

    # TODO: switch to use binary search. It will be much faster
    coevolve, gen = load_last_gen(pathToSavedGens, fileName)

    coevolve[0].playback(play_all=True)
