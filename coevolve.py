from parallelpy.utils import Work, Letter
from parallelpy import parallel_evaluate

import math
import constants as c
import numpy as np
import pyrosim
from copy import deepcopy

class SIM(Work):
    """
    Wrapper for a simulation instance which allows us to parallelize the simulation of aggregates and controllers
    across a cluster of computers.
    """
    def __init__(self, aggregate, aggregate_key, controller, controller_key, seed):
        """
        :param aggregate: The instance of the aggregate
        :param aggregate_key: The key of the aggregate in the dict of controllers.
        :param controller: The instance of the controller
        :param controller_key: The key of the controller in the dict of controllers
        """
        self.aggregate = aggregate
        self.aggregate_key = aggregate_key
        self.controller = controller
        self.controller_key = controller_key
        self.keys = [aggregate_key,controller_key,seed]
        self.fitness = -1

    def compute_work(self, serial=False):
        for i in range(10):
          sim = pyrosim.Simulator(eval_steps=COEVOLVE.TIME_STEPS, play_blind=True, play_paused=False, dt=COEVOLVE.DT)
          #print("Simulating aggregate", self.aggregate_key, "with controller", self.controller_key)
          self.fitness = self.aggregate.evaluate(sim, self.controller, idNum=self.keys, debug=False)
          if self.fitness > -1:
            break
          #print("fitness of aggregate", self.aggregate_key, "and controller", self.controller_key, "retrieved")
        if self.fitness < 0: self.fitness = 0

    def write_letter(self):
        return Letter((self.fitness, self.aggregate_key, self.controller_key), None)

    def open_letter(self, letter):
        self.fitness, _, _ = letter.get_data()

class COEVOLVE:
    '''
    handles co-evolutionary methods for AGGREGATE and CONTROLLER classes
        
    Attributes
    ----------
    aggrs    : POPULATION instance
        Population of aggregate objects
    contrs    : POPULATION instance
        Population of controller objects
    '''
    
    DT = 0.01
    TIME_STEPS = 1000
    def __init__(self, aggrs, contrs, mode, seed):
        '''
        initializes the two populations 
        '''
        
        self.aggrs = aggrs
        self.contrs = contrs
        self.mode = mode #1 for robustness, 0 for max fitness
        self.fpi = math.ceil(len(self.aggrs.p)*.05)
        self.seed = seed
        
    def non_MPI_exhaustive(self):
        """
        non-parallel exhaustive evaluation
        """
        
        for j in range(len(self.contrs.p)):
            contr = self.contrs.p[j]
            for i in range(len(self.aggrs.p)):
                aggr = self.aggrs.p[i]
                sim = pyrosim.Simulator(eval_steps=COEVOLVE.TIME_STEPS, play_blind=True, play_paused=False, dt=COEVOLVE.DT)
                fit = aggr.evaluate(sim, self.contrs.p[j], idNum = [i,j,0])
                self.contrs.p[j].scores.append(fit)
                
        self.calculate_fitness()

    def exhaustive(self):
        '''
        Evaluates every single aggregate composed with 
            every single controller
        '''

        # pre allocate work_array to avoid need to expand array upon append.
        work_to_complete = [None]*(len(self.aggrs.p)*len(self.contrs.p))
        work_index = 0 # keep track of which index in the array we are at.
        for j in range(len(self.aggrs.p)):
            aggr = self.aggrs.p[j]
            for i in range(len(self.contrs.p)):
                work_to_complete[work_index] = SIM(aggr, j, self.contrs.p[i], i, self.seed)
                work_index += 1
        print("Simulating %d robots" % len(work_to_complete))
        parallel_evaluate.batch_complete_work(work_to_complete)
        
        #print("appending fitnesses")
        for work in work_to_complete:
            aggr_key = work.aggregate_key
            elmt_key = work.controller_key
            fit = work.fitness
            if c.DEBUG:
                print("Sim fit:",fit)

            self.contrs.p[elmt_key].scores.append(fit)

        self.calculate_fitness()
                
    def calculate_fitness(self):
        """
        Each controller's fitness is set to the sum of the 5th percentile of its scores. If there are too few scores to take a 5th percentile, take the lowest.
        """
        if self.mode == 1:
            for i in range(len(self.contrs.p)):
                try:
                     self.contrs.p[i].scores.sort()
                     fifth_percentile = self.contrs.p[i].scores[0:self.fpi]
                     while len(fifth_percentile) != self.fpi:
                        fifth_percentile = self.contrs.p[i].scores[0:self.fpi]
                     fit = sum(fifth_percentile)/self.fpi
                     if (np.isnan(fit) or np.isinf(fit) or len(self.contrs.p[i].scores)==0):
                         fit = 0
                     self.contrs.p[i].fitness = fit
                     print(fit, fifth_percentile)
                except Exception as e:
                    print(e)
                    raise(e)
                    self.contrs.p[i].fitness = 0
        elif self.mode == 0:
            for i in range(len(self.contrs.p)):
                try:
                    self.contrs.p[i].scores.sort()
                    fit = self.contrs.p[i].scores[-1]
                    self.contrs.p[i].fitness = fit
                
                except Exception as e:
                    print(e)
                    raise(e)
                
    def print_fitness(self):
        '''
        prints the top controller fitness
        '''

        print('Best Controller of',len(self.contrs.p),':')
        best = 0
        besti = 0
        for i in range(len(self.contrs.p)):
            if self.contrs.p[i].fitness > best:
                best = self.contrs.p[i].fitness
                besti = i
        
        fpi = math.ceil(len(self.contrs.p[besti].scores)*.05)
        print(besti, ":", best, self.contrs.p[besti].scores[0:fpi])

    def reset(self):
        '''
        calls reset on both populations
        '''
        self.contrs.reset()
        
    def selection(self):
        '''
        calls selection on controllers
        '''
        self.contrs.selection()
        
    def playback(self, play_all=False):
        '''
        for review purposes, plays the best aggregate and controller, with play_blind off
        '''

        fit = 0
        eindex = 0
        for j in range(len(self.contrs.p)):
            if abs(self.contrs.p[j].fitness) > abs(fit):
                print("fit")
                print(j)
                fit = self.contrs.p[j].fitness
                eindex = j

        if play_all:
            for a in self.aggrs.p:
                aggr = a
                elmt = self.contrs.p[eindex]
                sim = pyrosim.Simulator(eval_steps=1000, play_blind=False, play_paused=False, dt=.01)
                try:
                    print(aggr.evaluate(sim, elmt, debug=True))
                except Exception as e:
                    print("error")
                    pass
        else:
            
            fit = 99999
            aindex = -1
            elmt = self.contrs.p[eindex]
            
            for i in range(len(elmt.scores)):
                if elmt.scores[i] < fit:
                    fit = elmt.scores[i]
                    aindex = i

            aggr = self.aggrs.p[aindex]
            print(aindex, eindex)
            sim = pyrosim.Simulator(eval_steps=1000, play_blind=False, play_paused=True, dt=.01, use_textures=True)
            aggr.evaluate(sim, elmt, debug=False)
