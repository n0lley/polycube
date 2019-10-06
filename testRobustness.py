from coevolve import COEVOLVE
from population import POPULATION
from aggregate import AGGREGATE
from element import ELEMENT
from element import TouchSensorUniversalHingeJointCPGElement
from playback import load_last_gen

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
        
        print(work_to_complete)
        
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
    times = {}
    
    #initialize the array,
    for eval in os.listdir(target_file):
        if os.path.isdir(os.path.join(target_file, eval)):
            robustness_data[eval] = {}
            for run in os.listdir(target_file+eval):
                if os.path.isdir(target_file+eval+"/"+run):
                    coevolve, g = load_last_gen(target_file+eval+"/"+run+"/saved_generations/", "gen%d.p")
                    if coevolve is not None:
                        e = find_best(coevolve)
                        robustness_data[eval][run] = []
                        elements[eval+"."+run] = [e,g]

    
    if newData:
        robustness_data = test_robustness(elements, 500, robustness_data)

        print("Saving Data")
        for eval in robustness_data:
            for run in robustness_data[eval]:
                g = elements[eval+"."+run][1]
                f = open("robustness_data/"+eval+"/"+run+".gen%d"%g + ".p", 'wb')
                pickle.dump(robustness_data[eval][run],f)
                f.close()

    else:
        for eval in robustness_data:
            for run in robustness_data[eval]:
                g = elements[eval+"."+run][1]
                f = open("robustness_data/"+eval+"_"+run+".gen%d"%g + ".p", 'rb')
                robustness_data[eval][run] = pickle.load(f)
                f.close()

            tf = try_load_generation("robustness_targets/"+eval+"/run_111/saved_generations/gen1.p",'rb')
            times[eval] = tf.DT * tf.TIME_STEPS / 60

    return robustness_data, times

def chart_data(genfits, times):
    numRuns = 0
    i = 1
    for e in genfits:
        numRuns += 1
    axmaster = plt.subplot(numRuns,1,1)
    for eval in genfits:
        ax = plt.subplot(numRuns, 1, i, sharex=axmaster, sharey=axmaster)
        color = np.random.random(size=3)
        fit = np.empty((0))
        firstFits = []
        evolvedFits = []
        
        for run in genfits[eval]:
            gen, g = load_last_gen(target + eval + "/" + run + "/saved_generations/gen1000.p", "gen%d.p")
            f = open(target + eval + "/" + run + "/saved_generations/gen1.p", 'rb')
            gen1 = pickle.load(f)
            f.close()
            
            if gen is not None and gen1 is not None:
                bestE = find_best(gen)
                e1 = find_best(gen1)
                for score in bestE.scores:
                    evolvedFits.append(score)
                for score in e1.scores:
                    firstFits.append(score)
            
            tmp = np.asarray(genfits[eval][run])
            fit = np.append(fit, tmp)
                
        evolvedFits = np.asarray(evolvedFits)
        firstFits = np.asarray(firstFits)
        print(firstFits.shape)
        
        ax.hist(x=(firstFits/c.SCALE)/times[eval], bins=36, label="First Gen Fitnesses", alpha = .45, weights=(np.ones(firstFits.shape[0]) / firstFits.shape[0]), density=False, color=[.1, .4, .4])
        ax.hist(x=(evolvedFits/c.SCALE)/times[eval], bins=36, label="Run Champion Fitnesses", alpha = .45, weights=(np.ones(evolvedFits.shape[0]) / evolvedFits.shape[0]), density=False, color=[.8, .2, .1])
        ax.hist(x=(fit/c.SCALE)/times[eval], bins=36, label=eval, alpha = .75, weights=(np.ones(len(fit)) / len(fit)), density=False, color=color)
        i += 1
        plt.legend()

        plt.ylabel("Density")

    plt.xlabel("Speed (cube lengths per minute)")

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
genfits, times = analyze_best_elements(target)

if not newData:
    chart_data(genfits, times)
