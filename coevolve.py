from parallelpy.utils import Work, Letter
from parallelpy import parallel_evaluate

import numpy as np
import pyrosim

class SIM(Work):
    """
    Wrapper for a simulation instance which allows us to parallelize the simulation of aggregates and elements
    across a cluster of computers.
    """
    def __init__(self, aggregate, aggregate_key, element, element_key):
        """
        :param aggregate: The instance of the aggregate
        :param aggregate_key: The key of the aggregate in the dict of elements.
        :param element: The instance of the element
        :param element_key: The key of the element in the dict of elements
        """
        self.aggregate = aggregate
        self.aggregate_key = aggregate_key
        self.element = element
        self.element_key = element_key
        self.fitness = None

    def compute_work(self, serial=False):

        sim = pyrosim.Simulator(eval_steps=COEVOLVE.TIME_STEPS, play_blind=True, play_paused=False, dt=COEVOLVE.DT)
        print("Simulating aggregate", self.aggregate_key, "with element", self.element_key)
        self.fitness = self.aggregate.evaluate(sim, self.element, debug=False)
        print("fitness of aggregate", self.aggregate_key, "and element", self.element_key, "retrieved")

    def write_letter(self):
        return Letter((self.fitness, self.aggregate_key, self.element_key), None)

    def open_letter(self, letter):
        self.fitness, _, _ = letter.get_data()

class COEVOLVE:
    '''
    handles co-evolutionary methods for AGGREGATE and ELEMENT classes
        
    Attributes
    ----------
    aggrs    : POPULATION instance
        Population of aggregate objects
    elmts    : POPULATION instance
        Population of element objects
    '''

    COOPERATIVE_MODE = 0
    COMPETITIVE_MODE = 1
    DT = 0.01
    TIME_STEPS = 1000
    def __init__(self, aggrs, elmts):
        '''
        initializes the two populations 
        '''
        
        self.aggrs = aggrs
        self.elmts = elmts
        
    def exhaustive(self):
        '''
        Evaluates every single aggregate composed with 
            every single element 
        '''

        # pre allocate work_array to avoid need to expand array upon append.
        work_to_complete = [None]*(len(self.aggrs.p)*len(self.elmts.p))
        work_index = 0 # keep track of which index in the array we are at.
        for j in range(len(self.aggrs.p)):
            aggr = self.aggrs.p[j]
            for i in range(len(self.elmts.p)):
                work_to_complete[work_index] = SIM(aggr, j, self.elmts.p[i], i)
                work_index += 1
        print("Simulating %d robots" % len(work_to_complete))
        parallel_evaluate.batch_complete_work(work_to_complete)
        
        print("appending fitnesses")
        for work in work_to_complete:
            aggr_key = work.aggregate_key
            elmt_key = work.element_key
            fit = work.fitness

            self.elmts.p[elmt_key].scores.append(fit)

        print("averaging element fitnesses")
        for i in range(len(self.elmts.p)):
            fit = np.mean(self.elmts.p[i].scores)
            if (np.isnan(fit) or np.isinf(fit)):
                fit = 0
            self.elmts.p[i].fitness = fit

                
    def random_subset(self, p=0.1):
        '''
        Selects subsets of proportion p from aggregate 
            and proportion q from elements for evaluation
        '''
        assert 0 <= p <= 1, print('Input needs to be a valid proportion')
        
        N = len(self.elmts.p)
        #k = int(N*p) //Switched out for constant k
        k = 10
        
        # pre allocate work_array to avoid need to expand array upon append.
        work_to_complete = [None]*(k*(len(self.aggrs.p)+len(self.elmts.p)))
        work_index = 0 # keep track of which index in the array we are at.
        for j in range(len(self.aggrs.p)):
            aggr = self.aggrs.p[j]
            for i in np.random.choice(range(N), size=k, replace=False):
                elmt = self.elmts.p[i]
                work_to_complete[work_index] = SIM(aggr, j, elmt, i)
                work_index += 1
        for j in range(len(self.elmts.p)):
            elmt = self.elmts.p[j]
            for i in np.random.choice(range(N), size=k, replace=False):
                aggr = self.aggrs.p[i]
                work_to_complete[work_index] = SIM(aggr, i, elmt, j)
                work_index += 1
        print("Simulating %d robots" % len(work_to_complete))
        parallel_evaluate.batch_complete_work(work_to_complete)

        for work in work_to_complete:
            aggr_key = work.aggregate_key
            elmt_key = work.element_key
            fit = work.fitness

            self.aggrs.p[aggr_key].scores.append(fit)
            self.elmts.p[elmt_key].scores.append(fit)

        for j in range(len(self.aggrs.p)):
            fit = np.mean(self.aggrs.p[j].scores)
            if (np.isnan(fit) or np.isinf(fit)):
                fit = 0
            self.aggrs.p[j].fitness = fit
            
        #fitness of 0 if not selected at all (unlikely)    
        for i in range(len(self.elmts.p)):
            try:
                fit = np.mean(self.elmts.p[i].scores)
                if self.evolution_mode == COEVOLVE.COOPERATIVE_MODE:
                    pass
                elif self.evolution_mode == COEVOLVE.COMPETITIVE_MODE:
                    fit *= -1
                if (np.isnan(fit) or np.isinf(fit)):
                    fit = 0
                self.elmts.p[i].fitness = fit
            except:
                self.aggrs.p[i].fitness = 0
                
    def print_fitness(self):
        '''
        prints the top element fitness
        '''

        print('Best Element of',len(self.elmts.p),':')
        print('\n', self.elmts.p[0].fitness)

    def reset(self):
        '''
        calls reset on both populations
        '''
        
        self.aggrs.reset()
        self.elmts.reset()
        
    def selection(self):
        '''
        calls selection on elements
        '''
        self.elmts.selection()
        
    def playback(self, play_all=False):
        '''
        for review purposes, plays the best aggregate and element, with play_blind off
        '''

        fit = 0
        fit2 = -1
        aindex = 0
        aindex2 = 0
        for j in range(len(self.aggrs.p)):
            if abs(self.aggrs.p[j].fitness) > abs(fit):
                print("fit")
                print(j)
                fit = self.aggrs.p[j].fitness
                aindex = j
            elif abs(self.aggrs.p[j].fitness) > abs(fit2):
                fit2 = self.aggrs.p[j].fitness
                aindex2 = j

        if play_all:
            for e in self.elmts.p:
                aggr = self.aggrs.p[aindex]
                elmt = e
                sim = pyrosim.Simulator(eval_steps=1000, play_blind=True, play_paused=False, dt=.01)
                print("Fitness: %.2f" %aggr.evaluate(sim, elmt, debug=True))

                sim = pyrosim.Simulator(eval_steps=1000, play_blind=False, play_paused=False, dt=.01)
                try:
                    aggr.evaluate(sim, elmt, debug=True)
                except Exception as e:
                    pass
        else:

            fit = 0
            index = 0
            
            for e in range(len(self.elmts.p)):
                if self.elmts.p[e].fitness > fit:
                    index = e
                    fit = self.elmts.p[index].fitness

            aggr = self.aggrs.p[aindex]
            aggr2 = self.aggrs.p[aindex2]
            print(aindex, aindex2, index)
            elmt = self.elmts.p[index]
            sim = pyrosim.Simulator(eval_steps=1000, play_blind=False, play_paused=True, dt=.01, use_textures=False)
            aggr.evaluate(sim, elmt, debug=True)
            sim2 = pyrosim.Simulator(eval_steps=1000, play_blind=False, play_paused=True, dt=.01, use_textures=False)
            aggr2.evaluate(sim2, elmt, debug=True)
