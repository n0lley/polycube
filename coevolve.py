import math
import constants as c
import numpy as np
import pyrosim
from copy import deepcopy

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
    
    DT = 0.01
    TIME_STEPS = 1000
    def __init__(self, aggrs, elmts):
        '''
        initializes the two populations 
        '''
        
        self.aggrs = aggrs
        self.elmts = elmts
        self.fpi = math.ceil(len(self.aggrs.p)*.05)
        
    def exhaustive(self):
        """
        non-parallel exhaustive evaluation
        iterate through each element, evaluate that element with every aggregate, then calculate fitness.
        """
        
        parent = deepcopy(self.elmts.p)
        
        for j in range(len(self.elmts.p)):
            elmt = self.elmts.p[j]
            for i in range(len(self.aggrs.p)):
                aggr = self.aggrs.p[i]
                sim = pyrosim.Simulator(eval_steps=COEVOLVE.TIME_STEPS, play_blind=True, play_paused=False, dt=COEVOLVE.DT)
                fit = aggr.evaluate(sim, elmt, idNum = [i,j])
                self.elmts.p[j].scores.append(fit)
                
        self.calculate_fitness()
                
    def calculate_fitness(self):
        """
        Each element's fitness is set to the sum of the 5th percentile of its scores. If there are too few scores to take a 5th percentile, take the lowest.
        """
    
        for i in range(len(self.elmts.p)):
            try:
                 self.elmts.p[i].scores.sort()
                 fifth_percentile = self.elmts.p[i].scores[0:self.fpi]
                 while len(fifth_percentile) != self.fpi:
                    fifth_percentile = self.elmts.p[i].scores[0:self.fpi]
                 fit = sum(fifth_percentile)/self.fpi
                 if (np.isnan(fit) or np.isinf(fit) or len(self.elmts.p[i].scores)==0):
                     fit = 0
                 self.elmts.p[i].fitness = fit
                 print(fit, fifth_percentile)
            except Exception as e:
                print(e)
                raise(e)
                self.elmts.p[i].fitness = 0
                
    def print_fitness(self):
        '''
        prints the top element fitness
        '''

        print('Best Element:',len(self.elmts.pfront),':')
        best = 0
        besti = 0
        for i in range(len(self.elmts.pfront)):
            if self.elmts.pfront[i].fitness > best:
                best = self.elmts.pfront[i].fitness
                besti = i

        print(besti, ":", best, self.elmts.pfront[besti].scores[0:self.fpi])

    def reset(self):
        '''
        calls reset on element population
        '''
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
        eindex = 0
        for j in range(len(self.elmts.p)):
            if abs(self.elmts.p[j].fitness) > abs(fit):
                print("fit")
                print(j)
                fit = self.elmts.p[j].fitness
                eindex = j

        if play_all:
            for a in self.aggrs.p:
                aggr = a
                elmt = self.elmts.p[eindex]
                sim = pyrosim.Simulator(eval_steps=1000, play_blind=False, play_paused=False, dt=.01)
                try:
                    print(aggr.evaluate(sim, elmt, debug=True))
                except Exception as e:
                    print("error")
                    pass
        else:
            
            fit = 99999
            aindex = -1
            elmt = self.elmts.p[eindex]
            
            for i in range(len(elmt.scores)):
                if elmt.scores[i] < fit:
                    fit = elmt.scores[i]
                    aindex = i

            aggr = self.aggrs.p[aindex]
            print(aindex, eindex)
            sim = pyrosim.Simulator(eval_steps=1000, play_blind=False, play_paused=True, dt=.01, use_textures=True)
            aggr.evaluate(sim, elmt, debug=False)
