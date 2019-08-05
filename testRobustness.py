from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT
from element import TouchSensorUniversalHingeJointCPGElement

from parallelpy.utils import Work, Letter
from parallelpy import parallel_evaluate

import pyrosim
import constants as c
import os
import pickle
import sys
import matplotlib.pyplot as plt
import numpy as np
from time import time

newData = False

class SIM(Work):
    """
        Wrapper for a simulation instance which allows us to parallelize the simulation of aggregates and elements
        across a cluster of computers.
        """
    def __init__(self, aggregate, element, key):
        """
            :param aggregate: The instance of the aggregate
            :param aggregate_key: The key of the aggregate in the dict of elements.
            :param element: The instance of the element
            :param element_key: The key of the element in the dict of elements
            """
        self.aggregate = aggregate
        self.eval = key.split(".")[0]
        self.run = key.split(".")[1]
        self.element = element
        self.fitness = None
    
    def compute_work(self, serial=False):
        
        sim = pyrosim.Simulator(eval_steps=COEVOLVE.TIME_STEPS, play_blind=True, play_paused=False, dt=COEVOLVE.DT)
        self.fitness = self.aggregate.evaluate(sim, self.element, debug=False)
    
    def write_letter(self):
        return Letter((self.fitness, self.eval, self.run), None)
    
    def open_letter(self, letter):
        self.fitness, _, _ = letter.get_data()

parallel_evaluate.setup(parallel_evaluate.PARALLEL_MODE_MPI_INTER)

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

def GetNewElement():
    raise NotImplementedError

def find_best(coevolve):
    """
    find the fitnesses of the most fit element in a population
    """
    elm = None
    fit = 0
    for j in coevolve.elmts.p:
        if j.fitness > fit:
            fit = j.fitness
            elm = j
    return elm

def test_robustness(elements, tests, fits):
    
    for i in range(0, tests):
        
        #create an aggregate of random size, normally distributed between 5 and 45
        size = int(np.random.normal(loc=25, scale=12.5)+1)
        while size > 45 or size < 5:
            size = int(np.random.normal(loc=25, scale=12.5)+1)
        a = AGGREGATE(size)
        print(size)
        
        start = time()
        
        work_to_complete = [None]*(len(elements))
        work_index = 0
    
        for e in elements:
            name = e.split(".")
            work_to_complete[work_index] = SIM(a, elements[e], e)
            work_index += 1
        
        parallel_evaluate.batch_complete_work(work_to_complete)
        
        for work in work_to_complete:
            eval = work.eval
            run = work.run
            fits[eval][run].append(work.fitness)
        
        print("Iteration %d, Time taken: "%i + format((time()-start), '.0f'))

    return fits

def analyze_best_elements(target_file):
    
    robustness_data = {}
    elements = {}
    
    #initialize the array,
    for eval in os.listdir(target_file):
        if os.path.isdir(os.path.join(target_file, eval)):
            robustness_data[eval] = {}
            for run in os.listdir(target_file+eval):
                if os.path.isdir(target_file+eval+"/"+run):
                    coevolve = try_load_generation(target_file+eval+"/"+run+"/saved_generations/gen1000.p")
                    if coevolve is not None:
                        e = find_best(coevolve)
                        robustness_data[eval][run] = []
                        elements[eval+"."+run] = e
    
    if newData:
        robustness_data = test_robustness(elements, 500, robustness_data)

        print("Saving Data")
        for eval in robustness_data:
            for run in robustness_data[eval]:
                f = open("robustness_data/"+eval+"_"+run+".gen1000.p", 'wb')
                pickle.dump(robustness_data[eval][run], f)
                f.close()

    else:
        for eval in robustness_data:
            for run in robustness_data[eval]:
                f = open("robustness_data/"+eval+"_"+run+".gen1000.p", 'rb')
                robustness_data[eval][run] = pickle.load(f)
                f.close()

    return robustness_data

def chart_data(genfits):
    for eval in genfits:
        i = 0
        color = np.random.random(size=3)
        for run in genfits[eval]:
            fit = np.asarray(genfits[eval][run])
            if i == 0:
                plt.hist(x=fit*c.SCALE*3, bins=36, label=eval.split("_")[2], alpha = .75, weights=np.ones(len(fit)) / len(fit), density=False, color=color)
                i += 1
            else:
                plt.hist(x=fit*c.SCALE*3, bins=36, alpha = .3, weights=np.ones(len(fit)) / len(fit), density=False, color=color)

    plt.ylabel("Density")
    plt.xlabel("Speed (cube lengths per minute)")

    plt.legend()
    plt.show()

#System input should give the directory path to the run, and the generations being compared
assert len(sys.argv) > 2, "Please run as python testrobustness.py <seed> <target directory>"

try:
    seed = int(sys.argv[1])
    np.random.seed(seed)
except:
    print("Please give seed as an int.")

target = sys.argv[2]
if target[-1] != "/":
    target += "/"

print("Loading best...")
genfits = analyze_best_elements(target)

if not newData:
    chart_data(genfits)
