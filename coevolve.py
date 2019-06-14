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
        self.fitness = self.aggregate.evaluate(sim, self.element)

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
        
    Methods
    -------
    exhaustive()
        Evaluates with every combination of aggregate and element
    random_subset(p=0.5)
        Evaluates every aggregate with p proportion of elements
    '''

    COOPERATIVE_MODE = 0
    COMPETITIVE_MODE = 1
    DT = 0.01
    TIME_STEPS = 1500
    def __init__(self, aggrs, elmts, evolution_mode=COOPERATIVE_MODE):
        '''
        initializes the two populations 
        '''
        
        self.aggrs = aggrs
        self.elmts = elmts
        self.evolution_mode = evolution_mode
        
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

        for i in range(len(self.elmts.p)):
            fit = np.mean(self.elmts.p[i].scores)
            if self.evolution_mode == COEVOLVE.COOPERATIVE_MODE:
                pass
            elif self.evolution_mode == COEVOLVE.COMPETITIVE_MODE:
                fit *= -1
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
        k = int(N*p)
        
        # pre allocate work_array to avoid need to expand array upon append.
        work_to_complete = [None]*(len(self.aggrs.p)*k)
        work_index = 0 # keep track of which index in the array we are at.
        for j in range(len(self.aggrs.p)):
            aggr = self.aggrs.p[j]
            for i in np.random.choice(range(N), size=k, replace=False):
                elmt = self.elmts.p[i]
                work_to_complete[work_index] = SIM(aggr, j, elmt, i)
                work_index += 1
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
        prints aggrs and elmts fitness values
        '''

        print('AGGREGATES:', len(self.aggrs.p))
        print('\n'.join(list([str(indv) for indv in self.aggrs.getNonDominated()])))
        print()

        print('ELEMENTS:',len(self.elmts.p))
        print('\n'.join(list([str(indv) for indv in self.elmts.getNonDominated()])))
        print()

    def reset(self):
        '''
        calls reset on both populations
        '''
        
        self.aggrs.reset()
        self.elmts.reset()
        
    def selection(self):
        '''
        calls selection on both populations
        '''
        
        self.aggrs.selection()
        self.elmts.selection()
        
    def playback(self):
        '''
        for review purposes, plays the best aggregate and element, with play_blind off
        '''

        fit = 0
        aindex = 0
        for j in range(len(self.aggrs.p)):
            if self.aggrs.p[j].fitness > fit:
                fit = self.aggrs.p[j].fitness
                aindex = j
            
        fit = 0
        for e in range(len(self.elmts.p)):
            index = 0
            if self.elmts.p[e].fitness > fit:
                fit = self.elmts.p[j].fitness
                index = e
        
        aggr = self.aggrs.p[j]
        elmt = self.elmts.p[e]
        sim = pyrosim.Simulator(eval_steps=1000, play_blind=False, play_paused=True, dt=.01)
        aggr.evaluate(sim, elmt)

        


        
                
                
