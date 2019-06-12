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
        sim = pyrosim.Simulator(eval_steps=1500, play_blind=True, play_paused=False, dt=.01)
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
    random_subset(p=0.5, q=0.5)
        Evaluates every combination within given subsets, with size
        determined by the given proportions
    '''
    
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
        for j in self.aggrs.p:
            aggr = self.aggrs.p[j]
            for i in self.elmts.p:
                work_to_complete[work_index] = SIM(aggr, j, self.elmts.p[i], i)
                work_index += 1
        parallel_evaluate.batch_complete_work(work_to_complete)
        for work in work_to_complete:
            aggr_key = work.aggregate_key
            elmt_key = work.element_key
            fit = work.fitness

            self.aggrs.p[aggr_key].scores.append(fit)
            self.elmts.p[elmt_key].scores.append(fit)

        for j in self.aggrs.p:
            self.aggrs.p[j].fitness = np.mean(self.aggrs.p[j].scores)

        for i in self.elmts.p:
            self.elmts.p[i].fitness = np.mean(self.elmts.p[i].scores)
                
    def random_subset(self, p=0.5, q=0.5):
        '''
        Selects subsets of proportion p from aggregate 
            and proportion q from elements for evaluation
        '''
        
        assert 0 <= p <= 1, print('First input needs to be a valid proportion')
        assert 0 <= q <= 1, print('Second input needs to be a valid proportion')
        
        n1 = self.aggrs.popSize
        n2 = self.elmts.popSize
        
        aggrSub = np.random.choice(n1, size=int(np.ceil(p*n1)))
        elmtSub = np.random.choice(n2, size=int(np.ceil(q*n2)))
        
        for i in elmtSub:
            elmt = self.elmts.p[i]
            for j in aggrSub:
                aggr = self.aggrs.p[j]
                aggr.send_to_sim(sim, elmt)
                
    def print_fitness(self, g):
        '''
        prints aggrs and elmts fitness values
        '''
        
        output = 'FITNESS: GENERATION %d \n'%g
        
        output += 'AGGREGATES: '
        
        for i in self.aggrs.p:
            output += '%0.3f '%self.aggrs.p[i].fitness
            
        output += '\nELEMENTS: '
        
        for i in self.elmts.p:
            output += '%0.3f '%self.elmts.p[i].fitness
            
        print(output)
    
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
        for j in self.aggrs.p:
            if self.aggrs.p[j].fitness > fit:
                fit = self.aggrs.p[j].fitness
                aindex = j
            
        fit = 0
        for e in self.elmts.p:
            index = 0
            if self.elmts.p[e].fitness > fit:
                fit = self.elmts.p[j].fitness
                index = e
        
        aggr = self.aggrs.p[j]
        elmt = self.elmts.p[e]
        sim = pyrosim.Simulator(eval_steps=1000, play_blind=False, play_paused=True, dt=.01)
        aggr.evaluate(sim, elmt)

        


        
                
                
